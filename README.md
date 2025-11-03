# 🎮 StreamDeck PC - Configuration

Application web pour contrôler votre PC avec 50+ actions système. Choisissez vos 5 actions favorites et contrôlez-les facilement depuis n'importe quel appareil (ESP32, smartphone, navigateur).

## 📦 Installation

1. **Installer les dépendances** (déjà fait) :
```powershell
python -m pip install --user flask pywin32 psutil pyautogui pyperclip
```

## 🚀 Démarrage

Lancer le serveur :
```powershell
python "c:\Users\PC MARKET\controle\fentre.py"
```

Le serveur démarre sur : **http://localhost:8080**

## 🌐 Interface Web

Ouvrez votre navigateur et allez sur : **http://localhost:8080**

### Fonctionnalités :

1. **Parcourir 50+ actions** organisées par catégories :
   - 📱 Applications (Chrome, VS Code, Notepad, etc.)
   - 🎯 Focus sur applications
   - ❌ Fermer applications
   - 📋 Presse-papiers (Copier, Coller, Couper)
   - ⌨️ Raccourcis clavier (Ctrl+S, Ctrl+Z, etc.)
   - 🔊 Contrôles système (Volume, Média)
   - 🪟 Gestion fenêtres (Minimiser, Maximiser, Bureau)
   - ✍️ Texte personnalisé

2. **Sélectionner 5 favoris** :
   - Cliquez sur une action pour l'ajouter aux favoris
   - Maximum 5 actions sélectionnables
   - Les actions sélectionnées s'affichent avec un badge numéroté

3. **Enregistrer la configuration** :
   - Cliquez sur "💾 Enregistrer la configuration"
   - La config est sauvegardée dans `config.json`

4. **Tester les actions** :
   - Utilisez la zone "🎯 Tester mes favoris" en bas
   - Cliquez sur un bouton pour exécuter l'action immédiatement

## 📡 API REST

### Endpoints disponibles :

#### 1. Liste toutes les actions
```bash
GET /actions
```
Retourne : `[{id, name, category, icon}, ...]`

#### 2. Sauvegarder la configuration
```bash
POST /config
Content-Type: application/json

{
  "favorites": ["open_chrome", "copy_text", "paste_text", "volume_up", "focus_chrome"]
}
```

#### 3. Charger la configuration
```bash
GET /config
```
Retourne : `{favorites: [...]}`

#### 4. Exécuter une action par ID
```bash
POST /execute/<action_id>
```
Exemple :
```powershell
curl.exe -X POST "http://localhost:8080/execute/open_chrome"
```

#### 5. Ancien endpoint CMD (compatibilité)
```bash
POST /cmd
Content-Type: application/json

{"cmd": "focus:chrome"}
```

## 🎯 Exemples d'utilisation

### Depuis PowerShell :
```powershell
# Ouvrir Chrome
Invoke-RestMethod -Uri "http://localhost:8080/execute/open_chrome" -Method POST

# Copier du texte (Ctrl+C)
Invoke-RestMethod -Uri "http://localhost:8080/execute/copy_text" -Method POST

# Volume +
Invoke-RestMethod -Uri "http://localhost:8080/execute/volume_up" -Method POST
```

### Depuis curl :
```bash
# Focus sur VS Code
curl.exe -X POST "http://localhost:8080/execute/focus_vscode"

# Fermer Chrome
curl.exe -X POST "http://localhost:8080/execute/close_chrome"

# Afficher le bureau
curl.exe -X POST "http://localhost:8080/execute/show_desktop"
```

### Depuis ESP32 / Arduino :
```cpp
#include <HTTPClient.h>

void executeAction(String actionId) {
  HTTPClient http;
  String url = "http://192.168.1.100:8080/execute/" + actionId;
  http.begin(url);
  int httpCode = http.POST("");
  http.end();
}

// Exemples :
executeAction("open_chrome");
executeAction("volume_up");
executeAction("focus_vscode");
```

## 📋 Liste des actions disponibles

### Applications (15)
- Ouvrir : Chrome, Firefox, Edge, Notepad, VS Code, Explorateur, CMD, PowerShell, Calculatrice, Paint, Capture d'écran, Gestionnaire des tâches, Paramètres, Panneau de configuration

### Focus (3)
- Focus Chrome, VS Code, Notepad

### Fermer (3)
- Fermer Chrome, VS Code, Notepad

### Kill (2)
- Kill Chrome, Kill tous Chrome

