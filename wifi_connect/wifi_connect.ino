/*
 * StreamDeck PC - ESP32
 * Version avec connexion WiFi dynamique (WiFiManager)
 * et découverte automatique du serveur (mDNS).

// Inclusions des bibliothèques nécessaires
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiManager.h> // Gère le portail de connexion WiFi
#include <ESPmDNS.h>     // Gère la découverte du serveur sur le réseau

// ===== CONFIGURATION =====
const char* MDNS_HOSTNAME = "streamdeck-server"; // Le nom que votre serveur PC annonce sur le réseau.
const int SERVER_PORT = 8080;

// Cette variable sera remplie automatiquement par mDNS
String server_ip_string = ""; 

// Pins des boutons
const int BTN_PINS[] = {12, 13, 14, 27, 26};
const int NUM_BUTTONS = 5;

// États des boutons
bool lastButtonStates[NUM_BUTTONS] = {false, false, false, false, false};

// IDs des actions favorites (à personnaliser selon votre config)
String favoriteActions[NUM_BUTTONS] = {
  "open_chrome",    // Bouton 1
  "volume_up",      // Bouton 2
  "volume_down",    // Bouton 3
  "copy_text",      // Bouton 4
  "paste_text"      // Bouton 5
};

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  Serial.println("\n\n🎮 StreamDeck PC - ESP32 v2 (Auto-Discovery)");
  
  // Configuration des boutons
  for (int i = 0; i < NUM_BUTTONS; i++) {
    pinMode(BTN_PINS[i], INPUT);
    Serial.printf("✓ Bouton %d configuré sur GPIO %d\n", i+1, BTN_PINS[i]);
  }
  
  // ----- 1. GESTION DE LA CONNEXION WIFI via WiFiManager -----
  WiFi.mode(WIFI_STA); // Met l'ESP32 en mode station
  WiFiManager wm;

  // Décommentez la ligne suivante pour effacer les identifiants WiFi enregistrés à chaque démarrage (utile pour les tests)
  // wm.resetSettings();

  // Tente de se connecter. Si échec, lance un Point d'Accès "StreamDeckPC-Config" (mdp: "password")
  Serial.println("📡 Tentative de connexion WiFi...");
  bool res = wm.autoConnect("StreamDeckPC-Config", "password"); 

  if(!res) {
    Serial.println("❌ Échec de la connexion. Redémarrage...");
    delay(3000);
    ESP.restart(); // Redémarre l'ESP s'il n'a pas pu se connecter
  } 
  
  // Si on arrive ici, le WiFi est connecté !
  Serial.println("\n✅ WiFi connecté !");
  Serial.printf("📍 IP de l'ESP32: %s\n", WiFi.localIP().toString().c_str());

  // ----- 2. DÉCOUVERTE DU SERVEUR PC via mDNS -----
  Serial.printf("🔍 Recherche du serveur '%s.local' sur le réseau...\n", MDNS_HOSTNAME);
  
  // On démarre le service mDNS sur l'ESP32
  if (!MDNS.begin("esp32-streamdeck-client")) {
      Serial.println("❌ Erreur au démarrage du responder mDNS !");
      return; // On ne peut pas continuer
  }

  // On cherche les services de type "_http" sur le protocole "_tcp"
  int n = MDNS.queryService("http", "tcp");
  
  if (n == 0) {
      Serial.println("❌ Aucun serveur web trouvé sur le réseau !");
      Serial.println("   Vérifiez que l'application sur votre PC est bien lancée.");
  } else {
      Serial.printf("✅ %d service(s) web trouvé(s)\n", n);
      bool serverFound = false;
      // On parcourt tous les services trouvés pour trouver le nôtre
      for (int i = 0; i < n; ++i) {
          // On compare le nom d'hôte du service avec celui que l'on cherche
          if (MDNS.hostname(i) == MDNS_HOSTNAME) {
              server_ip_string = MDNS.IP(i).toString();
              Serial.printf("🖥️  Serveur StreamDeck trouvé ! Adresse IP : %s\n", server_ip_string.c_str());
              serverFound = true;
              break; // On a trouvé le serveur, on arrête la recherche
          }
      }
      if (!serverFound) {
          Serial.printf("❌ Serveur trouvé, mais aucun ne correspond au nom '%s'\n", MDNS_HOSTNAME);
      }
  }

  // ----- 3. VERIFICATION FINALE -----
  if (server_ip_string.length() > 0) {
    Serial.println("\n🚀 Prêt ! Appuyez sur un bouton...\n");
  } else {
    Serial.println("\n🛑 ERREUR CRITIQUE : Impossible de trouver l'IP du serveur PC.");
    Serial.println("   Le StreamDeck ne peut pas fonctionner. Redémarrage dans 10 secondes...");
    delay(10000);
    ESP.restart();
  }
}

// ===== LOOP =====
void loop() {
  // Vérifier chaque bouton
  for (int i = 0; i < NUM_BUTTONS; i++) {
    bool currentState = digitalRead(BTN_PINS[i]);
    
    // Détection front montant (bouton pressé)
    if (currentState && !lastButtonStates[i]) {
      Serial.printf("🔘 Bouton %d pressé → %s\n", i+1, favoriteActions[i].c_str());
      executeAction(favoriteActions[i]);
      delay(50); // Debounce
    }
    
    lastButtonStates[i] = currentState;
  }
  
  delay(10);
}

// ===== FONCTIONS =====

/**
 * Exécute une action sur le PC en utilisant l'adresse IP découverte par mDNS
 
void executeAction(String actionId) {
  // Vérification double : WiFi connecté ET IP du serveur connue
  if (WiFi.status() != WL_CONNECTED || server_ip_string.length() == 0) {
    Serial.println("❌ WiFi déconnecté ou IP du serveur inconnue. Action annulée.");
    return;
  }
  
  HTTPClient http;
  String url = "http://" + server_ip_string + ":" + String(SERVER_PORT) + "/execute/" + actionId;
  
  Serial.printf("📤 Envoi: %s\n", url.c_str());
  
  http.begin(url);
  http.setTimeout(3000);
  
  int httpCode = http.POST("");
  
  if (httpCode > 0) {
    String response = http.getString();
    Serial.printf("📥 Réponse (%d): %s\n", httpCode, response.c_str());
  } else {
    Serial.printf("❌ Erreur HTTP: %s\n", http.errorToString(httpCode).c_str());
  }
  
  http.end();
}*/


