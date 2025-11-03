from flask import Flask, request, jsonify, send_from_directory
import win32gui
import win32process
import psutil
import os
import sys
import io
import json
import subprocess
import pyperclip
import time
from pathlib import Path
from zeroconf import ServiceInfo, Zeroconf
import socket
import threading

app = Flask(__name__)

# Fichier de configuration pour les 5 actions favorites
CONFIG_FILE = Path(__file__).parent / "config.json"

# 📋 Liste complète des 50+ actions disponibles
ACTIONS_CATALOGUE = {
    # Ouvrir des applications
    "open_chrome": {"name": "Ouvrir Chrome", "category": "Applications", "cmd": "start chrome", "icon": "🌐"},
    "open_firefox": {"name": "Ouvrir Firefox", "category": "Applications", "cmd": "start firefox", "icon": "🦊"},
    "open_edge": {"name": "Ouvrir Edge", "category": "Applications", "cmd": "start msedge", "icon": "🔷"},
    "open_notepad": {"name": "Ouvrir Bloc-notes", "category": "Applications", "cmd": "notepad", "icon": "📝"},
    "open_notepadpp": {"name": "Ouvrir Notepad++", "category": "Applications", "cmd": "notepad++", "icon": "📄"},
    "open_vscode": {"name": "Ouvrir VS Code", "category": "Applications", "cmd": "code", "icon": "💻"},
    "open_explorer": {"name": "Ouvrir Explorateur", "category": "Applications", "cmd": "explorer", "icon": "📁"},
    "open_cmd": {"name": "Ouvrir CMD", "category": "Applications", "cmd": "cmd", "icon": "⚫"},
    "open_powershell": {"name": "Ouvrir PowerShell", "category": "Applications", "cmd": "powershell", "icon": "🔵"},
    "open_calculator": {"name": "Ouvrir Calculatrice", "category": "Applications", "cmd": "calc", "icon": "🔢"},
    "open_paint": {"name": "Ouvrir Paint", "category": "Applications", "cmd": "mspaint", "icon": "🎨"},
    "open_snipping": {"name": "Outil Capture d'écran", "category": "Applications", "cmd": "snippingtool", "icon": "✂️"},
    "open_taskmgr": {"name": "Gestionnaire des tâches", "category": "Applications", "cmd": "taskmgr", "icon": "📊"},
    "open_settings": {"name": "Paramètres Windows", "category": "Applications", "cmd": "start ms-settings:", "icon": "⚙️"},
    "open_controlpanel": {"name": "Panneau de configuration", "category": "Applications", "cmd": "control", "icon": "🎛️"},
    
    # Focus sur applications
    "focus_chrome": {"name": "Focus Chrome", "category": "Focus", "action": "focus", "exe": "chrome", "icon": "🎯"},
    "focus_vscode": {"name": "Focus VS Code", "category": "Focus", "action": "focus", "exe": "code", "icon": "🎯"},
    "focus_notepad": {"name": "Focus Bloc-notes", "category": "Focus", "action": "focus", "exe": "notepad", "icon": "🎯"},
    
    # Fermer des applications
    "close_chrome": {"name": "Fermer Chrome", "category": "Fermer", "action": "close", "exe": "chrome", "icon": "❌"},
    "close_vscode": {"name": "Fermer VS Code", "category": "Fermer", "action": "close", "exe": "code", "icon": "❌"},
    "close_notepad": {"name": "Fermer Bloc-notes", "category": "Fermer", "action": "close", "exe": "notepad", "icon": "❌"},
    
    # Kill applications
    "kill_chrome": {"name": "Kill Chrome", "category": "Kill", "action": "kill", "exe": "chrome", "icon": "💀"},
    "kill_all_chrome": {"name": "Kill tous Chrome", "category": "Kill", "action": "killall", "exe": "chrome", "icon": "💀"},
    
    # Presse-papiers
    "copy_text": {"name": "Copier (Ctrl+C)", "category": "Presse-papiers", "action": "hotkey", "keys": ["ctrl", "c"], "icon": "📋"},
    "paste_text": {"name": "Coller (Ctrl+V)", "category": "Presse-papiers", "action": "hotkey", "keys": ["ctrl", "v"], "icon": "📄"},
    "cut_text": {"name": "Couper (Ctrl+X)", "category": "Presse-papiers", "action": "hotkey", "keys": ["ctrl", "x"], "icon": "✂️"},
    "select_all": {"name": "Tout sélectionner", "category": "Presse-papiers", "action": "hotkey", "keys": ["ctrl", "a"], "icon": "🔲"},
    
    # Raccourcis clavier système
    "save_file": {"name": "Enregistrer (Ctrl+S)", "category": "Raccourcis", "action": "hotkey", "keys": ["ctrl", "s"], "icon": "💾"},
    "undo": {"name": "Annuler (Ctrl+Z)", "category": "Raccourcis", "action": "hotkey", "keys": ["ctrl", "z"], "icon": "↩️"},
    "redo": {"name": "Rétablir (Ctrl+Y)", "category": "Raccourcis", "action": "hotkey", "keys": ["ctrl", "y"], "icon": "↪️"},
    "new_tab": {"name": "Nouvel onglet (Ctrl+T)", "category": "Raccourcis", "action": "hotkey", "keys": ["ctrl", "t"], "icon": "➕"},
    "close_tab": {"name": "Fermer onglet (Ctrl+W)", "category": "Raccourcis", "action": "hotkey", "keys": ["ctrl", "w"], "icon": "➖"},
    "refresh": {"name": "Actualiser (F5)", "category": "Raccourcis", "action": "hotkey", "keys": ["f5"], "icon": "🔄"},
    "find": {"name": "Rechercher (Ctrl+F)", "category": "Raccourcis", "action": "hotkey", "keys": ["ctrl", "f"], "icon": "🔍"},
    "print": {"name": "Imprimer (Ctrl+P)", "category": "Raccourcis", "action": "hotkey", "keys": ["ctrl", "p"], "icon": "🖨️"},
    
    # Contrôles système
    "volume_up": {"name": "Volume +", "category": "Système", "action": "hotkey", "keys": ["volumeup"], "icon": "🔊"},
    "volume_down": {"name": "Volume -", "category": "Système", "action": "hotkey", "keys": ["volumedown"], "icon": "🔉"},
    "volume_mute": {"name": "Muet", "category": "Système", "action": "hotkey", "keys": ["volumemute"], "icon": "🔇"},
    "next_track": {"name": "Piste suivante", "category": "Système", "action": "hotkey", "keys": ["nexttrack"], "icon": "⏭️"},
    "prev_track": {"name": "Piste précédente", "category": "Système", "action": "hotkey", "keys": ["prevtrack"], "icon": "⏮️"},
    "play_pause": {"name": "Lecture/Pause", "category": "Système", "action": "hotkey", "keys": ["playpause"], "icon": "⏯️"},
    
    # Gestion des fenêtres
    "minimize_window": {"name": "Minimiser fenêtre", "category": "Fenêtres", "action": "hotkey", "keys": ["win", "down"], "icon": "🔽"},
    "maximize_window": {"name": "Maximiser fenêtre", "category": "Fenêtres", "action": "hotkey", "keys": ["win", "up"], "icon": "🔼"},
    "show_desktop": {"name": "Afficher bureau", "category": "Fenêtres", "action": "hotkey", "keys": ["win", "d"], "icon": "🖥️"},
    "lock_screen": {"name": "Verrouiller", "category": "Fenêtres", "action": "hotkey", "keys": ["win", "l"], "icon": "🔒"},
    "alt_tab": {"name": "Changer fenêtre", "category": "Fenêtres", "action": "hotkey", "keys": ["alt", "tab"], "icon": "🔄"},
    "task_view": {"name": "Vue des tâches", "category": "Fenêtres", "action": "hotkey", "keys": ["win", "tab"], "icon": "📑"},
    
    # Actions texte personnalisées
    "focus_textbox": {"name": "Focus zone de saisie", "category": "Texte", "action": "hotkey", "keys": ["tab"], "icon": "�"},
    "open_youtube": {"name": "Ouvrir YouTube", "category": "Applications", "cmd": "start firefox https://youtube.com", "icon": "▶️"},
    "open_spotify": {"name": "Ouvrir Spotify", "category": "Applications", "cmd": "start spotify:", "icon": "🎵"},
}

