import os
import shutil

BALATRO_DIR = r"E:\BalatroTest\balatro_mod\Balatro"
TARGET_RAW_DIR = r"E:\BalatroTest\balatro_mod\src\python_orchestrator\dataaw"

def extract_lua_files():
    print(f"Extracting Lua files from {BALATRO_DIR} to {TARGET_RAW_DIR}")

    if not os.path.exists(TARGET_RAW_DIR):
        os.makedirs(TARGET_RAW_DIR)

    files_to_copy = []

    # Always copy card.lua as it's likely a primary definition file
    card_lua_path = os.path.join(BALATRO_DIR, "card.lua")
    if os.path.exists(card_lua_path):
        files_to_copy.append(card_lua_path)

    # Search for other relevant files (joker, tarot, planet)
    for root, _, files in os.walk(BALATRO_DIR):
        for file in files:
            lower_file = file.lower()
            if lower_file.endswith(".lua") and ("joker" in lower_file or "tarot" in lower_file or "planet" in lower_file):
                files_to_copy.append(os.path.join(root, file))

    if not files_to_copy:
        print("No relevant Lua files found to copy.")
        return

    for src_path in files_to_copy:
        try:
            dest_path = os.path.join(TARGET_RAW_DIR, os.path.basename(src_path))
            shutil.copy2(src_path, dest_path)
            print(f"Copied: {src_path} to {dest_path}")
        except Exception as e:
            print(f"Error copying {src_path}: {e}")
    print("Lua file extraction complete.")

if __name__ == "__main__":
    extract_lua_files()
