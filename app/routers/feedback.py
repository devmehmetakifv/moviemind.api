"""Feedback router for data error reporting."""

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.database import get_db
from app.dependencies import get_optional_user
from app.schemas import FeedbackCreate, Feedback, MessageResponse, UserInfo
from app.services.feedback_service import FeedbackService


router = APIRouter()


@router.post("", response_model=Feedback, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback: FeedbackCreate,
    current_user: UserInfo = Depends(get_optional_user),
    db: Client = Depends(get_db)
):
    """
    Submit data error feedback.
    
    - **movie_id**: The movie with the error
    - **field_name**: Which field has the error (e.g., "director", "year")
    - **reported_issue**: Description of the error
    
    Authentication is optional - anonymous feedback is allowed.
    """
    feedback_service = FeedbackService(db)
    user_id = current_user.id if current_user else None
    
    result = await feedback_service.create_feedback(feedback, user_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to submit feedback"
        )
    
    return result


@router.get("/movie/{movie_id}", response_model=list[Feedback])
async def get_movie_feedback(
    movie_id: int,
    db: Client = Depends(get_db)
):
    """Get all feedback for a specific movie."""
    feedback_service = FeedbackService(db)
    return await feedback_service.get_feedback_for_movie(movie_id)
