# 🚀 DÉMARRAGE RAPIDE

## Méthode 1 : Script automatique (recommandé)

```powershell
.\start.ps1
```

Le script va :
1. ✅ Vérifier Python et les dépendances
2. ✅ Installer les packages manquants si nécessaire
3. ✅ Démarrer le serveur
4. ✅ Ouvrir automatiquement votre navigateur sur http://localhost:8080

## Méthode 2 : Manuelle

```powershell
python fentre.py
```

Puis ouvrez : **http://localhost:8080**

---

## 🎯 ÉTAPES DE CONFIGURATION (1 minute)

### 1️⃣ Ouvrez l'interface web
- Allez sur http://localhost:8080
- Vous verrez 50+ actions disponibles

### 2️⃣ Sélectionnez vos 5 favoris
- Parcourez les catégories (Applications, Raccourcis, Système...)
- Cliquez sur une action pour l'ajouter à vos favoris
- Un badge numéroté (1-5) apparaît sur les actions sélectionnées
- Le panneau de droite affiche vos 5 choix

### 3️⃣ Enregistrez
- Cliquez sur "💾 Enregistrer la configuration"
- Votre config est sauvegardée dans `config.json`

### 4️⃣ Testez !
- En bas de page : zone "🎯 Tester mes favoris"
- Cliquez sur un bouton pour exécuter l'action immédiatement
- Exemple : cliquez "Ouvrir Chrome" → Chrome s'ouvre !

---

## 🎮 UTILISATION DEPUIS ESP32 / AUTRE APPAREIL

Une fois configuré, envoyez des requêtes HTTP POST :

```
POST http://<IP_DE_VOTRE_PC>:8080/execute/<action_id>
```

### Trouver l'IP de votre PC :
```powershell
ipconfig
# Cherchez "Adresse IPv4" (ex: 192.168.1.100)
```

### Exemples d'actions disponibles :

| ID Action | Description | Effet |
|-----------|-------------|-------|
| `open_chrome` | Ouvrir Chrome | Lance le navigateur |
| `open_vscode` | Ouvrir VS Code | Lance l'éditeur |
| `copy_text` | Copier (Ctrl+C) | Copie le texte sélectionné |
| `paste_text` | Coller (Ctrl+V) | Colle depuis le presse-papiers |
| `volume_up` | Volume + | Augmente le volume |
| `volume_down` | Volume - | Diminue le volume |
| `volume_mute` | Muet | Active/désactive le muet |
| `focus_chrome` | Focus Chrome | Met Chrome au premier plan |
| `close_chrome` | Fermer Chrome | Ferme Chrome proprement |
| `show_desktop` | Bureau | Affiche le bureau (Win+D) |
| `lock_screen` | Verrouiller | Verrouille la session (Win+L) |
| `save_file` | Enregistrer | Ctrl+S |
| `undo` | Annuler | Ctrl+Z |
| `new_tab` | Nouvel onglet | Ctrl+T |
| `refresh` | Actualiser | F5 |

Voir la liste complète dans l'interface web ou dans `README.md`

---

## 📱 EXEMPLE CODE ESP32

```cpp
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "VotreWiFi";
const char* password = "VotreMotDePasse";
const char* serverIP = "192.168.1.100"; // IP de votre PC

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnecté !");
}

void executeAction(String actionId) {
  HTTPClient http;
  String url = "http://" + String(serverIP) + ":8080/execute/" + actionId;
  
  http.begin(url);
  int httpCode = http.POST("");
  
  if (httpCode > 0) {
    String response = http.getString();
    Serial.println("✅ " + response);
  } else {
    Serial.println("❌ Erreur");
  }
  
  http.end();
}

void loop() {
  // Exemple : ouvrir Chrome toutes les 10 secondes
  executeAction("open_chrome");
  delay(10000);
}
```

---

## 🔧 PERSONNALISER LES ACTIONS

Éditez `fentre.py` dans la section `ACTIONS_CATALOGUE` :

```python
"mon_action_perso": {
    "name": "Mon Action",
    "category": "Personnalisé",
    "icon": "🎨",
    "cmd": "notepad"  # Commande à exécuter
}
```

Ou pour un raccourci clavier :

```python
"mon_raccourci": {
    "name": "Mon Raccourci",
    "category": "Personnalisé",
    "icon": "⌨️",
    "action": "hotkey",
    "keys": ["ctrl", "shift", "a"]
}
```

Relancez le serveur pour voir vos nouvelles actions !

---

## ✅ TOUT FONCTIONNE ?

Vous devriez maintenant avoir :
- ✅ Un serveur Flask qui tourne sur port 8080
- ✅ Une interface web magnifique pour configurer vos actions
- ✅ 5 actions favorites enregistrées
- ✅ La possibilité de contrôler votre PC depuis n'importe où

## ❓ PROBLÈMES ?

Consultez `README.md` section "🔧 Dépannage"

---

**🎉 Amusez-vous bien avec votre StreamDeck PC !**
