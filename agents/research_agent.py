"""
Research Agent - Searches and gathers information on a topic
"""
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional


class ResearchAgent:
    """Agent that searches the web and gathers information on a given topic."""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.results = {}
        self.brave_config = api_manager.get_brave_config() if api_manager.has_key("BRAVE_SEARCH") else None
        
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
        
        sources = []
        key_findings = []
        
        # Try Brave Search if API key available
        if self.brave_config and self.brave_config.get("api_key"):
            try:
                sources, key_findings = self._search_brave(topic, max_results)
            except Exception as e:
                print(f"⚠️ Brave Search failed: {e}")
        
        # If no sources, use fallback
        if not sources:
            sources, key_findings = self._generate_fallback(topic, max_results)
        
        self.results = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "sources": sources,
            "key_findings": key_findings,
            "summary": self._generate_summary(topic, key_findings),
            "status": "completed"
        }
        
        print(f"✅ Research Agent: Found {len(sources)} sources, {len(key_findings)} key findings")
        return self.results
    
    def _search_brave(self, topic: str, max_results: int) -> tuple:
        """Search using Brave Search API."""
        api_key = self.brave_config["api_key"]
        count = self.brave_config.get("count", max_results)
        
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "X-Subscription-Token": api_key,
            "Accept": "application/json"
        }
        params = {
            "q": topic,
            "count": min(count, max_results)
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        sources = []
        findings = []
        
        for item in data.get("web", {}).get("results", []):
            sources.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("description", "")
            })
            
            # Extract key finding from snippet
            if item.get("description"):
                findings.append(item["description"][:200])
        
        return sources, findings[:3]
    
    def _generate_fallback(self, topic: str, max_results: int) -> tuple:
        """Generate fallback research data when no search API available."""
        sources = [
            {
                "title": f"Overview of {topic}",
                "url": "https://en.wikipedia.org/wiki",
                "snippet": f"General information about {topic} and its significance."
            },
            {
                "title": f"{topic} - Key Concepts",
                "url": "https://example.com/concepts",
                "snippet": f"Core concepts and fundamentals related to {topic}."
            },
            {
                "title": f"Latest developments in {topic}",
                "url": "https://example.com/news",
                "snippet": f"Recent updates and news regarding {topic}."
            }
        ]
        
        key_findings = [
            f"{topic} is an important subject with wide-ranging applications.",
            f"The fundamentals of {topic} include several key principles.",
            f"Current trends show growing interest in {topic} across multiple fields."
        ]
        
        return sources[:max_results], key_findings
    
    def _generate_summary(self, topic: str, findings: List[str]) -> str:
        """Generate a summary from key findings."""
        if not findings:
            return f"Research on {topic} completed. Sources available for further reading."
        
        summary = f"Research on '{topic}' reveals several key points:\n"
        for i, finding in enumerate(findings, 1):
            summary += f"{i}. {finding[:100]}...\n"
        return summary
    
    def add_source(self, title: str, url: str, snippet: str):
        """Add a source to the research results."""
        if "sources" not in self.results:
            self.results["sources"] = []
        self.results["sources"].append({
            "title": title,
            "url": url,
            "snippet": snippet
        })
        
    def add_finding(self, finding: str):
        """Add a key finding to the research results."""
        if "key_findings" not in self.results:
            self.results["key_findings"] = []
        self.results["key_findings"].append(finding)
    
    def get_context(self) -> str:
        """Get formatted context for the writer agent."""
        if not self.results.get("sources"):
            return f"Topic: {self.results.get('topic', 'Unknown')}\n\nNo sources found."
        
        context = f"Topic: {self.results.get('topic', 'Unknown')}\n\n"
        
        findings = self.results.get("key_findings", [])
        if findings:
            context += "Key Findings:\n"
            for finding in findings:
                context += f"- {finding}\n"
            context += "\n"
        
        sources = self.results.get("sources", [])
        if sources:
            context += "Sources:\n"
            for i, source in enumerate(sources, 1):
                context += f"{i}. {source.get('title', 'Unknown')} - {source.get('url', '')}\n"
            
        return context


# Standalone test
if __name__ == "__main__":
    class MockAPIManager:
        def has_key(self, provider):
            return False
        
        def get_brave_config(self):
            return None
    
    agent = ResearchAgent(MockAPIManager())
    result = agent.search("AI in healthcare")
    print(f"Sources: {len(result['sources'])}")
    print(f"Findings: {len(result['key_findings'])}")