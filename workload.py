import time
import hashlib
import os

duration = 60  # seconds
end_time = time.time() + duration

while time.time() < end_time:
    data = os.urandom(1024)
    hashlib.sha256(data).hexdigest()
    time.sleep(0.01)

print("Test workload finished.")
