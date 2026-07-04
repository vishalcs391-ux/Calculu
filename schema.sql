-- ============================================================
-- AI Super Study Platform - PostgreSQL Schema (MVP v1)
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------------------------------------------------------
-- USERS
-- Auth identity comes from Firebase; we mirror a profile row.
-- ---------------------------------------------------------
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firebase_uid    VARCHAR(128) UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    display_name    VARCHAR(255),
    role            VARCHAR(20) NOT NULL DEFAULT 'student', -- student | teacher | admin
    plan            VARCHAR(30) NOT NULL DEFAULT 'free',    -- free | premium_monthly | student_yearly | school | teacher
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_firebase_uid ON users(firebase_uid);

-- ---------------------------------------------------------
-- SOURCES  (uploaded PDF or YouTube link)
-- ---------------------------------------------------------
CREATE TABLE sources (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_type     VARCHAR(20) NOT NULL,   -- pdf | youtube
    title           VARCHAR(500),
    original_ref    TEXT NOT NULL,          -- file path/URL or youtube link
    raw_text        TEXT,                   -- extracted transcript / pdf text
    status          VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending | processing | ready | failed
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_sources_user_id ON sources(user_id);
CREATE INDEX idx_sources_status ON sources(status);

-- ---------------------------------------------------------
-- SUMMARIES / NOTES generated from a source
-- ---------------------------------------------------------
CREATE TABLE summaries (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id       UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_md      TEXT NOT NULL,          -- structured markdown notes
    key_points       JSONB,                  -- ["point 1", "point 2", ...]
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_summaries_source_id ON summaries(source_id);
CREATE INDEX idx_summaries_user_id ON summaries(user_id);

-- ---------------------------------------------------------
-- FLASHCARDS
-- ---------------------------------------------------------
CREATE TABLE flashcards (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    summary_id      UUID NOT NULL REFERENCES summaries(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question        TEXT NOT NULL,
    answer          TEXT NOT NULL,
    difficulty      VARCHAR(10) DEFAULT 'medium', -- easy | medium | hard
    times_reviewed  INTEGER NOT NULL DEFAULT 0,
    last_result     VARCHAR(10),             -- correct | incorrect
    next_review_at  TIMESTAMPTZ,             -- simple spaced repetition
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_flashcards_summary_id ON flashcards(summary_id);
CREATE INDEX idx_flashcards_user_id ON flashcards(user_id);
CREATE INDEX idx_flashcards_next_review ON flashcards(next_review_at);

-- ---------------------------------------------------------
-- QUIZZES (generated question sets) + questions inline as JSONB
-- ---------------------------------------------------------
CREATE TABLE quizzes (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    summary_id      UUID NOT NULL REFERENCES summaries(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    questions       JSONB NOT NULL, -- [{question, options[], correct_index, explanation}]
    difficulty      VARCHAR(10) DEFAULT 'medium',
    score           NUMERIC(5,2),   -- last attempt score %
    attempts        INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_quizzes_summary_id ON quizzes(summary_id);
CREATE INDEX idx_quizzes_user_id ON quizzes(user_id);

-- ---------------------------------------------------------
-- PRACTICE TESTS (exam-style, timed, mixed sources)
-- ---------------------------------------------------------
CREATE TABLE practice_tests (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    source_ids      UUID[] NOT NULL,       -- sources it was generated from
    questions       JSONB NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 30,
    difficulty      VARCHAR(10) DEFAULT 'medium',
    score           NUMERIC(5,2),
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_practice_tests_user_id ON practice_tests(user_id);

-- ---------------------------------------------------------
-- STUDY SESSIONS (planner entries + AI tutor chat log ref)
-- ---------------------------------------------------------
CREATE TABLE study_sessions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_type    VARCHAR(20) NOT NULL, -- planner | flashcards | quiz | practice_test | tutor_chat
    topic           VARCHAR(255),
    scheduled_at    TIMESTAMPTZ,
    duration_minutes INTEGER,
    status          VARCHAR(20) NOT NULL DEFAULT 'planned', -- planned | in_progress | done | skipped
    metadata        JSONB,          -- e.g. chat messages, notes
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_study_sessions_user_id ON study_sessions(user_id);
CREATE INDEX idx_study_sessions_scheduled_at ON study_sessions(scheduled_at);

-- ---------------------------------------------------------
-- PROGRESS METRICS (rollup stats per user per day/topic)
-- ---------------------------------------------------------
CREATE TABLE progress_metrics (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    metric_date         DATE NOT NULL DEFAULT CURRENT_DATE,
    flashcards_reviewed INTEGER NOT NULL DEFAULT 0,
    quizzes_taken       INTEGER NOT NULL DEFAULT 0,
    avg_quiz_score      NUMERIC(5,2),
    study_minutes       INTEGER NOT NULL DEFAULT 0,
    streak_days         INTEGER NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, metric_date)
);
CREATE INDEX idx_progress_metrics_user_date ON progress_metrics(user_id, metric_date);

-- ---------------------------------------------------------
-- SUBSCRIPTIONS / BILLING
-- ---------------------------------------------------------
CREATE TABLE subscriptions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan            VARCHAR(30) NOT NULL, -- free | premium_monthly | student_yearly | school | teacher
    provider        VARCHAR(30) NOT NULL DEFAULT 'stripe',
    provider_customer_id VARCHAR(255),
    provider_subscription_id VARCHAR(255),
    status          VARCHAR(20) NOT NULL DEFAULT 'active', -- active | canceled | past_due | trialing
    current_period_end TIMESTAMPTZ,
    seats           INTEGER DEFAULT 1,     -- for school/college licenses
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);

-- ---------------------------------------------------------
-- Trigger to auto-update updated_at columns
-- ---------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_sources_updated_at BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
