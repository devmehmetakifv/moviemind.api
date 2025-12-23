"""User preferences router for favorites and not-interested."""

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.database import get_supabase_admin_client
from app.dependencies import get_current_user
from app.schemas import (
    FavoriteCreate, Favorite, FavoriteList,
    NotInterestedCreate, NotInterested, NotInterestedList,
    MessageResponse, UserInfo
)
from app.services.preference_service import PreferenceService


router = APIRouter()


# ============ FAVORITES ============

@router.get("/favorites", response_model=FavoriteList)
async def get_favorites(
    current_user: UserInfo = Depends(get_current_user),
    db: Client = Depends(get_supabase_admin_client)
):
    """Get all favorite movies for the current user."""
    pref_service = PreferenceService(db)
    return await pref_service.get_favorites(current_user.id)


@router.post("/favorites", response_model=Favorite, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    data: FavoriteCreate,
    current_user: UserInfo = Depends(get_current_user),
    db: Client = Depends(get_supabase_admin_client)
):
    """Add a movie to favorites."""
    pref_service = PreferenceService(db)
    result = await pref_service.add_favorite(current_user.id, data.movie_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add favorite"
        )
    
    return result


@router.delete("/favorites/{movie_id}", response_model=MessageResponse)
async def remove_favorite(
    movie_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: Client = Depends(get_supabase_admin_client)
):
    """Remove a movie from favorites."""
    pref_service = PreferenceService(db)
    await pref_service.remove_favorite(current_user.id, movie_id)
    return MessageResponse(message="Favorite removed successfully")


@router.get("/favorites/{movie_id}/check")
async def check_favorite(
    movie_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: Client = Depends(get_supabase_admin_client)
):
    """Check if a movie is in user's favorites."""
    pref_service = PreferenceService(db)
    is_fav = await pref_service.is_favorite(current_user.id, movie_id)
    return {"is_favorite": is_fav}


# ============ NOT INTERESTED ============

@router.get("/not-interested", response_model=NotInterestedList)
async def get_not_interested(
    current_user: UserInfo = Depends(get_current_user),
    db: Client = Depends(get_supabase_admin_client)
):
    """Get all not-interested movies for the current user."""
    pref_service = PreferenceService(db)
    return await pref_service.get_not_interested(current_user.id)


@router.post("/not-interested", response_model=NotInterested, status_code=status.HTTP_201_CREATED)
async def add_not_interested(
    data: NotInterestedCreate,
    current_user: UserInfo = Depends(get_current_user),
    db: Client = Depends(get_supabase_admin_client)
):
    """Mark a movie as not interested."""
    pref_service = PreferenceService(db)
    result = await pref_service.add_not_interested(current_user.id, data.movie_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to mark as not interested"
        )
    
    return result


@router.delete("/not-interested/{movie_id}", response_model=MessageResponse)
async def remove_not_interested(
    movie_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: Client = Depends(get_supabase_admin_client)
):
    """Remove a movie from not-interested list."""
    pref_service = PreferenceService(db)
    await pref_service.remove_not_interested(current_user.id, movie_id)
    return MessageResponse(message="Removed from not interested")
