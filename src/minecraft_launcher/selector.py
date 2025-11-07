import questionary
import minecraft_launcher_lib
import os
import json
import re
from questionary import Separator
from .path_manager import get_minecraft_dir

LAUNCHER_CONFIG_PATH = os.path.abspath("launcher_config.json")


def _load_recent_version():
    if os.path.exists(LAUNCHER_CONFIG_PATH):
        try:
            with open(LAUNCHER_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("recently_played")
        except Exception:
            pass
    return None


def _extract_version_number(vname: str):
    match = re.search(r"(\d+\.\d+(?:\.\d+)*)", vname)
    if match:
        return tuple(int(p) for p in match.group(1).split("."))
    return (0, 0, 0)


def _sort_versions(version_list):
    return sorted(version_list, key=lambda v: _extract_version_number(v), reverse=True)


def select_version(mode: str = "download"):
    if mode not in ("download", "installed", "config"):
        raise ValueError("mode must be 'download', 'installed', or 'config'")

    if mode == "config":
        config_dir = os.path.abspath("min_configs")

        if not os.path.isdir(config_dir):
            print(f"Config directory not found: {config_dir}")
            return None

        configs = sorted(
            f for f in os.listdir(config_dir)
            if f.endswith(".json") and os.path.isfile(os.path.join(config_dir, f))
        )

        if not configs:
            print("No configuration files found in 'min_configs'.")
            return None

        if len(configs) == 1:
            selected = configs[0]
            print(f"Only one configuration found: {selected}")
            return selected

        print("\n[Config Selector] Choose from existing configuration profiles\n")

        choices = configs + [Separator(" "), "Quit"]

        selected = questionary.select(
            "Select a configuration profile:",
            choices=choices,
        ).ask()

        if selected == "Quit":
            return "Back"

        return selected

    elif mode == "installed":
        minecraft_dir = get_minecraft_dir()

        installed = minecraft_launcher_lib.utils.get_installed_versions(minecraft_dir)

        if not installed:
            print("No installed versions found.")
            return None

        if len(installed) == 1:
            selected = installed[0]["id"]
            print(f"Only one installed version found: {selected}")
            return selected

        installed_names = [v["id"] for v in installed]

        recent = _load_recent_version()

        releases = []
        modded = []
        snapshots = []

        for v in installed_names:
            vid = v.lower()

            if "forge" in vid or "fabric" in vid:
                modded.append(v)
                continue

            if (
                re.search(r"\d{2}w\d{2}[a-z]", vid)
                or "snapshot" in vid
                or "rc" in vid
                or "pre" in vid
            ):
                snapshots.append(v)
                continue

            releases.append(v)

        releases = _sort_versions(releases)
        modded = _sort_versions(modded)
        snapshots = _sort_versions(snapshots)

        choices = []

        if recent and recent in installed_names:
            choices.append(Separator("Recently played"))
            choices.append(recent)
            choices.append(Separator(" "))

        if releases:
            choices.append(Separator("---Releases (newest → oldest)---"))
            choices.extend(releases)
            choices.append(Separator(" "))
        if modded:
            choices.append(Separator("---Modded versions (Forge/Fabric)---"))
            choices.extend(modded)
            choices.append(Separator(" "))
        if snapshots:
            choices.append(Separator("---Snapshots / RCs---"))
            choices.extend(snapshots)
            choices.append(Separator(" "))

        choices.append("Back")

        print("\n[Version Selector] Choose from installed Minecraft versions\n")
        print("Select 'Back' to return to the previous menu. This option appears last in the list.\n")

        selected = questionary.select(
            "Select an installed version:",
            choices=choices
        ).ask()

        if selected == "Back" or not selected:
            print("\nReturning to previous menu.\n")
            return "Back"

        return selected

    else:
        print("\n[Version Selector] Choose a version to download/install\n")
    
        version_type = questionary.select(
            "Select version type:",
            choices=[
                "Latest",
                "Releases",
                "Snapshots",
                Separator(" "),
                "Back"
            ]
        ).ask()
    
        if version_type == "Back":
            return "Back"
    
        all_versions = minecraft_launcher_lib.utils.get_version_list()
    
        if version_type == "Latest":
            latest_release = minecraft_launcher_lib.utils.get_latest_version()["release"]
            print(f"\nLatest release selected: {latest_release}")
            return latest_release
    
        elif version_type == "Releases":
            versions = [v["id"] for v in all_versions if v["type"] == "release"]
        else:
            versions = [v["id"] for v in all_versions if v["type"] != "release"]
    
        print("\nTip: Press [TAB] to autocomplete version names. Select 'Quit' to return to the previous menu. This option appears last in the list.\n")
    
        while True:
            selected = questionary.autocomplete(
                "Choose Minecraft version:",
                choices=versions + ["Quit"],
                validate=lambda val: True
            ).ask()
    
            if selected is None or selected == "Quit":
                print("Selection cancelled, going back.")
                return "Back"
    
            if not selected.strip():
                print("Please enter or select a valid version.\n")
                continue
            
            if selected not in versions:
                print(f"'{selected}' is not a valid Minecraft version. Please try again.\n")
                continue
            
            break
        
        print(f"\nSelected Minecraft version: {selected}")
        return selected
