"""Supabase database client initialization."""

from functools import lru_cache
from supabase import create_client, Client
from app.config import get_settings


@lru_cache
def get_supabase_client() -> Client:
    """Get cached Supabase client instance."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_key)


@lru_cache
def get_supabase_admin_client() -> Client:
    """Get cached Supabase admin client with service role key."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_key)


def get_db() -> Client:
    """Dependency for getting database client."""
    return get_supabase_client()
