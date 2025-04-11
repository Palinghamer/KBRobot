import os
import logging
from datetime import datetime

def setup_logger(log_dir="logs"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, log_dir)
    os.makedirs(logs_dir, exist_ok=True)

    log_filename = os.path.join(logs_dir, f"wikidata_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger()
