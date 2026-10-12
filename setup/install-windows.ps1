# One-time install for Windows. Run in PowerShell from the repo root:
#   powershell -ExecutionPolicy Bypass -File setup\install-windows.ps1
$ErrorActionPreference = "Continue"

Write-Host "==> Node.js, FFmpeg, Python"
winget install -e --id OpenJS.NodeJS.LTS
winget install -e --id Gyan.FFmpeg
winget install -e --id Python.Python.3.13

# Pick up the new PATH entries in this window.
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path", "User")

Write-Host "==> faster-whisper"
python -m pip install -r requirements.txt

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
  Write-Host "==> Claude Code"
  irm https://claude.ai/install.ps1 | iex
}

Write-Host "==> HyperFrames plugin for Claude Code"
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes

Write-Host "==> Chrome for rendering"
npx --yes hyperframes@0.8.149 browser ensure

python scripts\check_setup.py --doctor
Write-Host ""
Write-Host "Done. Open a NEW terminal so your computer finds the new tools."
