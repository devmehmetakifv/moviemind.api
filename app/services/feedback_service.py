"""Feedback service for data error reporting."""

from typing import Optional
from supabase import Client

from app.schemas import Feedback, FeedbackCreate


class FeedbackService:
    """Service for feedback operations."""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def create_feedback(
        self,
        feedback: FeedbackCreate,
        user_id: Optional[str] = None
    ) -> Optional[Feedback]:
        """Create a new feedback entry for data error reporting."""
        data = {
            "movie_id": feedback.movie_id,
            "field_name": feedback.field_name,
            "reported_issue": feedback.reported_issue
        }
        
        if user_id:
            data["user_id"] = user_id
        
        result = self.db.table("feedback").insert(data).execute()
        
        if result.data:
            return Feedback(**result.data[0])
        return None
    
    async def get_feedback_for_movie(self, movie_id: int) -> list[Feedback]:
        """Get all feedback entries for a movie."""
        result = self.db.table("feedback") \
            .select("*") \
            .eq("movie_id", movie_id) \
            .order("created_at", desc=True) \
            .execute()
        
        return [Feedback(**item) for item in result.data]
