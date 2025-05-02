"""
Utility module for managing API key storage and retrieval.
"""
import os
from pathlib import Path
from cryptography.fernet import Fernet

class APIKeyManager:
    """Manages the storage and retrieval of API keys."""
    
    def __init__(self):
        self.key_file = Path("api_key.bin")
        self.key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.key)
    
    def _get_or_create_key(self):
        """Get or create encryption key."""
        key_path = Path("encryption.key")
        if key_path.exists():
            return key_path.read_bytes()
        else:
            key = Fernet.generate_key()
            key_path.write_bytes(key)
            return key
    
    def save_api_key(self, api_key: str):
        """Encrypt and save API key to file."""
        encrypted_key = self.cipher_suite.encrypt(api_key.encode())
        self.key_file.write_bytes(encrypted_key)
    
    def load_api_key(self) -> str:
        """Load and decrypt API key from file."""
        try:
            if not self.key_file.exists():
                return None
            encrypted_key = self.key_file.read_bytes()
            decrypted_key = self.cipher_suite.decrypt(encrypted_key)
            return decrypted_key.decode()
        except Exception:
            return None

def get_api_key() -> str:
    """Get API key from environment or encrypted file."""
    # First try to get from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
        
    # If not in environment, try to get from encrypted file
    manager = APIKeyManager()
    return manager.load_api_key()

def save_api_key(api_key: str):
    """Save API key to encrypted file."""
    manager = APIKeyManager()
    manager.save_api_key(api_key) 