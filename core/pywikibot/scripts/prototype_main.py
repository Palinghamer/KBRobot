from uploader import WikidataUploader
from config_loader import load_config
from data_loader import read_csv_to_df
from logger_setup import setup_logger
from lock_manager import is_recently_run, update_last_run
import argparse
import pywikibot
import sys
import os
import json

def main():
    parser = argparse.ArgumentParser(description="Upload CSV data to Wikidata.")
    parser.add_argument("csv_path", help="Path to the CSV file to process")
    parser.add_argument("--config", help="Path to a custom config JSON file")
    parser.add_argument("--mode", help="Predefined mode (e.g., 'author', 'work')")
    args = parser.parse_args()

    if is_recently_run(min_minutes=5):
        print("Script ran recently. Wait 5 minutes before running again.")
        sys.exit(1)

    update_last_run()
    logger, run_timestamp = setup_logger()

    # Determine config path
    if args.config:
        config_path = args.config
        mode_label = "custom config"
    elif args.mode:
        profiles_path = os.path.join(os.path.dirname(__file__), "profiles.json")
        try:
            with open(profiles_path, "r") as f:
                profiles = json.load(f)
            relative_path = profiles.get(args.mode)
            if not relative_path:
                print(f"Error: Mode '{args.mode}' not found in profiles.json. Available modes: {', '.join(profiles.keys())}")
                sys.exit(1)
            config_path = os.path.join(os.path.dirname(__file__), relative_path)
            if not os.path.exists(config_path):
                print(f"Error: Config file for mode '{args.mode}' not found at: {config_path}")
                sys.exit(1)
            mode_label = args.mode
        except Exception as e:
            print(f"Error loading profiles.json: {e}")
            sys.exit(1)
    else:
        config_path = os.path.join(os.path.dirname(__file__), "configs/config.json")
        mode_label = "default"

    print(f"\nYou are about to run the script in {mode_label.upper()} mode. Editing Wikidata using the incorrect mode will result in unintended changes.")
    confirm = input("--- Continue? (Y/N): ").strip().lower()
    if confirm not in ("y", "yes"):
        print("Aborting.")
        sys.exit(0)

    config = load_config(config_path)
    property_map = config["property_map"]
    source_map = config["source_map"]

    df = read_csv_to_df(args.csv_path)
    site = pywikibot.Site()

    site.login()

    uploader = WikidataUploader(site, property_map, source_map, logger)
    uploader.upload_from_dataframe(df, args.csv_path)

    summary_filename = f"summary_log_{run_timestamp}.csv"
    uploader.save_summary_csv(summary_filename)

    logger.info("Script finished.")
    logger.info(f"Items processed: {uploader.stats['processed']}, Created: {uploader.stats['created']}, Skipped: {uploader.stats['skipped']}")
    logger.info(f"Claims Added: {uploader.stats['claims_added']}, Claims Skipped: {uploader.stats['claims_skipped']}")
    logger.info(f"Sources Added: {uploader.stats['sources_added']}, Sources Skipped: {uploader.stats['sources_skipped']}")

if __name__ == "__main__":
    main()
