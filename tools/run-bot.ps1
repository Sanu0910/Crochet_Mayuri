# Mayuri'z: run the Telegram uploader on this PC instead of on GitHub.
#
# Does what .github/workflows/telegram-uploader.yml does, in a loop:
#   check Telegram -> resize photo, edit index.html + theme.ts -> commit ->
#   push to main -> ask Pages to rebuild -> finish the message in Telegram.
#
# It works in its own copy of the site (%LOCALAPPDATA%\MayurizBot\site), never
# in the folder you edit by hand, so it can't trample your unsaved work.
#
# Secrets stay on this PC, outside the repository:
#   %USERPROFILE%\.mayuriz\bot.env    TELEGRAM_TOKEN=...   (from @BotFather)
#                                     ALLOWED_USER_IDS=... (optional)
#   GitHub login: Windows' Git Credential Manager (the one `git push` uses).
#
# Run by hand:   powershell -ExecutionPolicy Bypass -File tools\run-bot.ps1
# Started automatically at logon by the "Mayuriz Telegram bot" scheduled task
# (tools\install-bot.ps1). Log: %LOCALAPPDATA%\MayurizBot\bot.log
#
# Only one thing may read the bot at a time. This deletes the Telegram
# webhook (the Cloudflare Worker) on start, and the GitHub workflow should be
# disabled while this runs. See bot/README.md, "Running it on a PC".

param([int]$EverySeconds = 15)   # pause after an error before trying again

$ErrorActionPreference = "Stop"
$Repo    = "Sanu0910/Crochet_Mayuri"
$Branch  = "main"
$SiteUrl = "https://mayurisyarntales.online/"
$Home_   = Join-Path $env:LOCALAPPDATA "MayurizBot"
$Site    = Join-Path $Home_ "site"
$LogFile = Join-Path $Home_ "bot.log"
$Tmp     = Join-Path $Home_ "tmp"
$Config  = Join-Path $env:USERPROFILE ".mayuriz\bot.env"

New-Item -ItemType Directory -Force -Path $Home_, $Tmp | Out-Null

function Log($text) {
    $line = "{0:yyyy-MM-dd HH:mm:ss}  {1}" -f (Get-Date), $text
    Add-Content -Path $LogFile -Value $line -Encoding utf8
    Write-Host $line
}

# Keep the log from growing forever.
if ((Test-Path $LogFile) -and (Get-Item $LogFile).Length -gt 5MB) {
    Move-Item -Force $LogFile "$LogFile.old"
}

# One copy at a time: two pollers would fight over the same messages.
$mutex = New-Object System.Threading.Mutex($false, "Global\MayurizTelegramBot")
if (-not $mutex.WaitOne(0)) { Write-Host "The bot is already running."; exit 0 }

# --- tools on PATH (a logon task doesn't always get the user's PATH) ---
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [Environment]::GetEnvironmentVariable("Path", "User")
$Python = (Get-Command py -ErrorAction SilentlyContinue).Source
if (-not $Python) { Log "Python ('py') is not installed. Run tools\setup-windows.ps1."; exit 1 }
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

# --- secrets ------------------------------------------------------------
if (-not (Test-Path $Config)) { Log "Missing $Config (needs TELEGRAM_TOKEN=...)."; exit 1 }
$settings = @{}
foreach ($line in Get-Content $Config) {
    if ($line -match '^\s*([A-Z_]+)\s*=\s*(.*?)\s*$') { $settings[$Matches[1]] = $Matches[2] }
}
$Token = $settings["TELEGRAM_TOKEN"]
if (-not $Token -or $Token -like "*paste*") { Log "TELEGRAM_TOKEN is not filled in in $Config."; exit 1 }
$Allowed = if ($settings["ALLOWED_USER_IDS"]) { $settings["ALLOWED_USER_IDS"] } else { "924868395,5770732970" }

function GitHub-Token {
    # The same login `git push` uses, read from Windows' credential manager.
    $answer = "protocol=https`nhost=github.com`n`n" | git credential fill 2>$null
    foreach ($l in $answer) { if ($l -like "password=*") { return $l.Substring(9) } }
    return ""
}

# --- the bot's own copy of the site ---------------------------------------
if (-not (Test-Path (Join-Path $Site ".git"))) {
    Log "Cloning the site into $Site ..."
    git clone --quiet --branch $Branch "https://github.com/$Repo.git" $Site 2>&1 | ForEach-Object { Log "$_" }
}
git -C $Site config core.autocrlf true
git -C $Site config user.name  "Sanu Roy"
git -C $Site config user.email "sanuroybhs@gmail.com"

# Telegram allows a webhook OR polling, never both. Take over from the Worker.
try {
    $info = Invoke-RestMethod "https://api.telegram.org/bot$Token/getWebhookInfo"
    if ($info.result.url) {
        Invoke-RestMethod "https://api.telegram.org/bot$Token/deleteWebhook" | Out-Null
        Log "Telegram webhook removed (was the Cloudflare Worker); this PC now handles the bot."
    }
    $me = Invoke-RestMethod "https://api.telegram.org/bot$Token/getMe"
    Log "Running as @$($me.result.username), pushing to $Repo@$Branch."
} catch {
    Log "Can't reach Telegram with that token: $($_.Exception.Message)"
    exit 1
}

