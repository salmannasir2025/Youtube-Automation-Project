from governor import Governor
from urdu_engine import UrduEngine
from api_manager import APIManager
from agents import Orchestrator, Platform

def main():
    # Initialize all components
    print("=" * 60)
    print("🎬 OSCF - Youtube Automation Project")
    print("   Multi-Agent Video Creation System")
    print("=" * 60)
    
    # Initialize components
    gov = Governor()
    api = APIManager()
    engine = UrduEngine()
    orchestrator = Orchestrator(api, engine)
    
    print(f"\n📊 Hardware Profile: {gov.profile}")
    print(f"   CPU Cores: {gov.cpu_count}")
    print(f"   RAM: {gov.ram_gb:.1f} GB")
    print(f"   OS: {gov.os_type}")
    
    print("\n🤖 Agents Loaded:")
    print("   • Research Agent - Web search & information gathering")
    print("   • Writer Agent - Script generation with LLM")
    print("   • Fact-Checker Agent - Claim verification")
    print("   • Audio Agent - Voice generation (ElevenLabs/gTTS)")
    print("   • Video Agent - Scroll video rendering")
    print("   • Publisher Agent - YouTube/TikTok/Instagram/Twitter")
    print("   • Orchestrator - Pipeline coordination")
    
    # Show LLM status
    llm_config = api.get_llm_config()
    print(f"\n🧠 LLM Status:")
    print(f"   Provider: {llm_config.get('brain', 'NONE')}")
    if llm_config.get("api_key"):
        print(f"   Model: {llm_config.get('model')}")
        print(f"   ✅ Connected")
    else:
        print(f"   ⚠️ No API key - using template generation")
    
    # Show available APIs
    print(f"\n🔗 API Status:")
    if api.has_key("BRAVE_SEARCH"):
        print(f"   ✅ Brave Search")
    if api.has_key("ELEVENLABS"):
        print(f"   ✅ ElevenLabs")
    if api.has_key("YOUTUBE"):
        print(f"   ✅ YouTube API")
    
    # Check if user wants to run pipeline
    import sys
    
    if len(sys.argv) > 1:
        # Run with command line arguments
        topic = " ".join(sys.argv[1:])
        style = "educational"
        publish = False
        
        # Parse optional flags
        if "--publish" in sys.argv:
            publish = True
        if "--style" in sys.argv:
            idx = sys.argv.index("--style")
            if idx + 1 < len(sys.argv):
                style = sys.argv[idx + 1]
        
        print("\n" + "=" * 60)
        print(f"Running pipeline: {topic}")
        print(f"Style: {style} | Publish: {publish}")
        print("=" * 60 + "\n")
        
        result = orchestrator.run_pipeline(topic, style, publish=publish)
        
        print("\n📋 Pipeline Results:")
        print(f"   Status: {result['status']}")
        print(f"   Topic: {result['topic']}")
        
        if result.get('script'):
            print(f"   Script: ✅ ({result['script'].get('word_count', 0)} words)")
        
        if result.get('video_path'):
            print(f"   Video: ✅ {result['video_path']}")
        
        if result.get('publish'):
            pub = result['publish']
            print(f"   Published: {pub.get('overall_status')}")
            for platform, info in pub.get('platforms', {}).items():
                print(f"      - {platform}: {info.get('status')}")
        
        if result.get('errors'):
            print(f"\n❌ Errors:")
            for err in result['errors']:
                print(f"   - {err}")
        
        return result
    else:
        # Interactive mode
        print("\n" + "=" * 60)
        print("Ready for video creation!")
        print("=" * 60)
        print("\nUsage:")
        print("  python main.py \"Your topic here\"")
        print("  python main.py \"Your topic\" --style educational")
        print("  python main.py \"Your topic\" --publish")
        print("\nStyles: educational, news, storytelling")
        
        return {"status": "ready"}
    
if __name__ == "__main__":
    main()