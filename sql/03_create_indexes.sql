-- =============================================
-- Moviemind Performance Indexes
-- 03_create_indexes.sql
-- Run this script in Supabase SQL Editor
-- =============================================

-- =============================================
-- Movies Table Indexes
-- =============================================

-- Index for genre filtering (using GIN for text search)
CREATE INDEX IF NOT EXISTS idx_movies_genres 
    ON movies USING GIN (to_tsvector('english', genres));

-- Index for year sorting
CREATE INDEX IF NOT EXISTS idx_movies_year 
    ON movies (year);

-- Index for rating sorting
CREATE INDEX IF NOT EXISTS idx_movies_rating 
    ON movies (rating DESC);

-- Index for decade filtering
CREATE INDEX IF NOT EXISTS idx_movies_decade 
    ON movies (decade);

-- Index for title sorting and searching
CREATE INDEX IF NOT EXISTS idx_movies_title 
    ON movies (title);

-- Index for director searching
CREATE INDEX IF NOT EXISTS idx_movies_director 
    ON movies (director);

-- =============================================
-- User Preference Indexes
-- =============================================

-- Favorites: Fast lookup by user
CREATE INDEX IF NOT EXISTS idx_favorites_user_id 
    ON favorites (user_id);

-- Favorites: Fast lookup for specific user-movie combination
CREATE INDEX IF NOT EXISTS idx_favorites_user_movie 
    ON favorites (user_id, movie_id);

-- Not Interested: Fast lookup by user
CREATE INDEX IF NOT EXISTS idx_not_interested_user_id 
    ON not_interested (user_id);

-- Not Interested: Fast lookup for specific user-movie combination
CREATE INDEX IF NOT EXISTS idx_not_interested_user_movie 
    ON not_interested (user_id, movie_id);

-- =============================================
-- Feedback Indexes
-- =============================================

-- Feedback: Fast lookup by movie
CREATE INDEX IF NOT EXISTS idx_feedback_movie_id 
    ON feedback (movie_id);

-- Feedback: Fast lookup by user
CREATE INDEX IF NOT EXISTS idx_feedback_user_id 
    ON feedback (user_id);
