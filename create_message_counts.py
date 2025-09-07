import json
import os
from datetime import datetime, timezone
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# File path
MESSAGE_COUNTS_FILE = 'message_counts.json'

# Function to create message_counts.json with sample data
def create_message_counts_file():
    # Sample data with current timestamp (12:41 PM IST, September 7, 2025)
    sample_data = {
        "counts": {
            "123456789012345678": 10,
            "987654321098765432": 5,
            "456789123456789123": 20
        },
        "last_reset": 1733639460  # 12:41 PM IST, September 7, 2025 (UTC timestamp)
    }

    try:
        if os.path.exists(MESSAGE_COUNTS_FILE):
            logger.info(f"{MESSAGE_COUNTS_FILE} already exists, overwriting with sample data")
        with open(MESSAGE_COUNTS_FILE, 'w') as f:
            json.dump(sample_data, f, indent=4)
        logger.info(f"Created {MESSAGE_COUNTS_FILE} with sample data")
    except PermissionError as e:
        logger.error(f"PermissionError saving {MESSAGE_COUNTS_FILE}: {e}")
    except Exception as e:
        logger.error(f"Error creating {MESSAGE_COUNTS_FILE}: {e}")

if __name__ == "__main__":
    create_message_counts_file()