/*
 * StreamDeck PC - ESP32
 * Version avec saisie dans le moniteur série (sans boutons physiques)
 * Connexion WiFi dynamique (WiFiManager) et découverte automatique du serveur (mDNS)
 */

/*
 * StreamDeck PC - ESP32
 * Version avec récupération dynamique des actions depuis le serveur Flask
 * + saisie dans le moniteur série (pas de boutons physiques)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiManager.h>
#include <ESPmDNS.h>
#include <ArduinoJson.h>  // ⚠️ Nécessaire pour décoder le JSON

// ===== CONFIGURATION =====
const char* MDNS_HOSTNAME = "streamdeck-server";
const int SERVER_PORT = 8080;

// Adresse du serveur découverte via mDNS
String server_ip_string = "";

// Liste d’actions (remplie dynamiquement)
String favoriteActions[5];
int NUM_ACTIONS = 0;
// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  Serial.println("\n\n🎮 StreamDeck PC - ESP32 v4 (Actions dynamiques)");

  // ----- 1. Connexion WiFi -----
  WiFi.mode(WIFI_STA);
  WiFiManager wm;
  bool res = wm.autoConnect("StreamDeckPC-Config", "password");
  if (!res) {
    Serial.println("❌ WiFi non connecté. Redémarrage...");
    delay(3000);
    ESP.restart();
  }

  Serial.printf("✅ WiFi connecté : %s\n", WiFi.localIP().toString().c_str());

  // ----- 2. Découverte du serveur via mDNS -----
  Serial.printf("🔍 Recherche du serveur '%s.local'...\n", MDNS_HOSTNAME);
  if (!MDNS.begin("esp32-streamdeck-client")) {
    Serial.println("❌ Erreur mDNS !");
    return;
  }

  int n = MDNS.queryService("http", "tcp");
  if (n > 0) {
    for (int i = 0; i < n; i++) {
      if (MDNS.hostname(i) == MDNS_HOSTNAME) {
        server_ip_string = MDNS.IP(i).toString();
        Serial.printf("🖥️ Serveur trouvé : %s\n", server_ip_string.c_str());
        break;
      }
    }
  }

  if (server_ip_string.isEmpty()) {
    Serial.println("❌ Impossible de trouver le serveur. Redémarrage...");
    delay(5000);
    ESP.restart();
  }

  // ----- 3. Charger les actions favorites depuis le serveur -----
  loadFavoritesFromServer();

  // ----- 4. Afficher les actions -----
  if (NUM_ACTIONS > 0) {
    Serial.println("\n🚀 Prêt !");
    Serial.println("Tape un numéro pour exécuter une action :");
    for (int i = 0; i < NUM_ACTIONS; i++) {
      Serial.printf("  %d → %s\n", i + 1, favoriteActions[i].c_str());
    }
    Serial.println("-----------------------------------");
  } else {
    Serial.println("⚠️ Aucune action favorite trouvée sur le serveur !");
  }
}

// ===== LOOP =====
void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.length() > 0) {
      int choice = input.toInt();

      if (choice >= 1 && choice <= NUM_ACTIONS) {
        Serial.printf("🔘 Action %d → %s\n", choice, favoriteActions[choice - 1].c_str());
        executeAction(favoriteActions[choice - 1]);
      }else if (input.equalsIgnoreCase("reload")) {
          loadFavoritesFromServer();
      }else {
        Serial.println("⚠️ Numéro invalide !");
      }
    }
  }

  delay(10);
}

// ===== FONCTIONS =====

/**
 * 🔄 Récupère la liste des actions favorites depuis le serveur Flask
 */