# 🔍 Trouve HWND par nom EXE (chrome.exe → hwnd)
def get_hwnd_by_exe(exe_name):
    exe_name = exe_name.lower() + ".exe" if not exe_name.endswith(".exe") else exe_name.lower()
    def enum_cb(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                if psutil.Process(pid).name().lower() == exe_name:
                    results.append(hwnd)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return True
    results = []
    win32gui.EnumWindows(enum_cb, results)
    return results[-1] if results else None  # Dernière fenêtre

# 🎯 Actions - version étendue avec toutes les actions système
def do_action(cmd):
    """Exécute une action (ancien format 'action:exe' ou nouvel ID d'action)"""
    # Si c'est un ID d'action du catalogue, l'exécuter
    if cmd in ACTIONS_CATALOGUE:
        return execute_action_by_id(cmd)
    
    # Sinon, utiliser l'ancien format 'action:exe'
    if not cmd:
        return "❌ Aucune commande fournie"
    if ':' not in cmd:
        return f"❌ Commande invalide: {cmd}"

    action, arg = cmd.split(':', 1)
    action = action.lower().strip()
    exe = arg.strip()

    if action == 'focus':
        hwnd = get_hwnd_by_exe(exe)
        if hwnd:
            try:
                win32gui.SetForegroundWindow(hwnd)
                return f"✅ Focus {exe}"
            except Exception as e:
                return f"❌ Échec focus {exe}: {e}"
        return f"❌ App {exe} non trouvée"

    if action == 'close':
        hwnd = get_hwnd_by_exe(exe)
        if hwnd:
            try:
                win32gui.PostMessage(hwnd, 0x0010, 0, 0)  # WM_CLOSE
                return f"✅ Close {exe}"
            except Exception as e:
                return f"❌ Échec close {exe}: {e}"
        return f"❌ App {exe} non trouvée"

    if action == 'kill':
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == (exe + ".exe").lower():
                    proc.kill()
                    return f"💀 Kill {exe}"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return f"❌ App {exe} non trouvée"

    return f"❌ Action inconnue: {action}"


def execute_action_by_id(action_id):
    """Exécute une action du catalogue par son ID"""
    if action_id not in ACTIONS_CATALOGUE:
        return f"❌ Action inconnue: {action_id}"
    
    action_def = ACTIONS_CATALOGUE[action_id]
    action_type = action_def.get('action', 'cmd')
    
    try:
        # Exécuter une commande shell
        if 'cmd' in action_def:
            subprocess.Popen(action_def['cmd'], shell=True)
            return f"✅ {action_def['name']}"
        
        # Focus sur une application
        elif action_type == 'focus':
            exe = action_def['exe']
            hwnd = get_hwnd_by_exe(exe)
            if hwnd:
                win32gui.SetForegroundWindow(hwnd)
                return f"✅ {action_def['name']}"
            return f"❌ {exe} non trouvé"
        
        # Fermer une application
        elif action_type == 'close':
            exe = action_def['exe']
            hwnd = get_hwnd_by_exe(exe)
            if hwnd:
                win32gui.PostMessage(hwnd, 0x0010, 0, 0)
                return f"✅ {action_def['name']}"
            return f"❌ {exe} non trouvé"
        
        # Kill une application
        elif action_type == 'kill':
            exe = action_def['exe']
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and proc.info['name'].lower() == (exe + ".exe").lower():
                        proc.kill()
                        return f"✅ {action_def['name']}"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return f"❌ {exe} non trouvé"
        
        # Kill toutes les instances
        elif action_type == 'killall':
            exe = action_def['exe']
            count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and proc.info['name'].lower() == (exe + ".exe").lower():
                        proc.kill()
                        count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            if count > 0:
                return f"✅ {count} instance(s) de {exe} fermée(s)"
            return f"❌ {exe} non trouvé"
        
        # Raccourcis clavier
        elif action_type == 'hotkey':
            import pyautogui
            # Désactiver le fail-safe qui peut bloquer dans certains contextes
            pyautogui.FAILSAFE = False
            keys = action_def['keys']
            if len(keys) == 1:
                pyautogui.press(keys[0])
            else:
                pyautogui.hotkey(*keys)
            return f"✅ {action_def['name']}"
        
        # Taper du texte
        elif action_type == 'type':
            import pyautogui
            pyautogui.FAILSAFE = False
            time.sleep(0.1)  # Petit délai pour laisser la fenêtre se préparer
            pyautogui.write(action_def['text'], interval=0.05)
            return f"✅ {action_def['name']}"
        
        else:
            return f"❌ Type d'action non supporté: {action_type}"
            
    except Exception as e:
        # Log l'exception complète pour le debugging
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Exception in execute_action_by_id({action_id}):\n{error_details}")
        return f"❌ Erreur: {e}"

# 🌐 API CMD (ESP appelle !)
@app.route('/cmd', methods=['POST'])
def cmd():
    # Accept JSON, form-encoded or plain body. Use silent get_json to avoid
    # raising 415 when Content-Type is not application/json.
    data = request.get_json(silent=True)
    if not data:
        # Prefer request.form if available (curl -d sends form data)
        if request.form:
            data = request.form.to_dict()
        else:
            # Fallback: parse raw body like "cmd=focus:chrome"
            raw = request.get_data(as_text=True) or ''
            if raw.startswith('cmd='):
                try:
                    from urllib.parse import parse_qs
                    parsed = parse_qs(raw)
                    data = {k: v[0] for k, v in parsed.items()}
                except Exception:
                    data = {'cmd': raw}
            else:
                data = {'cmd': raw}

    cmd_text = data.get('cmd', '')
    result = do_action(cmd_text)
    print(f"🎯 {result}")  # Log
    return jsonify({'status': 'OK', 'result': result})


# 📋 Liste toutes les actions disponibles
@app.route('/actions', methods=['GET'])
def list_actions():
    """Retourne la liste complète des actions avec leurs métadonnées"""
    actions_list = []
    for action_id, action_def in ACTIONS_CATALOGUE.items():
        actions_list.append({
            'id': action_id,
            'name': action_def['name'],
            'category': action_def['category'],
            'icon': action_def['icon']
        })
    return jsonify(actions_list)


# ⚙️ Sauvegarder la configuration (5 favoris)
@app.route('/config', methods=['POST'])
def save_config():
    """Sauvegarde les 5 actions favorites sélectionnées"""
    data = request.get_json()
    favorites = data.get('favorites', [])
    
    if len(favorites) > 5:
        return jsonify({'status': 'error', 'message': 'Maximum 5 favoris'}), 400
    
    # Valider que toutes les actions existent
    for fav_id in favorites:
        if fav_id not in ACTIONS_CATALOGUE:
            return jsonify({'status': 'error', 'message': f'Action inconnue: {fav_id}'}), 400
    
    # Sauvegarder dans config.json
    config = {'favorites': favorites}
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return jsonify({'status': 'OK', 'message': 'Configuration sauvegardée'})


# ⚙️ Charger la configuration
@app.route('/config', methods=['GET'])
def load_config():
    """Charge les 5 actions favorites"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return jsonify(config)
    else:
        return jsonify({'favorites': []})


# 🎯 Exécuter une action par son ID
@app.route('/execute/<action_id>', methods=['POST'])
def execute_action(action_id):
    """Exécute une action du catalogue par son ID"""
    print(f"📥 Executing action: {action_id}")
    result = execute_action_by_id(action_id)
    print(f"🎯 Result: {result}")
    return jsonify({'status': 'OK', 'result': result})


# 🏠 Page d'accueil - Interface web
@app.route('/')
def index():
    """Sert la page HTML de configuration"""
    return send_from_directory('.', 'index.html')

# 📱 Liste APPS ouvertes (pour config web)
@app.route('/apps', methods=['GET'])
def apps():
    apps = {}
    def enum_cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                exe = psutil.Process(pid).name().lower()
                title = win32gui.GetWindowText(hwnd)
                if exe and title:
                    apps[title[:30]] = exe.replace('.exe', '')  # "Google Chrome" → "chrome"
            except:
                pass
        return True
    win32gui.EnumWindows(enum_cb, None)
    return jsonify(list(apps.items()))  # [{"Google Chrome":"chrome"}, ...]

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # N'a pas besoin d'être joignable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def register_mdns_service():
    zeroconf = Zeroconf()
    ip_address = get_local_ip()
    port = 8080
    
    service_info = ServiceInfo(
        "_http._tcp.local.", # Type de service standard pour les serveurs web
        "StreamDeck Server._http._tcp.local.", # Nom du service
        addresses=[socket.inet_aton(ip_address)],
        port=port,
        properties={'path': '/'},
        server="streamdeck-server.local." # Le nom que l'ESP32 cherchera
    )
    
    print(f"Annonce du service mDNS 'streamdeck-server.local.' sur {ip_address}:{port}")
    zeroconf.register_service(service_info)

# --- Fin de la section mDNS ---

# 🚀 Serveur
if __name__ == '__main__':
    # Ensure stdout/stderr can handle Unicode (emoji) on Windows consolese
    try:
        # Python 3.7+: reconfigure the existing streams
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        # Fallback: wrap the buffer with a text wrapper
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except Exception:
            # If we can't change streams, continue and let Python raise if needed
            pass

    print("🚀 StreamDeck PC Server: http://localhost:8080")
    print("📱 Apps: http://localhost:8080/apps")
    print("🎯 Test: curl -X POST http://localhost:8080/cmd -d 'cmd=focus:chrome'")

    # Allow tests to run the file without starting the Flask server by settingi anolemment,
    # the environment variable FENTRE_NO_RUN=1. This makes automated checks safe.
    if os.environ.get('FENTRE_NO_RUN') == '1':
        print('Skipping app.run because FENTRE_NO_RUN=1')
    else:
            # Lancer l'annonce mDNS dans un thread séparé pour ne pas bloquer Flask
        mdns_thread = threading.Thread(target=register_mdns_service)
        mdns_thread.daemon = True
        mdns_thread.start()
        app.run(host='0.0.0.0', port=8080, debug=False)