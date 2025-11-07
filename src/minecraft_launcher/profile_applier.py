import json
import os
import questionary
import hashlib
import uuid


def get_minecraft_offline_uuid(username: str) -> str:
    name = f"OfflinePlayer:{username}"
    name_bytes = name.encode("utf-8")
    hash_bytes = hashlib.md5(name_bytes).digest()
    generated_uuid = uuid.UUID(bytes=hash_bytes)
    return str(generated_uuid)


def apply_profile(config: dict, output_path: str = None):
    username = config.get("username", "Player")
    uuid_value = get_minecraft_offline_uuid(username)
    token = ""

    ram_amount = config.get("ram_amount", "4G").upper()
    disable_multiplayer = config.get("disable_multiplayer", False)
    disable_chat = config.get("disable_chat", False)

    jvm_args = [
        "-Xms4G",
        f"-Xmx{ram_amount}"
    ]

    profile_data = {
        "username": username,
        "uuid": uuid_value,
        "token": token,
        "jvmArguments": jvm_args,
        "disableMultiplayer": disable_multiplayer,
        "disableChat": disable_chat
    }

    config_dir = os.path.abspath("min_configs")
    os.makedirs(config_dir, exist_ok=True)

    while True:
        profile_name = questionary.text(
            "Enter a name for this Minecraft profile (e.g., 'MySurvivalProfile'):",
            default="MyMinecraftProfile"
        ).ask()

        if not profile_name:
            print("Profile name cannot be empty.")
            continue

        safe_name = "".join(c for c in profile_name if c.isalnum() or c in (" ", "_", "-")).strip()
        if not safe_name:
            print("Invalid profile name. Use letters, numbers, underscores, or hyphens.")
            continue

        while True:
            output_path = os.path.join(config_dir, f"{safe_name}.json")

            if os.path.exists(output_path):
                print(f"\nA profile named '{safe_name}.json' already exists in 'min_configs'.")
                confirm = questionary.text(
                    "Type YES (in ALL CAPS) to overwrite, or enter a NEW profile name:"
                ).ask()

                if confirm == "YES":
                    print(f"Overwriting existing profile '{safe_name}.json'...")
                    break
                elif confirm:
                    safe_name = "".join(c for c in confirm if c.isalnum() or c in (" ", "_", "-")).strip()
                    continue
                else:
                    continue
            else:
                break

        break

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

    print(f"\nMinecraft profile created at: {output_path}")
    return output_path
