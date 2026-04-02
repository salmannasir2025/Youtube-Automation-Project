import os
import psutil
import platform

class Governor:
    """
    The Governor Module manages system resources and hardware acceleration profiles.
    Specifically tuned for:
    - Primary: MacBook Pro 9,2 (Dual-Core i5, 16GB RAM, macOS)
    - Secondary: i7 Linux Laptop
    """
    
    def __init__(self):
        self.cores = psutil.cpu_count(logical=False)
        self.logical_cores = psutil.cpu_count(logical=True)
        self.system = platform.system()
        self.machine = platform.machine()
        self.profile = self._determine_profile()
        
    def _determine_profile(self):
        """
        Determines the hardware profile based on CPU cores and OS.
        """
        if self.cores < 4:
            return "LEGACY_INTEL"
        return "STANDARD_COMPUTE"

    def get_ffmpeg_params(self):
        """
        Returns the appropriate FFmpeg video encoder and parameters based on the profile.
        """
        if self.profile == "LEGACY_INTEL":
            if self.system == "Darwin":
                # macOS hardware acceleration for H.264
                return {
                    "vcodec": "h264_videotoolbox",
                    "crf": None, # Videotoolbox uses different rate control
                    "bitrate": "4000k",
                    "preset": None
                }
            else:
                # Linux/Windows legacy Intel might use vaapi or just libx264
                return {
                    "vcodec": "libx264",
                    "crf": 23,
                    "preset": "veryfast"
                }
        
        # Default for Standard Compute (e.g., i7 Linux)
        return {
            "vcodec": "libx264",
            "crf": 18,
            "preset": "medium"
        }

    def status_report(self):
        """
        Prints a diagnostic report of the current system profile.
        """
        print(f"--- Youtube-Content Factory Governor ---")
        print(f"OS: {self.system} ({self.machine})")
        print(f"Cores: {self.cores} Physical / {self.logical_cores} Logical")
        print(f"Detected Profile: {self.profile}")
        params = self.get_ffmpeg_params()
        print(f"Recommended FFmpeg Encoder: {params['vcodec']}")
        print(f"----------------------------------------")

if __name__ == "__main__":
    gov = Governor()
    gov.status_report()
