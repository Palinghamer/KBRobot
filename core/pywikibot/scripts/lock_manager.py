from datetime import datetime, timedelta
import os

LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_run.lock")

def is_recently_run(min_minutes=5):
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE, "r") as f:
            try:
                last_run = datetime.fromisoformat(f.read().strip())
                return datetime.now() - last_run < timedelta(minutes=min_minutes)
            except Exception:
                pass
    return False

def update_last_run():
    with open(LOCK_FILE, "w") as f:
        f.write(datetime.now().isoformat())
