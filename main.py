from governor import Governor
from urdu_engine import UrduEngine
from api_manager import APIManager
from agents import Orchestrator, Platform, VoiceSource

def main():
    # Initialize all components
    print("=" * 60)
    print("🎬 OSCF - Youtube Automation Project")
    print("   Multi-Agent Video Creation System v2.0")
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
    print("   • Scout (Research) - Web search & information gathering")
    print("   • Scribe (Writer) - Script generation with LLM")
    print("   • Verifier (Fact-Checker) - Claim verification")
    print("   • Artisan (Audio+Video) - Voice & video rendering")
    print("   • Publisher - YouTube/TikTok/Instagram/Twitter")
    print("   • Orchestrator - State Machine coordination")
    
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
    
    # Parse command line arguments
    import sys
    
    if len(sys.argv) > 1:
        # Get topic (first non-flag argument)
        topic = None
        style = "educational"
        publish = False
        voice_source = "ai_tts"
        pre_recorded_path = None
        
        i = 1
        while i < len(sys.argv):
            arg = sys.argv[i]
            
            if arg == "--publish":
                publish = True
            elif arg == "--style" and i + 1 < len(sys.argv):
                style = sys.argv[i + 1]
                i += 1
            elif arg == "--voice" and i + 1 < len(sys.argv):
                voice_source = sys.argv[i + 1]
                i += 1
            elif arg == "--audio-path" and i + 1 < len(sys.argv):
                pre_recorded_path = sys.argv[i + 1]
                i += 1
            elif not arg.startswith("--"):
                topic = arg
            i += 1
        
        if not topic:
            print("\n❌ Error: Please provide a topic")
            print("\nUsage: python main.py \"Your topic\" [options]")
            print("\nOptions:")
            print("  --style [educational|news|storytelling]  Script style")
            print("  --voice [ai_tts|pre_recorded|none]         Voice source")
            print("  --audio-path <path>                       Path to pre-recorded audio")
            print("  --publish                                 Publish to YouTube")
            return {"error": "No topic provided"}
        
        print("\n" + "=" * 60)
        print(f"Running pipeline: {topic}")
        print(f"Style: {style} | Voice: {voice_source} | Publish: {publish}")
        print("=" * 60 + "\n")
        
        # Set voice source in project state
        orchestrator.project_state.set_metadata("voice_source", voice_source)
        if voice_source == "pre_recorded" and pre_recorded_path:
            orchestrator.project_state.set_metadata("pre_recorded_audio_path", pre_recorded_path)
        
        # Run pipeline
        result = orchestrator.run_pipeline(topic, style, publish=publish)
        
        print("\n📋 Pipeline Results:")
        print(f"   Status: {result['status']}")
        print(f"   Topic: {result['summary'].get('topic', result.get('project_id'))}")
        
        if result.get('summary'):
            print(f"   Agents: {result['summary'].get('agents_completed', 0)}/{result['summary'].get('agents_total', 0)} completed")
        
        if result.get('full_state', {}).get('metadata', {}).get('voice_source'):
            print(f"   Voice: {result['full_state']['metadata']['voice_source']}")
        
        if result.get('full_state', {}).get('agents', {}).get('artisan', {}).get('metadata', {}).get('phase') == 'audio':
            audio_meta = result['full_state']['agents']['artisan']['metadata']
            print(f"   Audio: {audio_meta.get('voice_source', 'unknown')} ({audio_meta.get('duration', 0):.1f}s)")
        
        if result.get('errors'):
            print(f"\n❌ Errors:")
            for err in result['errors']:
                print(f"   - {err['error']}")
        
        # Show state file location
        print(f"\n📁 State file: {result.get('state_file')}")
        
        return result
    else:
        # Show help
        print("\n" + "=" * 60)
        print("Ready for video creation!")
        print("=" * 60)
        print("\nUsage:")
        print("  python main.py \"Your topic here\"")
        print("  python main.py \"Your topic\" --style news")
        print("  python main.py \"Your topic\" --voice ai_tts")
        print("  python main.py \"Your topic\" --voice pre_recorded --audio-path myvoice.mp3")
        print("  python main.py \"Your topic\" --publish")
        print("\nOptions:")
        print("  --style [educational|news|storytelling]  Script style")
        print("  --voice [ai_tts|pre_recorded|none]       Voice source")
        print("  --audio-path <path>                       Path to pre-recorded audio (for pre_recorded)")
        print("  --publish                                 Publish to YouTube after rendering")
        
        return {"status": "ready"}
    
if __name__ == "__main__":
    main()