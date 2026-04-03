"""
Audio Agent - Handles voice generation and audio processing
Supports multiple voice sources: Pre-recorded, AI TTS
"""
import json
import os
import shutil
import subprocess
from datetime import datetime
from typing import Optional
from enum import Enum
import requests


class VoiceSource(Enum):
    """Voice source options."""
    PRE_RECORDED = "pre_recorded"  # User provides .mp3 file
    AI_TTS = "ai_tts"              # Generate with AI (ElevenLabs/gTTS)
    NONE = "none"                  # No audio


class AudioAgent:
    """Agent that handles audio from multiple sources."""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.elevenlabs_config = None
        
        if api_manager.has_key("ELEVENLABS"):
            self.elevenlabs_config = api_manager.get_elevenlabs_config()
        
        self.audio_config = {
            "voice_source": VoiceSource.AI_TTS,  # Default to AI
            "pre_recorded_path": None,           # Path to user's audio
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "speed": 1.0,
            "pitch": 0,
            "cleanup_enabled": True,
            "output_format": "mp3"
        }
    
    # === Voice Source Configuration ===
    
    def set_voice_source(self, source: VoiceSource, pre_recorded_path: str = None):
        """
        Set the voice source.
        
        Args:
            source: VoiceSource enum (PRE_RECORDED, AI_TTS, NONE)
            pre_recorded_path: Path to .mp3 file (required if source is PRE_RECORDED)
        """
        self.audio_config["voice_source"] = source
        
        if source == VoiceSource.PRE_RECORDED:
            if not pre_recorded_path:
                raise ValueError("pre_recorded_path required for PRE_RECORDED source")
            self.audio_config["pre_recorded_path"] = pre_recorded_path
            print(f"🎤 Audio Agent: Voice source set to PRE_RECORDED ({pre_recorded_path})")
        elif source == VoiceSource.AI_TTS:
            self.audio_config["pre_recorded_path"] = None
            print(f"🎤 Audio Agent: Voice source set to AI_TTS")
        else:
            print(f"🎤 Audio Agent: Voice source set to NONE")
    
    def set_ai_voice(self, voice_id: str = None, speed: float = 1.0):
        """Configure AI voice settings."""
        if voice_id:
            self.audio_config["voice_id"] = voice_id
        self.audio_config["speed"] = speed
    
    # === Main Audio Processing ===
    
    def process_audio(self, text: str, output_path: str) -> dict:
        """
        Process audio based on configured voice source.
        
        Args:
            text: Text for TTS (not used if pre-recorded)
            output_path: Where to save/process the audio
            
        Returns:
            Dictionary with processing results
        """
        source = self.audio_config["voice_source"]
        
        print(f"🎤 Audio Agent: Processing audio")
        print(f"   Source: {source.value}")
        print(f"   Output: {output_path}")
        
        if source == VoiceSource.PRE_RECORDED:
            return self._process_pre_recorded(output_path)
        elif source == VoiceSource.AI_TTS:
            return self._generate_ai_voice(text, output_path)
        else:
            return self._create_silent_audio(output_path)
    
    def _process_pre_recorded(self, output_path: str) -> dict:
        """Use pre-recorded audio file."""
        source_path = self.audio_config.get("pre_recorded_path")
        
        print(f"   → Using pre-recorded audio: {source_path}")
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "voice_source": "pre_recorded",
            "source_path": source_path,
            "output_path": output_path,
            "status": "pending",
            "duration_seconds": 0
        }
        
        if not source_path or not os.path.exists(source_path):
            result["status"] = "error"
            result["error"] = f"Source file not found: {source_path}"
            return result
        
        try:
            # Copy or process the pre-recorded file
            if self.audio_config.get("cleanup_enabled"):
                result = self._cleanup_audio(source_path, output_path)
                result["voice_source"] = "pre_recorded"
                result["source_path"] = source_path
            else:
                # Just copy
                shutil.copy2(source_path, output_path)
                result["status"] = "completed"
                result["duration_seconds"] = self.get_duration(output_path)
            
            print(f"✅ Audio Agent: Pre-recorded audio ready ({result['duration_seconds']:.1f}s)")
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def _generate_ai_voice(self, text: str, output_path: str) -> dict:
        """Generate voice using AI TTS."""
        print(f"   → Generating AI voice...")
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "voice_source": "ai_tts",
            "input_text_length": len(text),
            "output_path": output_path,
            "status": "pending",
            "duration_seconds": 0,
            "format": "mp3"
        }
        
        # Try ElevenLabs first
        if self.elevenlabs_config and self.elevenlabs_config.get("api_key"):
            try:
                duration = self._generate_elevenlabs(text, output_path)
                result["duration_seconds"] = duration
                result["status"] = "completed"
                print(f"✅ Audio Agent: Generated via ElevenLabs ({duration:.1f}s)")
                return result
            except Exception as e:
                print(f"   ⚠️ ElevenLabs failed: {e}")
        
        # Fallback to gTTS
        try:
            duration = self._generate_gtts(text, output_path)
            result["duration_seconds"] = duration
            result["status"] = "completed"
            print(f"✅ Audio Agent: Generated via gTTS ({duration:.1f}s)")
        except Exception as e:
            print(f"⚠️ gTTS failed: {e}")
            result["status"] = "placeholder"
            result["error"] = str(e)
        
        return result
    
    def _create_silent_audio(self, output_path: str) -> dict:
        """Create silent audio placeholder."""
        duration = 60
        self._create_placeholder(output_path, duration)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "voice_source": "none",
            "output_path": output_path,
            "status": "completed",
            "duration_seconds": duration
        }
    
    # === TTS Methods ===
    
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
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        word_count = len(text.split())
        duration = (word_count / 150) * 60 / speed
        
        return duration
    
    def _generate_gtts(self, text: str, output_path: str) -> float:
        """Generate audio using gTTS."""
        try:
            from gtts import gTTS
            
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            
            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(output_path)
            
            word_count = len(text.split())
            duration = (word_count / 150) * 60
            
            return duration
        except ImportError:
            return self._create_placeholder(output_path, 60)
    
    def _create_placeholder(self, output_path: str, duration_sec: int = 60) -> float:
        """Create a silent placeholder audio file."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        try:
            subprocess.run([
                "ffmpeg", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
                "-t", str(duration_sec), "-y", output_path
            ], capture_output=True, timeout=30)
        except:
            with open(output_path, "wb") as f:
                f.write(b"")
        
        return float(duration_sec)
    
    # === Audio Processing ===
    
    def _cleanup_audio(self, input_path: str, output_path: str) -> dict:
        """Clean up audio - normalize, etc."""
        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        try:
            cmd = [
                "ffmpeg", "-i", input_path,
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                "-y", output_path
            ]
            subprocess.run(cmd, capture_output=True, check=True, timeout=120)
            result["status"] = "completed"
            result["duration_seconds"] = self.get_duration(output_path)
        except:
            shutil.copy2(input_path, output_path)
            result["status"] = "completed"
            result["duration_seconds"] = self.get_duration(output_path)
        
        return result
    
    def get_duration(self, audio_path: str) -> float:
        """Get audio file duration."""
        if not os.path.exists(audio_path):
            return 0.0
        
        try:
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
                   "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return float(result.stdout.strip() or 0)
        except:
            return 60.0
    
    def get_config(self) -> dict:
        """Get current audio configuration."""
        return self.audio_config.copy()


# Keep backward compatibility
def generate_voice(text: str, output_path: str) -> dict:
    """Legacy function for backward compatibility."""
    class MockAPIManager:
        def has_key(self, provider):
            return False
    
    agent = AudioAgent(MockAPIManager())
    return agent.process_audio(text, output_path)


if __name__ == "__main__":
    class MockAPIManager:
        def has_key(self, provider):
            return False
    
    # Test different modes
    agent = AudioAgent(MockAPIManager())
    
    print("=" * 40)
    print("Mode 1: AI TTS (default)")
    print("=" * 40)
    agent.set_voice_source(VoiceSource.AI_TTS)
    result = agent.process_audio("Hello world", "output/test_tts.mp3")
    print(f"Result: {result['status']}")
    
    print("\n" + "=" * 40)
    print("Mode 2: Pre-recorded")
    print("=" * 40)
    # Note: Would need actual file to test
    # agent.set_voice_source(VoiceSource.PRE_RECORDED, "path/to/audio.mp3")
    
    print(f"Config: {agent.get_config()}")