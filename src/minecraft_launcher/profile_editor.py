import os
import json
import re
import questionary
from .selector import select_version
from .profile_applier import get_minecraft_offline_uuid


def update_jvm_ram(jvm_args, ram: str):
    updated_args = []
    xmx_set = False
    for arg in jvm_args:
        if arg.startswith("-Xmx"):
            updated_args.append(f"-Xmx{ram}")
            xmx_set = True
        else:
            updated_args.append(arg)
    if not xmx_set:
        updated_args.append(f"-Xmx{ram}")
    return updated_args


def edit_existing_profile():
    config_dir = os.path.abspath("min_configs")
    os.makedirs(config_dir, exist_ok=True)

    print("\n[Profile Editor] Starting...\n")

    selected = select_version("config")
    if not selected:
        print("No configuration selected or available.")
        return

    profile_path = os.path.join(config_dir, selected)

    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to load profile: {e}")
        return

    print(f"\nEditing profile: {selected}\n")

    old_username = data.get("username", "")
    old_jvm = data.get("jvmArguments", [])

    def _validate_username(name: str):
        return bool(re.match(r"^[A-Za-z0-9_]{3,16}$", name))

    while True:
        username = questionary.text(
            "Enter username:",
            default=old_username,
            validate=lambda val: _validate_username(val) or "Invalid username (3–16 chars, letters/numbers/_ only)"
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

    current_ram = next((arg[4:] for arg in old_jvm if arg.startswith("-Xmx")), "4G")
    while True:
        ram_amount = questionary.text(
            "Enter RAM amount (e.g., 4G, 4096M) [Default = 4G]:",
            default=current_ram,
            validate=_validate_ram
        ).ask()
        if ram_amount:
            break

    disable_multiplayer = questionary.confirm(
        "Disable Multiplayer?", default=data.get("disableMultiplayer", False)
    ).ask()

    disable_chat = questionary.confirm(
        "Disable Chat?", default=data.get("disableChat", False)
    ).ask()

    new_data = data.copy()
    new_data["username"] = username
    new_data["disableMultiplayer"] = disable_multiplayer
    new_data["disableChat"] = disable_chat
    new_data["jvmArguments"] = update_jvm_ram(old_jvm, ram_amount)

    if username != old_username:
        new_data["uuid"] = get_minecraft_offline_uuid(username)
        print(f"\nUsername changed → generated new UUID: {new_data['uuid']}")

    print("\n[Profile Preview After Edits]")
    for k, v in new_data.items():
        print(f" - {k}: {v}")

    confirm = questionary.text("\nType YES to save these changes (anything else to cancel):").ask()
    if confirm != "YES":
        print("Changes discarded.")
        return

    try:
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=2)
        print(f"\nProfile updated successfully: {profile_path}")
    except Exception as e:
        print(f"Failed to save profile: {e}")