void loadFavoritesFromServer() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ Pas de connexion WiFi !");
    return;
  }

  HTTPClient http;
  String url = "http://" + server_ip_string + ":" + String(SERVER_PORT) + "/config";
  Serial.printf("🌐 Récupération des favoris depuis : %s\n", url.c_str());

  http.begin(url);
  int httpCode = http.GET();

  if (httpCode == 200) {
    String payload = http.getString();
    Serial.printf("📥 Réponse brute : %s\n", payload.c_str());

    // Analyse JSON
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, payload);

    if (!error && doc.containsKey("favorites")) {
      JsonArray favorites = doc["favorites"].as<JsonArray>();
      NUM_ACTIONS = favorites.size();
      for (int i = 0; i < NUM_ACTIONS; i++) {
        favoriteActions[i] = favorites[i].as<String>();
      }
      Serial.printf("✅ %d actions chargées depuis le serveur.\n", NUM_ACTIONS);
    } else {
      Serial.println("⚠️ Erreur de lecture du JSON !");
    }
  } else {
    Serial.printf("❌ Erreur HTTP: %d\n", httpCode);
  }

  http.end();
}

/**
 * 🚀 Exécute une action sur le PC
 */
void executeAction(String actionId) {
  if (WiFi.status() != WL_CONNECTED || server_ip_string.isEmpty()) {
    Serial.println("❌ WiFi ou IP serveur invalide.");
    return;
  }

  HTTPClient http;
  String url = "http://" + server_ip_string + ":" + String(SERVER_PORT) + "/execute/" + actionId;

  Serial.printf("📤 Envoi: %s\n", url.c_str());
  http.begin(url);
  http.setTimeout(3000);

  int httpCode = http.POST("");
  if (httpCode > 0) {
    String response = http.getString();
    Serial.printf("📥 Réponse (%d): %s\n", httpCode, response.c_str());
  } else {
    Serial.printf("❌ Erreur HTTP: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}
