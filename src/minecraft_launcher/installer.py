import os
from tqdm import tqdm
import minecraft_launcher_lib
from .path_manager import get_minecraft_dir
import questionary
from .selector import select_version

_progress_bar = None
_current_max = 0


def _set_status(status: str):
    pass


def _set_max(new_max: int):
    global _progress_bar, _current_max
    _current_max = new_max

    if new_max <= 0:
        return

    if _progress_bar:
        _progress_bar.close()

    _progress_bar = tqdm(
        total=new_max,
        desc="Installing",
        ncols=100,
        colour="white"
    )


def _set_progress(progress: int):
    global _progress_bar, _current_max
    if not _progress_bar or _current_max == 0:
        return

    _progress_bar.n = progress
    _progress_bar.refresh()


CALLBACKS = {
    "setStatus": _set_status,
    "setProgress": _set_progress,
    "setMax": _set_max
}


def install_version(config: dict):
    global _progress_bar

    minecraft_dir = get_minecraft_dir()

    version = config.get("selected_version")
    modloader = config.get("modloader")

    print(f"\n[Installer] Preparing to install Minecraft {version} ({modloader or 'Vanilla'})")
    print(f"Install directory: {minecraft_dir}\n")

    action = questionary.select(
        "Do you want to proceed with the installation?",
        choices=[
            "Proceed",
            "Abort"
        ]
    ).ask()

    if action == "Abort":
        print("\nInstallation aborted by user. Returning to previous menu.\n")
        return "Back"

    try:
        if modloader == "Forge":
            print(f"Installing Forge for version {version}...")
            forge_version = minecraft_launcher_lib.forge.find_forge_version(version)
            if not forge_version:
                print("No compatible Forge version found.")
                return config
            minecraft_launcher_lib.forge.install_forge_version(
                forge_version, minecraft_dir, callback=CALLBACKS
            )

        elif modloader == "Fabric":
            print(f"Installing Fabric for version {version}...")
            minecraft_launcher_lib.fabric.install_fabric(
                version, minecraft_dir, callback=CALLBACKS
            )

        else:
            print(f"Installing Vanilla Minecraft {version}...")
            minecraft_launcher_lib.install.install_minecraft_version(
                version, minecraft_dir, callback=CALLBACKS
            )

        print("\nInstallation complete!")

    except Exception as exc:
        print(f"\nInstallation failed: {exc}")

    finally:
        if _progress_bar:
            _progress_bar.close()
            _progress_bar = None

    return config


def delete_version():
    selected = select_version(mode="installed")

    if selected == "Back" or not selected:
        print("\nDeletion canceled.\n")
        return

    confirm = questionary.text(
        f"Type YES to confirm deletion of Minecraft version '{selected}':"
    ).ask()

    if confirm != "YES":
        print("\nDeletion aborted (confirmation not given).\n")
        return

    minecraft_dir = get_minecraft_dir()
    version_path = os.path.join(minecraft_dir, "versions", selected)

    try:
        for root, dirs, files in os.walk(version_path, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(version_path)
        print(f"\nMinecraft version '{selected}' successfully deleted.\n")
    except Exception as e:
        print(f"\nFailed to delete Minecraft version '{selected}': {e}\n")
