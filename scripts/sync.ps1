# Sincroniza los cambios con GitHub: commit + pull --rebase + push.
#   .\scripts\sync.ps1 "mensaje del commit"
param([string]$Message)

Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not (Test-Path ".git")) {
    Write-Host "Esto todavia no es un repositorio git. Mira la seccion 'Git' del README." -ForegroundColor Red
    exit 1
}

# Red de seguridad: nunca subir ficheros de credenciales
$tracked = git ls-files | Select-String -Pattern '(^|/)\.env$'
if ($tracked) {
    Write-Host "Hay un .env dentro del repositorio. Abortando: $tracked" -ForegroundColor Red
    exit 1
}

git add -A
if (git status --porcelain) {
    if (-not $Message) { $Message = "Update " + (Get-Date -Format "yyyy-MM-dd HH:mm") }
    git commit -m $Message
} else {
    Write-Host "Sin cambios que confirmar."
}

git pull --rebase
if ($LASTEXITCODE -ne 0) { Write-Host "Conflicto al hacer pull. Resuelvelo y vuelve a ejecutar." -ForegroundColor Red; exit 1 }
git push -u origin HEAD
if ($LASTEXITCODE -eq 0) { Write-Host "Sincronizado con GitHub." -ForegroundColor Green }
