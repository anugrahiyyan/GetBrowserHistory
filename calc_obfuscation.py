import base64

def deep_obfuscate(text, key):
    reversed_text = text[::-1]
    xor_bytes = bytearray()
    for i, char in enumerate(reversed_text):
        xor_bytes.append(ord(char) ^ key[i % len(key)])
    encoded = base64.b64encode(xor_bytes).decode()
    return encoded

key = [0x42, 0x13, 0x99, 0xFA, 0x24, 0x77]

token = "PC-TOKEN"
chat_id = "PC-ID"
url = "PC_URL"

enc_token = deep_obfuscate(token, key)
enc_chat_id = deep_obfuscate(chat_id, key)
enc_url = deep_obfuscate(url, key)

print(f"KEY = {key}")
print(f"TOKEN = \"{enc_token}\"")
print(f"CHAT_ID = \"{enc_chat_id}\"")
print(f"URL = \"{enc_url}\"")
