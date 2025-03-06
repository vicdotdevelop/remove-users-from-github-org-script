"""Encryption utilities for handling GitHub tokens."""

import base64
import getpass
import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class TokenManager:
    """Manage GitHub tokens with encryption."""

    def __init__(self, salt: Optional[bytes] = None):
        """Initialize the token manager with optional salt."""
        # Use provided salt or generate a new one
        self.salt = salt or os.urandom(16)

    def _get_key_from_password(self, password: str) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt_token(self, token: str, password: str) -> bytes:
        """Encrypt a GitHub token using password-based encryption."""
        key = self._get_key_from_password(password)
        f = Fernet(key)
        encrypted_token = f.encrypt(token.encode())
        
        # Combine salt and encrypted token for storage
        result = self.salt + encrypted_token
        return result

    def decrypt_token(self, encrypted_data: bytes, password: str) -> str:
        """Decrypt a GitHub token using the provided password."""
        # First 16 bytes are the salt
        salt = encrypted_data[:16]
        encrypted_token = encrypted_data[16:]
        
        # Create key using the extracted salt
        key = self._get_key_from_password(password)
        f = Fernet(key)
        
        decrypted_token = f.decrypt(encrypted_token).decode()
        return decrypted_token

    def save_encrypted_token(self, token: str, filepath: str) -> None:
        """Save an encrypted GitHub token to a file."""
        password = getpass.getpass("Enter password to encrypt GitHub token: ")
        confirm = getpass.getpass("Confirm password: ")
        
        if password != confirm:
            raise ValueError("Passwords do not match")
        
        encrypted_data = self.encrypt_token(token, password)
        
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "wb") as file:
            file.write(encrypted_data)
        
        print(f"Token encrypted and saved to {filepath}")

    def load_encrypted_token(self, filepath: str) -> str:
        """Load and decrypt a GitHub token from a file."""
        with open(filepath, "rb") as file:
            encrypted_data = file.read()
        
        password = getpass.getpass("Enter password to decrypt GitHub token: ")
        
        try:
            return self.decrypt_token(encrypted_data, password)
        except Exception as e:
            raise ValueError(f"Failed to decrypt token: {e}") from e