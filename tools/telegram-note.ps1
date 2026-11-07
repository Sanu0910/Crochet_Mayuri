# Posts a short update note to the team's Telegram group
# ("Mayuri's Yarn Tales Updates") through the shop bot.
#
#   pwsh tools/telegram-note.ps1 "Welcome popup is live" "Shows the 2 newest pieces"
#
# Each argument becomes one bullet line. Sending is done by bot/send_pack.py;
# this only loads the token from %USERPROFILE%\.mayuriz\bot.env (never printed).
param([Parameter(Mandatory, ValueFromRemainingArguments)][string[]]$Lines)

$ErrorActionPreference = "Stop"
$Config = Join-Path $env:USERPROFILE ".mayuriz\bot.env"
if (-not (Test-Path $Config)) { throw "No bot settings at $Config" }

$settings = @{}
foreach ($line in Get-Content $Config) {
    if ($line -match '^\s*([A-Z_]+)\s*=\s*(.*)$') { $settings[$Matches[1]] = $Matches[2].Trim() }
}
if (-not $settings["TELEGRAM_TOKEN"]) { throw "TELEGRAM_TOKEN missing in $Config" }
$Chats = if ($settings["REPORT_CHATS"]) { $settings["REPORT_CHATS"] } else { "-1003843804840" }

function Escape([string]$s) { $s.Replace('&', '&amp;').Replace('<', '&lt;').Replace('>', '&gt;') }

$date = Get-Date -Format "d MMM yyyy, h:mm tt"
$body = ($Lines | ForEach-Object { "• " + (Escape $_) }) -join "`n"
$text = "🧶 <b>Mayuri'z · Update</b>  <i>$date</i>`n`n$body"

$env:PYTHONUTF8 = "1"
$env:PACK = ConvertTo-Json -Compress -InputObject @(@{ text = $text })
$env:TELEGRAM_TOKEN = $settings["TELEGRAM_TOKEN"]
$sender = Join-Path $PSScriptRoot "..\bot\send_pack.py"
$failed = $false
try {
    foreach ($id in $Chats.Split(",")) {
        $env:CHAT_ID = $id.Trim()
        $out = & py $sender 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0) {
            $failed = $true
            Write-Output "Note NOT sent to $($env:CHAT_ID): $($out -replace 'bot[0-9]+:[A-Za-z0-9_-]+', 'bot<token>')"
        } else {
            Write-Output "Note sent to $($env:CHAT_ID)"
        }
    }
} finally {
    Remove-Item Env:TELEGRAM_TOKEN, Env:PACK, Env:CHAT_ID -ErrorAction SilentlyContinue
}
if ($failed) { exit 1 }
