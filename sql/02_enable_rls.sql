-- =============================================
-- Moviemind Row Level Security Policies
-- 02_enable_rls.sql
-- Run this script in Supabase SQL Editor
-- =============================================

-- =============================================
-- Enable RLS on all tables
-- =============================================
ALTER TABLE favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE not_interested ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- =============================================
-- Favorites Policies
-- Users can only access their own favorites
-- =============================================

-- Select: Users can read their own favorites
CREATE POLICY "Users can view their own favorites"
    ON favorites FOR SELECT
    USING (auth.uid() = user_id);

-- Insert: Users can add to their own favorites
CREATE POLICY "Users can add to their favorites"
    ON favorites FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Delete: Users can remove from their own favorites
CREATE POLICY "Users can remove from their favorites"
    ON favorites FOR DELETE
    USING (auth.uid() = user_id);

-- =============================================
-- Not Interested Policies
-- Users can only access their own not-interested list
-- =============================================

-- Select: Users can read their own not-interested
CREATE POLICY "Users can view their own not-interested"
    ON not_interested FOR SELECT
    USING (auth.uid() = user_id);

-- Insert: Users can add to their own not-interested
CREATE POLICY "Users can add to not-interested"
    ON not_interested FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Delete: Users can remove from their not-interested
CREATE POLICY "Users can remove from not-interested"
    ON not_interested FOR DELETE
    USING (auth.uid() = user_id);

-- =============================================
-- Feedback Policies
-- Anyone can submit feedback, users can view their own
-- =============================================

-- Select: Users can view their own feedback
CREATE POLICY "Users can view their own feedback"
    ON feedback FOR SELECT
    USING (auth.uid() = user_id OR user_id IS NULL);

-- Insert: Anyone can submit feedback (authenticated or not via API)
CREATE POLICY "Anyone can submit feedback"
    ON feedback FOR INSERT
    WITH CHECK (true);

-- =============================================
-- Movies Table (if needed)
-- Allow public read access
-- =============================================
-- ALTER TABLE movies ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY "Movies are publicly readable"
--     ON movies FOR SELECT
--     USING (true);
