import os
import json

def update_skin_pack_formats(minecraft_dir, current_version, pack_format_map_path, launcher_config_path):
    print("\n[Resource Pack Updater] Checking skin packs...")

    resourcepacks_dir = os.path.join(minecraft_dir, "resourcepacks")

    if not os.path.exists(pack_format_map_path):
        print(f"Missing resourcepack_pack_format.json at {pack_format_map_path}")
        return

    try:
        with open(pack_format_map_path, "r", encoding="utf-8") as f:
            version_to_pack = json.load(f)
    except Exception as e:
        print(f"Failed to read resourcepack_pack_format.json: {e}")
        return

    pack_format = version_to_pack.get(current_version)
    if pack_format is None:
        print(f"No exact pack_format found for version {current_version}.")
        try:
            numeric_formats = [float(v) for v in version_to_pack.values() if isinstance(v, (int, float, str))]
            pack_format = int(max(numeric_formats))
            print(f"Using latest known pack_format: {pack_format}")
        except Exception:
            pack_format = 18

    tracked_packs = []
    if os.path.exists(launcher_config_path):
        try:
            with open(launcher_config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                tracked_packs = data.get("custom_skins", [])
        except Exception as e:
            print(f"Could not read launcher_config.json: {e}")

    if not tracked_packs:
        print("No tracked custom skins found in launcher_config.json.")
        return

    updated_count = 0
    for pack_name in tracked_packs:
        pack_dir = os.path.join(resourcepacks_dir, pack_name)
        mcmeta_path = os.path.join(pack_dir, "pack.mcmeta")

        if not os.path.exists(mcmeta_path):
            continue

        try:
            with open(mcmeta_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            pack_data = data.get("pack", {})
            old_pack_format = pack_data.get("pack_format")

            if old_pack_format != pack_format:
                pack_data["pack_format"] = pack_format

            pack_data["min_format"] = [1, 0]
            pack_data["max_format"] = [pack_format, 0]
            pack_data["supported_formats"] = [1, pack_format]

            data["pack"] = pack_data

            with open(mcmeta_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            print(f"Updated '{pack_name}' pack.mcmeta: {old_pack_format} → {pack_format}, formats added.")
            updated_count += 1

        except Exception as e:
            print(f"Failed to update {pack_name}: {e}")

    if updated_count == 0:
        print("All tracked skin packs are already up to date.")
    else:
        print(f"Updated {updated_count} tracked skin packs to pack_format {pack_format}.")
