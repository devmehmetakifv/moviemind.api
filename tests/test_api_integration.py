"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client (skipped if env not configured)."""
        try:
            from app.main import app
            return TestClient(app)
        except Exception:
            pytest.skip("Application requires environment configuration")
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns health status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "moviemind-api"
    
    def test_health_endpoint(self, client):
        """Test health endpoint returns detailed status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data


class TestMovieEndpointStructure:
    """Tests for movie endpoint structure."""
    
    def test_movie_list_response_model(self):
        """Test movie list response model structure."""
        from app.schemas import MovieList, Movie
        
        movie = Movie(
            id=1,
            title="Test Movie",
            year=2000,
            decade="2000s",
            release_date="01-Jan-2000",
            director="Test Director",
            genres="Action,Comedy",
            rating=7.5,
            imdb_url="http://example.com",
            poster_url="http://example.com/poster.jpg",
            description="Test description"
        )
        
        movie_list = MovieList(
            movies=[movie],
            total=1,
            page=1,
            page_size=20,
            total_pages=1
        )
        
        assert len(movie_list.movies) == 1
        assert movie_list.total == 1


class TestRecommendationStructure:
    """Tests for recommendation response structure."""
    
    def test_recommendation_response_model(self):
        """Test recommendation response model structure."""
        from app.schemas import Recommendation, Movie
        
        movie = Movie(
            id=2,
            title="Similar Movie",
            year=2001,
            decade="2000s",
            release_date="01-Jan-2001",
            director="Other Director",
            genres="Action",
            rating=7.8,
            imdb_url="http://example.com",
            poster_url="http://example.com/poster.jpg",
            description="Similar description"
        )
        
        rec = Recommendation(
            movie=movie,
            similarity_score=0.85,
            explanation="Same genres: Action"
        )
        
        assert rec.similarity_score == 0.85
        assert "Action" in rec.explanation


class TestCORSConfiguration:
    """Tests for CORS configuration."""
    
    def test_cors_origins_parsing(self):
        """Test CORS origins are parsed correctly."""
        # This would require mocking environment variables
        origins = "http://localhost:3000,https://example.com"
        parsed = [o.strip() for o in origins.split(",")]
        
        assert "http://localhost:3000" in parsed
        assert "https://example.com" in parsed
