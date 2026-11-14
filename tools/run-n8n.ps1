# Starts n8n for Mayuri'z (Instagram + Facebook auto-posting).
# n8n lives outside the repo in E:\dev\n8n and needs the portable Node 24 in
# E:\dev\node24 (its native parts don't build on newer Node). Keys come from
# %USERPROFILE%\.mayuriz\bot.env and meta.env; they are passed to n8n as
# environment variables and never written into the repo.
#
#   pwsh tools/run-n8n.ps1            # start n8n, editor at http://localhost:5678
#   pwsh tools/run-n8n.ps1 -Import    # (re)import tools/n8n/shop-autopost.json first

param([switch]$Import)
$ErrorActionPreference = "Stop"

$N8nDir = "E:\dev\n8n"
$NodeDir = "E:\dev\node24"
$Workflow = Join-Path $PSScriptRoot "n8n\shop-autopost.json"

foreach ($f in "bot.env", "meta.env") {
    $p = Join-Path $env:USERPROFILE ".mayuriz\$f"
    if (-not (Test-Path $p)) { Write-Output "Missing $p"; exit 1 }
    foreach ($line in Get-Content $p) {
        if ($line -match '^\s*([A-Z_][A-Z0-9_]*)\s*=\s*(.*)$') {
            Set-Item -Path "Env:$($Matches[1])" -Value $Matches[2].Trim()
        }
    }
}

$env:PATH = "$NodeDir;$env:PATH"
$env:N8N_DIAGNOSTICS_ENABLED = "false"
$env:N8N_PERSONALIZATION_ENABLED = "false"
$env:N8N_BLOCK_ENV_ACCESS_IN_NODE = "false"   # the workflow reads the keys above
$env:GENERIC_TIMEZONE = "Asia/Kolkata"
$env:NODE_OPTIONS = "--max-old-space-size=1024"
$LogDir = Join-Path $env:LOCALAPPDATA "MayurizN8n"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$env:N8N_LOG_OUTPUT = "console,file"
$env:N8N_LOG_FILE_LOCATION = Join-Path $LogDir "n8n.log"
$env:N8N_LOG_FILE_MAXSIZE = "10"      # MB per file
$env:N8N_LOG_FILE_MAXCOUNT = "3"
$n8n = Join-Path $N8nDir "node_modules\.bin\n8n.cmd"

Set-Location $N8nDir
if ($Import) {
    & $n8n import:workflow --input="$Workflow"
    & $n8n publish:workflow --id=mzShopAutopost1
}
& $n8n start
