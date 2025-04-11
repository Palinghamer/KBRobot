import json
import os

def load_config(filename="config.json"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, filename)
    with open(config_path, "r") as f:
        return json.load(f)
