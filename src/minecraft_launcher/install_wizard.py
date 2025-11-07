import questionary
from .selector import select_version


def _ask_modloader():
    use_modloader = questionary.confirm(
        "Would you like to install a modloader (Forge/Fabric)?",
        default=False
    ).ask()

    if not use_modloader:
        return None

    modloader_choice = questionary.select(
        "Select modloader:",
        choices=["Forge", "Fabric", "Back"]
    ).ask()

    if modloader_choice == "Back":
        return "Back"

    return modloader_choice


def run_install_wizard():
    print("\n[Minecraft Installation Setup]\n")

    while True:
        selected_version = select_version("download")
        if selected_version == "Back":
            return "Back"

        modloader = _ask_modloader()
        if modloader == "Back":
            continue

        print("\nSelection complete:")
        print(f" - Version: {selected_version}")
        print(f" - Modloader: {modloader or 'Vanilla'}")

        return {
            "selected_version": selected_version,
            "modloader": modloader
        }
