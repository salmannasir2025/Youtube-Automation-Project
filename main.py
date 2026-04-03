from governor import Governor
from urdu_engine import UrduEngine
from api_manager import APIManager
from agents import Orchestrator

def main():
    # Initialize all components
    print("=" * 60)
    print("🎬 OSCF - Youtube Automation Project")
    print("   Multi-Agent Video Creation System")
    print("=" * 60)
    
    gov = Governor()
    api = APIManager()
    engine = UrduEngine()
    orchestrator = Orchestrator(api)
    
    print(f"\n📊 Hardware Profile: {gov.profile}")
    print(f"   CPU Cores: {gov.cpu_count}")
    print(f"   RAM: {gov.ram_gb:.1f} GB")
    print(f"   OS: {gov.os_type}")
    
    print("\n🤖 Agents Loaded:")
    print("   • Research Agent - Searches and gathers information")
    print("   • Writer Agent - Converts research into scripts")
    print("   • Fact-Checker Agent - Verifies claims and facts")
    print("   • Audio Agent - Voice generation & cleanup")
    print("   • Video Agent - Renders scroll videos")
    print("   • Publisher Agent - Publishes to YouTube, TikTok, etc.")
    print("   • Orchestrator - Coordinates the pipeline")
    
    # Example: Run the pipeline
    print("\n" + "=" * 60)
    print("Running pipeline example...")
    print("=" * 60 + "\n")
    
    # Run the full pipeline
    result = orchestrator.run_pipeline(
        topic="Artificial Intelligence in Healthcare",
        style="educational"
    )
    
    print("\n📋 Pipeline Results:")
    print(f"   Status: {result['status']}")
    print(f"   Topic: {result['topic']}")
    print(f"   Research: {'✅' if result['research'] else '❌'}")
    print(f"   Script: {'✅' if result['script'] else '❌'}")
    print(f"   Verification: {'✅' if result['verification'] else '❌'}")
    
    if result['errors']:
        print(f"\n❌ Errors: {result['errors']}")
    
    print("\n✅ System Initialized. Ready for video creation.")
    
if __name__ == "__main__":
    main()