### Presse-papiers (4)
- Copier (Ctrl+C), Coller (Ctrl+V), Couper (Ctrl+X), Tout sélectionner

### Raccourcis clavier (10)
- Enregistrer, Annuler, Rétablir, Nouvel onglet, Fermer onglet, Actualiser, Rechercher, Imprimer

### Système (6)
- Volume +/-, Muet, Piste suivante/précédente, Lecture/Pause

### Fenêtres (6)
- Minimiser, Maximiser, Bureau, Verrouiller, Changer fenêtre, Vue des tâches

### Texte (3)
- Taper email, téléphone, signature (personnalisables)

## ⚙️ Personnalisation

Pour ajouter vos propres actions, éditez `fentre.py` et ajoutez dans `ACTIONS_CATALOGUE` :

```python
"mon_action": {
    "name": "Mon Action",
    "category": "Ma Catégorie",
    "icon": "🎨",
    "cmd": "notepad"  # ou
    "action": "hotkey",
    "keys": ["ctrl", "alt", "delete"]
}
```

## 🔧 Dépannage

### Problème : DLL load failed
**Solution** : Réinstaller pywin32 et psutil :
```powershell
python -m pip uninstall -y pywin32 psutil
python -m pip install --user pywin32 psutil
```

### Problème : Emoji ne s'affichent pas
**Solution** : Le script reconfigure automatiquement UTF-8. Si problème persiste, utilisez un terminal moderne (Windows Terminal).

### Problème : Actions ne fonctionnent pas
**Vérifications** :
- Le serveur Flask est-il lancé ?
- L'application cible est-elle installée ?
- Pour les raccourcis clavier, la fenêtre cible a-t-elle le focus ?

## 📝 Fichiers

- `fentre.py` - Serveur Flask + logique métier
- `index.html` - Interface web de configuration
- `config.json` - Configuration des 5 favoris (créé automatiquement)
- `README.md` - Cette documentation

## 🪟 Application Desktop (Windows)

Si vous préférez une vraie application Windows (qui lance le serveur en local et embarque l'interface web), utilisez `streamdeck_app.py` :

Lancer l'application desktop (dépendances : pywebview, requests) :

```powershell
python streamdeck_app.py
```

Ce script :
- Démarre le serveur Flask localement sur `127.0.0.1:8080` en arrière-plan
- Lance une fenêtre native qui affiche l'interface web (via pywebview)
- Démarre aussi l'annonce mDNS (Zeroconf) si disponible

Packaging (générer un .exe avec PyInstaller) :

1. Installer PyInstaller et pywebview :
```powershell
python -m pip install --user pyinstaller pywebview requests
```

2. Construire l'exécutable (exemple simple) :
```powershell
pyinstaller --onefile --add-data "index.html;." --add-data "static;static" streamdeck_app.py
```

Notes :
- Selon votre système et la version de pywebview, vous aurez peut-être besoin de WebView2 (Edge) ou CEF pour une intégration native complète. Si WebView n'est pas disponible, l'application ouvrira le navigateur par défaut.
- Incluez `index.html` et tout dossier `static` lors de la création de l'exécutable pour que l'UI soit disponible.

## 🎉 Utilisation recommandée

1. **Configuration initiale** :
   - Démarrez le serveur
   - Ouvrez http://localhost:8080
   - Sélectionnez vos 5 actions favorites
   - Enregistrez

2. **Utilisation quotidienne** :
   - Le serveur tourne en arrière-plan
   - Contrôlez via ESP32, smartphone, ou navigateur
   - Les actions favorites sont dans `config.json`

3. **Depuis un ESP32** :
   - Connectez l'ESP32 au même réseau WiFi
   - Utilisez l'IP de votre PC (ex: 192.168.1.100)
   - Envoyez des requêtes POST vers `/execute/<action_id>`

## 🔐 Sécurité

⚠️ **Important** : Ce serveur écoute sur `0.0.0.0` (toutes les interfaces réseau).

Pour production :
- Utilisez un firewall
- Ajoutez une authentification
- Utilisez HTTPS
- Restreignez aux IPs de confiance

Pour usage local uniquement, changez dans `fentre.py` :
```python
app.run(host='127.0.0.1', port=8080, debug=False)
```

## 📞 Support

En cas de problème :
1. Vérifiez que Python 3.9+ est installé
2. Vérifiez que tous les packages sont installés
3. Consultez les logs du serveur Flask
4. Testez les actions manuellement depuis l'interface web

---

**Auteur** : StreamDeck PC Controller  
**Version** : 1.0  
**License** : MIT
