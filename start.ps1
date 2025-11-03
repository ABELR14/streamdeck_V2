# 🚀 StreamDeck PC - Démarrage rapide
# Ce script lance le serveur et ouvre automatiquement l'interface web

Write-Host "🎮 StreamDeck PC - Démarrage..." -ForegroundColor Cyan
Write-Host ""

# Vérifier que Python est installé
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python détecté: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python non trouvé. Installez Python 3.9+ depuis python.org" -ForegroundColor Red
    exit 1
}

# Vérifier les dépendances
Write-Host ""
Write-Host "📦 Vérification des dépendances..." -ForegroundColor Yellow
$packages = @("flask", "pywin32", "psutil", "pyautogui", "pyperclip")
$missing = @()

foreach ($pkg in $packages) {
    $result = python -c "import $pkg" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missing += $pkg
        Write-Host "  ✗ $pkg manquant" -ForegroundColor Red
    } else {
        Write-Host "  ✓ $pkg installé" -ForegroundColor Green
    }
}

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "Installation des packages manquants..." -ForegroundColor Yellow
    python -m pip install --user $missing
}

# Démarrer le serveur en arrière-plan
Write-Host ""
Write-Host "🚀 Démarrage du serveur..." -ForegroundColor Cyan
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "  🌐 Interface Web : http://localhost:8080" -ForegroundColor Green
Write-Host "  📱 API REST      : http://localhost:8080/actions" -ForegroundColor Green
Write-Host "  📋 Documentation : README.md" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""
Write-Host "💡 Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Gray
Write-Host ""

# Attendre 2 secondes puis ouvrir le navigateur
Start-Sleep -Seconds 2
Start-Process "http://localhost:8080"

# Lancer le serveur (bloquant)
python "$PSScriptRoot\fentre.py"
