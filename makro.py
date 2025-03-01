import keyboard
import pyautogui
import time
import pyttsx3
import threading
import json
import os

# Konfigurationsdatei im Benutzerordner speichern
CONFIG_FILE = os.path.expanduser("~/config.json")

waiting_for_confirmation = {}
cooldown = {}
lock = threading.Lock()

# Automatische Umwandlung von "numpad X" in die korrekten Tasten
NUMPAD_MAP = {
    "numpad 1": "end",
    "numpad 2": "down",
    "numpad 3": "page down",
    "numpad 4": "left",
    "numpad 5": "clear",
    "numpad 6": "right",
    "numpad 7": "home",
    "numpad 8": "up",
    "numpad 9": "page up",
    "numpad 0": "insert",
    "numpad .": "delete"
}

def load_config():
    """Lädt die Makros aus der JSON-Datei und ersetzt 'numpad X' durch die richtigen Tasten."""
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
        # Ersetze alle NumPad-Bezeichnungen mit den echten Namen
        return {NUMPAD_MAP.get(k, k): v for k, v in config.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️ Fehler: config.json beschädigt oder fehlt. Erstelle neue Datei...")
        default_config = {
            "numpad 1": {"insert": "Banane", "speak": "Banane"},
            "numpad 2": {"insert": "Apfel", "speak": "Apfel"}
        }
        save_config(default_config)
        return {NUMPAD_MAP.get(k, k): v for k, v in default_config.items()}

def save_config(config):
    """Speichert die Makros in die JSON-Datei."""
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

def speak(text):
    """Spielt die Sprachausgabe ab."""
    def run():
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=run, daemon=True).start()

def reset_confirmation(key):
    """Setzt die Bestätigungs-Wartezeit nach 3 Sekunden zurück."""
    time.sleep(3)
    with lock:
        waiting_for_confirmation[key] = False

def reset_cooldown(key):
    """Setzt den Cooldown nach 2 Sekunden zurück."""
    time.sleep(2)
    cooldown[key] = False

def macro_action(key, data):
    """Führt die Makroaktion aus: Erst sprechen, dann Text einfügen."""
    with lock:
        if cooldown.get(key, False):
            return  # Cooldown aktiv

        if not waiting_for_confirmation.get(key, False):
            speak(data["speak"])
            waiting_for_confirmation[key] = True
            threading.Thread(target=reset_confirmation, args=(key,), daemon=True).start()
        else:
            pyautogui.write(data["insert"])
            waiting_for_confirmation[key] = False
            cooldown[key] = True
            threading.Thread(target=reset_cooldown, args=(key,), daemon=True).start()

def main():
    config = load_config()

    if not config:
        print("❌ Keine Makros gefunden. Bitte erstelle welche mit makro_editor.py!")
        return

    try:
        for key, data in config.items():
            try:
                keyboard.add_hotkey(key, lambda k=key, d=data: macro_action(k, d), suppress=True)
                print(f"✅ Makro geladen: {key} → {data['insert']} (Sagt: {data['speak']})")
            except ValueError:
                print(f"⚠️ Fehler: Taste '{key}' ist ungültig und wird übersprungen!")

        keyboard.wait()
    except KeyboardInterrupt:
        print("🔴 Programm wird beendet...")

if __name__ == "__main__":
    main()
