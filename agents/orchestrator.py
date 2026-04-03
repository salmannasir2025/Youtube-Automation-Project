"""
Orchestrator - Coordinates all agents in the pipeline
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from .research_agent import ResearchAgent
from .writer_agent import WriterAgent
from .fact_checker_agent import FactCheckerAgent
from .audio_agent import AudioAgent
from .video_agent import VideoAgent
from .publisher_agent import PublisherAgent, Platform


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
    Keeps track of state, coordinates agents, and ensures workflow executes properly.
    """
    
    def __init__(self, api_manager, urdu_engine=None):
        self.api_manager = api_manager
        self.urdu_engine = urdu_engine
        self.state = PipelineState.IDLE
        
        # Initialize all agents
        self.research_agent = ResearchAgent(api_manager)
        self.writer_agent = WriterAgent(api_manager)
        self.fact_checker_agent = FactCheckerAgent(api_manager)
        self.audio_agent = AudioAgent(api_manager)
        self.video_agent = VideoAgent(api_manager, urdu_engine)
        self.publisher_agent = PublisherAgent(api_manager)
        
        # Output directory
        self.output_dir = "output"
        
        # Pipeline context - shared data between agents
        self.context = {
            "topic": None,
            "style": "educational",
            "research_results": None,
            "script": None,
            "verification_results": None,
            "audio_path": None,
            "video_path": None,
            "publish_results": None,
            "errors": [],
            "started_at": None,
            "completed_at": None
        }
        
        print("🎛️ Orchestrator: All agents initialized")
        print("   • Research Agent")
        print("   • Writer Agent")
        print("   • Fact-Checker Agent")
        print("   • Audio Agent")
        print("   • Video Agent")
        print("   • Publisher Agent")
    
    def run_pipeline(self, topic: str, style: str = "educational", 
                     publish: bool = False, platforms: list = None) -> dict:
        """
        Run the full pipeline from topic to video and optionally publish.
        
        Args:
            topic: Video topic to research and write about
            style: Script style (educational, news, storytelling)
            publish: Whether to publish after rendering
            platforms: List of platforms to publish to
            
        Returns:
            Final pipeline results
        """
        self.context["topic"] = topic
        self.context["style"] = style
        self.context["started_at"] = datetime.now().isoformat()
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"🎬 Starting Pipeline: {topic}")
        print(f"   Style: {style}")
        print(f"   Publish: {publish}")
        print(f"{'='*60}\n")
        
        try:
            # Step 1: Research
            self._set_state(PipelineState.RESEARCHING)
            research_results = self._run_research(topic)
            self.context["research_results"] = research_results
            
            # Step 2: Write script
            self._set_state(PipelineState.WRITING)
            script = self._run_writer(research_results, style)
            self.context["script"] = script
            
            # Step 3: Fact-check
            self._set_state(PipelineState.FACT_CHECKING)
            verification = self._run_fact_check(script, research_results)
            self.context["verification_results"] = verification
            
            # Check if should proceed
            if verification.get("overall_status") == "failed":
                raise Exception("Fact-checking failed - cannot proceed")
            
            # Step 4: Generate audio
            self._set_state(PipelineState.AUDIO_GENERATING)
            audio_path = self._run_audio(script)
            self.context["audio_path"] = audio_path
            
            # Step 5: Render video
            self._set_state(PipelineState.VIDEO_RENDERING)
            script_text = self.writer_agent.format_for_urdu_engine(script)
            video_path = self._run_video(script_text, audio_path)
            self.context["video_path"] = video_path
            
            # Step 6: Publish (if requested)
            if publish:
                self._set_state(PipelineState.PUBLISHING)
                publish_results = self._run_publish(video_path, script, platforms or [Platform.YOUTUBE])
                self.context["publish_results"] = publish_results
            
            # Complete
            self._set_state(PipelineState.COMPLETED)
            self.context["completed_at"] = datetime.now().isoformat()
            
            print(f"\n{'='*60}")
            print(f"✅ Pipeline Completed Successfully!")
            print(f"{'='*60}\n")
            
            return self._get_results()
            
        except Exception as e:
            self._set_state(PipelineState.FAILED)
            self.context["errors"].append(str(e))
            print(f"\n❌ Pipeline Failed: {e}")
            return self._get_results()
    
    def _run_research(self, topic: str) -> dict:
        """Run the research agent."""
        print("\n📋 Step 1/6: Research")
        print("-" * 40)
        
        results = self.research_agent.search(topic)
        
        return results
    
    def _run_writer(self, research_data: dict, style: str) -> dict:
        """Run the writer agent."""
        print("\n📋 Step 2/6: Script Writing")
        print("-" * 40)
        
        script = self.writer_agent.write_script(research_data, style)
        
        return script
    
    def _run_fact_check(self, script_data: dict, research_data: dict) -> dict:
        """Run the fact-checker agent."""
        print("\n📋 Step 3/6: Fact Verification")
        print("-" * 40)
        
        results = self.fact_checker_agent.check_claims(script_data, research_data)
        
        return results
    
    def _run_audio(self, script_data: dict) -> str:
        """Run the audio agent."""
        print("\n📋 Step 4/6: Audio Generation")
        print("-" * 40)
        
        # Get text for TTS
        text = self.writer_agent.format_for_urdu_engine(script_data)
        
        # Generate audio
        output_path = os.path.join(self.output_dir, f"audio_{int(datetime.now().timestamp())}.mp3")
        
        result = self.audio_agent.generate_voice(text, output_path)
        
        return result.get("output_path", output_path)
    
    def _run_video(self, text: str, audio_path: str) -> str:
        """Run the video agent."""
        print("\n📋 Step 5/6: Video Rendering")
        print("-" * 40)
        
        output_path = os.path.join(self.output_dir, f"video_{int(datetime.now().timestamp())}.mp4")
        
        result = self.video_agent.render_scroll_video(text, audio_path, output_path)
        
        return result.get("output_path", output_path)
    
    def _run_publish(self, video_path: str, script_data: dict, platforms: list) -> dict:
        """Run the publisher agent."""
        print("\n📋 Step 6/6: Publishing")
        print("-" * 40)
        
        title = script_data.get("topic", "Video")
        description = script_data.get("full_script", "")[:5000]  # YouTube limit
        
        result = self.publisher_agent.publish(
            video_path=video_path,
            title=title,
            description=description,
            platforms=platforms
        )
        
        return result
    
    def _set_state(self, state: PipelineState):
        """Update pipeline state."""
        self.state = state
        print(f"📍 State: {state.value}")
    
    def _get_results(self) -> dict:
        """Get final pipeline results."""
        return {
            "status": self.state.value,
            "topic": self.context["topic"],
            "style": self.context["style"],
            "research": self.context["research_results"],
            "script": self.context["script"],
            "verification": self.context["verification_results"],
            "audio_path": self.context["audio_path"],
            "video_path": self.context["video_path"],
            "publish": self.context["publish_results"],
            "errors": self.context["errors"],
            "started_at": self.context["started_at"],
            "completed_at": self.context["completed_at"]
        }
    
    def get_status(self) -> dict:
        """Get current pipeline status."""
        return {
            "state": self.state.value,
            "topic": self.context["topic"],
            "has_research": self.context["research_results"] is not None,
            "has_script": self.context["script"] is not None,
            "has_verification": self.context["verification_results"] is not None,
            "has_audio": self.context["audio_path"] is not None,
            "has_video": self.context["video_path"] is not None,
            "has_publish": self.context["publish_results"] is not None
        }
    
    def reset(self):
        """Reset the pipeline for a new run."""
        self.state = PipelineState.IDLE
        self.context = {
            "topic": None,
            "style": "educational",
            "research_results": None,
            "script": None,
            "verification_results": None,
            "audio_path": None,
            "video_path": None,
            "publish_results": None,
            "errors": [],
            "started_at": None,
            "completed_at": None
        }
        print("🔄 Orchestrator: Pipeline reset")


# Standalone test
if __name__ == "__main__":
    class MockAPIManager:
        def get_active_brain(self):
            return None
        
        def get_llm_config(self):
            return {"provider": "GEMINI", "api_key": None}
        
        def has_key(self, provider):
            return False
    
    class MockUrduEngine:
        pass
    
    orchestrator = Orchestrator(MockAPIManager(), MockUrduEngine())
    print("Orchestrator initialized")
    print(f"Status: {orchestrator.get_status()}")