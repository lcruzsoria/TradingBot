# Arranca TradingBot.
#   1. Lee tradingbot.env y pasa sus valores a la app como variables de entorno.
#   2. Si APP_AUTO_UPDATE=true, trae el codigo nuevo de GitHub (git pull) antes de arrancar.
#   3. Lanza la app con uv (crea el entorno e instala dependencias la primera vez).
#
#   .\scripts\run.ps1                 -> cuenta por defecto del .env de MT5
#   .\scripts\run.ps1 --demo          -> datos sinteticos, sin MT5
#   .\scripts\run.ps1 --theme blanco  -> otra paleta solo esta vez
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

$EnvFile = Join-Path $Root "tradingbot.env"
$cfg = @{}
if (Test-Path $EnvFile) {
    foreach ($line in Get-Content $EnvFile -Encoding UTF8) {
        if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$') {
            $cfg[$matches[1]] = $matches[2]
            Set-Item -Path "Env:$($matches[1])" -Value $matches[2]
        }
    }
    Write-Host "Configuracion: tradingbot.env (paleta: $($cfg['UI_THEME']))"
} else {
    Write-Host "Aviso: no existe tradingbot.env; se usan los valores por defecto." -ForegroundColor Yellow
}

if ("$($cfg['APP_AUTO_UPDATE'])" -match '^(true|1|si|yes|on)$') {
    if ((Test-Path (Join-Path $Root ".git")) -and (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host "Buscando actualizaciones en GitHub..."
        git pull --rebase --autostash --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Host "No se pudo actualizar; se arranca con el codigo actual. Revisa 'git status'." -ForegroundColor Yellow
        }
    } else {
        Write-Host "APP_AUTO_UPDATE activo, pero esta carpeta no es un repositorio git (ver README, seccion Git)." -ForegroundColor Yellow
    }
}

uv run python -m tradingbot @args
