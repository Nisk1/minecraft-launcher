import questionary
from questionary import Separator
import os
import sys
import json
import subprocess
from os import name

from .config_wizard import run_setup_wizard
from .install_wizard import run_install_wizard
from .installer import install_version, delete_version
from .profile_applier import apply_profile
from .launcher import run_launcher
from .skin_manager import apply_skin, rename_skin, delete_skin
from .profile_editor import edit_existing_profile


def clearscreen():
    if name == 'nt':
        _ = os.system("cls")
    else:
        _ = os.system("clear")


def load_launcher_config():
    config_path = os.path.abspath("launcher_config.json")
    if not os.path.exists(config_path):
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to read launcher_config.json: {e}")
        return {}


def skin_related_menu():
    while True:
        action = questionary.select(
            "Skin-related options:",
            choices=[
                "Create new skin",
                "Rename existing skin",
                "Delete existing skin",
                Separator(" "),
                "Back"
            ]
        ).ask()

        if action == "Create new skin":
            apply_skin()

        elif action == "Rename existing skin":
            rename_skin()

        elif action == "Delete existing skin":
            delete_skin()

        elif action == "Back":
            clearscreen()
            break


def profile_related_menu():
    while True:
        action = questionary.select(
            "Minecraft profiles related options:",
            choices=[
                "Create new profile",
                "Edit existing profile",
                "Delete existing profile",
                Separator(" "),
                "Back"
            ]
        ).ask()

        if action == "Create new profile":
            config = run_setup_wizard()
            profile_path = apply_profile(config)
            print(f"\nProfile successfully created at: {profile_path}")

        elif action == "Edit existing profile":
            edit_existing_profile()

        elif action == "Delete existing profile":
            delete_existing_profile()

        elif action == "Back":
            clearscreen()
            break

def delete_existing_profile():
    config_dir = os.path.abspath("min_configs")

    if not os.path.exists(config_dir):
        print(f"\nConfig directory not found at: {config_dir}")
        return

    configs = [f for f in os.listdir(config_dir) if f.endswith(".json")]

    if not configs:
        print("\nNo profiles found in min_config/. Nothing to delete.\n")
        return

    selected = questionary.select(
        "Select a profile to delete:",
        choices=configs + [Separator(" "), "Cancel"]
    ).ask()

    if selected == "Cancel" or not selected:
        print("\nDeletion canceled.\n")
        return

    confirm = questionary.text(
        f"Type YES to confirm deletion of '{selected}':"
    ).ask()

    if confirm != "YES":
        print("\nDeletion aborted (confirmation not given).\n")
        return

    try:
        file_path = os.path.join(config_dir, selected)
        os.remove(file_path)
        print(f"\nProfile '{selected}' successfully deleted.\n")
    except Exception as e:
        print(f"\nFailed to delete profile '{selected}': {e}\n")


def directories_related_menu():
    while True:
        action = questionary.select(
            "Directory-related options:",
            choices=[
                "Open launcher directory",
                "Open Minecraft directory",
                Separator(" "),
                "Back"
            ]
        ).ask()

        if action == "Open launcher directory":
            open_directory(os.getcwd(), "Launcher (root)")

        elif action == "Open Minecraft directory":
            open_minecraft_directory()

        elif action == "Back":
            clearscreen()
            break


def open_minecraft_directory():
    config = load_launcher_config()
    mc_path = config.get("minecraft_dir")

    if mc_path and os.path.exists(mc_path):
        print(f"\nOpening Minecraft directory from config: {mc_path}")
        open_directory(mc_path, "Minecraft")
    else:
        print("\nMinecraft directory not found in launcher_config.json or path invalid.")
        print("Opening default Minecraft directory instead (./min_dir).")
        fallback = os.path.abspath("min_dir")
        open_directory(fallback, "Default Minecraft")


def open_directory(path: str, label: str):
    directory = os.path.abspath(path)
    print(f"\nOpening {label} directory: {directory}")

    try:
        if not os.path.exists(directory):
            print(f"{label} directory does not exist at: {directory}")
            return

        if name == 'nt':
            os.startfile(directory)
        elif os.name == 'posix':
            subprocess.run(['xdg-open' if sys.platform.startswith('linux') else 'open', directory])
        else:
            print("Unsupported platform. Please open manually.")
    except Exception as e:
        print(f"Failed to open {label} directory: {e}")


def installations_related_menu():
    while True:
        action = questionary.select(
            "Installations-related options:",
            choices=[
                "Install new MC version",
                "Delete existing MC version",
                Separator(" "),
                "Back"
            ]
        ).ask()

        if action == "Install new MC version":
            install_info = run_install_wizard()
            print("install_info: ",install_info)
            if install_info != "Back":
                install_version(install_info)
                print(f"\nMinecraft {install_info['selected_version']} installation complete!")
            else:
                print("\nAborting Minecraft installation!")

        elif action == "Delete existing MC version":
            delete_version()

        elif action == "Back":
            clearscreen()
            break


def main():
    while True:
        action = questionary.select(
            "What do you want to do?",
            choices=[
                "Launcher",
                "Install new MC version",
                "Other",
                Separator(" "),
                "Exit"
            ]
        ).ask()

        if action == "Launcher":
            run_launcher()

        elif action == "Install new MC version":
            install_info = run_install_wizard()
            if install_info != "Back":
                install_version(install_info)
                print(f"\nMinecraft {install_info['selected_version']} installation complete!")
            else:
                print("\nAborting Minecraft installation!")

        elif action == "Other":
            sub_action = questionary.select(
                "Other options:",
                choices=[
                    "Skin related",
                    "MC profiles related",
                    "Installations related",
                    "Directories related",
                    Separator(" "),
                    "Back"
                ]
            ).ask()

            if sub_action == "Skin related":
                clearscreen()
                skin_related_menu()

            elif sub_action == "MC profiles related":
                clearscreen()
                profile_related_menu()

            elif sub_action == "Installations related":
                clearscreen()
                installations_related_menu()

            elif sub_action == "Directories related":
                clearscreen()
                directories_related_menu()

            elif sub_action == "Back":
                clearscreen()
                continue

        elif action == "Exit":
            print("\nExiting launcher. Goodbye!\n")
            break


if __name__ == "__main__":
    main()
