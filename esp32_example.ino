/*
 * StreamDeck PC - Exemple ESP32
 * 
 * Ce code montre comment contrôler votre PC depuis un ESP32
 * avec des boutons physiques ou via WiFi.
 * 
 * Matériel suggéré :
 * - ESP32 Dev Board
 * - 5 boutons poussoirs
 * - Résistances 10kΩ (pull-down)
 * 
 * Connexions :
 * - Bouton 1 → GPIO 12
 * - Bouton 2 → GPIO 13
 * - Bouton 3 → GPIO 14
 * - Bouton 4 → GPIO 27
 * - Bouton 5 → GPIO 26
 */

#include <WiFi.h>
#include <HTTPClient.h>

// ===== CONFIGURATION =====
const char* WIFI_SSID = "VotreWiFi";
const char* WIFI_PASSWORD = "VotreMotDePasse";
const char* SERVER_IP = "192.168.1.100";  // IP de votre PC Windows
const int SERVER_PORT = 8080;

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
  Serial.println("\n🎮 StreamDeck PC - ESP32");
  
  // Configuration des boutons
  for (int i = 0; i < NUM_BUTTONS; i++) {
    pinMode(BTN_PINS[i], INPUT);
    Serial.printf("✓ Bouton %d configuré sur GPIO %d\n", i+1, BTN_PINS[i]);
  }
  
  // Connexion WiFi
  Serial.printf("\n📡 Connexion à %s...\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connecté !");
    Serial.printf("📍 IP ESP32: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("🖥️  Serveur PC: http://%s:%d\n", SERVER_IP, SERVER_PORT);
  } else {
    Serial.println("\n❌ Échec connexion WiFi");
  }
  
  Serial.println("\n🚀 Prêt ! Appuyez sur un bouton...\n");
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
 * Exécute une action sur le PC
 */
void executeAction(String actionId) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi déconnecté");
    return;
  }
  
  HTTPClient http;
  String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/execute/" + actionId;
  
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

/**
 * Charger la configuration des favoris depuis le serveur
 */
void loadFavoritesFromServer() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi déconnecté");
    return;
  }
  
  HTTPClient http;
  String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/config";
  
  http.begin(url);
  int httpCode = http.GET();
  
  if (httpCode == 200) {
    String response = http.getString();
    Serial.println("✅ Configuration chargée :");
    Serial.println(response);
    
    // TODO: Parser le JSON et mettre à jour favoriteActions[]
    // Nécessite la bibliothèque ArduinoJson
  } else {
    Serial.printf("❌ Erreur chargement config: %d\n", httpCode);
  }
  
  http.end();
}

/**
 * Tester toutes les actions favorites
 */
void testAllActions() {
  Serial.println("\n🧪 Test de toutes les actions...\n");
  
  for (int i = 0; i < NUM_BUTTONS; i++) {
    Serial.printf("Test action %d/%d: %s\n", i+1, NUM_BUTTONS, favoriteActions[i].c_str());
    executeAction(favoriteActions[i]);
    delay(2000);
  }
  
  Serial.println("\n✅ Tests terminés\n");
}

/*
 * ===== EXEMPLES D'UTILISATION =====
 * 
 * 1. Configuration de base :
 *    - Modifiez WIFI_SSID et WIFI_PASSWORD
 *    - Trouvez l'IP de votre PC (ipconfig dans PowerShell)
 *    - Mettez à jour SERVER_IP
 *    - Personnalisez favoriteActions[] selon vos besoins
 * 
 * 2. Test sans boutons :
 *    - Décommentez dans setup() : testAllActions();
 *    - Uploadez le code
 *    - Observez le moniteur série
 * 
 * 3. IDs d'actions disponibles :
 *    open_chrome, open_vscode, open_notepad
 *    focus_chrome, focus_vscode
 *    close_chrome, close_vscode
 *    copy_text, paste_text, cut_text
 *    volume_up, volume_down, volume_mute
 *    save_file, undo, redo
 *    new_tab, close_tab, refresh
 *    show_desktop, lock_screen
 *    ... et 30+ autres !
 * 
 * 4. Charger la config automatiquement :
 *    - Décommentez dans setup() : loadFavoritesFromServer();
 *    - Installez ArduinoJson : https://arduinojson.org
 *    - Les favoris seront chargés depuis config.json
 * 
 * 5. Ajout d'un écran OLED :
 *    - Affichez le nom de l'action avant exécution
 *    - Montrez le statut WiFi
 *    - Feedback visuel de succès/erreur
 * 
 * 6. Mode StreamDeck complet :
 *    - Ajoutez un écran TFT tactile
 *    - Affichez les 5 boutons avec leurs icônes
 *    - Touch pour exécuter
 * 
 * ===== DÉPANNAGE =====
 * 
 * Problème : ESP32 ne se connecte pas au WiFi
 * Solution : Vérifiez SSID/Password, redémarrez votre routeur
 * 
 * Problème : Erreur HTTP -1 ou timeout
 * Solution : Vérifiez que le serveur PC tourne (python fentre.py)
 *           Vérifiez l'IP avec ipconfig
 *           Ping depuis l'ESP32 : WiFi.ping(SERVER_IP)
 * 
 * Problème : Actions ne s'exécutent pas
 * Solution : Vérifiez les IDs dans favoriteActions[]
 *           Testez via curl depuis PowerShell d'abord
 *           Consultez les logs du serveur Flask
 * 
 * ===== AMÉLIORATIONS POSSIBLES =====
 * 
 * - Deep sleep entre les pressions (économie batterie)
 * - Serveur web embarqué pour config via WiFi
 * - Support MQTT pour notifications bidirectionnelles
 * - Mode offline avec actions locales
 * - LED RGB pour feedback visuel
 * - Buzzer pour confirmation sonore
 * - Encoder rotatoire pour volume/navigation
 * - Mode macro : séquence d'actions
 */
