"""Encryption utilities for sensitive data"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os
from ..config import Config


def get_encryption_key() -> bytes:
    """
    Get or generate encryption key
    Uses SECRET_KEY from config to derive a Fernet key
    """
    # Use SECRET_KEY as password for key derivation
    password = Config.SECRET_KEY.encode()
    
    # Use a fixed salt (in production, this should be stored securely)
    salt = b'patient_support_salt_2024'
    
    # Derive key using PBKDF2
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


# Initialize Fernet cipher
_cipher = None


def get_cipher():
    """Get Fernet cipher instance"""
    global _cipher
    if _cipher is None:
        key = get_encryption_key()
        _cipher = Fernet(key)
    return _cipher


def encrypt_field(value: str) -> str:
    """
    Encrypt a field value using AES-256
    
    Args:
        value: Plain text value
    
    Returns:
        Encrypted value as string
    """
    if not value:
        return value
    
    cipher = get_cipher()
    encrypted = cipher.encrypt(value.encode('utf-8'))
    return encrypted.decode('utf-8')


def decrypt_field(encrypted_value: str) -> str:
    """
    Decrypt a field value
    
    Args:
        encrypted_value: Encrypted value
    
    Returns:
        Decrypted plain text value
    """
    if not encrypted_value:
        return encrypted_value
    
    cipher = get_cipher()
    try:
        decrypted = cipher.decrypt(encrypted_value.encode('utf-8'))
        return decrypted.decode('utf-8')
    except Exception:
        # If decryption fails, return original value (might not be encrypted)
        return encrypted_value
