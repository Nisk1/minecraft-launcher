import os
import shutil
import json
import re
import questionary
from tkinter import Tk, filedialog
from PIL import Image

from .path_manager import get_minecraft_dir


def _sanitize_name(name: str) -> str:
    base = os.path.splitext(name)[0]
    sanitized = re.sub(r"[^\w\-]", "_", base.strip().replace(" ", "_"))
    return sanitized


def _confirm_overwrite(path: str, overwrite_all_flag: dict) -> bool:
    if overwrite_all_flag.get("yes_all", False):
        return True

    print(f"\nResource pack folder '{path}' already exists.")
    confirm = questionary.text(
        "Type YES to overwrite, YES-ALL to overwrite all remaining, or anything else to skip:"
    ).ask()

    if confirm == "YES-ALL":
        overwrite_all_flag["yes_all"] = True
        return True
    return confirm == "YES"


def _convert_to_png_if_needed(src_path: str, dest_dir: str) -> str:
    ext = os.path.splitext(src_path)[1].lower()
    if ext in (".png",):
        return src_path

    if ext not in (".jpg", ".jpeg"):
        return None

    try:
        img = Image.open(src_path).convert("RGBA")
        new_name = _sanitize_name(os.path.basename(src_path)) + ".png"
        new_path = os.path.join(dest_dir, new_name)
        img.save(new_path, "PNG")
        print(f"Converted {src_path} -> {new_path}")
        return new_path
    except Exception as e:
        print(f"Failed to convert {src_path}: {e}")
        return None


def _copy_skin_pack(skin_image_path: str, minecraft_dir: str, overwrite_all_flag: dict, skin_name: str = None):
    resourcepacks_dir = os.path.join(minecraft_dir, "resourcepacks")

    original_filename = os.path.basename(skin_image_path)
    default_name = _sanitize_name(original_filename)

    if not skin_name:
        new_name = questionary.text(
            "Enter skin pack name:",
            default=default_name
        ).ask()
        if not new_name:
            print("No name entered, skipping this skin pack.")
            return False
        skin_name = _sanitize_name(new_name)
    else:
        skin_name = _sanitize_name(skin_name)

    resourcepack_dir = os.path.join(resourcepacks_dir, skin_name)

    if os.path.exists(resourcepack_dir):
        if not _confirm_overwrite(resourcepack_dir, overwrite_all_flag):
            print(f"Skipping skin '{skin_name}'.")
            return False
        shutil.rmtree(resourcepack_dir)

    textures_dir = os.path.join(resourcepack_dir, "assets", "minecraft", "textures", "entity", "player")
    branches = ["slim", "wide"]
    player_variants = ["alex", "ari", "efe", "kai", "makena", "noor", "steve", "sunny", "zuri"]

    for branch in branches:
        branch_dir = os.path.join(textures_dir, branch)
        os.makedirs(branch_dir, exist_ok=True)

    for branch in branches:
        for variant in player_variants:
            shutil.copy2(skin_image_path, os.path.join(textures_dir, branch, f"{variant}.png"))

    entity_dir = os.path.join(resourcepack_dir, "assets", "minecraft", "textures", "entity")
    for name in ["alex", "steve"]:
        shutil.copy2(skin_image_path, os.path.join(entity_dir, f"{name}.png"))

    pack_icon_ext = os.path.splitext(original_filename)[1]
    pack_icon_path = os.path.join(resourcepack_dir, f"pack{pack_icon_ext}")
    shutil.copy2(skin_image_path, pack_icon_path)

    mcmeta_path = os.path.join(resourcepack_dir, "pack.mcmeta")
    if not os.path.exists(mcmeta_path):
        mcmeta_content = {
            "pack": {
                "pack_format": 0,
                "min_format": [0, 0],
                "max_format": [0, 0],
                "supported_formats": [0, 0],
                "description": "Custom Player Skin"
            }
        }
        try:
            with open(mcmeta_path, "w", encoding="utf-8") as f:
                json.dump(mcmeta_content, f, indent=2)
        except Exception as e:
            print(f"Failed to create pack.mcmeta: {e}")

    print(f"Skin pack created successfully at:\n{resourcepack_dir}")
    _register_custom_skin_pack(os.path.basename(resourcepack_dir))
    return True


def _open_file_manager(select_type: str):
    root = Tk()
    root.withdraw()
    root.update()
    selected = []

    if select_type == "files":
        selected = filedialog.askopenfilenames(
            title="Select one or more skin image files",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )

    root.destroy()
    return list(selected)


