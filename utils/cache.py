import json
import os
from datetime import datetime
from typing import Dict, Optional
from utils.logger import Logger
import logging


class MusicCache:
    def __init__(self, cache_file: str = "music_cache.json"):
        """Initialize the cache manager with a specified cache file.

        Args:
            cache_file: Path to the JSON file that will store the cache
        """
        self.cache_file = cache_file
        self.cache: Dict[str, dict] = {}
        self.logger = Logger("Music Cache")

        # Load existing cache if it exists
        self._load_cache()

    def _load_cache(self) -> None:
        """Load the cache from disk if it exists."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    self.cache = json.load(f)
                self.logger.info(f"Loaded {len(self.cache)} entries from cache")
            else:
                self.logger.info("No existing cache file found")
        except Exception as e:
            self.logger.error(f"Error loading cache: {str(e)}")
            self.cache = {}  # Start with empty cache if loading fails

    def _save_cache(self) -> None:
        """Save the current cache to disk."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
            self.logger.info(f"Saved {len(self.cache)} entries to cache")
        except Exception as e:
            self.logger.error(f"Error saving cache: {str(e)}")

    def get(self, query: str) -> Optional[dict]:
        """Get a cached entry if it exists.

        Args:
            query: The search query or URL to look up

        Returns:
            Dict containing audio URL and metadata if found, None otherwise
        """
        return self.cache.get(query.lower())

    def update(self, query: str, data: dict) -> None:
        """Update the cache with new data and save to disk.

        Args:
            query: The search query or URL to cache
            data: Dictionary containing audio URL and metadata
        """
        # Add timestamp to track when this entry was cached
        data["cached_at"] = datetime.now().isoformat()

        # Update memory cache
        self.cache[query.lower()] = data

        # Save to disk
        self._save_cache()

    def clear(self) -> None:
        """Clear the entire cache from memory and disk."""
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        self.logger.info("Cache cleared")

    def get_stats(self) -> dict:
        """Get basic statistics about the cache."""
        return {
            "total_entries": len(self.cache),
            "cache_size_kb": (
                os.path.getsize(self.cache_file) / 1024
                if os.path.exists(self.cache_file)
                else 0
            ),
            "oldest_entry": min(
                (entry["cached_at"] for entry in self.cache.values()), default=None
            ),
            "newest_entry": max(
                (entry["cached_at"] for entry in self.cache.values()), default=None
            ),
        }
