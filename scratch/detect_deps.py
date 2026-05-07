import os
import re
import sys

def get_imports():
    imports = set()
    app_dir = r"c:\Users\admin\Documents\Backend-Project2cp\app"
    for root, dirs, files in os.walk(app_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        match = re.match(r"^(?:import|from)\s+([a-zA-Z0-9_]+)", line)
                        if match:
                            imports.add(match.group(1))
    return imports

# Standard library modules (approximate list)
std_lib = {
    "os", "sys", "re", "json", "datetime", "random", "string", "smtplib", "logging", "ssl", 
    "typing", "email", "difflib", "unicodedata", "pathlib", "abc", "collections", "functools",
    "hashlib", "hmac", "base64", "time", "asyncio", "inspect", "math", "threading"
}

all_imports = get_imports()
external = all_imports - std_lib - {"app"}

print("Detected external imports:")
for imp in sorted(external):
    print(imp)
