# Mayuri'z: make this PC the Telegram bot, starting by itself at every logon.
#
#   powershell -ExecutionPolicy Bypass -File tools\install-bot.ps1            # install / restart
#   powershell -ExecutionPolicy Bypass -File tools\install-bot.ps1 -Remove    # hand back to GitHub
#
# Install: makes %USERPROFILE%\.mayuriz\bot.env for the Telegram token (opens
# it in Notepad the first time), registers the "Mayuriz Telegram bot" task,
# switches off the GitHub "Telegram uploader" workflow so the two don't fight
# over messages, and starts the bot.
#
# -Remove: stops and deletes the task and switches the GitHub workflow back
# on. The Cloudflare Worker also needs its webhook set again; see
# bot/README.md.

param([switch]$Remove)

$ErrorActionPreference = "Stop"
$Repo     = "Sanu0910/Crochet_Mayuri"
$TaskName = "Mayuriz Telegram bot"
$Runner   = Join-Path $PSScriptRoot "run-bot.ps1"
$Config   = Join-Path $env:USERPROFILE ".mayuriz\bot.env"

function Ok($t)   { Write-Host "   OK  $t" -ForegroundColor Green }
function Warn($t) { Write-Host "   !!  $t" -ForegroundColor Yellow }

function GitHub-Workflow($action) {
    $answer = "protocol=https`nhost=github.com`n`n" | git credential fill 2>$null
    $token = ($answer | Where-Object { $_ -like "password=*" }) -replace '^password=', ''
    if (-not $token) { Warn "No GitHub login on this PC; $action the 'Telegram uploader' workflow by hand in the Actions tab."; return }
    try {
        Invoke-RestMethod -Method Put `
            -Uri "https://api.github.com/repos/$Repo/actions/workflows/telegram-uploader.yml/$action" `
            -Headers @{ Authorization = "Bearer $token"; Accept = "application/vnd.github+json"; "User-Agent" = "mayuriz-bot" } | Out-Null
        Ok "GitHub 'Telegram uploader' workflow: $($action)d"
    } catch { Warn "Couldn't $action the GitHub workflow: $($_.Exception.Message)" }
}

if ($Remove) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Ok "Stopped and removed the '$TaskName' task"
    }
    GitHub-Workflow "enable"
    Warn "Set the Cloudflare Worker's webhook again (bot/README.md, step 3) for instant replies."
    exit 0
}

# 1. The token file, outside the repository.
if (-not (Test-Path $Config)) {
    New-Item -ItemType Directory -Force -Path (Split-Path $Config) | Out-Null
    Set-Content -Path $Config -Encoding ascii -Value @(
        "# Mayuri'z Telegram bot. This file stays on this PC: never commit it.",
        "# Get the token from @BotFather (/mybots -> the bot -> API Token).",
        "TELEGRAM_TOKEN=paste-the-token-here",
        "ALLOWED_USER_IDS=924868395,5770732970"
    )
    Ok "Made $Config"
}
if ((Get-Content $Config -Raw) -match "TELEGRAM_TOKEN=paste") {
    Warn "Put the bot token into the file that just opened, save it, then run this again."
    Start-Process notepad.exe $Config
    exit 1
}

# 2. A logon task that runs the bot hidden, and restarts it if it stops.
$action   = New-ScheduledTaskAction -Execute "powershell.exe" `
            -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Runner`""
$trigger  = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
            -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
            -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
    -Description "Publishes photos sent to the Mayuri'z Telegram bot to mayurisyarntales.online" -Force | Out-Null
Ok "Task '$TaskName' starts the bot at every logon"

# 3. Only one reader of the bot at a time.
GitHub-Workflow "disable"

# 4. Go.
Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
Start-ScheduledTask -TaskName $TaskName
Ok "Bot started. Log: $env:LOCALAPPDATA\MayurizBot\bot.log"
