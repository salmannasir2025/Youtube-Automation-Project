"""
Video Agent - Renders the final video using UrduEngine
"""
import json
import os
import subprocess
from datetime import datetime
from typing import Optional, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont


class VideoAgent:
    """Agent that renders the final scroll video."""
    
    def __init__(self, api_manager, urdu_engine):
        self.api_manager = api_manager
        self.urdu_engine = urdu_engine
        self.render_config = {
            "resolution": (1080, 1920),  # 9:16 vertical video
            "fps": 30,
            "font_size": 50,
            "text_color": "white",
            "background_color": "black",
            "scroll_speed": "auto"
        }
        
    def render_scroll_video(self, text: str, audio_path: str, output_path: str) -> dict:
        """
        Render a scroll video with the given text and audio.
        
        Args:
            text: Scroll text content
            audio_path: Path to audio file
            output_path: Where to save the video
            
        Returns:
            Dictionary with render results
        """
        print(f"🎬 Video Agent: Rendering scroll video")
        print(f"   Text length: {len(text)} chars")
        print(f"   Audio: {audio_path}")
        print(f"   Output: {output_path}")
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "text_length": len(text),
            "audio_path": audio_path,
            "output_path": output_path,
            "status": "pending",
            "duration_seconds": 0,
            "resolution": self.render_config["resolution"],
            "file_size_mb": 0
        }
        
        # Check if audio exists
        audio_duration = 60  # default
        if os.path.exists(audio_path):
            audio_duration = self._get_audio_duration(audio_path)
        else:
            # Estimate from text
            word_count = len(text.split())
            audio_duration = (word_count / 150) * 60  # 150 words/min
        
        result["duration_seconds"] = audio_duration
        
        # Try using UrduEngine if available
        try:
            if hasattr(self.urdu_engine, 'create_scroll_video'):
                print("   Using UrduEngine...")
                clip = self.urdu_engine.create_scroll_video(text, audio_path, output_path)
                result["status"] = "completed"
                print(f"✅ Video Agent: Rendered via UrduEngine")
                return result
        except Exception as e:
            print(f"   UrduEngine not available: {e}")
        
        # Fallback: render with moviepy directly
        try:
            self._render_with_moviepy(text, audio_path, output_path, audio_duration)
            result["status"] = "completed"
            print(f"✅ Video Agent: Rendered with MoviePy")
        except Exception as e:
            print(f"⚠️ MoviePy failed: {e}")
            # Create placeholder
            self._create_placeholder_video(output_path, audio_duration)
            result["status"] = "placeholder"
            result["error"] = str(e)
        
        # Get file size
        if os.path.exists(output_path):
            result["file_size_mb"] = os.path.getsize(output_path) / (1024 * 1024)
        
        return result
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds."""
        try:
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
                   "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return float(result.stdout.strip() or 60)
        except:
            return 60
    
    def _render_with_moviepy(self, text: str, audio_path: str, output_path: str, duration: float):
        """Render video using MoviePy."""
        try:
            from moviepy.editor import TextClip, AudioFileClip, CompositeVideoClip
        except ImportError:
            raise ImportError("MoviePy not installed")
        
        # Create text clip - simple scrolling effect
        width, height = self.render_config["resolution"]
        
        # Split text into lines for scrolling
        lines = text.split("\n")
        
        # Create a simple static text for now (full scroll would need more complex setup)
        txt_clip = TextClip(
            text[:500],  # Limit text length
            fontsize=self.render_config["font_size"],
            color=self.render_config["text_color"],
            size=(width - 100, height - 100),
            method="caption"
        )
        
        # Load audio
        if os.path.exists(audio_path):
            audio = AudioFileClip(audio_path)
            txt_clip = txt_clip.set_duration(audio.duration)
            txt_clip = txt_clip.set_audio(audio)
        else:
            txt_clip = txt_clip.set_duration(duration)
        
        # Write video
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        txt_clip.write_videofile(output_path, fps=self.render_config["fps"], codec="libx264")
    
    def _create_placeholder_video(self, output_path: str, duration: float):
        """Create a placeholder video."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        # Use ffmpeg to create a black video
        try:
            cmd = [
                "ffmpeg", "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:d={duration}",
                "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
                "-c:v", "libx264", "-c:a", "aac", "-y", output_path
            ]
            subprocess.run(cmd, capture_output=True, check=True, timeout=60)
        except:
            # Last resort - just touch the file
            with open(output_path, "wb") as f:
                f.write(b"\x00" * 1000)
    
    def configure(self, **kwargs):
        """Configure video rendering settings."""
        self.render_config.update(kwargs)
    
    def set_resolution(self, width: int, height: int):
        """Set video resolution."""
        self.render_config["resolution"] = (width, height)
    
    def set_fps(self, fps: int):
        """Set frames per second."""
        self.render_config["fps"] = fps
    
    def set_font_size(self, size: int):
        """Set text font size."""
        self.render_config["font_size"] = size


# Standalone test
if __name__ == "__main__":
    class MockAPIManager:
        pass
    
    class MockUrduEngine:
        pass
    
    agent = VideoAgent(MockAPIManager(), MockUrduEngine())
    result = agent.render_scroll_video("Test text", "audio.mp3", "output.mp4")
    print(f"Status: {result['status']}")