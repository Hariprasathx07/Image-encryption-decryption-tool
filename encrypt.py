from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from PIL import Image
import numpy as np
import json

def encrypt_image(img_path, password, output_path="encrypted.bin"):
    """Encrypts an image with mandatory password protection"""
    if not password or len(password) < 4:
        raise ValueError("Password must be at least 4 characters long")

    try:
        # Open and prepare image
        img = Image.open(img_path)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        img_array = np.array(img)
        flat_data = img_array.flatten().tobytes()

        # Generate encryption components
        salt = get_random_bytes(16)
        nonce = get_random_bytes(16)
        key = PBKDF2(password, salt, dkLen=32, count=1000000)
        
        # Encrypt data
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(flat_data)

        # Store image metadata
        shape_info = {
            'shape': img_array.shape,
            'format': img.format.lower() if img.format else 'png',
            'mode': img.mode,
            'password_protected': True
        }
        shape_bytes = json.dumps(shape_info).encode('utf-8')

        # Write encrypted file
        with open(output_path, "wb") as f:
            f.write(salt)
            f.write(nonce)
            f.write(tag)
            f.write(len(shape_bytes).to_bytes(2, 'big'))
            f.write(shape_bytes)
            f.write(ciphertext)

        return output_path

    except Exception as e:
        raise Exception(f"Encryption error: {str(e)}")