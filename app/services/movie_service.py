"""Movie service with cosine similarity recommendation algorithm."""

from typing import Optional
import numpy as np
from numpy.linalg import norm
from supabase import Client

from app.schemas import (
    Movie, MovieList, MovieDetail, Recommendation, RecommendationList
)


# All possible genres from MovieLens dataset
ALL_GENRES = [
    "Action", "Adventure", "Animation", "Children", "Comedy",
    "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir",
    "Horror", "Musical", "Mystery", "Romance", "Sci-Fi",
    "Thriller", "War", "Western"
]

# All decades
ALL_DECADES = [
    "1920s", "1930s", "1940s", "1950s", "1960s",
    "1970s", "1980s", "1990s"
]


def _parse_genres(genres_str: str) -> list[str]:
    """Parse comma-separated genres string into list."""
    if not genres_str:
        return []
    return [g.strip() for g in genres_str.split(",")]


def _create_genre_vector(genres_str: str) -> np.ndarray:
    """Create multi-hot encoding for genres."""
    genres = _parse_genres(genres_str)
    vector = np.zeros(len(ALL_GENRES))
    for i, genre in enumerate(ALL_GENRES):
        if genre in genres:
            vector[i] = 1.0
    return vector


def _create_decade_vector(decade: str) -> np.ndarray:
    """Create one-hot encoding for decade."""
    vector = np.zeros(len(ALL_DECADES))
    if decade in ALL_DECADES:
        idx = ALL_DECADES.index(decade)
        vector[idx] = 1.0
    return vector


def _create_director_vector(director: str, dim: int = 50) -> np.ndarray:
    """Create hashed vector for director (for similarity grouping)."""
    vector = np.zeros(dim)
    if director:
        hash_idx = hash(director.lower().strip()) % dim
        vector[hash_idx] = 1.0
    return vector


def _create_feature_vector(movie: dict) -> np.ndarray:
    """Create combined feature vector for a movie."""
    genre_vec = _create_genre_vector(movie.get("genres", ""))
    decade_vec = _create_decade_vector(movie.get("decade", ""))
    director_vec = _create_director_vector(movie.get("director", ""))
    
    # Combine all vectors with weights
    # Genres are most important, then decade, then director
    return np.concatenate([
        genre_vec * 2.0,      # Weight: 2x for genres
        decade_vec * 1.5,     # Weight: 1.5x for decade
        director_vec * 1.0    # Weight: 1x for director
    ])


def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    norm_a = norm(vec_a)
    norm_b = norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


def _generate_explanation(source: dict, target: dict) -> str:
    """Generate human-readable explanation for recommendation."""
    reasons = []
    
    # Check for shared genres
    source_genres = set(_parse_genres(source.get("genres", "")))
    target_genres = set(_parse_genres(target.get("genres", "")))
    shared_genres = source_genres & target_genres
    if shared_genres:
        reasons.append(f"Same genres: {', '.join(sorted(shared_genres))}")
    
    # Check for same director
    if source.get("director") and source.get("director") == target.get("director"):
        reasons.append(f"Same director: {source['director']}")
    
    # Check for same decade
    if source.get("decade") and source.get("decade") == target.get("decade"):
        reasons.append(f"Same decade: {source['decade']}")
    
    # Check for similar rating
    source_rating = source.get("rating", 0)
    target_rating = target.get("rating", 0)
    if abs(source_rating - target_rating) <= 0.5:
        reasons.append(f"Similar rating: {target_rating}")
    
    return " • ".join(reasons) if reasons else "Similar characteristics"


class MovieService:
    """Service for movie operations."""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def get_movies(
        self,
        page: int = 1,
        page_size: int = 20,
        genres: Optional[list[str]] = None,
        decade: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        director: Optional[str] = None,
        sort_by: str = "title",
        sort_order: str = "asc",
        search: Optional[str] = None,
        exclude_ids: Optional[list[int]] = None
    ) -> MovieList:
        """Get paginated list of movies with optional filters."""
        
        # Start query
        query = self.db.table("movies").select("*", count="exact")
        
        # Apply filters
        if genres:
            # Filter movies that contain any of the specified genres
            for genre in genres:
                query = query.ilike("genres", f"%{genre}%")
        
        if decade:
            query = query.eq("decade", decade)
        
        if min_rating is not None:
            query = query.gte("rating", min_rating)
        
        if max_rating is not None:
            query = query.lte("rating", max_rating)
        
        if director:
            query = query.ilike("director", f"%{director}%")
        
        if search:
            # Search in title and director
            query = query.or_(f"title.ilike.%{search}%,director.ilike.%{search}%")
        
        if exclude_ids:
            query = query.not_.in_("id", exclude_ids)
        
        # Apply sorting
        query = query.order(sort_by, desc=(sort_order == "desc"))
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        
        # Execute query
        result = query.execute()
        
        total = result.count if result.count else 0
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        
        movies = [Movie(**movie) for movie in result.data]
        
        return MovieList(
            movies=movies,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    async def get_movie_by_id(self, movie_id: int) -> Optional[MovieDetail]:
        """Get a single movie by ID."""
        result = self.db.table("movies").select("*").eq("id", movie_id).execute()
        
        if not result.data:
            return None
        
        return MovieDetail(**result.data[0])
    
    async def get_movie_by_slug(self, slug: str) -> Optional[MovieDetail]:
        """Get a single movie by slug."""
        result = self.db.table("movies").select("*").eq("slug", slug).execute()
        
        if not result.data:
            return None
        
        return MovieDetail(**result.data[0])
    
    async def search_movies(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20
    ) -> MovieList:
        """Search movies by title or director."""
        return await self.get_movies(
            page=page,
            page_size=page_size,
            search=query
        )
    
    async def get_recommendations(
        self,
        movie_id: int,
        limit: int = 6,
        exclude_ids: Optional[list[int]] = None
    ) -> Optional[RecommendationList]:
        """Get movie recommendations using cosine similarity."""
        
        # Get the source movie
        source_result = self.db.table("movies").select("*").eq("id", movie_id).execute()
        if not source_result.data:
            return None
        
        source_movie = source_result.data[0]
        source_vector = _create_feature_vector(source_movie)
        
        # Get all other movies
        all_movies_result = self.db.table("movies").select("*").neq("id", movie_id).execute()
        
        if not all_movies_result.data:
            return RecommendationList(recommendations=[], source_movie_id=movie_id)
        
        # Calculate similarities
        similarities = []
        for movie in all_movies_result.data:
            # Skip excluded movies (not interested)
            if exclude_ids and movie["id"] in exclude_ids:
                continue
            
            target_vector = _create_feature_vector(movie)
            similarity = _cosine_similarity(source_vector, target_vector)
            explanation = _generate_explanation(source_movie, movie)
            
            similarities.append({
                "movie": movie,
                "similarity": similarity,
                "explanation": explanation
            })
        
        # Sort by similarity (descending) and take top N
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        top_recommendations = similarities[:limit]
        
        recommendations = [
            Recommendation(
                movie=Movie(**item["movie"]),
                similarity_score=round(item["similarity"], 4),
                explanation=item["explanation"]
            )
            for item in top_recommendations
        ]
        
        return RecommendationList(
            recommendations=recommendations,
            source_movie_id=movie_id
        )
    
    async def get_genres(self) -> list[str]:
        """Get all available genres."""
        return ALL_GENRES
    
    async def get_decades(self) -> list[str]:
        """Get all available decades."""
        return ALL_DECADES
