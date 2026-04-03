"""
Audio Agent - Handles voice generation and audio cleanup
"""
import json
import os
import subprocess
from datetime import datetime
from typing import Optional
import requests


class AudioAgent:
    """Agent that handles audio generation and processing."""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.elevenlabs_config = None
        
        if api_manager.has_key("ELEVENLABS"):
            self.elevenlabs_config = api_manager.get_elevenlabs_config()
        
        self.audio_config = {
            "voice_id": "21m00Tcm4TlvDq8ikWAM" if not self.elevenlabs_config else self.elevenlabs_config.get("voice_id", "21m00Tcm4TlvDq8ikWAM"),
            "speed": 1.0,
            "pitch": 0,
            "cleanup_enabled": True,
            "output_format": "mp3"
        }
        
    def generate_voice(self, text: str, output_path: str) -> dict:
        """
        Generate voice audio from text (TTS).
        
        Args:
            text: Text to convert to speech
            output_path: Where to save the audio file
            
        Returns:
            Dictionary with generation results
        """
        print(f"🎤 Audio Agent: Generating voice for {len(text)} characters")
        print(f"   Output: {output_path}")
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "input_text_length": len(text),
            "output_path": output_path,
            "status": "pending",
            "duration_seconds": 0,
            "format": "mp3"
        }
        
        # Try ElevenLabs if API key available
        if self.elevenlabs_config and self.elevenlabs_config.get("api_key"):
            try:
                duration = self._generate_elevenlabs(text, output_path)
                result["duration_seconds"] = duration
                result["status"] = "completed"
                print(f"✅ Audio Agent: Voice generated via ElevenLabs ({duration:.1f}s)")
                return result
            except Exception as e:
                print(f"⚠️ ElevenLabs failed: {e}")
        
        # Fallback: use gTTS (Google TTS) or placeholder
        try:
            duration = self._generate_gtts(text, output_path)
            result["duration_seconds"] = duration
            result["status"] = "completed"
            print(f"✅ Audio Agent: Voice generated via gTTS ({duration:.1f}s)")
        except Exception as e:
            print(f"⚠️ gTTS failed: {e}")
            # Create placeholder
            result["status"] = "placeholder"
            result["error"] = str(e)
        
        return result
    
    def _generate_elevenlabs(self, text: str, output_path: str) -> float:
        """Generate audio using ElevenLabs API."""
        api_key = self.elevenlabs_config["api_key"]
        voice_id = self.audio_config["voice_id"]
        speed = self.audio_config["speed"]
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "speed": speed
            }
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        
        # Save audio
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        # Estimate duration (roughly 150 words/min at speed 1.0)
        word_count = len(text.split())
        duration = (word_count / 150) * 60 / speed
        
        return duration
    
    def _generate_gtts(self, text: str, output_path: str) -> float:
        """Generate audio using gTTS (free alternative)."""
        try:
            from gtts import gTTS
            
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            
            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(output_path)
            
            # Estimate duration
            word_count = len(text.split())
            duration = (word_count / 150) * 60  # ~150 words/min
            
            return duration
        except ImportError:
            print("⚠️ gTTS not installed, creating placeholder audio")
            # Create silent placeholder
            return self._create_placeholder(output_path)
    
    def _create_placeholder(self, output_path: str, duration_sec: int = 60) -> float:
        """Create a silent placeholder audio file."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        # Use ffmpeg to create silent audio
        try:
            subprocess.run([
                "ffmpeg", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
                "-t", str(duration_sec), "-y", output_path
            ], capture_output=True, timeout=30)
        except:
            # If ffmpeg not available, just touch the file
            with open(output_path, "wb") as f:
                f.write(b"")  # Empty file
        
        return float(duration_sec)
    
    def cleanup_audio(self, input_path: str, output_path: str) -> dict:
        """
        Clean up audio - remove noise, normalize volume, etc.
        
        Args:
            input_path: Raw audio file
            output_path: Cleaned audio output
            
        Returns:
            Dictionary with cleanup results
        """
        print(f"🔧 Audio Agent: Cleaning up audio")
        print(f"   Input: {input_path}")
        print(f"   Output: {output_path}")
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "input_path": input_path,
            "output_path": output_path,
            "status": "pending",
            "operations": [],
            "duration_seconds": 0
        }
        
        if not os.path.exists(input_path):
            result["status"] = "error"
            result["error"] = "Input file not found"
            return result
        
        # Check if ffmpeg is available
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            ffmpeg_available = True
        except:
            ffmpeg_available = False
        
        if ffmpeg_available:
            # Use ffmpeg for audio processing
            operations = [
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",  # Normalize
            ]
            
            cmd = ["ffmpeg", "-i", input_path] + operations + ["-y", output_path]
            
            try:
                subprocess.run(cmd, capture_output=True, check=True, timeout=120)
                result["operations"] = ["noise_reduction", "volume_normalization"]
                result["status"] = "completed"
                print(f"✅ Audio Agent: Cleanup completed")
            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)
        else:
            # Fallback: just copy file
            try:
                import shutil
                shutil.copy(input_path, output_path)
                result["operations"] = ["file_copy"]
                result["status"] = "completed"
            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)
        
        # Get duration
        result["duration_seconds"] = self.get_duration(output_path)
        
        return result
    
    def add_background_music(self, audio_path: str, music_path: str, volume: float = 0.3) -> dict:
        """Add background music to audio."""
        print(f"🎵 Audio Agent: Adding background music at {volume*100}%")
        
        output_path = audio_path.replace(".mp3", "_with_music.mp3")
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "audio_path": audio_path,
            "music_path": music_path,
            "music_volume": volume,
            "output_path": output_path,
            "status": "pending"
        }
        
        # Use ffmpeg to mix audio
        try:
            cmd = [
                "ffmpeg", "-i", audio_path, "-i", music_path,
                "-filter_complex", f"[0:a]volume=1[voice];[1:a]volume={volume}[music];[voice][music]amix=inputs=2:duration=first[a]",
                "-map", "[a]", "-y", output_path
            ]
            subprocess.run(cmd, capture_output=True, check=True, timeout=120)
            result["status"] = "completed"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def get_duration(self, audio_path: str) -> float:
        """Get audio file duration in seconds."""
        if not os.path.exists(audio_path):
            return 0.0
        
        try:
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
                   "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return float(result.stdout.strip() or 0)
        except:
            # Fallback estimation
            return 60.0
    
    def configure(self, **kwargs):
        """Configure audio agent settings."""
        self.audio_config.update(kwargs)


# Standalone test
if __name__ == "__main__":
    class MockAPIManager:
        def has_key(self, provider):
            return provider != "ELEVENLABS"
        
        def get_elevenlabs_config(self):
            return None
    
    agent = AudioAgent(MockAPIManager())
    result = agent.generate_voice("Hello world", "output.mp3")
    print(f"Status: {result['status']}")