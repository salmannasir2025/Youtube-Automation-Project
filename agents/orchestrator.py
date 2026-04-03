"""
Orchestrator - Coordinates all agents in the pipeline
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from .research_agent import ResearchAgent
from .writer_agent import WriterAgent
from .fact_checker_agent import FactCheckerAgent


class PipelineState(Enum):
    """Pipeline execution states."""
    IDLE = "idle"
    RESEARCHING = "researching"
    WRITING = "writing"
    FACT_CHECKING = "fact_checking"
    COMPLETED = "completed"
    FAILED = "failed"


class Orchestrator:
    """
    The main coordinator that manages the video creation pipeline.
    Keeps track of state, coordinates agents, and ensures workflow executes properly.
    """
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.state = PipelineState.IDLE
        
        # Initialize all agents
        self.research_agent = ResearchAgent(api_manager)
        self.writer_agent = WriterAgent(api_manager)
        self.fact_checker_agent = FactCheckerAgent(api_manager)
        
        # Pipeline context - shared data between agents
        self.context = {
            "topic": None,
            "research_results": None,
            "script": None,
            "verification_results": None,
            "errors": [],
            "started_at": None,
            "completed_at": None
        }
        
        print("🎛️ Orchestrator: All agents initialized")
    
    def run_pipeline(self, topic: str, style: str = "educational") -> dict:
        """
        Run the full pipeline from topic to script.
        
        Args:
            topic: Video topic to research and write about
            style: Script style (educational, news, storytelling)
            
        Returns:
            Final pipeline results
        """
        self.context["topic"] = topic
        self.context["started_at"] = datetime.now().isoformat()
        
        print(f"\n{'='*50}")
        print(f"🎬 Starting Pipeline: {topic}")
        print(f"{'='*50}\n")
        
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
            
            # Complete
            self._set_state(PipelineState.COMPLETED)
            self.context["completed_at"] = datetime.now().isoformat()
            
            print(f"\n{'='*50}")
            print(f"✅ Pipeline Completed Successfully!")
            print(f"{'='*50}\n")
            
            return self._get_results()
            
        except Exception as e:
            self._set_state(PipelineState.FAILED)
            self.context["errors"].append(str(e))
            print(f"\n❌ Pipeline Failed: {e}")
            return self._get_results()
    
    def _run_research(self, topic: str) -> dict:
        """Run the research agent."""
        print("\n📋 Step 1/3: Research")
        print("-" * 30)
        
        results = self.research_agent.search(topic)
        
        # Add findings from context
        self.research_agent.add_finding(f"Research completed on {topic}")
        
        return results
    
    def _run_writer(self, research_data: dict, style: str) -> dict:
        """Run the writer agent."""
        print("\n📋 Step 2/3: Script Writing")
        print("-" * 30)
        
        # Get context for the writer
        context = self.research_agent.get_context()
        
        # Write script (using LLM if available, otherwise template)
        script = self.writer_agent.write_script(research_data, style)
        
        return script
    
    def _run_fact_check(self, script_data: dict, research_data: dict) -> dict:
        """Run the fact-checker agent."""
        print("\n📋 Step 3/3: Fact Verification")
        print("-" * 30)
        
        results = self.fact_checker_agent.check_claims(script_data, research_data)
        
        return results
    
    def _set_state(self, state: PipelineState):
        """Update pipeline state."""
        self.state = state
        print(f"State: {state.value}")
    
    def _get_results(self) -> dict:
        """Get final pipeline results."""
        return {
            "status": self.state.value,
            "topic": self.context["topic"],
            "research": self.context["research_results"],
            "script": self.context["script"],
            "verification": self.context["verification_results"],
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
            "has_verification": self.context["verification_results"] is not None
        }
    
    def reset(self):
        """Reset the pipeline for a new run."""
        self.state = PipelineState.IDLE
        self.context = {
            "topic": None,
            "research_results": None,
            "script": None,
            "verification_results": None,
            "errors": [],
            "started_at": None,
            "completed_at": None
        }
        print("🔄 Orchestrator: Pipeline reset")


# Standalone test
if __name__ == "__main__":
    class MockAPIManager:
        pass
    
    orchestrator = Orchestrator(MockAPIManager())
    results = orchestrator.run_pipeline("Artificial Intelligence in Healthcare", "educational")
    print(json.dumps(results, indent=2, default=str))