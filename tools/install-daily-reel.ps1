# Mayuri'z: one short animated product reel every day, posted to Instagram
# and Facebook at 18:00 IST, using tools/daily_reel.py. The task starts at
# 16:45 so the render (~10 min on this PC) is done well before; post_video.py
# then waits and publishes on time, and the team gets a Telegram note.
#
#   pwsh tools/install-daily-reel.ps1                    # render 16:45, post 18:00
#   pwsh tools/install-daily-reel.ps1 -Start 17:30 -Post 19:00
#   pwsh tools/install-daily-reel.ps1 -Remove
#
# Needs: the venv + video/node_modules + ffmpeg + music (see video/README.md),
# keys in %USERPROFILE%\.mayuriz\ (meta.env, woopsocial.env, bot.env).
# Log: %LOCALAPPDATA%\MayurizVideo\daily.log

param([string]$Start = "16:45", [string]$Post = "18:00", [switch]$Remove)
$ErrorActionPreference = "Stop"
$TaskName = "Mayuriz daily reel"
$Repo     = Split-Path $PSScriptRoot
$Venv     = Join-Path $env:LOCALAPPDATA "MayurizVideo\venv"

if ($Remove) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "   OK  Removed '$TaskName'" -ForegroundColor Green
    exit 0
}
foreach ($f in "meta.env", "woopsocial.env", "bot.env") {
    if (-not (Test-Path (Join-Path $env:USERPROFILE ".mayuriz\$f"))) { Write-Host "   !!  Missing .mayuriz\$f" -ForegroundColor Yellow; exit 1 }
}
if (-not (Test-Path "$Venv\Scripts\python.exe")) {
    Write-Host "   ..  creating $Venv (numpy + pillow)"
    py -m venv $Venv
    & "$Venv\Scripts\python.exe" -m pip install --quiet numpy pillow
}
if (-not (Test-Path (Join-Path $Repo "video\node_modules"))) {
    Write-Host "   !!  Run 'npm install' in video\ first" -ForegroundColor Yellow; exit 1
}

# Pull first so the newest pieces from the Telegram bot are included.
$cmd = "git -C '$Repo' pull --quiet origin main; & '$Venv\Scripts\python.exe' -X utf8 '$Repo\tools\daily_reel.py' --at $Post *>> '$env:LOCALAPPDATA\MayurizVideo\daily.log'"
$pwsh = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
if (-not $pwsh) { $pwsh = (Get-Command powershell).Source }
$action   = New-ScheduledTaskAction -Execute $pwsh -Argument "-NoProfile -Command `"$cmd`"" -WorkingDirectory $Repo
$trigger  = New-ScheduledTaskTrigger -Daily -At $Start
# StartWhenAvailable: PC off at 16:45 -> runs when it's back; posts right away if 18:00 has passed.
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
            -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 6) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
    -Description "Renders and posts one Mayuri'z product reel to Instagram + Facebook (post $Post)" -Force | Out-Null
Write-Host "   OK  '$TaskName' renders daily at $Start and posts at $Post" -ForegroundColor Green
