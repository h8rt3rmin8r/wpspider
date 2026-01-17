import argparse
import sys
import logging
import traceback
from wpspider.config import Config
from wpspider.logger import setup_logging
from wpspider.database import DatabaseManager
from wpspider.crawler import WPCrawler

def parse_args():
    parser = argparse.ArgumentParser(description="WPSpider: WordPress Content Crawler")
    parser.add_argument("--target", "-t", "--url", "--site", "--domain", type=str, help="Target WordPress URL or domain")

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--output", "-o", "--db", "--database", "--db-name", type=str, help="Output SQLite database file")
    output_group.add_argument("--directory", "-d", "--outdirectory", "--outputdirectory", type=str, help="Output directory (used only when --output is not provided)")

    parser.add_argument("--useragent", "--user-agent", "-u", dest="user_agent", type=str, help="Custom User-Agent string")
    return parser.parse_args()

def main():
    logger = None
    try:
        # 1. Parse Args
        args = parse_args()
        
        # 2. Init Config
        config = Config(args=args)

        # Validate guarantees target is set, but type checker doesn't know
        if not config.target:
            raise ValueError("Target URL is missing")
        
        # 3. Init Logging
        logger = setup_logging(config.log_file)
        
        logger.info("WPSpider Phase 1 Initialization Complete")
        logger.info(f"Target: {config.target}")
        logger.info(f"Database: {config.db_name}")
        logger.info(f"Endpoints: {', '.join(config.endpoints)}")
        
        # 4. Integrate Database & Crawler
        try:
            with DatabaseManager(config.db_name) as db:
                # Log the crawl target session
                target_id = db.log_target(config.target)
                
                # Initialize Crawler
                crawler = WPCrawler(config.target, user_agent=config.user_agent)
                
                # 5. Pipeline Orchestration
                for endpoint in config.endpoints:
                    logger.info(f"--- Starting Endpoint: {endpoint} ---")
                    try:
                        total_items = 0
                        # Iterate through batches yielded by the crawler
                        for batch, request_meta in crawler.crawl_endpoint(endpoint):
                            request_id = db.log_http_request(target_id, endpoint, request_meta)
                            if batch:
                                db.save_batch(endpoint, batch, target_id=target_id, request_id=request_id)
                                total_items += len(batch)
                                logger.debug(f"Saved {len(batch)} items for {endpoint}. Total so far: {total_items}")
                        
                        logger.info(f"--- Finished Endpoint: {endpoint}. Total items: {total_items} ---")
                        
                    except Exception as ep_err:
                        # Error Handling Polish: One failed endpoint doesn't crash the run
                        logger.error(f"Failed to crawl endpoint '{endpoint}': {ep_err}")
                        logger.debug(traceback.format_exc())
                        continue

        except Exception as db_err:
            logger.critical(f"Database error or critical failure: {db_err}")
            logger.debug(traceback.format_exc())
            sys.exit(1)
        
        logger.info("WPSpider Crawl Complete.")

    except Exception as e:
        # Fallback provided logger might not be setup if config failed
        if logger:
            logger.critical(f"Unexpected error: {e}")
            logger.debug(traceback.format_exc())
        else:
            print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
