"""User preferences service for favorites and not-interested."""

from typing import Optional
from supabase import Client

from app.schemas import (
    Favorite, FavoriteList, Movie,
    NotInterested, NotInterestedList
)


class PreferenceService:
    """Service for user preference operations."""
    
    def __init__(self, db: Client):
        self.db = db
    
    # Favorites
    async def add_favorite(self, user_id: str, movie_id: int) -> Optional[Favorite]:
        """Add a movie to user's favorites."""
        # Check if already exists
        existing = self.db.table("favorites") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("movie_id", movie_id) \
            .execute()
        
        if existing.data:
            return Favorite(**existing.data[0])
        
        # Insert new favorite
        result = self.db.table("favorites").insert({
            "user_id": user_id,
            "movie_id": movie_id
        }).execute()
        
        if result.data:
            return Favorite(**result.data[0])
        return None
    
    async def remove_favorite(self, user_id: str, movie_id: int) -> bool:
        """Remove a movie from user's favorites."""
        result = self.db.table("favorites") \
            .delete() \
            .eq("user_id", user_id) \
            .eq("movie_id", movie_id) \
            .execute()
        
        return True
    
    async def get_favorites(self, user_id: str) -> FavoriteList:
        """Get all favorites for a user with movie details."""
        result = self.db.table("favorites") \
            .select("*, movies(*)") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .execute()
        
        favorites = []
        for item in result.data:
            movie_data = item.pop("movies", None)
            fav = Favorite(**item)
            if movie_data:
                fav.movie = Movie(**movie_data)
            favorites.append(fav)
        
        return FavoriteList(favorites=favorites, total=len(favorites))
    
    async def get_favorite_movie_ids(self, user_id: str) -> list[int]:
        """Get list of favorite movie IDs for a user."""
        result = self.db.table("favorites") \
            .select("movie_id") \
            .eq("user_id", user_id) \
            .execute()
        
        return [item["movie_id"] for item in result.data]
    
    async def is_favorite(self, user_id: str, movie_id: int) -> bool:
        """Check if a movie is in user's favorites."""
        result = self.db.table("favorites") \
            .select("id") \
            .eq("user_id", user_id) \
            .eq("movie_id", movie_id) \
            .execute()
        
        return len(result.data) > 0
    
    # Not Interested
    async def add_not_interested(self, user_id: str, movie_id: int) -> Optional[NotInterested]:
        """Mark a movie as not interested."""
        # Check if already exists
        existing = self.db.table("not_interested") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("movie_id", movie_id) \
            .execute()
        
        if existing.data:
            return NotInterested(**existing.data[0])
        
        # Insert new entry
        result = self.db.table("not_interested").insert({
            "user_id": user_id,
            "movie_id": movie_id
        }).execute()
        
        if result.data:
            return NotInterested(**result.data[0])
        return None
    
    async def remove_not_interested(self, user_id: str, movie_id: int) -> bool:
        """Remove a movie from not-interested list."""
        result = self.db.table("not_interested") \
            .delete() \
            .eq("user_id", user_id) \
            .eq("movie_id", movie_id) \
            .execute()
        
        return True
    
    async def get_not_interested(self, user_id: str) -> NotInterestedList:
        """Get all not-interested movies for a user."""
        result = self.db.table("not_interested") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .execute()
        
        items = [NotInterested(**item) for item in result.data]
        return NotInterestedList(items=items, total=len(items))
    
    async def get_not_interested_ids(self, user_id: str) -> list[int]:
        """Get list of not-interested movie IDs for a user."""
        result = self.db.table("not_interested") \
            .select("movie_id") \
            .eq("user_id", user_id) \
            .execute()
        
        return [item["movie_id"] for item in result.data]
