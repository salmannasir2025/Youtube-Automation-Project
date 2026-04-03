# OSCF Architecture - Core Logic Explained

## Overview

The **OSCF (Open Source Content Factory)** is a multi-agent video creation pipeline. It automates the entire process from topic research to YouTube publishing.

```
Topic Input → Research → Write Script → Fact-Check → Audio → Video → Publish
```

---

## System Architecture

### High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR                             │
│                    (Pipeline Coordinator)                       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼
   ┌─────────┐   ┌─────────┐   ┌──────────┐   ┌─────────┐
   │Research │   │ Writer  │   │Fact-Check│   │  Audio  │
   │ Agent   │──▶│ Agent   │──▶│  Agent   │   │  Agent  │
   └─────────┘   └─────────┘   └──────────┘   └─────────┘
                                                │
                                                ▼
                                             ┌─────────┐
                                             │  Video  │
                                             │  Agent  │
                                             └─────────┘
                                                │
                                                ▼
                                             ┌─────────┐
                                             │Publisher│
                                             │  Agent  │
                                             └─────────┘
```

### Component Responsibilities

| Component | Role | Key Methods |
|-----------|------|-------------|
| **Governor** | Hardware profiling, encoder selection | `get_ffmpeg_params()` |
| **APIManager** | API key management, LLM failover | `load_keys()`, `get_active_brain()` |
| **UrduEngine** | Scroll video rendering | `create_scroll_video()` |
| **Orchestrator** | Pipeline coordination, state management | `run_pipeline()` |
| **ResearchAgent** | Web search, source gathering | `search()`, `add_source()` |
| **WriterAgent** | Script generation | `write_script()`, `generate_with_llm()` |
| **FactCheckerAgent** | Claim verification | `check_claims()`, `verify_with_search()` |
| **AudioAgent** | TTS, audio cleanup | `generate_voice()`, `cleanup_audio()` |
| **VideoAgent** | Video rendering wrapper | `render_scroll_video()` |
| **PublisherAgent** | Platform publishing | `publish()`, `add_platform()` |

---

## Core Logic

### 1. Pipeline State Machine (Orchestrator)

The Orchestrator manages pipeline execution through states:

```python
class PipelineState(Enum):
    IDLE = "idle"
    RESEARCHING = "researching"
    WRITING = "writing"
    FACT_CHECKING = "fact_checking"
    COMPLETED = "completed"
    FAILED = "failed"
```

**Flow:**
1. `run_pipeline(topic)` called
2. State → RESEARCHING → run ResearchAgent
3. State → WRITING → pass research to WriterAgent
4. State → FACT_CHECKING → verify script claims
5. State → COMPLETED or FAILED

### 2. Agent Communication

Agents communicate via **shared context** (not direct messaging):

```python
self.context = {
    "topic": None,
    "research_results": None,   # From ResearchAgent
    "script": None,             # From WriterAgent
    "verification_results": None, # From FactCheckerAgent
    "errors": [],
    "started_at": None,
    "completed_at": None
}
```

**Data Flow:**
```
ResearchAgent.search() → context["research_results"]
                                       ↓
WriterAgent.write_script(research_data) → context["script"]
                                               ↓
FactCheckerAgent.check_claims(script, research) → context["verification_results"]
```

### 3. Hardware-Aware Rendering (Governor)

The Governor detects hardware and selects optimal encoding:

```python
def _determine_profile(self):
    if self.cpu_count <= 2:
        return "LEGACY_INTEL"  # MacBook Pro 9,2
    return "PERFORMANCE"

def get_ffmpeg_params(self):
    if self.os_type == "Darwin" and self.profile == "LEGACY_INTEL":
        return ["-c:v", "h264_videotoolbox", "-b:v", "2000k", "-preset", "fast"]
    return ["-c:v", "libx264", "-preset", "ultrafast"]
```

### 4. API Failover (APIManager)

Manages multiple LLM providers with automatic failover:

```python
def get_active_brain(self):
    # Try Gemini first, fall back to Grok
    return self.keys["GEMINI"] or self.keys["GROK"]
```

### 5. Script Styles (WriterAgent)

Three video script formats supported:

| Style | Sections | Use Case |
|-------|----------|----------|
| `educational` | intro, main_content, summary | Tutorials, explainers |
| `news` | headline, story, closing | Current events, reports |
| `storytelling` | hook, narrative, conclusion | Stories, narratives |

### 6. Claim Verification (FactCheckerAgent)

Claims are verified against sources:

```python
def check_claims(self, script_data, research_data):
    # Extract claims from script (via LLM)
    # Cross-check against research["sources"]
    # Return: verified / uncertain / failed
```

### 7. Platform Publishing (PublisherAgent)

Multi-platform support with scheduling:

```python
def publish(video_path, title, description, 
            platforms=[Platform.YOUTUBE], 
            schedule_time=None):
    # Upload to each platform
    # Return video URLs and IDs
