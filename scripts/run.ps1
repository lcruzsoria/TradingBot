# Arranca TradingBot con uv (crea el entorno e instala dependencias la primera vez).
#   .\scripts\run.ps1                 -> cuenta por defecto del .env
#   .\scripts\run.ps1 --demo          -> datos sintéticos, sin MT5
#   .\scripts\run.ps1 --profile real  -> otro perfil del .env
Set-Location (Split-Path $PSScriptRoot -Parent)
uv run python -m tradingbot @args
