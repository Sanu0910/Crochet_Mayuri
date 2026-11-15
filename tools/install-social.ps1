# Mayuri'z: post one product poster to Instagram + Facebook every day at
# 13:00 and 20:00 (this PC's clock, IST), using tools/social_daily.py.
#
#   pwsh tools/install-social.ps1                 # install / refresh
#   pwsh tools/install-social.ps1 -Times 12:30,19:30
#   pwsh tools/install-social.ps1 -Remove
#
# Keys: %USERPROFILE%\.mayuriz\meta.env, woopsocial.env, bot.env (never committed).
# Log and state: %LOCALAPPDATA%\MayurizSocial\ (social.log, state.json, posters\, todo.txt)

param([string[]]$Times = @("13:00", "20:00"), [switch]$Remove)
$ErrorActionPreference = "Stop"
$TaskName = "Mayuriz daily social post"
$Script   = Join-Path $PSScriptRoot "social_daily.py"

if ($Remove) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "   OK  Removed '$TaskName'" -ForegroundColor Green
    exit 0
}
foreach ($f in "meta.env", "woopsocial.env", "bot.env") {
    if (-not (Test-Path (Join-Path $env:USERPROFILE ".mayuriz\$f"))) { Write-Host "   !!  Missing .mayuriz\$f" -ForegroundColor Yellow; exit 1 }
}
$py = (Get-Command py -ErrorAction SilentlyContinue).Source
if (-not $py) { $py = (Get-Command python).Source }

$action   = New-ScheduledTaskAction -Execute $py -Argument "`"$Script`"" -WorkingDirectory (Split-Path $PSScriptRoot)
$triggers = $Times | ForEach-Object { New-ScheduledTaskTrigger -Daily -At $_ }
# StartWhenAvailable: if the PC was off at post time, post soon after it's back on.
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
            -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 15) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $triggers -Settings $settings `
    -Description "Posts one Mayuri'z product poster to Instagram + Facebook ($($Times -join ', '))" -Force | Out-Null
Write-Host "   OK  '$TaskName' posts daily at $($Times -join ' and ')" -ForegroundColor Green
