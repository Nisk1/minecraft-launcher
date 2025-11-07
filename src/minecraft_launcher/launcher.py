import os
import json
import sys
import subprocess
import minecraft_launcher_lib
from .selector import select_version
from .config_wizard import run_setup_wizard
from .installer import install_version
from .profile_applier import apply_profile
from .install_wizard import run_install_wizard
from .update_pack_formats import update_skin_pack_formats


def get_minecraft_dir():
    config_path = os.path.abspath("launcher_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                dir_path = config.get("minecraft_dir")
                if dir_path and os.path.exists(dir_path):
                    return dir_path
        except Exception:
            pass
    default_dir = os.path.abspath("min_dir")
    if not os.path.exists(default_dir):
        os.makedirs(default_dir, exist_ok=True)
    return default_dir


def run_launcher():
    minecraft_directory = get_minecraft_dir()
    config_directory = os.path.abspath("min_configs")

    print("\n[Launcher] Starting Minecraft Launcher\n")

    if not os.path.exists(minecraft_directory):
        print(f"Minecraft directory not found at {minecraft_directory}. Creating it...")
        os.makedirs(minecraft_directory, exist_ok=True)

    selected_version = select_version("installed")
    if not selected_version:
        print("\nNo installed versions found. Running setup and installation...\n")
        install_info = run_install_wizard()
        install_version(install_info)
        selected_version = select_version("installed")
        if not selected_version:
            print("Installation failed or no version was installed.")
            return

    if selected_version == "Back":
        return

    selected_config = select_version("config")
    if selected_config == "Back":
        return

    if not selected_config:
        print("\nNo configuration found. Running setup wizard...\n")
        config = run_setup_wizard()
        selected_config = apply_profile(config)
        print(f"New config created: {selected_config}")

    config_path = os.path.join(config_directory, selected_config)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
    except Exception as e:
        print(f"Failed to load config '{selected_config}': {e}")
        return

    options = {
        "username": profile.get("username", "Player"),
        "uuid": profile.get("uuid", "00000000-0000-0000-0000-000000000000"),
        "token": profile.get("token", ""),
        "jvmArguments": profile.get("jvmArguments", ["-Xms4G", "-Xmx4G"]),
        "disableMultiplayer": profile.get("disableMultiplayer", False),
        "disableChat": profile.get("disableChat", False),
    }

    print("\n[Launcher Summary]")
    print(f" - Minecraft directory: {minecraft_directory}")
    print(f" - Selected version: {selected_version}")
    print(f" - Using config: {selected_config}\n")

    try:
        pack_format_map_path = os.path.abspath("resourcepack_pack_format.json")
        launcher_config_path = os.path.abspath("launcher_config.json")

        update_skin_pack_formats(
            minecraft_dir=minecraft_directory,
            current_version=selected_version,
            pack_format_map_path=pack_format_map_path,
            launcher_config_path=launcher_config_path
        )
    except Exception as e:
        print(f"Failed to update resource pack formats: {e}")

    try:
        minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(
            version=selected_version,
            minecraft_directory=minecraft_directory,
            options=options
        )

        print("Launching Minecraft... please wait.\n")
        completed = subprocess.run(minecraft_command, cwd=os.path.abspath("."))

        if completed.returncode != 0:
            print(f"Minecraft exited with a non-zero code: {completed.returncode}")
            sys.exit(completed.returncode)

        print("\nMinecraft exited successfully!")

        try:
            launcher_config_path = os.path.abspath("launcher_config.json")
            config_data = {}
            if os.path.exists(launcher_config_path):
                with open(launcher_config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            config_data["recently_played"] = selected_version
            with open(launcher_config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            print(f"Saved recently played version: {selected_version}")
        except Exception as e:
            print(f"Failed to save recently played version: {e}")

    except Exception as e:
        print(f"Failed to launch Minecraft: {e}")
