"""Old-film look: colour fade, gate weave, flicker, grain, dust, scratches, vignette.

    python3 oldfilm.py raw/temple.mp4 -o work/film.mp4 --look kodachrome
    python3 oldfilm.py raw/temple.mp4 --stills 3,22,50 --look sepia      # check frames only

Every frame is a pure function of its index (seeded), so re-renders match.
"""
import argparse, subprocess, sys, json
import numpy as np
import cv2

LOOKS = {
    # gain per channel (R,G,B), saturation, black lift, white roll-off, contrast
    "kodachrome": dict(gain=(1.06, 1.0, 0.86), sat=0.75, lift=0.05, roll=0.91, con=1.12, tint=(0.04, 0.02, -0.02)),
    "sepia":      dict(gain=(1.0, 1.0, 1.0),  sat=0.0,  lift=0.09, roll=0.88, con=1.12, tint=None),
}
SEPIA = np.array([1.07, 0.94, 0.74], np.float32)


def vignette(h, w, k=0.55):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / np.sqrt(2)
    return (1 - k * np.clip(r, 0, 1) ** 2.2)[..., None]


def process(img, i, look, vig, fps):
    h, w = img.shape[:2]
    rng = np.random.default_rng(1000 + i)
    L = LOOKS[look]
    f = img[..., ::-1].astype(np.float32) / 255.0             # RGB 0..1

    # gate weave: slow wobble + tiny per-frame jitter, then slight overscan so edges never show
    t = i / fps
    dx = 2.2 * np.sin(t * 1.7) + rng.normal(0, 0.6)
    dy = 3.0 * np.sin(t * 2.3 + 1) + rng.normal(0, 0.8)
    M = np.float32([[1.03, 0, -w * 0.015 + dx], [0, 1.03, -h * 0.015 + dy]])
    f = cv2.warpAffine(f, M, (w, h), borderMode=cv2.BORDER_REFLECT)

    # soften a touch (old lenses / print generation)
    f = cv2.GaussianBlur(f, (0, 0), 0.9)

    # colour
    lum = (f @ np.float32([0.299, 0.587, 0.114]))[..., None]
    if look == "sepia":
        f = lum * SEPIA
    else:
        f = lum + (f - lum) * L["sat"]
        f = f * np.float32(L["gain"]) + np.float32(L["tint"]) * (1 - lum)
    f = (f - 0.5) * L["con"] + 0.5
    f = L["lift"] + f * (L["roll"] - L["lift"])               # faded blacks, soft whites

    # flicker (exposure breathing per frame)
    f *= 1 + 0.035 * np.sin(t * 13.0) * np.sin(t * 3.1) + rng.normal(0, 0.012)

    # grain (luma, slightly blurred so it's clumpy like film)
    g = rng.normal(0, 1, (h // 2, w // 2)).astype(np.float32)
    g = cv2.resize(g, (w, h), interpolation=cv2.INTER_LINEAR)
    f += g[..., None] * 0.045

    f *= vig

    # dust specks (dark and light), a few per frame
    out = np.clip(f * 255, 0, 255).astype(np.uint8)
    for _ in range(rng.integers(2, 9)):
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        r = int(rng.integers(1, 4))
        col = (25, 20, 15) if rng.random() < 0.75 else (235, 228, 210)
        if rng.random() < 0.3:     # hair / fibre
            pts = np.cumsum(rng.normal(0, 4, (12, 2)), 0).astype(np.int32) + [x, y]
            cv2.polylines(out, [pts], False, col, 1, cv2.LINE_AA)
        else:
            cv2.circle(out, (x, y), r, col, -1, cv2.LINE_AA)

    # vertical scratches that persist for a while (seeded by time block, not by frame)
    blk = np.random.default_rng(77 + i // 18)
    if blk.random() < 0.55:
        sx = int(blk.integers(int(w * 0.1), int(w * 0.9))) + int(rng.integers(-2, 3))
        a = 0.25 + 0.2 * rng.random()
        ov = out.copy()
        cv2.line(ov, (sx, 0), (sx + int(blk.integers(-10, 10)), h), (225, 220, 205), 1, cv2.LINE_AA)
        out = cv2.addWeighted(ov, a, out, 1 - a, 0)

    return out[..., ::-1]                                       # back to BGR


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("-o", "--out", default="work/film.mp4")
    ap.add_argument("--look", default="kodachrome", choices=LOOKS)
    ap.add_argument("--stills", help="comma-separated seconds; writes work/still_<look>_<t>.png and exits")
    a = ap.parse_args()

    cap = cv2.VideoCapture(a.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    Y0, Y1 = 98, 992                     # picture area inside the source's baked-in letterbox (cropdetect)
    vig = vignette(Y1 - Y0, w)

    def frame(img, i):
        out = np.zeros_like(img)
        out[Y0:Y1] = process(img[Y0:Y1], i, a.look, vig, fps)
        return out

    if a.stills:
        for s in a.stills.split(","):
            i = int(float(s) * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ok, img = cap.read()
            cv2.imwrite(f"work/still_{a.look}_{s}.png", frame(img, i))
        return

    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}",
                            "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                            "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    i = 0
    while True:
        ok, img = cap.read()
        if not ok:
            break
        enc.stdin.write(frame(img, i).tobytes())
        i += 1
        if i % 240 == 0:
            print(f"  {i / fps:.0f}s", flush=True)
    enc.stdin.close(); enc.wait()
    print(f"film look -> {a.out} ({i} frames)")


if __name__ == "__main__":
    main()
