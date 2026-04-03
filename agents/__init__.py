"""
Agents Package - Multi-agent system for video creation pipeline
v2.0 - Graph-based State Machine Architecture
"""

from .research_agent import ResearchAgent
from .writer_agent import WriterAgent
from .fact_checker_agent import FactCheckerAgent
from .audio_agent import AudioAgent
from .video_agent import VideoAgent
from .publisher_agent import PublisherAgent, Platform, PublishStatus
from .orchestrator import Orchestrator, PipelineState
from .llm_client import LLMClient

__all__ = [
    "ResearchAgent",
    "WriterAgent", 
    "FactCheckerAgent",
    "AudioAgent",
    "VideoAgent",
    "PublisherAgent",
    "Platform",
    "PublishStatus",
    "Orchestrator",
    "PipelineState",
    "LLMClient"
]

# Agent role mapping
AGENT_ROLES = {
    "scout": "ResearchAgent",       # Searches and gathers information
    "verifier": "FactCheckerAgent", # Verifies claims with self-correction
    "scribe": "WriterAgent",        # Converts research to script
    "artisan": "AudioAgent + VideoAgent",  # Audio and video generation
    "publisher": "PublisherAgent"  # Publishes to platforms
}