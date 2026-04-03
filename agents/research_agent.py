"""
Research Agent - Searches and gathers information on a topic
"""
import json
import os
from datetime import datetime


class ResearchAgent:
    """Agent that searches the web and gathers information on a given topic."""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.results = []
        
    def search(self, topic: str, max_results: int = 5) -> dict:
        """
        Main research entry point.
        
        Args:
            topic: The topic to research
            max_results: Maximum number of sources to gather
            
        Returns:
            Dictionary with research results and metadata
        """
        print(f"🔍 Research Agent: Starting research on '{topic}'")
        
        # This is where you'd integrate web search APIs
        # For now, returns structured format for the pipeline
        
        self.results = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "sources": [],  # Would be populated by actual search
            "key_findings": [],
            "summary": "",
            "status": "completed"
        }
        
        print(f"✅ Research Agent: Found {len(self.results['sources'])} sources")
        return self.results
    
    def add_source(self, title: str, url: str, snippet: str):
        """Add a source to the research results."""
        self.results["sources"].append({
            "title": title,
            "url": url,
            "snippet": snippet
        })
        
    def add_finding(self, finding: str):
        """Add a key finding to the research results."""
        self.results["key_findings"].append(finding)
    
    def get_context(self) -> str:
        """Get formatted context for the writer agent."""
        if not self.results["sources"]:
            return f"Topic: {self.results['topic']}\n\nNo sources found."
        
        context = f"Topic: {self.results['topic']}\n\n"
        context += "Key Findings:\n"
        for finding in self.results["key_findings"]:
            context += f"- {finding}\n"
        
        context += "\nSources:\n"
        for i, source in enumerate(self.results["sources"], 1):
            context += f"{i}. {source['title']} - {source['url']}\n"
            
        return context


# Standalone test
if __name__ == "__main__":
    # Mock API manager for testing
    class MockAPIManager:
        pass
    
    agent = ResearchAgent(MockAPIManager())
    result = agent.search("AI in healthcare")
    print(json.dumps(result, indent=2))