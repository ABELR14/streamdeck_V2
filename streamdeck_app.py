

import threading
import time
import sys
import os

# Ensure the current dir is project root
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

# Import the server module (fentre.py). It defines `app` and register_mdns_service.
import fentre

# Optional: try to use requests to poll server readiness
try:
    import requests
except Exception:
    requests = None

# Try to import pywebview
try:
    import webview
except Exception:
    webview = None


def start_flask():
    """Start the Flask server from fentre in a background thread."""
    # Determine bind host: env FENTRE_BIND overrides auto-discovery
    bind_host = os.environ.get('FENTRE_BIND') or fentre.get_local_ip()
    print(f"Starting Flask server on {bind_host}:8080")
    try:
        fentre.app.run(host=bind_host, port=8080, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print('Failed to start Flask server:', e)


def wait_for_server(url=None, timeout=10.0):
    """Poll the server until it's up or timeout (returns True if up)."""
    if requests is None:
        # no requests installed; do a naive sleep and hope for the best
        time.sleep(1.0)
        return True
    # Default to the bind host discovered from fentre
    if not url:
        bind_host = os.environ.get('FENTRE_BIND') or fentre.get_local_ip()
        url = f'http://{bind_host}:8080'

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=1.0)
            return True
        except Exception:
            time.sleep(0.2)
    return False


def open_desktop_window(url=None):
    """Open the UI in a native webview window if available, otherwise open browser."""
    if webview is None:
        print('pywebview not installed or failed to import. Opening default browser instead.')
        import webbrowser
        webbrowser.open(url)
        return

    # Create a window and start the event loop. When the window closes, the process will exit.
    window = webview.create_window('StreamDeck PC', url, width=1200, height=820, resizable=True)
    # Start pywebview; this call blocks until the window is closed.
    webview.start(gui=None)


def main():
    print('Starting StreamDeck PC desktop app...')

    # Start Flask in a background daemon thread
    server_thread = threading.Thread(target=start_flask, daemon=True)
    server_thread.start()

    # Start mDNS advertisement in another thread (fentre.register_mdns_service)
    try:
        mdns_thread = threading.Thread(target=fentre.register_mdns_service, daemon=True)
        mdns_thread.start()
    except Exception:
        # If zeroconf missing or registration fails, continue without mDNS
        pass

    # Wait for server to be ready (use bind host or env override)
    bind_host = os.environ.get('FENTRE_BIND') or fentre.get_local_ip()
    server_url = f'http://{bind_host}:8080'
    ok = wait_for_server(server_url, timeout=10.0)
    if not ok:
        print('Warning: server did not respond in time. The UI may not load correctly.')

    # Open the web UI inside a native window (or fallback to browser)
    try:
        open_desktop_window(server_url)
    except Exception as e:
        print('Failed to open native window:', e)
        print('Falling back to the default browser...')
        import webbrowser
        webbrowser.open('http://127.0.0.1:8080')

    print('StreamDeck PC desktop app exiting.')


if __name__ == '__main__':
    main()
