"""Unit tests for movie service."""

import pytest
import numpy as np
from unittest.mock import MagicMock, AsyncMock

from app.services.movie_service import (
    MovieService,
    _parse_genres,
    _create_genre_vector,
    _create_decade_vector,
    _create_director_vector,
    _create_feature_vector,
    _cosine_similarity,
    _generate_explanation,
    ALL_GENRES,
    ALL_DECADES
)


class TestGenreParsing:
    """Tests for genre parsing functionality."""
    
    def test_parse_single_genre(self):
        """Test parsing a single genre."""
        result = _parse_genres("Comedy")
        assert result == ["Comedy"]
    
    def test_parse_multiple_genres(self):
        """Test parsing multiple comma-separated genres."""
        result = _parse_genres("Action,Adventure,Sci-Fi")
        assert result == ["Action", "Adventure", "Sci-Fi"]
    
    def test_parse_genres_with_spaces(self):
        """Test parsing genres with spaces around commas."""
        result = _parse_genres("Action, Adventure, Comedy")
        assert result == ["Action", "Adventure", "Comedy"]
    
    def test_parse_empty_genres(self):
        """Test parsing empty genre string."""
        result = _parse_genres("")
        assert result == []
    
    def test_parse_none_genres(self):
        """Test parsing None genre value (null tolerance)."""
        result = _parse_genres(None)
        assert result == []


class TestFeatureVectorCreation:
    """Tests for feature vector creation."""
    
    def test_genre_vector_single(self):
        """Test genre vector with single genre."""
        vector = _create_genre_vector("Comedy")
        assert vector[ALL_GENRES.index("Comedy")] == 1.0
        assert np.sum(vector) == 1.0
    
    def test_genre_vector_multiple(self):
        """Test genre vector with multiple genres."""
        vector = _create_genre_vector("Action,Comedy,Drama")
        assert vector[ALL_GENRES.index("Action")] == 1.0
        assert vector[ALL_GENRES.index("Comedy")] == 1.0
        assert vector[ALL_GENRES.index("Drama")] == 1.0
        assert np.sum(vector) == 3.0
    
    def test_genre_vector_empty(self):
        """Test genre vector with empty string."""
        vector = _create_genre_vector("")
        assert np.sum(vector) == 0.0
    
    def test_decade_vector(self):
        """Test decade vector creation."""
        vector = _create_decade_vector("1990s")
        assert vector[ALL_DECADES.index("1990s")] == 1.0
        assert np.sum(vector) == 1.0
    
    def test_decade_vector_invalid(self):
        """Test decade vector with invalid decade."""
        vector = _create_decade_vector("invalid")
        assert np.sum(vector) == 0.0
    
    def test_director_vector(self):
        """Test director vector is deterministic."""
        vector1 = _create_director_vector("Steven Spielberg")
        vector2 = _create_director_vector("Steven Spielberg")
        assert np.array_equal(vector1, vector2)
    
    def test_director_vector_different(self):
        """Test different directors produce different vectors."""
        vector1 = _create_director_vector("Steven Spielberg")
        vector2 = _create_director_vector("Martin Scorsese")
        assert not np.array_equal(vector1, vector2)


class TestCosineSimilarity:
    """Tests for cosine similarity calculation."""
    
    def test_identical_vectors(self):
        """Test similarity of identical vectors is 1.0."""
        vec = np.array([1.0, 0.0, 1.0, 0.0])
        similarity = _cosine_similarity(vec, vec)
        assert similarity == pytest.approx(1.0)
    
    def test_orthogonal_vectors(self):
        """Test similarity of orthogonal vectors is 0.0."""
        vec1 = np.array([1.0, 0.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0, 0.0])
        similarity = _cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(0.0)
    
    def test_similar_vectors(self):
        """Test similarity of partially similar vectors."""
        vec1 = np.array([1.0, 1.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0, 0.0])
        similarity = _cosine_similarity(vec1, vec2)
        assert 0.0 < similarity < 1.0
    
    def test_zero_vector(self):
        """Test similarity with zero vector returns 0.0."""
        vec1 = np.array([1.0, 1.0, 1.0])
        vec2 = np.array([0.0, 0.0, 0.0])
        similarity = _cosine_similarity(vec1, vec2)
        assert similarity == 0.0


class TestExplanationGeneration:
    """Tests for recommendation explanation generation."""
    
    def test_shared_genres_explanation(self):
        """Test explanation includes shared genres."""
        source = {"genres": "Action,Comedy", "director": "A", "decade": "1990s", "rating": 7.0}
        target = {"genres": "Comedy,Drama", "director": "B", "decade": "2000s", "rating": 8.0}
        explanation = _generate_explanation(source, target)
        assert "Comedy" in explanation
    
    def test_same_director_explanation(self):
        """Test explanation includes same director."""
        source = {"genres": "Action", "director": "Steven Spielberg", "decade": "1990s", "rating": 7.0}
        target = {"genres": "Drama", "director": "Steven Spielberg", "decade": "2000s", "rating": 8.0}
        explanation = _generate_explanation(source, target)
        assert "Steven Spielberg" in explanation
    
    def test_same_decade_explanation(self):
        """Test explanation includes same decade."""
        source = {"genres": "Action", "director": "A", "decade": "1990s", "rating": 7.0}
        target = {"genres": "Drama", "director": "B", "decade": "1990s", "rating": 8.0}
        explanation = _generate_explanation(source, target)
        assert "1990s" in explanation
    
    def test_similar_rating_explanation(self):
        """Test explanation includes similar rating."""
        source = {"genres": "Action", "director": "A", "decade": "1990s", "rating": 8.0}
        target = {"genres": "Drama", "director": "B", "decade": "2000s", "rating": 8.3}
        explanation = _generate_explanation(source, target)
        assert "rating" in explanation.lower()
    
    def test_fallback_explanation(self):
        """Test fallback explanation when no specific matches."""
        source = {"genres": "Action", "director": "A", "decade": "1990s", "rating": 5.0}
        target = {"genres": "Documentary", "director": "B", "decade": "1990s", "rating": 9.0}
        explanation = _generate_explanation(source, target)
        assert explanation == "Similar characteristics"


class TestMovieServiceFiltering:
    """Tests for movie service filtering functionality."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database client."""
        mock = MagicMock()
        mock.table.return_value.select.return_value.execute.return_value = MagicMock(
            data=[],
            count=0
        )
        return mock
    
    @pytest.mark.asyncio
    async def test_get_movies_default_pagination(self, mock_db):
        """Test default pagination values."""
        service = MovieService(mock_db)
        result = await service.get_movies()
        
        assert result.page == 1
        assert result.page_size == 20
    
    @pytest.mark.asyncio
    async def test_get_genres_returns_all(self, mock_db):
        """Test get_genres returns all genres."""
        service = MovieService(mock_db)
        genres = await service.get_genres()
        
        assert "Action" in genres
        assert "Comedy" in genres
        assert "Drama" in genres
        assert len(genres) == len(ALL_GENRES)
    
    @pytest.mark.asyncio
    async def test_get_decades_returns_all(self, mock_db):
        """Test get_decades returns all decades."""
        service = MovieService(mock_db)
        decades = await service.get_decades()
        
        assert "1990s" in decades
        assert "2000s" in decades
        assert len(decades) == len(ALL_DECADES)
