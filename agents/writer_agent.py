"""
Writer Agent - Converts research into a video script
"""
import json
from datetime import datetime
from .llm_client import LLMClient


class WriterAgent:
    """Agent that writes video scripts based on research."""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.llm_client = LLMClient(api_manager)
        self.script = None
        
    def write_script(self, research_data: dict, style: str = "educational") -> dict:
        """
        Write a video script based on research results (with LLM).
        
        Args:
            research_data: Output from ResearchAgent
            style: Script style (educational, storytelling, news, etc.)
            
        Returns:
            Dictionary with script and metadata
        """
        topic = research_data.get("topic", "Unknown Topic")
        print(f"✍️ Writer Agent: Writing script for '{topic}'")
        
        # Build research context
        findings = research_data.get("key_findings", [])
        sources = research_data.get("sources", [])
        
        research_context = f"Topic: {topic}\n\n"
        if findings:
            research_context += "Key Findings:\n" + "\n".join([f"- {f}" for f in findings]) + "\n\n"
        if sources:
            research_context += "Sources:\n"
            for s in sources:
                research_context += f"- {s.get('title', 'Unknown')}: {s.get('url', '')}\n"
        
        # Try to generate with LLM
        try:
            if self.api_manager.get_active_brain():
                print("🤖 Writer Agent: Generating with LLM...")
                generated_script = self.llm_client.generate_script(topic, research_context, style)
            else:
                generated_script = self._generate_template(topic, style)
        except Exception as e:
            print(f"⚠️ LLM call failed: {e}, using template")
            generated_script = self._generate_template(topic, style)
        
        # Calculate word count
        word_count = len(generated_script.split())
        
        # Script structure
        script_data = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "style": style,
            "sections": [],
            "full_script": generated_script,
            "word_count": word_count,
            "estimated_duration_minutes": word_count / 150,  # ~150 words/min
            "status": "completed"
        }
        
        # Create sections
        if style == "educational":
            # Split script into intro, body, summary
            words = generated_script.split()
            intro_words = min(50, len(words) // 3)
            summary_words = min(50, len(words) // 3)
            
            script_data["sections"] = [
                {"type": "intro", "content": " ".join(words[:intro_words]), "duration_sec": int(intro_words / 2.5)},
                {"type": "main_content", "content": " ".join(words[intro_words:-summary_words]), "duration_sec": int((word_count - intro_words - summary_words) / 2.5)},
                {"type": "summary", "content": " ".join(words[-summary_words:]), "duration_sec": int(summary_words / 2.5)}
            ]
        elif style == "news":
            script_data["sections"] = [
                {"type": "headline", "content": generated_script[:100], "duration_sec": 5},
                {"type": "story", "content": generated_script[100:], "duration_sec": int(word_count / 2.5)},
                {"type": "closing", "content": "Thanks for watching.", "duration_sec": 3}
            ]
        elif style == "storytelling":
            script_data["sections"] = [
                {"type": "hook", "content": generated_script[:80], "duration_sec": 8},
                {"type": "narrative", "content": generated_script[80:], "duration_sec": int(word_count / 2.5)},
                {"type": "conclusion", "content": "The end.", "duration_sec": 5}
            ]
        
        self.script = script_data
        print(f"✅ Writer Agent: Script completed ({word_count} words, ~{script_data['estimated_duration_minutes']:.1f} min)")
        return script_data
    
    def _generate_template(self, topic: str, style: str) -> str:
        """Generate a template script when LLM is not available."""
        templates = {
            "educational": f"""Welcome to our video about {topic}!

In this video, we're going to explore the key aspects of {topic} and understand why it matters.

First, let's talk about what {topic} actually means and its importance in today's world.

{topic} has become increasingly relevant because it affects many areas of our lives. Whether we're talking about technology, daily routines, or future possibilities, understanding {topic} helps us make better decisions.

The main points to understand are the fundamental concepts, practical applications, and future implications of {topic}.

To sum up, {topic} represents an important development that continues to shape our understanding and opens new possibilities for the future.

Thanks for watching!""",
            "news": f"""Breaking News: {topic}

Today we're covering the latest developments in {topic} and what it means for everyone involved.

{topic} has been making headlines recently, with experts weighing in on its significance and potential impact.

Key details are emerging about how {topic} is affecting various sectors and what experts predict for the future.

We'll continue to follow this story and bring you updates as more information becomes available.

Stay tuned for more coverage on {topic} and other important news.""",
            "storytelling": f"""Have you ever wondered about {topic}? Let me tell you a story.

Once upon a time, people started paying attention to {topic} and what it meant for our world.

The journey of {topic} is filled with interesting developments, challenges, and breakthroughs.

Along the way, many people contributed to our understanding and shaped how we see {topic} today.

And now, we find ourselves in a new chapter of this ongoing story, where possibilities are still unfolding.

What happens next? Only time will tell. But one thing is certain - {topic} will continue to be part of our story.

The end... for now."""
        }
        return templates.get(style, templates["educational"])
    
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
        def get_active_brain(self):
            return None
        
        def get_llm_config(self):
            return {"provider": "GEMINI", "api_key": None}
    
    agent = WriterAgent(MockAPIManager())
    research = {"topic": "AI in Healthcare", "sources": [], "key_findings": ["AI helps diagnose diseases"]}
    script = agent.write_script(research, "educational")
    print(f"Script word count: {script['word_count']}")