```

---

## Data Structures

### Research Results
```python
{
    "topic": "AI in Healthcare",
    "timestamp": "2026-04-03T20:00:00",
    "sources": [{"title": "...", "url": "...", "snippet": "..."}],
    "key_findings": ["Finding 1", "Finding 2"],
    "summary": "...",
    "status": "completed"
}
```

### Script Data
```python
{
    "topic": "AI in Healthcare",
    "style": "educational",
    "sections": [
        {"type": "intro", "content": "...", "duration_sec": 10},
        {"type": "main_content", "content": "...", "duration_sec": 300},
        {"type": "summary", "content": "...", "duration_sec": 15}
    ],
    "full_script": "...",
    "word_count": 450,
    "estimated_duration_minutes": 3.0,
    "status": "draft"
}
```

### Verification Results
```python
{
    "topic": "AI in Healthcare",
    "claims_checked": 5,
    "verified_claims": [{"claim": "...", "source": "...", "confidence": 0.9}],
    "uncertain_claims": [{"claim": "...", "reason": "..."}],
    "failed_claims": [],
    "overall_status": "passed",  # passed / warning / failed
    "recommendations": []
}
```

---

## Configuration

### Environment Variables (.env)
```
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.provider.com/v1
LLM_MODEL_NAME=gpt-4
YOUTUBE_API_KEY=your_youtube_key
```

### Agent Configuration
Each agent can be configured via `configure()` method:
```python
audio_agent.configure(voice_id="custom", speed=1.0)
video_agent.set_resolution(1080, 1920)  # Vertical video
publisher_agent.add_platform(Platform.YOUTUBE, credentials)
```

---

## Extension Points

### Adding New Agents
1. Create agent class in `agents/` directory
2. Import in `agents/__init__.py`
3. Initialize in Orchestrator `__init__`
4. Add to pipeline in `run_pipeline()`

### Adding New Platforms
In `publisher_agent.py`:
```python
elif platform == Platform.NEW_PLATFORM:
    result = self._publish_new_platform(...)
```

### Adding Script Styles
In `writer_agent.py`:
```python
elif style == "my_style":
    script_data["sections"] = [...]
```

---

## File Structure

```
Youtube-Automation-Project/
├── agents/                  # Multi-agent system
│   ├── __init__.py
│   ├── research_agent.py
│   ├── writer_agent.py
│   ├── fact_checker_agent.py
│   ├── audio_agent.py
│   ├── video_agent.py
│   ├── publisher_agent.py
│   └── orchestrator.py
├── governor.py            # Hardware profiling
├── urdu_engine.py         # Video rendering
├── api_manager.py         # API key management
├── main.py                # Entry point
├── requirements.txt       # Dependencies
└── ARCHITECTURE.md        # This file
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `psutil` | Hardware detection |
| `moviepy` | Video rendering |
| `google-generativeai` | Gemini LLM |
| `cryptography` | Key encryption |
| `python-dotenv` | Environment variables |

---

*Last Updated: 2026-04-03 (Session 4)*
---

## LLM Integration

### Supported Providers

| Provider | Model | API Base | Free Tier |
|----------|-------|----------|-----------|
| Google Gemini | gemini-2.0-flash | `generativelanguage.googleapis.com` | ✅ |
| xAI Grok | grok-2 | `api.x.ai/v1` | ✅ |
| Moonshot Kimi | kimi-echo | `api.moonshot.cn/v1` | ✅ |
| DeepSeek | deepseek-chat | `api.deepseek.com/v1` | ✅ |
| Alibaba Qwen | qwen-plus | `dashscope.aliyuncs.com` | ✅ |

### Priority Order
```
Gemini → Grok → Kimi → DeepSeek → Qwen
```

### LLM Client Usage
```python
from agents import LLMClient

client = LLMClient(api_manager)
script = client.generate_script(topic, research_context, style)
verification = client.verify_claims(script_text, sources)
```

---

## Pipeline Execution

### Full Pipeline (6 Steps)
```bash
python main.py "Your topic" --style educational --publish
```

### Steps:
1. **Research** - Search web, gather sources
2. **Write** - Generate script with LLM
3. **Fact-Check** - Verify claims
4. **Audio** - Generate voice (ElevenLabs/gTTS)
5. **Video** - Render scroll video
6. **Publish** - Upload to YouTube

### Output
- `output/audio_*.mp3` - Generated voice
- `output/video_*.mp4` - Final video

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ❌ | Google Gemini API |
| `GROK_API_KEY` | ❌ | xAI Grok API |
| `KIMI_API_KEY` | ❌ | Moonshot Kimi API |
| `DEEPSEEK_API_KEY` | ❌ | DeepSeek API |
| `QIANWEN_API_KEY` | ❌ | Alibaba Qwen API |
| `BRAVE_API_KEY` | ❌ | Brave Search API |
| `ELEVENLABS_API_KEY` | ❌ | ElevenLabs TTS |
| `YOUTUBE_API_KEY` | ❌ | YouTube Data API |

*Last Updated: 2026-04-03 (Session 7)*