$CommitMsg = Join-Path $Tmp "commit-msg.txt"
$Announce  = Join-Path $Tmp "announce.json"

function Run-Python($script, [hashtable]$vars) {
    foreach ($k in $vars.Keys) { Set-Item "Env:$k" $vars[$k] }
    Push-Location (Join-Path $Site "bot")
    try {
        $out = & $Python $script 2>&1
        foreach ($l in $out) {
            $t = "$l"
            if ($t -and $t -notmatch "nothing to publish|update\(s\) waiting: 0|^INFO 0 update") { Log "  $t" }
        }
        return $LASTEXITCODE
    } finally {
        Pop-Location
        foreach ($k in $vars.Keys) { Remove-Item "Env:$k" -ErrorAction SilentlyContinue }
    }
}

function Publish-Once {
    # Wait (up to 25 s) for anything to arrive. This only peeks: nothing is
    # marked handled until poll_once.py has dealt with it, so an upload is
    # never lost if this PC goes off halfway. Replies are instant, and GitHub
    # is only touched when there is actually something to do.
    $peek = Invoke-RestMethod -TimeoutSec 60 `
        "https://api.telegram.org/bot$Token/getUpdates?timeout=25&limit=1"
    if (-not $peek.result -or @($peek.result).Count -eq 0) { return }

    # Start from exactly what is on GitHub, so the bot's code and the product
    # list are always current (including edits pushed from other PCs).
    git -C $Site fetch --quiet origin $Branch
    git -C $Site reset --quiet --hard "origin/$Branch"
    git -C $Site clean --quiet -fd
    Remove-Item $CommitMsg, $Announce -ErrorAction SilentlyContinue

    $ghToken = GitHub-Token
    $code = Run-Python "poll_once.py" @{
        TELEGRAM_TOKEN   = $Token
        GITHUB_TOKEN     = $ghToken
        GITHUB_REPO      = $Repo
        ALLOWED_USER_IDS = $Allowed
        GIT_BRANCH       = $Branch
        SITE_URL         = $SiteUrl
        COMMIT_MSG_FILE  = $CommitMsg
        ANNOUNCE_FILE    = $Announce
        PUSHED_UPDATE    = ""
    }
    if ($code -ne 0) { Log "poll_once.py exited with $code"; return }
    if (-not (Test-Path $CommitMsg)) { return }

    git -C $Site add -A
    git -C $Site diff --cached --quiet
    if ($LASTEXITCODE -eq 0) { Log "A message arrived but changed nothing."; return }
    git -C $Site commit --quiet --file $CommitMsg

    $pushed = $false
    for ($i = 1; $i -le 3 -and -not $pushed; $i++) {
        git -C $Site push --quiet origin "HEAD:$Branch" 2>&1 | ForEach-Object { Log "  $_" }
        if ($LASTEXITCODE -eq 0) { $pushed = $true; break }
        Log "Push rejected (try $i), catching up with GitHub and retrying."
        git -C $Site pull --quiet --rebase origin $Branch 2>&1 | ForEach-Object { Log "  $_" }
        if ($LASTEXITCODE -ne 0) { git -C $Site rebase --abort 2>$null; break }
    }
    if (-not $pushed) { Log "Could not push. The change is NOT live; send the photo again later."; return }

    $sha = (git -C $Site rev-parse HEAD).Trim()
    Log "Pushed $($sha.Substring(0,7)): $((Get-Content $CommitMsg -TotalCount 1))"

    # A push made with your own login rebuilds Pages by itself; asking as well
    # gives announce.py a real answer to report.
    $pages = ""
    if ($ghToken) {
        try {
            $r = Invoke-WebRequest -UseBasicParsing -Method Post `
                -Uri "https://api.github.com/repos/$Repo/pages/builds" `
                -Headers @{ Authorization = "Bearer $ghToken"; Accept = "application/vnd.github+json"; "User-Agent" = "mayuriz-bot" }
            $pages = "$($r.StatusCode)"
        } catch { $pages = "" }   # announce.py then says "queued": the push itself starts a build
    }

    Run-Python "announce.py" @{
        TELEGRAM_TOKEN = $Token
        GITHUB_REPO    = $Repo
        SITE_URL       = $SiteUrl
        ANNOUNCE_FILE  = $Announce
        COMMIT_SHA     = $sha
        PAGES_STATUS   = $pages
    } | Out-Null
}

while ($true) {
    try { Publish-Once; Start-Sleep -Seconds 1 }
    catch {
        # No internet, PC waking from sleep, GitHub hiccup: wait and carry on.
        Log "Error: $($_.Exception.Message)"
        Start-Sleep -Seconds $EverySeconds
    }
}
