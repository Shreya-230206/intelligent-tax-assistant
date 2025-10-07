from cryptography.fernet import Fernet
import base64

# Generate key in prod: Fernet.generate_key()
KEY = base64.urlsafe_b64encode(b'your-secret-key-here-32-bytes-long!!!')  # Replace!
cipher = Fernet(KEY)

def encrypt_data(data: bytes) -> bytes:
    return cipher.encrypt(data)

def decrypt_data(encrypted_data: bytes) -> bytes:
    return cipher.decrypt(encrypted_data)
