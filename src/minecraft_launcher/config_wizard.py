import os
import re
import questionary
import minecraft_launcher_lib


def _select_account_type():
    account_type = questionary.select(
        "Select account type:",
        choices=[
            "Offline",
            "Online (not available yet)"
        ]
    ).ask()

    if account_type.startswith("Online"):
        print("Online login not implemented. Using offline mode instead.")
        return "offline"

    return "offline"


def _get_player_settings():
    def _validate_username(name: str):
        return bool(re.match(r"^[A-Za-z0-9_]{3,16}$", name))

    while True:
        username = questionary.text(
            "Enter username:",
            validate=lambda val: _validate_username(val) or "Invalid username (3-16 chars, letters/numbers/_ only)"
        ).ask()
        if username:
            break

    def _validate_ram(ram: str):
        if not re.match(r"^\d+[GM]$", ram, re.IGNORECASE):
            return "Invalid format. Use e.g., 4G or 4096M."
        value = int(re.match(r"^(\d+)", ram).group(1))
        if ram.upper().endswith("G") and value < 4:
            return "Minimum RAM is 4G."
        if ram.upper().endswith("M") and value < 4096:
            return "Minimum RAM is 4096M."
        return True

    while True:
        ram_amount = questionary.text(
            "Enter RAM amount (e.g., 4G, 4096M) [Default = 4G]:",
            default="4G",
            validate=_validate_ram
        ).ask()
        if ram_amount:
            break

    disable_multiplayer = questionary.confirm("Disable Multiplayer?", default=False).ask()
    disable_chat = questionary.confirm("Disable Chat?", default=False).ask()

    return {
        "username": username,
        "ram_amount": ram_amount or "4G",
        "disable_multiplayer": disable_multiplayer,
        "disable_chat": disable_chat,
    }


def run_setup_wizard():
    account_type = _select_account_type()
    player_settings = _get_player_settings()

    config = {
        "account_type": account_type,
        **player_settings,
    }

    print("\nConfiguration complete:")
    for key, val in config.items():
        print(f" - {key}: {val}")

    return config
