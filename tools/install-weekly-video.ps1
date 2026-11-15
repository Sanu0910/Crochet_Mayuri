# Mayuri'z: make next week's two promo videos every Sunday morning, using
# tools/weekly_video.py. Nothing is posted: the videos, covers and captions
# land in %USERPROFILE%\Videos\Mayuriz Weekly\<week>\ for review, and the team
# gets a Telegram note when they're ready.
#
#   pwsh tools/install-weekly-video.ps1                # Sundays 10:00
#   pwsh tools/install-weekly-video.ps1 -Day Saturday -At 21:00
#   pwsh tools/install-weekly-video.ps1 -Remove
#
# Needs: Node + video/node_modules (cd video; npm install), ffmpeg
# (winget install Gyan.FFmpeg), music in %USERPROFILE%\Music\Copyright Free Music
# (see tools/video_music.json). The Python venv is created here if missing.

param([string]$Day = "Sunday", [string]$At = "10:00", [switch]$Remove)
$ErrorActionPreference = "Stop"
$TaskName = "Mayuriz weekly videos"
$Repo     = Split-Path $PSScriptRoot
$Venv     = Join-Path $env:LOCALAPPDATA "MayurizVideo\venv"

if ($Remove) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "   OK  Removed '$TaskName'" -ForegroundColor Green
    exit 0
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
$cmd = "git -C '$Repo' pull --quiet origin main; & '$Venv\Scripts\python.exe' -X utf8 '$Repo\tools\weekly_video.py' *>> '$env:LOCALAPPDATA\MayurizVideo\weekly.log'"
$pwsh = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
if (-not $pwsh) { $pwsh = (Get-Command powershell).Source }
$action   = New-ScheduledTaskAction -Execute $pwsh -Argument "-NoProfile -Command `"$cmd`"" -WorkingDirectory $Repo
$trigger  = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Day -At $At
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
            -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
    -Description "Renders next week's two Mayuri'z promo videos ($Day $At)" -Force | Out-Null
Write-Host "   OK  '$TaskName' runs every $Day at $At" -ForegroundColor Green
