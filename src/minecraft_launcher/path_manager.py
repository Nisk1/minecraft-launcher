import os
import sys
import json
import platform
import subprocess
from tkinter import Tk, filedialog
import questionary

DEFAULT_MIN_DIR = os.path.abspath("min_dir")
CONFIG_FILE = os.path.abspath("launcher_config.json")


def load_launcher_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            print("Failed to read launcher_config.json, using empty config.")
    return {}


def save_launcher_config(config: dict):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print(f"launcher_config.json updated successfully!")
    except Exception as e:
        print(f"Failed to save launcher configuration: {e}")


def open_in_file_manager(path):
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform.startswith("darwin"):
        subprocess.run(["open", path])
    elif sys.platform.startswith("linux"):
        subprocess.run(["xdg-open", path])
    else:
        print(f"File manager open not supported. Folder: {path}")


def prompt_minecraft_dir():
    print("\n[Minecraft Directory Setup]")

    options = [
        f"Root folder (default min_dir) → {DEFAULT_MIN_DIR}",
        "Choose custom location..."
    ]

    choice = questionary.select(
        "Select an installation folder option:",
        choices=options,
        default=None
    ).ask()

    if choice.startswith("Root"):
        selected_dir = DEFAULT_MIN_DIR
    else:
        print("Please select a folder in the dialog...")
        root = Tk()
        root.withdraw()
        selected_dir = filedialog.askdirectory()
        root.destroy()
        if not selected_dir:
            print("No folder selected, falling back to default root folder.")
            selected_dir = DEFAULT_MIN_DIR
        else:
            print(f"Selected folder: {selected_dir}")

    os.makedirs(selected_dir, exist_ok=True)

    config = load_launcher_config()
    config["minecraft_dir"] = selected_dir
    save_launcher_config(config)

    return selected_dir


def get_minecraft_dir():
    config = load_launcher_config()
    saved_dir = config.get("minecraft_dir")

    if saved_dir and os.path.exists(saved_dir):
        return saved_dir

    versions_dir = os.path.join(DEFAULT_MIN_DIR, "versions")
    versions_exist = os.path.exists(versions_dir) and os.listdir(versions_dir)

    if not saved_dir and not versions_exist:
        return prompt_minecraft_dir()

    if not saved_dir:
        os.makedirs(DEFAULT_MIN_DIR, exist_ok=True)
        print(f"\nUsing default Minecraft folder: {DEFAULT_MIN_DIR}")
        config["minecraft_dir"] = DEFAULT_MIN_DIR
        save_launcher_config(config)

    return config.get("minecraft_dir", DEFAULT_MIN_DIR)
