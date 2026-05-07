import os
import re

def get_imports():
    imports = set()
    root_dir = r"c:\Users\admin\Documents\Backend-Project2cp"
    for root, dirs, files in os.walk(root_dir):
        if ".venv" in root or ".git" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        match = re.match(r"^(?:import|from)\s+([a-zA-Z0-9_]+)", line)
                        if match:
                            imports.add(match.group(1))
    return imports

std_lib = {
    "os", "sys", "re", "json", "datetime", "random", "string", "smtplib", "logging", "ssl", 
    "typing", "email", "difflib", "unicodedata", "pathlib", "abc", "collections", "functools",
    "hashlib", "hmac", "base64", "time", "asyncio", "inspect", "math", "threading", "io", "csv", "shutil", "tempfile"
}

all_imports = get_imports()
external = all_imports - std_lib - {"app", "scripts"}

print("Detected external imports in project:")
for imp in sorted(external):
    print(imp)
