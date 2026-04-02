# Youtube-Content Factory (OSCF) Progress Log

## Project Overview
- **Primary Dev Machine:** MacBook Pro 9,2 (Dual-Core i5, 16GB RAM, macOS)
- **Secondary Render Machine:** i7 Linux Laptop
- **Core Goal:** Automated video content generation with hardware-aware profiling.

---

## Session History

### Session 1: 2026-04-02
**Focus:** Project Initialization & Hardware Governor

#### Accomplishments:
- **Git Integration:** Initialized git repository and configured `.gitignore` to protect sensitive files (`.env`, `config.json`).
- **Dependency Management:** Created `requirements.txt` with core libraries: `psutil`, `google-generativeai`, `cryptography`, `moviepy`, `Pillow`.
- **Governor Module:** Implemented `governor.py` for automated hardware profiling.
    - Detects CPU cores and OS.
    - Sets `LEGACY_INTEL` profile for < 4 cores (MacBook Pro 9,2).
    - Configures FFmpeg to use `h264_videotoolbox` for macOS hardware acceleration.

#### Technical Decisions:
- **Encoder:** Chose `h264_videotoolbox` for the legacy MacBook to offload H.264 encoding from the dual-core CPU.
- **Security:** Pre-configured `.gitignore` for local encrypted environment management.

#### Next Steps:
- [ ] Implement API Manager (GUI-based settings handler).
- [ ] Implement Urdu Engine (Text-scroller with Jameel Noori Nastaleeq).
- [ ] Develop Scroll Speed logic: `Scroll Speed = (Total Text Height / Audio File Duration)`.
