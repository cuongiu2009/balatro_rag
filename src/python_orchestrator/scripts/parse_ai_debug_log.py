import re
import sys

def parse_ai_debug_log(log_file_path):
    """
    Parses the ai_debug.txt log file to extract the first full _G.G table dump.
    """
    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.read()
    except FileNotFoundError:
        print(f"Error: Log file not found at '{log_file_path}'")
        return False

    # Regex to find the start of a full G table dump and capture its content
    # It looks for "DEBUG Lua: Full G table dump:" followed by '{' and captures everything
    # until the next "DEBUG Lua: Full G table dump:" or end of file,
    # ensuring it's a table structure.
    pattern = re.compile(r"DEBUG Lua: Full G table dump:\n(.*?)(?=\nDEBUG Lua: Full G table dump:|\Z)", re.DOTALL)

    matches = pattern.findall(log_content)
    if matches:
        print("--- START OF LAST FULL _G.G DUMP ---")
        print(matches[-1].strip())
        print("--- END OF LAST FULL _G.G DUMP ---")
        return True
    else:
        print("No full _G.G table dump found in the log file.")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_ai_debug_log.py <path_to_ai_debug.txt>")
        sys.exit(1)

    log_file = sys.argv[1]
    parse_ai_debug_log(log_file)
