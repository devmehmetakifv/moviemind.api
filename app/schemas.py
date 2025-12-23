"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# Movie Schemas
class MovieBase(BaseModel):
    """Base movie schema with common fields."""
    id: int
    slug: str
    title: str
    year: int
    decade: str
    release_date: str
    director: str
    genres: str
    rating: float
    imdb_url: str
    poster_url: str
    description: str


class Movie(MovieBase):
    """Movie schema for list responses."""
    pass


class MovieDetail(MovieBase):
    """Movie schema with additional details for single movie view."""
    pass


class MovieList(BaseModel):
    """Paginated movie list response."""
    movies: list[Movie]
    total: int
    page: int
    page_size: int
    total_pages: int


class Recommendation(BaseModel):
    """Movie recommendation with explanation."""
    movie: Movie
    similarity_score: float = Field(..., ge=0, le=1)
    explanation: str  # e.g., "Same genres: Comedy, Drama"


class RecommendationList(BaseModel):
    """List of movie recommendations."""
    recommendations: list[Recommendation]
    source_movie_id: int


# User Preference Schemas
class FavoriteCreate(BaseModel):
    """Schema for adding a movie to favorites."""
    movie_id: int


class Favorite(BaseModel):
    """Favorite movie response."""
    id: str
    user_id: str
    movie_id: int
    created_at: datetime
    movie: Optional[Movie] = None


class FavoriteList(BaseModel):
    """List of favorite movies."""
    favorites: list[Favorite]
    total: int


class NotInterestedCreate(BaseModel):
    """Schema for marking a movie as not interested."""
    movie_id: int


class NotInterested(BaseModel):
    """Not interested movie response."""
    id: str
    user_id: str
    movie_id: int
    created_at: datetime


class NotInterestedList(BaseModel):
    """List of not interested movies."""
    items: list[NotInterested]
    total: int


# Feedback Schemas
class FeedbackCreate(BaseModel):
    """Schema for creating data error feedback."""
    movie_id: int
    field_name: str  # Which field has the error
    reported_issue: str  # Description of the issue


class Feedback(BaseModel):
    """Feedback response."""
    id: str
    user_id: Optional[str]
    movie_id: int
    field_name: str
    reported_issue: str
    created_at: datetime


# Auth Schemas
class UserRegister(BaseModel):
    """User registration request."""
    email: str
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """User login request."""
    email: str
    password: str


class AuthResponse(BaseModel):
    """Authentication response with tokens."""
    access_token: str
    refresh_token: str
    user_id: str
    email: str


class UserInfo(BaseModel):
    """Current user information."""
    id: str
    email: str


class TokenRefresh(BaseModel):
    """Token refresh request."""
    refresh_token: str


# Filter/Sort Schemas
class MovieFilters(BaseModel):
    """Movie filtering options."""
    genres: Optional[list[str]] = None
    decade: Optional[str] = None
    min_rating: Optional[float] = Field(None, ge=0, le=10)
    max_rating: Optional[float] = Field(None, ge=0, le=10)
    director: Optional[str] = None


class SortOptions(BaseModel):
    """Sorting options for movie list."""
    field: str = Field(default="title", pattern="^(title|year|rating)$")
    order: str = Field(default="asc", pattern="^(asc|desc)$")


# Generic Response Schemas
class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response."""
    detail: str
    error_code: Optional[str] = None
