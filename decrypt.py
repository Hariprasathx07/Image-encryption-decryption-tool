from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from PIL import Image
import numpy as np
import json

def decrypt_image(encrypted_path, password=None, output_path=None):
    """Decrypts an image with password verification"""
    if not password:
        raise ValueError("Password is required for decryption")

    try:
        with open(encrypted_path, "rb") as f:
            salt = f.read(16)
            nonce = f.read(16)
            tag = f.read(16)
            shape_len = int.from_bytes(f.read(2), 'big')
            shape_bytes = f.read(shape_len)
            ciphertext = f.read()

        # Parse metadata
        shape_info = json.loads(shape_bytes.decode('utf-8'))
        
        # Derive key and decrypt
        key = PBKDF2(password, salt, dkLen=32, count=1000000)
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)

        # Reconstruct image
        img_array = np.frombuffer(decrypted_data, dtype=np.uint8)
        img_array = img_array.reshape(shape_info['shape'])
        img = Image.fromarray(img_array)
        
        if img.mode != shape_info['mode']:
            img = img.convert(shape_info['mode'])
        
        output_path = output_path or f"decrypted.{shape_info['format']}"
        img.save(output_path, format=shape_info['format'].upper())
        return output_path

    except Exception as e:
        raise Exception(f"Decryption error: {str(e)}")