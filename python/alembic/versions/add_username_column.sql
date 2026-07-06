-- Add username column to users table
-- This allows users to have a display username separate from their Cognito login (email)

ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(50) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Update existing users to use their email prefix as username
UPDATE users 
SET username = SPLIT_PART(email, '@', 1)
WHERE username IS NULL AND email IS NOT NULL;

-- Add comment
COMMENT ON COLUMN users.username IS 'Display username (different from cognito_username which is email)';
COMMENT ON COLUMN users.cognito_username IS 'Email address used for Cognito authentication';
