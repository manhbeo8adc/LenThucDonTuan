"""
Utility module for managing API key storage and retrieval.
"""
import os
import sys
import tempfile
from pathlib import Path
from cryptography.fernet import Fernet

def get_app_dir():
    """Get the application directory, works with both PyInstaller and normal Python."""
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running in normal Python
        return Path(os.path.dirname(os.path.abspath(__file__))).parent

class APIKeyManager:
    """Manages the storage and retrieval of API keys."""
    
    def __init__(self):
        self.app_dir = get_app_dir()
        self.key_file = Path(tempfile.gettempdir()) / "api_key.bin"
        self.key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.key)
    
    def _get_or_create_key(self):
        """Get or create encryption key."""
        key_path = Path(tempfile.gettempdir()) / "encryption.key"
        try:
            if key_path.exists():
                return key_path.read_bytes()
            else:
                key = Fernet.generate_key()
                # Ensure the file is created with appropriate permissions
                with open(key_path, 'wb') as f:
                    f.write(key)
                return key
        except Exception as e:
            print(f"Error handling encryption key: {e}")
            # If we can't read/write the file, generate a temporary key
            return Fernet.generate_key()
    
    def save_api_key(self, api_key: str):
        """Encrypt and save API key to file."""
        try:
            encrypted_key = self.cipher_suite.encrypt(api_key.encode())
            with open(self.key_file, 'wb') as f:
                f.write(encrypted_key)
        except Exception as e:
            print(f"Error saving API key: {e}")
    
    def load_api_key(self) -> str:
        """Load and decrypt API key from file."""
        try:
            if not self.key_file.exists():
                return None
            with open(self.key_file, 'rb') as f:
                encrypted_key = f.read()
            decrypted_key = self.cipher_suite.decrypt(encrypted_key)
            return decrypted_key.decode()
        except Exception as e:
            print(f"Error loading API key: {e}")
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