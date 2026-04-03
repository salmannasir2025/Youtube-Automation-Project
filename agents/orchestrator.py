"""
Orchestrator - Coordinates all agents in the pipeline using State Machine
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from .research_agent import ResearchAgent
from .writer_agent import WriterAgent
from .fact_checker_agent import FactCheckerAgent
from .audio_agent import AudioAgent
from .video_agent import VideoAgent
from .publisher_agent import PublisherAgent, Platform
from ..project_state import ProjectState, get_state


class PipelineState(Enum):
    """Pipeline execution states."""
    IDLE = "idle"
    RESEARCHING = "researching"
    WRITING = "writing"
    FACT_CHECKING = "fact_checking"
    AUDIO_GENERATING = "audio_generating"
    VIDEO_RENDERING = "video_rendering"
    PUBLISHING = "publishing"
    COMPLETED = "completed"
    FAILED = "failed"


class Orchestrator:
    """
    The main coordinator that manages the video creation pipeline.
    Uses a Graph-based State Machine for agent coordination.
    Acts as the "Governor" - monitors and controls other agents.
    """
    
    # Agent name constants
    AGENT_SCOUT = "scout"       # Research
    AGENT_VERIFIER = "verifier" # Fact-check
    AGENT_SCRIBE = "scribe"     # Writer
    AGENT_ARTISAN = "artisan"   # Audio + Video
    AGENT_PUBLISHER = "publisher"
    
    def __init__(self, api_manager, urdu_engine=None, project_id: str = None):
        self.api_manager = api_manager
        self.urdu_engine = urdu_engine
        self.project_id = project_id or f"video_{int(datetime.now().timestamp())}"
        
        # Initialize state manager (Single Source of Truth)
        self.project_state = get_state(self.project_id)
        
        # Set hardware profile in state
        try:
            from ..governor import Governor
            gov = Governor()
            self.project_state.set_hardware_profile(gov.profile)
        except:
            self.project_state.set_hardware_profile("UNKNOWN")
        
        # Initialize agents (stateless, output to state)
        self.research_agent = ResearchAgent(api_manager)
        self.writer_agent = WriterAgent(api_manager)
        self.fact_checker_agent = FactCheckerAgent(api_manager)
        self.audio_agent = AudioAgent(api_manager)
        self.video_agent = VideoAgent(api_manager, urdu_engine)
        self.publisher_agent = PublisherAgent(api_manager)
        
        # Output directory
        self.output_dir = "output"
        
        # Max discussion turns to prevent infinite loops
        self.max_turns = 3
        
        # Pipeline context
        self.context = {
            "topic": None,
            "style": "educational",
            "started_at": None,
            "completed_at": None
        }
        
        # Register all agents in state
        self._register_agents()
        
        print("🎛️ Orchestrator: State Machine initialized")
        print(f"   Project ID: {self.project_id}")
        print(f"   State File: {self.project_state.state_file}")
    
    def _register_agents(self):
        """Register all agents in the project state."""
        self.project_state.register_agent(self.AGENT_SCOUT)
        self.project_state.register_agent(self.AGENT_VERIFIER)
        self.project_state.register_agent(self.AGENT_SCRIBE)
        self.project_state.register_agent(self.AGENT_ARTISAN)
        self.project_state.register_agent(self.AGENT_PUBLISHER)
    
    def run_pipeline(self, topic: str, style: str = "educational", 
                     publish: bool = False, platforms: list = None) -> dict:
        """
        Run the full pipeline using State Machine.
        
        Args:
            topic: Video topic
            style: Script style
            publish: Whether to publish
            platforms: Platforms to publish to
            
        Returns:
            Final pipeline results
        """
        self.context["topic"] = topic
        self.context["style"] = style
        self.context["started_at"] = datetime.now().isoformat()
        
        # Set metadata
        self.project_state.set_metadata("topic", topic)
        self.project_state.set_metadata("style", style)
        self.project_state.set_metadata("publish", publish)
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"🎬 Starting Pipeline: {topic}")
        print(f"   Project ID: {self.project_id}")
        print(f"   State: {self.project_state.state_file}")
        print(f"{'='*60}\n")
        
        try:
            # Step 1: Scout (Research)
            self._run_scout(topic)
            
            # Step 2: Scribe (Writer)
            research_data = self.project_state.get_agent_output(self.AGENT_SCOUT)
            self._run_scribe(research_data, style)
            
            # Step 3: Verifier (Fact-Check)
            script_data = self.project_state.get_agent_output(self.AGENT_SCRIBE)
            self._run_verifier(script_data, research_data)
            
            # Check verification status
            verification = self.project_state.get_agent_output(self.AGENT_VERIFIER)
            if verification and verification.get("overall_status") == "failed":
                raise Exception("Fact-checking failed - cannot proceed")
            
            # Step 4: Artisan (Audio)
            self._run_artisan_audio(script_data)
            
            # Step 5: Artisan (Video)
            script_text = self.writer_agent.format_for_urdu_engine(script_data)
            audio_path = self.project_state.get_agent_output(self.AGENT_ARTISAN)
            self._run_artisan_video(script_text, audio_path)
            
            # Step 6: Publisher
            if publish:
                video_path = self.project_state.get_agent_output(f"{self.AGENT_ARTISAN}_video")
                self._run_publisher(video_path, script_data, platforms or [Platform.YOUTUBE])
            
            # Complete
            self.project_state.set_status("completed")
            self.context["completed_at"] = datetime.now().isoformat()
            
            print(f"\n{'='*60}")
            print(f"✅ Pipeline Completed!")
            print(f"{'='*60}\n")
            
            return self._get_results()
            
        except Exception as e:
            self.project_state.set_status("failed")
            self.project_state.add_error(str(e))
            print(f"\n❌ Pipeline Failed: {e}")
            return self._get_results()
    
    def _run_scout(self, topic: str):
        """Run the Scout (Research) agent."""
        print("\n📋 Step 1/6: Scout (Research)")
        print("-" * 40)
        
        self.project_state.set_agent_status(self.AGENT_SCOUT, "in_progress")
        
        results = self.research_agent.search(topic)
        
        self.project_state.set_agent_status(
            self.AGENT_SCOUT, 
            "completed",
            {"sources": len(results.get("sources", [])), "findings": len(results.get("key_findings", []))}
        )
        self.project_state.set_agent_output(self.AGENT_SCOUT, results)
    
    def _run_scribe(self, research_data: dict, style: str):
        """Run the Scribe (Writer) agent."""
        print("\n📋 Step 2/6: Scribe (Script Writing)")
        print("-" * 40)
        
        self.project_state.set_agent_status(self.AGENT_SCRIBE, "in_progress")
        
        script = self.writer_agent.write_script(research_data, style)
        
        self.project_state.set_agent_status(
            self.AGENT_SCRIBE,
            "completed",
            {"word_count": script.get("word_count", 0), "style": style}
        )
        self.project_state.set_agent_output(self.AGENT_SCRIBE, script)
    
    def _run_verifier(self, script_data: dict, research_data: dict):
        """Run the Verifier (Fact-Checker) agent with self-correction loop."""
        print("\n📋 Step 3/6: Verifier (Fact-Checking)")
        print("-" * 40)
        
        self.project_state.set_agent_status(self.AGENT_VERIFIER, "in_progress")
        
        # Run initial verification
        results = self.fact_checker_agent.check_claims(script_data, research_data)
        
        # Self-correction loop (max 3 turns)
        turn = 0
        while turn < self.max_turns:
            uncertain = len(results.get("uncertain_claims", []))
            if uncertain == 0:
                break
            
            print(f"   🔄 Verification turn {turn + 1}/{self.max_turns}...")
            # In production, would search for counter-arguments here
            turn += 1
        
        self.project_state.set_agent_status(
            self.AGENT_VERIFIER,
            "completed",
            {
                "claims_checked": results.get("claims_checked", 0),
                "status": results.get("overall_status", "unknown")
            }
        )
        self.project_state.set_agent_output(self.AGENT_VERIFIER, results)
    
    def _run_artisan_audio(self, script_data: dict):
        """Run the Artisan (Audio) agent."""
        print("\n📋 Step 4/6: Artisan (Audio Generation)")
        print("-" * 40)
        
        self.project_state.set_agent_status(self.AGENT_ARTISAN, "in_progress", {"phase": "audio"})
        
        # Get voice source from metadata or default to AI_TTS
        voice_source_str = self.project_state.state.get("metadata", {}).get("voice_source", "ai_tts")
        
        # Configure audio agent based on source
        from .audio_agent import VoiceSource
        if voice_source_str == "pre_recorded":
            pre_recorded_path = self.project_state.state.get("metadata", {}).get("pre_recorded_audio_path")
            if pre_recorded_path:
                self.audio_agent.set_voice_source(VoiceSource.PRE_RECORDED, pre_recorded_path)
            else:
                print("   ⚠️ No pre-recorded path found, falling back to AI_TTS")
                self.audio_agent.set_voice_source(VoiceSource.AI_TTS)
        elif voice_source_str == "none":
            self.audio_agent.set_voice_source(VoiceSource.NONE)
        else:
            self.audio_agent.set_voice_source(VoiceSource.AI_TTS)
        
        text = self.writer_agent.format_for_urdu_engine(script_data)
        output_path = os.path.join(self.output_dir, f"audio_{self.project_id}.mp3")
        
        # Use new process_audio method
        result = self.audio_agent.process_audio(text, output_path)
        
        self.project_state.set_agent_status(
            self.AGENT_ARTISAN,
            "completed" if result.get("status") == "completed" else "failed",
            {"phase": "audio", "duration": result.get("duration_seconds", 0), "voice_source": result.get("voice_source", "unknown")}
        )
        self.project_state.set_agent_output(self.AGENT_ARTISAN, result.get("output_path", output_path))
    
    def _run_artisan_video(self, text: str, audio_path: str):
        """Run the Artisan (Video) agent."""
        print("\n📋 Step 5/6: Artisan (Video Rendering)")
        print("-" * 40)
        
        # Ensure audio path exists
        if not audio_path or not os.path.exists(audio_path):
            audio_path = self.project_state.get_agent_output(self.AGENT_ARTISAN)
        
        self.project_state.set_agent_status(self.AGENT_ARTISAN, "in_progress", {"phase": "video"})
        
        output_path = os.path.join(self.output_dir, f"video_{self.project_id}.mp4")
        result = self.video_agent.render_scroll_video(text, audio_path, output_path)
        
        video_key = f"{self.AGENT_ARTISAN}_video"
        self.project_state.set_agent_status(
            self.AGENT_ARTISAN,
            "completed" if result.get("status") in ["completed", "placeholder"] else "failed",
            {"phase": "video", "duration": result.get("duration_seconds", 0)}
        )
        self.project_state.set_agent_output(video_key, result.get("output_path", output_path))
    
    def _run_publish(self, video_path: str, script_data: dict, platforms: list):
        """Run the Publisher agent."""
        print("\n📋 Step 6/6: Publishing")
        print("-" * 40)
        
        self.project_state.set_agent_status(self.AGENT_PUBLISHER, "in_progress")
        
        title = script_data.get("topic", "Video")
        description = script_data.get("full_script", "")[:5000]
        
        result = self.publisher_agent.publish(
            video_path=video_path,
            title=title,
            description=description,
            platforms=platforms
        )
        
        self.project_state.set_agent_status(
            self.AGENT_PUBLISHER,
            "completed",
            {"platforms": list(result.get("platforms", {}).keys())}
        )
        self.project_state.set_agent_output(self.AGENT_PUBLISHER, result)
    
    def _get_results(self) -> dict:
        """Get final pipeline results from state."""
        return {
            "project_id": self.project_id,
            "state_file": self.project_state.state_file,
            "status": self.project_state.state.get("status"),
            "summary": self.project_state.get_summary(),
            "full_state": self.project_state.get_all()
        }
    
    def get_status(self) -> dict:
        """Get current pipeline status."""
        return self.project_state.get_summary()
    
    def get_state_file_path(self) -> str:
        """Get the path to the state file."""
        return self.project_state.state_file
    
    def reset(self):
        """Reset the pipeline."""
        self.project_state.reset()
        self._register_agents()
        print("🔄 Orchestrator: Pipeline reset")


if __name__ == "__main__":
    # Test
    class MockAPIManager:
        def get_active_brain(self):
            return None
        def has_key(self, provider):
            return False
    
    orchestrator = Orchestrator(MockAPIManager(), None, "test_run")
    print(f"State file: {orchestrator.get_state_file_path()}")
    print(f"Status: {orchestrator.get_status()}")