# Mayuri'z: run n8n (Instagram + Facebook auto-posting) on this PC, starting by
# itself at every logon, hidden, and restarting if it stops.
#
#   pwsh tools/install-n8n.ps1           # install / refresh and start
#   pwsh tools/install-n8n.ps1 -Remove   # stop and remove
#
# Needs: E:\dev\n8n (npm install n8n), E:\dev\node24 (portable Node 24),
# %USERPROFILE%\.mayuriz\bot.env and meta.env (keys; never committed).
# Keys for meta.env: see tools/meta-setup.mjs. Log: %LOCALAPPDATA%\MayurizN8n\n8n.log

param([switch]$Remove)
$ErrorActionPreference = "Stop"
$TaskName = "Mayuriz n8n auto-post"
$Runner   = Join-Path $PSScriptRoot "run-n8n.ps1"

function Ok($t)   { Write-Host "   OK  $t" -ForegroundColor Green }
function Warn($t) { Write-Host "   !!  $t" -ForegroundColor Yellow }

if ($Remove) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Ok "Stopped and removed the '$TaskName' task"
    }
    exit 0
}

foreach ($p in "E:\dev\n8n\node_modules\.bin\n8n.cmd", "E:\dev\node24\node.exe",
               (Join-Path $env:USERPROFILE ".mayuriz\bot.env"), (Join-Path $env:USERPROFILE ".mayuriz\meta.env")) {
    if (-not (Test-Path $p)) { Warn "Missing $p"; exit 1 }
}
if (-not (Select-String -Path (Join-Path $env:USERPROFILE ".mayuriz\meta.env") -Pattern '^META_PAGE_TOKEN=.+' -Quiet)) {
    Warn "No META_PAGE_TOKEN yet: run  node tools/meta-setup.mjs  first."; exit 1
}

$shell = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
if (-not $shell) { $shell = "powershell.exe" }
$action   = New-ScheduledTaskAction -Execute $shell `
            -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Runner`""
$trigger  = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
            -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
            -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
    -Description "Posts new mayurisyarntales.online pieces to Facebook and Instagram (n8n)" -Force | Out-Null
Ok "Task '$TaskName' starts n8n at every logon"

Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
Start-ScheduledTask -TaskName $TaskName
Ok "n8n started. Editor: http://localhost:5678  Log: $env:LOCALAPPDATA\MayurizN8n\n8n.log"
