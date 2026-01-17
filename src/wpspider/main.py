import argparse
import sys
from wpspider.config import Config
from wpspider.logger import setup_logging

def parse_args():
    parser = argparse.ArgumentParser(description="WPSpider: WordPress Content Crawler")
    parser.add_argument("--target", "-t", type=str, help="Target WordPress URL or domain")
    parser.add_argument("--output", "-o", type=str, help="Output SQLite database file")
    return parser.parse_args()

def main():
    try:
        # 1. Parse Args
        args = parse_args()
        
        # 2. Init Config
        config = Config(args=args)
        
        # 3. Init Logging
        logger = setup_logging(config.log_file)
        
        logger.info("WPSpider Phase 1 Initialization Complete")
        logger.info(f"Target: {config.target}")
        logger.info(f"Database: {config.db_name}")
        logger.info(f"Endpoints: {', '.join(config.endpoints)}")
        
        # Future phases will be called here
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
