-- ============================================================
-- InternAI — Complete Supabase Schema
-- Paste this entire block into the Supabase SQL Editor and run.
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────
-- 1. USERS TABLE
-- Stores registered users with hashed passwords.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

-- ─────────────────────────────────────────────────────────────
-- 2. RESUMES TABLE
-- Stores parsed resume text linked to a user.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.resumes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    resume_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

-- ─────────────────────────────────────────────────────────────
-- 3. APPLICATIONS TABLE
-- Stores generated application materials per internship.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.applications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    company TEXT,
    role TEXT,
    match_score INTEGER,
    reasoning TEXT,
    cover_letter TEXT,
    tailored_resume TEXT,
    email_subject TEXT,
    email_body TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

-- ─────────────────────────────────────────────────────────────
-- INDEXES for fast lookups
-- ─────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON public.resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON public.applications(user_id);

-- ─────────────────────────────────────────────────────────────
-- ROW LEVEL SECURITY (RLS)
-- Required by Supabase — allows access via the anon/service key.
-- ─────────────────────────────────────────────────────────────
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.applications ENABLE ROW LEVEL SECURITY;

-- Allow full access via the service_role key (used by your backend)
CREATE POLICY "Allow all for service role" ON public.users
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for service role" ON public.resumes
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for service role" ON public.applications
    FOR ALL USING (true) WITH CHECK (true);
