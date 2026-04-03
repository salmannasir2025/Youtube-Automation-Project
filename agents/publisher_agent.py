"""
Publisher Agent - Handles video publishing to platforms
"""
import json
import os
import subprocess
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
import requests


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
        
        # YouTube config if available
        self.youtube_config = None
        if api_manager.has_key("YOUTUBE"):
            self.youtube_config = api_manager.get_youtube_config()
    
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
        print(f"   Title: {title[:50]}...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "video_path": video_path,
            "title": title,
            "description": description[:200] + "..." if len(description) > 200 else description,
            "platforms": {},
            "overall_status": "pending"
        }
        
        for platform in platforms:
            if platform.value not in self.platforms and platform != Platform.YOUTUBE:
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
            result = self._publish_youtube(video_path, title, description, tags, schedule_time)
        elif platform == Platform.TIKTOK:
            result = self._publish_tiktok(video_path, title, description, tags)
        elif platform == Platform.INSTAGRAM:
            result = self._publish_instagram(video_path, title, description)
        elif platform == Platform.TWITTER:
            result = self._publish_twitter(video_path, title, description)
            
        return result
    
    def _publish_youtube(self, video_path: str, title: str, description: str,
                         tags: List[str], schedule_time: Optional[datetime]) -> dict:
        """Publish to YouTube using Data API v3."""
        result = {
            "platform": "youtube",
            "status": "pending",
            "video_id": None,
            "url": None,
            "error": None
        }
        
        # Check if video file exists
        if not os.path.exists(video_path):
            result["status"] = "error"
            result["error"] = "Video file not found"
            return result
        
        # Check if youtube API available
        if not self.youtube_config or not self.youtube_config.get("api_key"):
            print("   → YouTube: No API key, saving metadata for manual upload")
            result["status"] = "pending_manual"
            result["metadata"] = {
                "title": title,
                "description": description,
                "tags": tags,
                "video_path": video_path
            }
            return result
        
        # Use YouTube API
        api_key = self.youtube_config["api_key"]
        
        try:
            # Step 1: Initialize upload
            upload_url = "https://www.googleapis.com/upload/youtube/v3/videos"
            params = {
                "part": "snippet,status",
                "uploadType": "resumable",
                "key": api_key
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": "22"  # People & Blogs
                },
                "status": {
                    "privacyStatus": "public" if not schedule_time else "private",
                    "selfDeclaredMadeForKids": False
                }
            }
            
            response = requests.post(upload_url, params=params, headers=headers, 
                                    json=body, timeout=30)
            
            if response.status_code == 401:
                # Token expired or invalid
                result["error"] = "YouTube API authentication failed"
                result["status"] = "error"
                return result
            
            if response.status_code != 200:
                result["error"] = f"API error: {response.status_code}"
                result["status"] = "error"
                return result
            
            # Get upload URL from headers
            upload_url = response.headers.get("Location")
            
            # Step 2: Upload video file
            with open(video_path, "rb") as f:
                video_data = f.read()
            
            headers = {"Content-Type": "video/*"}
            response = requests.put(upload_url, headers=headers, data=video_data, 
                                  timeout=300)
            
            if response.status_code == 200:
                result["status"] = "published"
                result["video_id"] = response.json().get("id")
                result["url"] = f"https://youtube.com/watch?v={result['video_id']}"
                print(f"   → YouTube: Published! {result['url']}")
            else:
                result["error"] = f"Upload failed: {response.status_code}"
                result["status"] = "error"
                
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"
            print(f"   → YouTube: Error - {e}")
        
        return result
    
    def _publish_tiktok(self, video_path: str, title: str, description: str, 
                       tags: List[str]) -> dict:
        """Publish to TikTok (requires TikTok API - placeholder)."""
        result = {
            "platform": "tiktok",
            "status": "pending",
            "video_id": None,
            "url": None,
            "error": "TikTok API not implemented - requires manual upload"
        }
        
        # Save metadata for manual upload
        metadata_file = video_path.replace(".mp4", "_tiktok_metadata.json")
        with open(metadata_file, "w") as f:
            json.dump({
                "title": title,
                "description": description,
                "tags": tags
            }, f, indent=2)
        
        print(f"   → TikTok: Saved metadata for manual upload")
        
        return result
    
    def _publish_instagram(self, video_path: str, title: str, 
                          description: str) -> dict:
        """Publish to Instagram (requires Instagram API - placeholder)."""
        result = {
            "platform": "instagram",
            "status": "pending",
            "video_id": None,
            "url": None,
            "error": "Instagram API not implemented - requires manual upload"
        }
        
        print(f"   → Instagram: Manual upload required")
        
        return result
    
    def _publish_twitter(self, video_path: str, title: str, 
                        description: str) -> dict:
        """Publish to Twitter/X (requires Twitter API - placeholder)."""
        result = {
            "platform": "twitter",
            "status": "pending",
            "video_id": None,
            "url": None,
            "error": "Twitter API not implemented - requires manual upload"
        }
        
        print(f"   → Twitter: Manual upload required")
        
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
        def has_key(self, provider):
            return provider == "YOUTUBE"
        
        def get_youtube_config(self):
            return {"api_key": None}
    
    agent = PublisherAgent(MockAPIManager())
    result = agent.publish("video.mp4", "Test Video", "Description", [Platform.YOUTUBE])
    print(f"Status: {result['overall_status']}")