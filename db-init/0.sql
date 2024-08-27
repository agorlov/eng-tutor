-- Phrases table
CREATE TABLE phrases (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    native_lang TEXT NOT NULL,
    studied_lang  TEXT NOT NULL,
    phrase TEXT NOT NULL,
    translation TEXT NOT NULL,
    total_repetitions INTEGER DEFAULT 0,
    success_repetitions INTEGER DEFAULT 0,
    first_success_repetition BOOLEAN DEFAULT f,
    first_repeat TIMESTAMP WITH TIME ZONE,
    last_repeat TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_phrases_user_id ON phrases (user_id);