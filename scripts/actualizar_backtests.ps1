# Regenera los backtests de todos los perfiles y reescribe el fichero de la ventana Backtest.
#   .\scripts\actualizar_backtests.ps1            -> TBR (puprime y metaquotes) + Calendario + CRT-C2, y commit en main
#   .\scripts\actualizar_backtests.ps1 -SinCommit -> igual, sin el commit
#   .\scripts\actualizar_backtests.ps1 -Solo crt  -> solo CRT-C2 (también: tbr)
# Lo lanza cada día la tarea programada de las 18:00 NY. Regenera todo desde el histórico de MT5 (los resultados de los días ya
# cerrados no cambian), así que el fichero queda al día hasta la última vela descargada. Tarda más de una hora; el log va a
# analisis/actualizar_backtests.log.
param([switch]$SinCommit, [ValidateSet("todo", "tbr", "crt")][string]$Solo = "todo")
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root
$Log = Join-Path $Root "analisis\actualizar_backtests.log"
$Fallos = @()

function Anota($texto) {
    $texto | Add-Content -Path $Log -Encoding utf8
    Write-Host $texto
}

function Paso($nombre, [scriptblock]$accion) {
    Anota ("[{0:yyyy-MM-dd HH:mm:ss}] {1}" -f (Get-Date), $nombre)
    & $accion 2>&1 | ForEach-Object { "$_" } | Add-Content -Path $Log -Encoding utf8
    if ($LASTEXITCODE -ne 0) {
        $script:Fallos += $nombre
        Anota "  FALLO ($LASTEXITCODE): $nombre"
        return $false
    }
    return $true
}

# Mercados de cada grupo, con los nombres del broker (los mismos de los backtests anteriores)
$Perfiles = [ordered]@{
    puprime    = [ordered]@{
        indices = @("NAS100ft.s", "SP500ft.s", "DJ30ft.s", "US2000.s")
        forex   = @("EURUSD.s", "GBPUSD.s", "USDJPY.s", "AUDUSD.s", "USDCAD.s", "USDCHF.s", "NZDUSD.s")
        oro     = @("XAUUSD.s", "XAGUSD.s")
        cripto  = @("BTCUSD", "ETHUSD")
    }
    metaquotes = [ordered]@{
        indices = @("US30", "US500", "USTEC", "US2000")
        forex   = @("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD")
        oro     = @("XAUUSD", "XAGUSD")
    }
}
$Etiquetas = @{ indices = "los índices americanos"; forex = "los pares de forex"; oro = "el oro y la plata"; cripto = "las criptomonedas" }

$tbrOk = $true
if ($Solo -in "todo", "tbr") {
    foreach ($perfil in $Perfiles.Keys) {
        foreach ($grupo in $Perfiles[$perfil].Keys) {
            $salida = "analisis\$perfil\backtest_$grupo.xlsx"
            $ok = Paso "TBR $perfil / $grupo" {
                uv run --with openpyxl python scripts/backtest_patrones.py --perfil $perfil --simbolos @($Perfiles[$perfil][$grupo]) `
                    --etiqueta $Etiquetas[$grupo] --salida $salida
            }
            $tbrOk = $tbrOk -and $ok
        }
    }
    if ($tbrOk) {
        # Reescribe backtest.json.gz con lo regenerado (conserva los grupos de CRT)
        $tbrOk = Paso "Exportar TBR y Calendario a backtest.json.gz" { uv run --with openpyxl python scripts/exportar_backtest.py }
    }
}

if ($Solo -in "todo", "crt") {
    Paso "CRT-C2: descargar velas M5 y M3" { uv run python scripts/exportar_backtest_crt.py --descargar } | Out-Null
    Paso "CRT-C2: simular y exportar" { uv run python scripts/exportar_backtest_crt.py --simular --cuartos 0 --sin-sesgo } | Out-Null
}

if ($Fallos.Count -gt 0) {
    Anota ("Terminó con fallos: " + ($Fallos -join "; "))
}
if (-not $SinCommit) {
    $rama = (git rev-parse --abbrev-ref HEAD).Trim()
    git add tradingbot/skills/stats/backtest.json.gz
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) {
        $msg = "Backtests actualizados hasta {0:yyyy-MM-dd} ({1})`n`nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -f (Get-Date), $(if ($Fallos.Count) { "con fallos: " + ($Fallos -join ", ") } else { "todos los perfiles" })
        git commit -m $msg --quiet
        Anota "Commit en $rama"
    } else {
        Anota "Sin cambios que subir"
    }
}
exit $(if ($Fallos.Count) { 1 } else { 0 })