def _register_custom_skin_pack(pack_name: str):
    launcher_config_path = os.path.abspath("launcher_config.json")
    data = {}

    if os.path.exists(launcher_config_path):
        try:
            with open(launcher_config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    if "custom_skins" not in data or not isinstance(data["custom_skins"], list):
        data["custom_skins"] = []

    if pack_name not in data["custom_skins"]:
        data["custom_skins"].append(pack_name)
        try:
            with open(launcher_config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"Registered custom skin pack: {pack_name}")
        except Exception as e:
            print(f"Failed to update launcher_config.json: {e}")


def _update_launcher_config_rename(old_name: str, new_name: str):
    launcher_config_path = os.path.abspath("launcher_config.json")
    if not os.path.exists(launcher_config_path):
        return
    try:
        with open(launcher_config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "custom_skins" in data and old_name in data["custom_skins"]:
            data["custom_skins"].remove(old_name)
            data["custom_skins"].append(new_name)
        with open(launcher_config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def _update_launcher_config_delete(name: str):
    launcher_config_path = os.path.abspath("launcher_config.json")
    if not os.path.exists(launcher_config_path):
        return
    try:
        with open(launcher_config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "custom_skins" in data and name in data["custom_skins"]:
            data["custom_skins"].remove(name)
        with open(launcher_config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def apply_skin():
    minecraft_dir = get_minecraft_dir()
    min_skin_dir = os.path.abspath("min_skin")
    os.makedirs(min_skin_dir, exist_ok=True)

    skin_files = _open_file_manager("files")
    if not skin_files:
        print("No images selected.")
        return

    processed_files = []
    overwrite_all_flag = {"yes_all": False}

    for src_path in skin_files:
        ext = os.path.splitext(src_path)[1].lower()
        if ext not in (".png", ".jpg", ".jpeg"):
            print(f"Skipping unsupported file: {src_path}")
            continue

        default_name = _sanitize_name(os.path.splitext(os.path.basename(src_path))[0])
        user_name = questionary.text("Enter skin pack name:", default=default_name).ask()
        if not user_name:
            print("No name entered, skipping this skin pack.")
            continue
        skin_name = _sanitize_name(user_name)

        dest_path = os.path.join(min_skin_dir, f"{skin_name}.png")

        if ext in (".jpg", ".jpeg"):
            converted_path = _convert_to_png_if_needed(src_path, min_skin_dir)
            if converted_path:
                final_path = os.path.join(min_skin_dir, f"{skin_name}.png")
                os.rename(converted_path, final_path)
                processed_files.append(final_path)
            continue
        else:
            if os.path.exists(dest_path) and not overwrite_all_flag["yes_all"]:
                confirm = questionary.text(
                    f"File '{skin_name}.png' exists in min_skin. Type YES to overwrite, YES-ALL to overwrite all remaining, anything else to skip:"
                ).ask()
                if confirm == "YES-ALL":
                    overwrite_all_flag["yes_all"] = True
                elif confirm != "YES":
                    print(f"Skipping {skin_name}")
                    continue
            shutil.copy2(src_path, dest_path)
            processed_files.append(dest_path)

    created_count = 0
    overwrite_all_flag = {"yes_all": False}
    for skin_path in processed_files:
        skin_base_name = os.path.splitext(os.path.basename(skin_path))[0]
        if _copy_skin_pack(skin_path, minecraft_dir, overwrite_all_flag, skin_name=skin_base_name):
            created_count += 1

    if created_count == 0:
        print("No skin packs were created.")
    else:
        print(f"\n{created_count} skin pack(s) created successfully.")


def rename_skin():
    minecraft_dir = get_minecraft_dir()
    resourcepacks_dir = os.path.join(minecraft_dir, "resourcepacks")
    min_skin_dir = os.path.abspath("min_skin")

    if not os.path.exists(resourcepacks_dir):
        print("\nNo resourcepacks directory found.\n")
        return

    skin_packs = [d for d in os.listdir(resourcepacks_dir) if os.path.isdir(os.path.join(resourcepacks_dir, d))]
    if not skin_packs:
        print("\nNo skins found to rename.\n")
        return

    selected = questionary.select(
        "Select a skin to rename:",
        choices=skin_packs + ["Cancel"]
    ).ask()

    if selected == "Cancel" or not selected:
        print("\nRename canceled.\n")
        return

    new_name = questionary.text(
        "Enter new skin name:",
        default=selected
    ).ask()

    if not new_name:
        print("\nNo new name entered.\n")
        return

    new_name_sanitized = _sanitize_name(new_name)
    old_pack_path = os.path.join(resourcepacks_dir, selected)
    new_pack_path = os.path.join(resourcepacks_dir, new_name_sanitized)

    if os.path.exists(new_pack_path):
        print("\nA skin with that name already exists.\n")
        return

    try:
        os.rename(old_pack_path, new_pack_path)

        old_skin_path = os.path.join(min_skin_dir, f"{selected}.png")
        new_skin_path = os.path.join(min_skin_dir, f"{new_name_sanitized}.png")
        if os.path.exists(old_skin_path):
            os.rename(old_skin_path, new_skin_path)

        _update_launcher_config_rename(selected, new_name_sanitized)
        print(f"\nSkin renamed to '{new_name_sanitized}'.\n")
    except Exception as e:
        print(f"\nFailed to rename skin: {e}\n")



def delete_skin():
    minecraft_dir = get_minecraft_dir()
    resourcepacks_dir = os.path.join(minecraft_dir, "resourcepacks")
    min_skin_dir = os.path.abspath("min_skin")

    if not os.path.exists(resourcepacks_dir):
        print("\nNo resourcepacks directory found.\n")
        return

    skin_packs = [d for d in os.listdir(resourcepacks_dir) if os.path.isdir(os.path.join(resourcepacks_dir, d))]
    if not skin_packs:
        print("\nNo skins found to delete.\n")
        return

    selected = questionary.select(
        "Select a skin to delete:",
        choices=skin_packs + ["Cancel"]
    ).ask()

    if selected == "Cancel" or not selected:
        print("\nDeletion canceled.\n")
        return

    confirm = questionary.text(
        f"Type YES to confirm deletion of '{selected}':"
    ).ask()

    if confirm != "YES":
        print("\nDeletion aborted.\n")
        return

    try:
        shutil.rmtree(os.path.join(resourcepacks_dir, selected))

        skin_file_path = os.path.join(min_skin_dir, f"{selected}.png")
        if os.path.exists(skin_file_path):
            os.remove(skin_file_path)

        _update_launcher_config_delete(selected)
        print(f"\nSkin '{selected}' deleted successfully.\n")
    except Exception as e:
        print(f"\nFailed to delete skin: {e}\n")
