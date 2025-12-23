"""Movies router with all movie-related endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client

from app.database import get_db
from app.dependencies import get_optional_user
from app.schemas import (
    MovieList, MovieDetail, RecommendationList, UserInfo
)
from app.services.movie_service import MovieService
from app.services.preference_service import PreferenceService


router = APIRouter()


@router.get("", response_model=MovieList)
async def get_movies(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    genres: Optional[str] = Query(None, description="Comma-separated genres"),
    decade: Optional[str] = Query(None, description="Decade filter (e.g., '1990s')"),
    min_rating: Optional[float] = Query(None, ge=0, le=10, description="Minimum rating"),
    max_rating: Optional[float] = Query(None, ge=0, le=10, description="Maximum rating"),
    director: Optional[str] = Query(None, description="Director name search"),
    sort_by: str = Query("title", pattern="^(title|year|rating)$", description="Sort field"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(None, description="Search in title or director"),
    current_user: Optional[UserInfo] = Depends(get_optional_user),
    db: Client = Depends(get_db)
):
    """
    Get paginated list of movies with optional filters.
    
    - **genres**: Filter by genre(s), comma-separated
    - **decade**: Filter by decade (e.g., "1990s")
    - **min_rating/max_rating**: Filter by rating range
    - **director**: Search by director name
    - **sort_by**: Sort by title, year, or rating
    - **sort_order**: asc or desc
    - **search**: Search in title or director
    """
    movie_service = MovieService(db)
    
    # Parse genres if provided
    genre_list = None
    if genres:
        genre_list = [g.strip() for g in genres.split(",")]
    
    # Exclude not-interested movies if user is logged in
    exclude_ids = None
    if current_user:
        pref_service = PreferenceService(db)
        exclude_ids = await pref_service.get_not_interested_ids(current_user.id)
    
    return await movie_service.get_movies(
        page=page,
        page_size=page_size,
        genres=genre_list,
        decade=decade,
        min_rating=min_rating,
        max_rating=max_rating,
        director=director,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
        exclude_ids=exclude_ids
    )


@router.get("/search", response_model=MovieList)
async def search_movies(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Client = Depends(get_db)
):
    """
    Search movies by title or director.
    
    - **q**: Search query (required)
    """
    movie_service = MovieService(db)
    return await movie_service.search_movies(q, page, page_size)


@router.get("/genres", response_model=list[str])
async def get_genres(db: Client = Depends(get_db)):
    """Get all available genres for filtering."""
    movie_service = MovieService(db)
    return await movie_service.get_genres()


@router.get("/decades", response_model=list[str])
async def get_decades(db: Client = Depends(get_db)):
    """Get all available decades for filtering."""
    movie_service = MovieService(db)
    return await movie_service.get_decades()


@router.get("/{slug}", response_model=MovieDetail)
async def get_movie(
    slug: str,
    db: Client = Depends(get_db)
):
    """Get a single movie by slug."""
    movie_service = MovieService(db)
    movie = await movie_service.get_movie_by_slug(slug)
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    return movie


@router.get("/{movie_id}/recommendations", response_model=RecommendationList)
async def get_recommendations(
    movie_id: int,
    limit: int = Query(6, ge=1, le=20, description="Number of recommendations"),
    current_user: Optional[UserInfo] = Depends(get_optional_user),
    db: Client = Depends(get_db)
):
    """
    Get movie recommendations based on cosine similarity.
    
    Returns similar movies with explanation of why they were recommended.
    Excludes movies marked as "not interested" if user is logged in.
    """
    movie_service = MovieService(db)
    
    # Exclude not-interested movies if user is logged in
    exclude_ids = None
    if current_user:
        pref_service = PreferenceService(db)
        exclude_ids = await pref_service.get_not_interested_ids(current_user.id)
    
    recommendations = await movie_service.get_recommendations(
        movie_id=movie_id,
        limit=limit,
        exclude_ids=exclude_ids
    )
    
    if recommendations is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    return recommendations
