from tkinter import Tk, Label, Entry, Button, Listbox, Scrollbar, END
import json
import os

CONFIG_FILE = os.path.join(os.path.expanduser("~"), "config.json")

def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

def add_macro():
    key = entry_key.get().lower().replace("num ", "numpad ")  # "num 1" → "numpad 1"
    speak_text = entry_speak.get()
    insert_text = entry_insert.get()

    if key and insert_text:
        config = load_config()
        config[key] = {"speak": speak_text, "insert": insert_text}
        save_config(config)
        update_listbox()
        entry_key.delete(0, END)
        entry_speak.delete(0, END)
        entry_insert.delete(0, END)


def delete_macro():
    """Löscht das ausgewählte Makro aus der Konfigurationsdatei."""
    try:
        selected_index = listbox.curselection()
        if not selected_index:
            return  # Falls nichts ausgewählt wurde, nichts tun
        
        # Hole den ausgewählten Eintrag
        selected_item = listbox.get(selected_index)
        key_to_delete = selected_item.split(":")[0]  # "numpad 1: Banane (Sagt: Du pastest Banane)" → "numpad 1"
        
        # Konfiguration laden
        config = load_config()
        
        if key_to_delete in config:
            del config[key_to_delete]  # Entferne das Makro
            save_config(config)  # Speichere die neue Konfiguration
            
            # Aktualisiere die Listbox
            update_listbox()
            print(f"Makro '{key_to_delete}' gelöscht.")
    
    except Exception as e:
        print(f"Fehler beim Löschen: {e}")


def update_listbox():
    """Aktualisiert die Makro-Liste im Editor."""
    listbox.delete(0, END)  # Löscht alle Einträge in der GUI
    config = load_config()
    for key, data in config.items():
        listbox.insert(END, f"{key}: {data['insert']} (Sagt: {data['speak']})")


# GUI
root = Tk()
root.title("Makro Editor")

Label(root, text="Taste:").grid(row=0, column=0)
entry_key = Entry(root)
entry_key.grid(row=0, column=1)

Label(root, text="Gesprochener Text:").grid(row=1, column=0)
entry_speak = Entry(root)
entry_speak.grid(row=1, column=1)

Label(root, text="Eingefügter Text:").grid(row=2, column=0)
entry_insert = Entry(root)
entry_insert.grid(row=2, column=1)

Button(root, text="Makro hinzufügen", command=add_macro).grid(row=3, column=0, columnspan=2)
Button(root, text="Makro löschen", command=delete_macro).grid(row=4, column=0, columnspan=2)

listbox = Listbox(root, height=10, width=50)
listbox.grid(row=5, column=0, columnspan=2)

scrollbar = Scrollbar(root)
scrollbar.grid(row=5, column=2, sticky="ns")
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

update_listbox()
root.mainloop()
