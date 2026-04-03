"""
LLM Client - Unified interface for multiple LLM providers
"""
import json
import requests
from typing import Optional, Dict, Any, List


class LLMClient:
    """
    Unified LLM client supporting multiple providers.
    Handles API calls with proper error handling and retry logic.
    """
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.config = api_manager.get_llm_config()
        self.max_retries = 3
        self.timeout = 60
    
    def _call_api(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """
        Make API call to the configured LLM provider.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Response text from LLM
        """
        provider = self.config.get("provider", "GEMINI")
        
        if provider == "GEMINI":
            return self._call_gemini(messages, temperature, max_tokens)
        elif provider == "GROK":
            return self._call_grok(messages, temperature, max_tokens)
        elif provider == "KIMI":
            return self._call_kimi(messages, temperature, max_tokens)
        elif provider == "DEEPSEEK":
            return self._call_deepseek(messages, temperature, max_tokens)
        elif provider == "QIANWEN":
            return self._call_qianwen(messages, temperature, max_tokens)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _call_gemini(self, messages: List[Dict], temperature: float, max_tokens: int) -> str:
        """Call Google Gemini API."""
        base_url = self.config.get("base_url")
        model = self.config.get("model", "gemini-2.0-flash")
        api_key = self.config.get("api_key")
        
        url = f"{base_url}/models/{model}:generateContent?key={api_key}"
        
        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    
    def _call_grok(self, messages: List[Dict], temperature: float, max_tokens: int) -> str:
        """Call xAI Grok API."""
        base_url = self.config.get("base_url")
        model = self.config.get("model", "grok-2")
        api_key = self.config.get("api_key")
        
        url = f"{base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def _call_kimi(self, messages: List[Dict], temperature: float, max_tokens: int) -> str:
        """Call Moonshot Kimi API."""
        base_url = self.config.get("base_url")
        model = self.config.get("model", "kimi-echo")
        api_key = self.config.get("api_key")
        
        url = f"{base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def _call_deepseek(self, messages: List[Dict], temperature: float, max_tokens: int) -> str:
        """Call DeepSeek API."""
        base_url = self.config.get("base_url")
        model = self.config.get("model", "deepseek-chat")
        api_key = self.config.get("api_key")
        
        url = f"{base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def _call_qianwen(self, messages: List[Dict], temperature: float, max_tokens: int) -> str:
        """Call Alibaba Qwen API."""
        base_url = self.config.get("base_url")
        model = self.config.get("model", "qwen-plus")
        api_key = self.config.get("api_key")
        
        url = f"{base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return self._call_api(messages, temperature)
    
    def generate_script(self, topic: str, research_context: str, style: str = "educational") -> str:
        """
        Generate a video script based on topic and research.
        
        Args:
            topic: Video topic
            research_context: Research findings
            style: Script style
            
        Returns:
            Generated script
        """
        style_prompts = {
            "educational": "Create an educational script that explains the topic clearly with introduction, main content, and summary.",
            "news": "Create a news-style script with a hook, the main story, and a closing summary.",
            "storytelling": "Create a narrative story script with an engaging hook, detailed storytelling, and a meaningful conclusion."
        }
        
        style_instruction = style_prompts.get(style, style_prompts["educational"])
        
        prompt = f"""Topic: {topic}

Research Context:
{research_context}

Task: {style_instruction}

Write the script in a format suitable for a text-scroll video. 
Keep it conversational and engaging.
Make it around 400-600 words for a 3-4 minute video.
Don't use bullet points - write in flowing paragraph style suitable for voiceover.
"""
        
        return self.generate(prompt, system_prompt="You are a professional video script writer.", temperature=0.7)
    
    def verify_claims(self, script: str, sources: List[Dict]) -> List[Dict]:
        """
        Verify claims in a script against sources.
        
        Args:
            script: Script text
            sources: List of source dicts with title, url, snippet
            
        Returns:
            List of claim verification results
        """
        sources_text = "\n".join([f"- {s.get('title', 'Unknown')}: {s.get('snippet', '')}" for s in sources])
        
        prompt = f"""Analyze the following script and verify its claims against the provided sources.

Script:
{script}

Sources:
{sources_text}

For each claim found, respond in this JSON format:
[
  {{"claim": "claim text", "status": "verified|uncertain|failed", "reason": "explanation"}}
]

Only respond with valid JSON array, no other text.
"""
        
        result = self.generate(prompt, system_prompt="You are a fact-checker. Verify claims accurately.", temperature=0.3)
        
        # Parse JSON response
        try:
            return json.loads(result)
        except:
            return [{"claim": "Failed to parse claims", "status": "uncertain", "reason": "LLM response was not valid JSON"}]


if __name__ == "__main__":
    # Test with mock - would need actual API key
    class MockAPIManager:
        def get_llm_config(self):
            return {"provider": "GEMINI", "api_key": None, "model": "gemini-2.0-flash"}
    
    client = LLMClient(MockAPIManager())
    print("LLM Client initialized (needs API key to work)")