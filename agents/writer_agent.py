"""
Writer Agent - Converts research into a video script
"""
import json
from datetime import datetime


class WriterAgent:
    """Agent that writes video scripts based on research."""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.script = None
        
    def write_script(self, research_data: dict, style: str = "educational") -> dict:
        """
        Write a video script based on research results.
        
        Args:
            research_data: Output from ResearchAgent
            style: Script style (educational, storytelling, news, etc.)
            
        Returns:
            Dictionary with script and metadata
        """
        topic = research_data.get("topic", "Unknown Topic")
        print(f"✍️ Writer Agent: Writing script for '{topic}'")
        
        # Script structure
        script_data = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "style": style,
            "sections": [],
            "full_script": "",
            "word_count": 0,
            "estimated_duration_minutes": 0,
            "status": "draft"
        }
        
        # Section templates based on style
        if style == "educational":
            script_data["sections"] = [
                {"type": "intro", "content": "", "duration_sec": 10},
                {"type": "main_content", "content": "", "duration_sec": 0},
                {"type": "summary", "content": "", "duration_sec": 15}
            ]
        elif style == "news":
            script_data["sections"] = [
                {"type": "headline", "content": "", "duration_sec": 5},
                {"type": "story", "content": "", "duration_sec": 0},
                {"type": "closing", "content": "", "duration_sec": 10}
            ]
        elif style == "storytelling":
            script_data["sections"] = [
                {"type": "hook", "content": "", "duration_sec": 8},
                {"type": "narrative", "content": "", "duration_sec": 0},
                {"type": "conclusion", "content": "", "duration_sec": 15}
            ]
        
        print(f"✅ Writer Agent: Script drafted ({script_data['word_count']} words)")
        return script_data
    
    def generate_with_llm(self, research_context: str, style: str = "educational") -> dict:
        """
        Use LLM to generate a more sophisticated script.
        
        Args:
            research_context: Formatted context from ResearchAgent
            style: Script style
            
        Returns:
            Generated script
        """
        # This would call the LLM API through api_manager
        # For now, returns placeholder
        print(f"🤖 Writer Agent: Calling LLM for script generation...")
        
        # Placeholder - would be replaced with actual LLM call
        script = self.write_script({"topic": "Generated"}, style)
        script["full_script"] = "Script would be generated here via LLM API call."
        
        return script
    
    def format_for_urdu_engine(self, script_data: dict) -> str:
        """
        Format script for the UrduEngine scroll video.
        
        Args:
            script_data: Script dictionary
            
        Returns:
            Plain text ready for scrolling
        """
        if not script_data.get("full_script"):
            # Use section contents
            parts = []
            for section in script_data.get("sections", []):
                if section.get("content"):
                    parts.append(section["content"])
            return "\n\n".join(parts)
        
        return script_data["full_script"]
    
    def get_duration_estimate(self, script_data: dict) -> float:
        """Estimate video duration in minutes (150 words/min)."""
        word_count = script_data.get("word_count", 0)
        if word_count == 0:
            # Estimate from section durations
            total_sec = sum(s.get("duration_sec", 0) for s in script_data.get("sections", []))
            return total_sec / 60
        return word_count / 150


# Standalone test
if __name__ == "__main__":
    class MockAPIManager:
        pass
    
    agent = WriterAgent(MockAPIManager())
    research = {"topic": "AI in Healthcare", "sources": [], "key_findings": ["AI helps diagnose diseases"]}
    script = agent.write_script(research, "educational")
    print(json.dumps(script, indent=2, default=str))