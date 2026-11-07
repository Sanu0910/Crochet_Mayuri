# Mayuri'z: set up a Windows PC to work on the website.
#
# Installs Git, Python, Node.js and Claude Code, clones the website from
# GitHub, installs what the Telegram bot's tests and the price list need,
# runs the tests, and builds a fresh price list next to the project.
#
# Run it from PowerShell (no admin needed):
#   powershell -ExecutionPolicy Bypass -File .\setup-windows.ps1
#
# Safe to run again: anything already installed is skipped, and an existing
# clone is updated instead of cloned again.

param(
    [string]$Folder = "E:\Mayuri_Crochet_Web",
    [string]$Name   = "Sanu Roy",
    [string]$Email  = "sanuroybhs@gmail.com"
)

$ErrorActionPreference = "Stop"
$Repo = "https://github.com/Sanu0910/Crochet_Mayuri.git"
$Project = Join-Path $Folder "Crochet_Mayuri"

function Step($text) { Write-Host "`n== $text" -ForegroundColor Cyan }
function Ok($text)   { Write-Host "   OK  $text" -ForegroundColor Green }
function Warn($text) { Write-Host "   !!  $text" -ForegroundColor Yellow }

function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User") + ";" +
                "$env:USERPROFILE\.local\bin"
}

function Have($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

function Install-WithWinget($id, $cmd, $label) {
    if (Have $cmd) { Ok "$label already installed"; return }
    if (-not (Have "winget")) {
        throw "winget is missing. Install 'App Installer' from the Microsoft Store, then run this again."
    }
    Write-Host "   Installing $label ..."
    winget install -e --id $id --silent --accept-source-agreements --accept-package-agreements | Out-Host
    Refresh-Path
    if (Have $cmd) { Ok "$label installed" } else { throw "$label did not install. Close PowerShell, open a new one and run this again." }
}

Refresh-Path

Step "1/6  Git, Python and Node.js"
Install-WithWinget "Git.Git"             "git"    "Git"
Install-WithWinget "Python.Python.3.12"  "py"     "Python"
Install-WithWinget "OpenJS.NodeJS.LTS"   "node"   "Node.js"

Step "2/6  Claude Code"
if (Have "claude") {
    Ok "Claude Code already installed"
} else {
    Invoke-RestMethod https://claude.ai/install.ps1 | Invoke-Expression
    $bin = "$env:USERPROFILE\.local\bin"
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$bin*") {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$bin", "User")
    }
    Refresh-Path
    if (Have "claude") { Ok "Claude Code installed" } else { Warn "Claude Code installed, but open a NEW PowerShell window before typing 'claude'." }
}

Step "3/6  The website from GitHub"
New-Item -ItemType Directory -Force -Path $Folder | Out-Null
if (Test-Path (Join-Path $Project ".git")) {
    git -C $Project pull origin main | Out-Host
    Ok "Updated $Project"
} else {
    git clone $Repo $Project | Out-Host
    Ok "Cloned into $Project"
}
git -C $Project config user.name  $Name
git -C $Project config user.email $Email
git -C $Project config core.autocrlf true
Ok "Git will commit as $Name <$Email>"

Step "4/6  Python packages for the bot tests and the price list"
py -m pip install --quiet --upgrade pip
py -m pip install --quiet httpx==0.28.1 Pillow==11.1.0 openpyxl
Ok "httpx, Pillow, openpyxl"

Step "5/6  Bot tests"
Push-Location (Join-Path $Project "bot")
try {
    py test_site_edit.py | Select-Object -Last 1 | Out-Host
    py test_publish.py   | Select-Object -Last 1 | Out-Host
} finally { Pop-Location }

Step "6/6  Fresh price list (kept OUTSIDE the project, it holds your costs)"
$Sheet = Join-Path $Folder "Mayuriz-Price-List-new.xlsx"
py (Join-Path $Project "bot\price_list.py") (Join-Path $Project "index.html") $Sheet | Out-Host
Ok "Built $Sheet  (an empty one: copy prices across from your filled copy)"

Write-Host "`nAll set." -ForegroundColor Green
Write-Host "Next time, open PowerShell and run:"
Write-Host "   cd `"$Project`""
Write-Host "   git pull origin main"
Write-Host "   claude"
Write-Host "To see the site on this PC:  py -m http.server 8000   then open http://localhost:8000"
Write-Host "The old ZIP copy (Crochet_Mayuri-main) can't push to GitHub. Delete it once you've copied out anything you changed."
