from uploader import WikidataUploader
from config_loader import load_config
from data_loader import read_csv_to_df
from logger_setup import setup_logger
from lock_manager import is_recently_run, update_last_run

import pywikibot
import sys

def main():
    if is_recently_run(min_minutes=0):
        print("Script ran recently. Wait 5 minutes or delete the lock file.")
        sys.exit(1)

    update_last_run()
    logger, run_timestamp = setup_logger()
    
    config = load_config("config.json")
    property_map = config["property_map"]
    source_map = config["source_map"]

    df = read_csv_to_df("test_data4.csv")
    site = pywikibot.Site("test", "wikidata")
    site.login()

    uploader = WikidataUploader(site, property_map, source_map, logger)
    uploader.upload_from_dataframe(df)


    summary_filename = f"summary_log_{run_timestamp}.csv"
    uploader.save_summary_csv(summary_filename)

    logger.info("Script finished.")
    logger.info(f"Items processed: {uploader.stats['processed']}, Created: {uploader.stats['created']}, Skipped: {uploader.stats['skipped']}")
    logger.info(f"Claims Added: {uploader.stats['claims_added']}, Claims Skipped: {uploader.stats['claims_skipped']}")
    logger.info(f"Sources Added: {uploader.stats['sources_added']}, Sources Skipped: {uploader.stats['sources_skipped']}")

if __name__ == "__main__":
    main()
