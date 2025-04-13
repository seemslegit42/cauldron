-- Core user management tables

-- Users table
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(180) NOT NULL UNIQUE,
    email VARCHAR(180) NOT NULL UNIQUE,
    full_name VARCHAR(180) NOT NULL,
    hashed_password TEXT NOT NULL,
    salt TEXT NOT NULL,
    is_system_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

COMMENT ON TABLE public.users IS 'Core user accounts for the Cauldron sEOS platform';

-- User profile information
CREATE TABLE public.user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    profile_image_url TEXT,
    job_title VARCHAR(180),
    department VARCHAR(180),
    bio TEXT,
    contact_email VARCHAR(180),
    phone VARCHAR(50),
    timezone VARCHAR(50),
    locale VARCHAR(10) DEFAULT 'en-US',
    theme VARCHAR(50) DEFAULT 'light',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

COMMENT ON TABLE public.user_profiles IS 'Extended user profile information';

-- User sessions
CREATE TABLE public.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    session_token TEXT NOT NULL UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.user_sessions IS 'Active user sessions';

-- API tokens
CREATE TABLE public.api_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    token_name VARCHAR(180) NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    scopes TEXT[] DEFAULT '{}',
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ
);

COMMENT ON TABLE public.api_tokens IS 'API tokens for programmatic access';

-- Create indexes
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_username ON public.users(username);
CREATE INDEX idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON public.user_sessions(expires_at);
CREATE INDEX idx_api_tokens_user_id ON public.api_tokens(user_id);
