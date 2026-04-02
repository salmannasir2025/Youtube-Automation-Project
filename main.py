import os
import sys
from governor import Governor
from api_manager import APIManager
from urdu_engine import UrduEngine
import google.generativeai as genai

def main():
    print("--- Welcome to Youtube-Content Factory (OSCF) ---")
    
    # 1. Initialize Governor (Hardware Detection)
    gov = Governor()
    gov.status_report()
    ffmpeg_params = gov.get_ffmpeg_params()
    
    # 2. Load API Keys via Manager
    api_manager = APIManager()
    keys = api_manager.get_keys()
    
    if not keys["gemini"]:
        print("\n[!] No Gemini API Key found. Please run 'python3 api_manager.py' to set your keys.")
        return

    # 3. Initialize Gemini for Script Generation
    genai.configure(api_key=keys["gemini"])
    model = genai.GenerativeModel('gemini-pro')
    
    print("\n--- Step 1: Generating Urdu Script ---")
    prompt = "Write a short, engaging 1-minute Urdu story or educational script about the history of technology. Use proper Urdu characters."
    
    try:
        response = model.generate_content(prompt)
        urdu_text = response.text
        print("Script generated successfully!")
        print("-" * 20)
        print(urdu_text[:100] + "...") # Preview
        print("-" * 20)
    except Exception as e:
        print(f"Error generating script: {e}")
        return

    # 4. Initialize Urdu Engine
    engine = UrduEngine()
    
    print("\n--- Step 2: Preparing Video Production ---")
    # Note: In a full implementation, you would generate audio here using a TTS engine
    # For now, we'll look for a placeholder or explain the requirement
    audio_path = "assets/audio/voiceover.mp3"
    output_path = "output/final_video.mp4"
    
    if not os.path.exists("assets/audio"):
        os.makedirs("assets/audio", exist_vars=True)
    if not os.path.exists("output"):
        os.makedirs("output", exist_vars=True)

    if not os.path.exists(audio_path):
        print(f"\n[!] Please place your voiceover audio file at: {audio_path}")
        print("Once the audio is present, the engine will calculate scroll speed and render the video.")
        return

    # 5. Generate Scrolling Video
    print(f"\n--- Step 3: Rendering Video ({ffmpeg_params['vcodec']}) ---")
    try:
        engine.create_scrolling_video(urdu_text, audio_path, output_path)
        print(f"Video successfully rendered to: {output_path}")
    except Exception as e:
        print(f"Error during video rendering: {e}")

if __name__ == "__main__":
    main()
