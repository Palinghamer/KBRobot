import os
import logging
from datetime import datetime

def setup_logger():
    # Create timestamp for both .log and .csv
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Go from scripts/ → core/ → pywiki/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pywiki_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    logs_dir = os.path.join(pywiki_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    log_filename = os.path.join(logs_dir, f"wikidata_upload_{timestamp}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)
    return logger, timestamp
