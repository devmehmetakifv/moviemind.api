-- =============================================
-- Moviemind Database Setup
-- 01_create_tables.sql
-- Run this script in Supabase SQL Editor
-- =============================================

-- Note: The 'movies' table should already exist with the imported data
-- This script creates the supporting tables for user preferences

-- =============================================
-- Favorites Table
-- =============================================
CREATE TABLE IF NOT EXISTS favorites (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    movie_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique user-movie combination
    UNIQUE(user_id, movie_id)
);

-- =============================================
-- Not Interested Table
-- =============================================
CREATE TABLE IF NOT EXISTS not_interested (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    movie_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique user-movie combination
    UNIQUE(user_id, movie_id)
);

-- =============================================
-- Feedback Table (Data Error Reports)
-- =============================================
CREATE TABLE IF NOT EXISTS feedback (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    movie_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    reported_issue TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- Add comments for documentation
-- =============================================
COMMENT ON TABLE favorites IS 'User favorite movies';
COMMENT ON TABLE not_interested IS 'Movies marked as not interested by users';
COMMENT ON TABLE feedback IS 'Data error reports submitted by users';
