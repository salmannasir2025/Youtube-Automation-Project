import os
import json
import base64
import tkinter as tk
from tkinter import messagebox, ttk
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv, set_key

class APIManager:
    """
    Handles Gemini/Grok API keys with a GUI and local encryption.
    Stores keys in a local .env file.
    """
    
    def __init__(self, env_path=".env"):
        self.env_path = env_path
        self.salt = b'\x12\x34\x56\x78\x90\xab\xcd\xef' # Fixed salt for local consistency
        self.key = self._generate_key()
        self.fernet = Fernet(self.key)
        
        # Load existing env
        if not os.path.exists(self.env_path):
            with open(self.env_path, "w") as f:
                f.write("")
        load_dotenv(self.env_path)

    def _generate_key(self):
        """Generates a consistent key based on machine hardware ID."""
        # Simple machine-bound key generation
        password = platform.node().encode() if hasattr(os, 'uname') else b"youtube-factory-local-secret"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))

    def encrypt_data(self, data):
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data):
        try:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        except Exception:
            return ""

    def save_keys(self, gemini_key, grok_key):
        """Encrypts and saves keys to .env"""
        enc_gemini = self.encrypt_data(gemini_key)
        enc_grok = self.encrypt_data(grok_key)
        
        set_key(self.env_path, "GEMINI_API_KEY", enc_gemini)
        set_key(self.env_path, "GROK_API_KEY", enc_grok)
        return True

    def get_keys(self):
        """Decrypts and returns keys from .env"""
        load_dotenv(self.env_path, override=True)
        gemini = os.getenv("GEMINI_API_KEY", "")
        grok = os.getenv("GROK_API_KEY", "")
        
        return {
            "gemini": self.decrypt_data(gemini),
            "grok": self.decrypt_data(grok)
        }

class SettingsGUI:
    def __init__(self, manager):
        self.manager = manager
        self.root = tk.Tk()
        self.root.title("OSCF API Manager")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        self._setup_ui()
        self._load_existing()

    def _setup_ui(self):
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10, "bold"))

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Gemini Key
        ttk.Label(main_frame, text="Gemini API Key:").pack(anchor=tk.W, pady=(0, 5))
        self.gemini_entry = ttk.Entry(main_frame, width=50, show="*")
        self.gemini_entry.pack(fill=tk.X, pady=(0, 15))

        # Grok Key
        ttk.Label(main_frame, text="Grok API Key:").pack(anchor=tk.W, pady=(0, 5))
        self.grok_entry = ttk.Entry(main_frame, width=50, show="*")
        self.grok_entry.pack(fill=tk.X, pady=(0, 15))

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.save_btn = ttk.Button(btn_frame, text="Save Keys", command=self.save_action)
        self.save_btn.pack(side=tk.RIGHT)

    def _load_existing(self):
        keys = self.manager.get_keys()
        if keys["gemini"]:
            self.gemini_entry.insert(0, keys["gemini"])
        if keys["grok"]:
            self.grok_entry.insert(0, keys["grok"])

    def save_action(self):
        gemini = self.gemini_entry.get()
        grok = self.grok_entry.get()
        
        if self.manager.save_keys(gemini, grok):
            messagebox.showinfo("Success", "API Keys encrypted and saved to .env")
            self.root.destroy()

    def run(self):
        self.root.mainloop()

import platform # Needed for machine node check
if __name__ == "__main__":
    manager = APIManager()
    gui = SettingsGUI(manager)
    gui.run()
