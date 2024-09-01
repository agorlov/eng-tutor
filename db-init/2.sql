-- Adding a check to get the answer right the first time
ALTER TABLE phrases
ADD COLUMN first_success_repetition BOOLEAN DEFAULT FALSE;