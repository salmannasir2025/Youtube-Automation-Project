import os
import json
from pathlib import Path
from cryptography.fernet import Fernet
from dotenv import load_dotenv


class APIManager:
    """
    Manages API keys for LLM and other services.
    Supports multiple providers with automatic failover.
    """
    
    def __init__(self, env_file: str = None):
        """
        Initialize APIManager.
        
        Args:
            env_file: Path to .env file (default: .env in project root)
        """
        self.keys = {
            "GEMINI": None,
            "GROK": None,
            "BRAVE_SEARCH": None,
            "ELEVENLABS": None,
            "YOUTUBE": None
        }
        
        self.config = {
            "gemini_model": "gemini-2.0-flash",
            "grok_model": "grok-2",
            "brave_count": 10,
            "elevenlabs_voice": " Rachel"
        }
        
        # Load environment
        if env_file is None:
            env_file = Path(__file__).parent / ".env"
        
        if Path(env_file).exists():
            load_dotenv(env_file)
        
        self.load_keys()
    
    def load_keys(self):
        """Load API keys from environment variables."""
        
        # LLM Keys
        self.keys["GEMINI"] = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.keys["GROK"] = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
        
        # Search
        self.keys["BRAVE_SEARCH"] = os.getenv("BRAVE_API_KEY")
        
        # Audio/TTS
        self.keys["ELEVENLABS"] = os.getenv("ELEVENLABS_API_KEY")
        
        # YouTube
        self.keys["YOUTUBE"] = os.getenv("YOUTUBE_API_KEY") or os.getenv("YOUTUBE_DATA_API_KEY")
        
        # Load config overrides
        if os.getenv("GEMINI_MODEL"):
            self.config["gemini_model"] = os.getenv("GEMINI_MODEL")
        if os.getenv("GROK_MODEL"):
            self.config["grok_model"] = os.getenv("GROK_MODEL")
            
        print("🔑 APIManager: Loaded API keys")
        self._print_available()
    
    def _print_available(self):
        """Print which APIs are available."""
        available = [k for k, v in self.keys.items() if v]
        print(f"   Available: {', '.join(available)}")
    
    def get_active_brain(self) -> str:
        """
        Get the primary LLM API key.
        
        Returns:
            API key string, or None if no keys available
        """
        # Priority: Gemini > Grok
        return self.keys["GEMINI"] or self.keys["GROK"]
    
    def get_brain_name(self) -> str:
        """Get name of active brain."""
        if self.keys["GEMINI"]:
            return "GEMINI"
        elif self.keys["GROK"]:
            return "GROK"
        return "NONE"
    
    def get_llm_config(self) -> dict:
        """Get LLM configuration."""
        return {
            "api_key": self.get_active_brain(),
            "model": self.config["gemini_model"] if self.keys["GEMINI"] else self.config["grok_model"],
            "brain": self.get_brain_name()
        }
    
    def get_brave_config(self) -> dict:
        """Get Brave Search configuration."""
        return {
            "api_key": self.keys["BRAVE_SEARCH"],
            "count": self.config["brave_count"]
        }
    
    def get_elevenlabs_config(self) -> dict:
        """Get ElevenLabs configuration."""
        return {
            "api_key": self.keys["ELEVENLABS"],
            "voice_id": self.config["elevenlabs_voice"]
        }
    
    def get_youtube_config(self) -> dict:
        """Get YouTube API configuration."""
        return {
            "api_key": self.keys["YOUTUBE"]
        }
    
    def has_key(self, provider: str) -> bool:
        """Check if API key exists for provider."""
        return bool(self.keys.get(provider.upper()))
    
    def is_available(self, provider: str) -> bool:
        """Check if provider is available and configured."""
        return self.has_key(provider)
    
    # === Encryption (for storing keys securely) ===
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new encryption key."""
        return Fernet.generate_key()
    
    def encrypt_keys(self, key: bytes) -> bytes:
        """Encrypt all keys for storage."""
        f = Fernet(key)
        data = json.dumps(self.keys).encode()
        return f.encrypt(data)
    
    def decrypt_keys(self, encrypted: bytes, key: bytes) -> dict:
        """Decrypt stored keys."""
        f = Fernet(key)
        decrypted = f.decrypt(encrypted)
        return json.loads(decrypted)


# Example .env structure
ENV_EXAMPLE = """
# LLM APIs (at least one required)
GEMINI_API_KEY=your_gemini_api_key_here
GROK_API_KEY=your_grok_api_key_here

# Optional: Specify models
# GEMINI_MODEL=gemini-2.0-flash
# GROK_MODEL=grok-2

# Search API (for ResearchAgent)
BRAVE_API_KEY=your_brave_api_key_here

# Audio/TTS (for AudioAgent)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# YouTube Publishing (for PublisherAgent)
YOUTUBE_API_KEY=your_youtube_api_key_here
"""


if __name__ == "__main__":
    # Test
    api = APIManager()
    print(f"\nActive Brain: {api.get_brain_name()}")
    print(f"LLM Config: {api.get_llm_config()}")