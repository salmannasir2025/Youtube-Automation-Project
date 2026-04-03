"""
Fact-Checker Agent - Verifies claims and validates information
"""
import json
from datetime import datetime
from typing import List, Dict, Tuple
from .llm_client import LLMClient


class FactCheckerAgent:
    """Agent that verifies claims and checks facts."""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.llm_client = LLMClient(api_manager)
        self.findings = []
        
    def check_claims(self, script_data: dict, research_data: dict) -> dict:
        """
        Check all claims in a script against research sources.
        
        Args:
            script_data: Script from WriterAgent
            research_data: Research from ResearchAgent
            
        Returns:
            Dictionary with verification results
        """
        topic = script_data.get("topic", "Unknown")
        print(f"🔎 Fact-Checker Agent: Verifying claims for '{topic}'")
        
        script = script_data.get("full_script", "")
        sources = research_data.get("sources", [])
        
        results = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "claims_checked": 0,
            "verified_claims": [],
            "uncertain_claims": [],
            "failed_claims": [],
            "overall_status": "warning",
            "recommendations": []
        }
        
        # Use LLM to verify claims if available
        if self.api_manager.get_active_brain() and script and sources:
            try:
                verification_results = self.llm_client.verify_claims(script, sources)
                
                for vr in verification_results:
                    claim = vr.get("claim", "")
                    status = vr.get("status", "uncertain")
                    reason = vr.get("reason", "")
                    
                    results["claims_checked"] += 1
                    
                    if status == "verified":
                        results["verified_claims"].append({
                            "claim": claim,
                            "reason": reason
                        })
                    elif status == "failed":
                        results["failed_claims"].append({
                            "claim": claim,
                            "reason": reason
                        })
                    else:
                        results["uncertain_claims"].append({
                            "claim": claim,
                            "reason": reason
                        })
                        
            except Exception as e:
                print(f"⚠️ LLM verification failed: {e}")
                results["recommendations"].append("Manual review recommended due to verification error")
        
        # If no LLM, do basic check
        if results["claims_checked"] == 0:
            results["claims_checked"] = 1
            results["uncertain_claims"].append({
                "claim": "Script content verification",
                "reason": "No automated verification - relies on source quality"
            })
            results["recommendations"].append("Verify sources manually before publishing")
        
        # Determine overall status
        if len(results["failed_claims"]) > 0:
            results["overall_status"] = "failed"
        elif len(results["uncertain_claims"]) > len(results["verified_claims"]):
            results["overall_status"] = "warning"
        else:
            results["overall_status"] = "passed"
        
        print(f"✅ Fact-Checker: {results['claims_checked']} claims - {results['overall_status']}")
        return results
    
    def add_verified_claim(self, claim: str, source: str, confidence: float):
        """Add a verified claim manually."""
        self.findings.append({
            "claim": claim,
            "status": "verified",
            "source": source,
            "confidence": confidence
        })
        
    def add_uncertain_claim(self, claim: str, reason: str):
        """Add a claim that couldn't be verified."""
        self.findings.append({
            "claim": claim,
            "status": "uncertain",
            "reason": reason
        })
        
    def add_failed_claim(self, claim: str, reason: str):
        """Add a claim that failed verification."""
        self.findings.append({
            "claim": claim,
            "status": "failed",
            "reason": reason
        })
    
    def verify_with_search(self, claim: str) -> Tuple[bool, str]:
        """
        Verify a specific claim by searching the web.
        
        Args:
            claim: The claim to verify
            
        Returns:
            Tuple of (is_verified, explanation)
        """
        print(f"🔍 Fact-Checker: Verifying claim: '{claim[:50]}...'")
        
        # This would integrate with search API for verification
        # For now, returns uncertain
        return (False, "Manual verification recommended")
    
    def get_summary(self) -> str:
        """Get a summary of fact-checking results."""
        if not self.findings:
            return "No claims checked yet."
        
        verified = sum(1 for f in self.findings if f["status"] == "verified")
        uncertain = sum(1 for f in self.findings if f["status"] == "uncertain")
        failed = sum(1 for f in self.findings if f["status"] == "failed")
        
        return f"Verified: {verified} | Uncertain: {uncertain} | Failed: {failed}"
    
    def should_proceed(self, results: dict) -> bool:
        """
        Determine if the pipeline should proceed based on verification.
        
        Args:
            results: Output from check_claims
            
        Returns:
            True if safe to proceed
        """
        if results["overall_status"] == "failed":
            return False
        if results["overall_status"] == "warning":
            # Could proceed but with flag
            return True
        return True


# Standalone test
if __name__ == "__main__":
    class MockAPIManager:
        def get_active_brain(self):
            return None
        
        def get_llm_config(self):
            return {"provider": "GEMINI", "api_key": None}
    
    agent = FactCheckerAgent(MockAPIManager())
    script = {"topic": "AI Healthcare", "full_script": "AI helps diagnose diseases."}
    research = {"topic": "AI Healthcare", "sources": [{"title": "AI in Medicine", "url": "http://test.com", "snippet": "AI diagnostic tools"}]}
    results = agent.check_claims(script, research)
    print(f"Status: {results['overall_status']}")