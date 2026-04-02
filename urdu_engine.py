import os
from PIL import Image, ImageDraw, ImageFont
import moviepy.editor as mp

class UrduEngine:
    """
    Handles Urdu text rendering and automated scrolling logic.
    Core Logic: Scroll Speed = (Total Text Height / Audio File Duration)
    """
    
    def __init__(self, font_path=None):
        # Default fallback font paths for macOS
        self.font_path = font_path or self._find_jameel_font()
        self.bg_color = (0, 0, 0, 0) # Transparent background
        self.text_color = (255, 255, 255) # White text
        self.width = 1080 # standard vertical video width (9:16)
        
    def _find_jameel_font(self):
        """Attempts to locate Jameel Noori Nastaleeq in standard macOS paths."""
        search_paths = [
            os.path.expanduser("~/Library/Fonts/Jameel Noori Nastaleeq.ttf"),
            "/Library/Fonts/Jameel Noori Nastaleeq.ttf",
            "assets/fonts/Jameel Noori Nastaleeq.ttf" # Local project assets
        ]
        for path in search_paths:
            if os.path.exists(path):
                return path
        return "Arial Unicode.ttf" # Last resort fallback

    def calculate_scroll_speed(self, text_height, audio_duration):
        """
        Calculates pixels per second for the scroll.
        Formula: Scroll Speed = (Total Text Height / Audio File Duration)
        """
        if audio_duration <= 0:
            return 0
        return text_height / audio_duration

    def render_text_image(self, text, font_size=40):
        """
        Renders the entire Urdu text into a single long vertical image.
        Uses Jameel Noori Nastaleeq for proper typography.
        """
        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except Exception:
            print(f"Warning: Could not load font at {self.font_path}. Using fallback.")
            font = ImageFont.load_default()

        # Wrap text logic (simple version)
        lines = text.split('\n')
        
        # Calculate total height
        temp_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        line_heights = [temp_draw.textbbox((0, 0), line, font=font)[3] for line in lines]
        total_height = sum(line_heights) + (len(lines) * 10) # 10px padding between lines
        
        # Create image
        img = Image.new('RGBA', (self.width, total_height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        current_y = 0
        for line in lines:
            # Draw text right-to-left (standard for Urdu)
            # We anchor at top-right for Urdu alignment
            draw.text((self.width - 20, current_y), line, font=font, fill=self.text_color, anchor="ra")
            current_y += temp_draw.textbbox((0, 0), line, font=font)[3] + 10
            
        return img, total_height

    def create_scrolling_video(self, text, audio_path, output_path):
        """
        Generates a video file where the Urdu text scrolls perfectly timed to the audio.
        """
        audio = mp.AudioFileClip(audio_path)
        duration = audio.duration
        
        # 1. Render text to image
        text_img, total_height = self.render_text_image(text)
        img_path = "temp_text.png"
        text_img.save(img_path)
        
        # 2. Create Clip
        text_clip = mp.ImageClip(img_path).set_duration(duration)
        
        # 3. Apply Scroll Logic
        # Initial position: top of the screen (y=0)
        # End position: bottom of the text is at the bottom of the screen
        # Or more simply: scroll based on calculated speed
        scroll_speed = self.calculate_scroll_speed(total_height, duration)
        
        def scroll(t):
            return (0, -scroll_speed * t)

        scrolling_clip = text_clip.set_position(scroll).set_audio(audio)
        
        # 4. Write result
        scrolling_clip.write_videofile(output_path, fps=24, codec="libx264")
        
        # Cleanup
        if os.path.exists(img_path):
            os.remove(img_path)

if __name__ == "__main__":
    engine = UrduEngine()
    print(f"Urdu Engine initialized with font: {engine.font_path}")
    # Example usage (commented out until an audio file is present)
    # engine.create_scrolling_video("اردو عبارت یہاں لکھیں", "sample_audio.mp3", "output.mp4")
