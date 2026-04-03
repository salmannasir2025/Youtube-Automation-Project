"""
Publisher Agent - Handles video publishing to platforms
"""
import json
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum


class Platform(Enum):
    """Supported publishing platforms."""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"


class PublishStatus(Enum):
    """Publishing status states."""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"


class PublisherAgent:
    """Agent that publishes videos to social platforms."""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.platforms = {}  # Store platform credentials
        self.publish_history = []
        
    def add_platform(self, platform: Platform, credentials: dict):
        """
        Add platform credentials for publishing.
        
        Args:
            platform: Platform to add
            credentials: API credentials dict
        """
        self.platforms[platform.value] = {
            "credentials": credentials,
            "enabled": True
        }
        print(f"📤 Publisher Agent: Added {platform.value} platform")
    
    def publish(self, video_path: str, title: str, description: str, 
                platforms: List[Platform] = None, tags: List[str] = None,
                schedule_time: Optional[datetime] = None) -> dict:
        """
        Publish a video to specified platforms.
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            platforms: List of platforms to publish to
            tags: List of tags
            schedule_time: Optional scheduled publish time
            
        Returns:
            Dictionary with publish results
        """
        if platforms is None:
            platforms = [Platform.YOUTUBE]
            
        print(f"📤 Publisher Agent: Publishing to {[p.value for p in platforms]}")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "video_path": video_path,
            "title": title,
            "platforms": {},
            "overall_status": "pending"
        }
        
        for platform in platforms:
            if platform.value not in self.platforms:
                print(f"⚠️ Publisher Agent: {platform.value} not configured")
                continue
                
            result = self._publish_to_platform(
                platform, video_path, title, description, tags, schedule_time
            )
            results["platforms"][platform.value] = result
        
        # Determine overall status
        published = sum(1 for r in results["platforms"].values() 
                       if r["status"] == "published")
        total = len(results["platforms"])
        results["overall_status"] = "published" if published == total else "partial"
        
        self.publish_history.append(results)
        print(f"✅ Publisher Agent: Published to {published}/{total} platforms")
        
        return results
    
    def _publish_to_platform(self, platform: Platform, video_path: str,
                            title: str, description: str, tags: List[str],
                            schedule_time: Optional[datetime]) -> dict:
        """Publish to a specific platform (YouTube, TikTok, etc.)."""
        
        result = {
            "platform": platform.value,
            "status": "pending",
            "video_id": None,
            "url": None,
            "error": None
        }
        
        if platform == Platform.YOUTUBE:
            # YouTube API integration would go here
            # Using google-api-python-client
            print(f"   → YouTube: Would upload '{title[:30]}...'")
            result["status"] = "published"
            result["video_id"] = "mock_video_id"
            result["url"] = "https://youtube.com/watch?v=mock_id"
            
        elif platform == Platform.TIKTOK:
            print(f"   → TikTok: Would upload '{title[:30]}...'")
            result["status"] = "published"
            result["video_id"] = "mock_tiktok_id"
            result["url"] = "https://tiktok.com/@user/video/mock"
            
        elif platform == Platform.INSTAGRAM:
            print(f"   → Instagram: Would upload '{title[:30]}...'")
            result["status"] = "published"
            
        elif platform == Platform.TWITTER:
            print(f"   → Twitter: Would upload '{title[:30]}...'")
            result["status"] = "published"
            
        return result
    
    def get_publish_history(self) -> List[dict]:
        """Get history of published videos."""
        return self.publish_history
    
    def enable_platform(self, platform: Platform):
        """Enable a platform."""
        if platform.value in self.platforms:
            self.platforms[platform.value]["enabled"] = True
    
    def disable_platform(self, platform: Platform):
        """Disable a platform."""
        if platform.value in self.platforms:
            self.platforms[platform.value]["enabled"] = False


# Standalone test
if __name__ == "__main__":
    class MockAPIManager:
        pass
    
    agent = PublisherAgent(MockAPIManager())
    agent.add_platform(Platform.YOUTUBE, {"token": "mock_token"})
    result = agent.publish("video.mp4", "Test Video", "Description", [Platform.YOUTUBE])
    print(json.dumps(result, indent=2))