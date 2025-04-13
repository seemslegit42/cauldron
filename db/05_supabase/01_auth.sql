-- Supabase integration - Authentication and user management

-- Create schema for Supabase Auth (if not already created)
CREATE SCHEMA IF NOT EXISTS auth;
COMMENT ON SCHEMA auth IS 'Supabase Auth functionality';

-- Supabase Auth users table
CREATE TABLE auth.users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    encrypted_password VARCHAR(255),
    email_confirmed_at TIMESTAMPTZ,
    phone_confirmed_at TIMESTAMPTZ,
    confirmation_token VARCHAR(255),
    confirmation_sent_at TIMESTAMPTZ,
    recovery_token VARCHAR(255),
    recovery_sent_at TIMESTAMPTZ,
    email_change_token VARCHAR(255),
    email_change VARCHAR(255),
    email_change_sent_at TIMESTAMPTZ,
    last_sign_in_at TIMESTAMPTZ,
    raw_app_meta_data JSONB,
    raw_user_meta_data JSONB,
    is_super_admin BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_sso_user BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMPTZ
);

COMMENT ON TABLE auth.users IS 'Supabase Auth users';

-- Supabase Auth sessions table
CREATE TABLE auth.sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    factor_id UUID,
    aal VARCHAR(20),
    not_after TIMESTAMPTZ
);

COMMENT ON TABLE auth.sessions IS 'Supabase Auth sessions';

-- Supabase Auth refresh tokens table
CREATE TABLE auth.refresh_tokens (
    id BIGSERIAL PRIMARY KEY,
    token VARCHAR(255) NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES auth.sessions(id) ON DELETE CASCADE,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE auth.refresh_tokens IS 'Supabase Auth refresh tokens';

-- Supabase Auth identities table
CREATE TABLE auth.identities (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    identity_data JSONB,
    provider VARCHAR(255),
    last_sign_in_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE auth.identities IS 'Supabase Auth identities for OAuth providers';

-- Supabase Auth factors table (MFA)
CREATE TABLE auth.factors (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    friendly_name VARCHAR(255),
    factor_type VARCHAR(20),
    status VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    secret VARCHAR(255)
);

COMMENT ON TABLE auth.factors IS 'Supabase Auth multi-factor authentication factors';

-- Create mapping between Supabase Auth users and application users
CREATE TABLE auth.user_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    app_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(auth_user_id),
    UNIQUE(app_user_id)
);

COMMENT ON TABLE auth.user_mappings IS 'Mapping between Supabase Auth users and application users';

-- Create indexes for efficient querying
CREATE INDEX idx_auth_users_email ON auth.users (email);
CREATE INDEX idx_auth_users_phone ON auth.users (phone);
CREATE INDEX idx_auth_users_created_at ON auth.users (created_at);
CREATE INDEX idx_auth_users_last_sign_in_at ON auth.users (last_sign_in_at);
CREATE INDEX idx_auth_users_is_super_admin ON auth.users (is_super_admin);

CREATE INDEX idx_auth_sessions_user_id ON auth.sessions (user_id);
CREATE INDEX idx_auth_sessions_created_at ON auth.sessions (created_at);

CREATE INDEX idx_auth_refresh_tokens_token ON auth.refresh_tokens (token);
CREATE INDEX idx_auth_refresh_tokens_user_id ON auth.refresh_tokens (user_id);
CREATE INDEX idx_auth_refresh_tokens_session_id ON auth.refresh_tokens (session_id);
CREATE INDEX idx_auth_refresh_tokens_revoked ON auth.refresh_tokens (revoked);

CREATE INDEX idx_auth_identities_user_id ON auth.identities (user_id);
CREATE INDEX idx_auth_identities_provider ON auth.identities (provider);

CREATE INDEX idx_auth_factors_user_id ON auth.factors (user_id);
CREATE INDEX idx_auth_factors_factor_type ON auth.factors (factor_type);
CREATE INDEX idx_auth_factors_status ON auth.factors (status);

CREATE INDEX idx_auth_user_mappings_auth_user_id ON auth.user_mappings (auth_user_id);
CREATE INDEX idx_auth_user_mappings_app_user_id ON auth.user_mappings (app_user_id);

-- Create function to sync Supabase Auth user to application user
CREATE OR REPLACE FUNCTION auth.sync_user_from_auth()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_app_user_id UUID;
    v_username VARCHAR;
    v_full_name VARCHAR;
BEGIN
    -- Extract username from email (before @)
    v_username := split_part(NEW.email, '@', 1);
    
    -- Extract full name from user metadata if available
    v_full_name := NEW.raw_user_meta_data->>'full_name';
    IF v_full_name IS NULL THEN
        v_full_name := v_username;
    END IF;
    
    -- Check if user already exists in application
    SELECT app_user_id INTO v_app_user_id
    FROM auth.user_mappings
    WHERE auth_user_id = NEW.id;
    
    IF v_app_user_id IS NULL THEN
        -- Create new application user
        INSERT INTO public.users (
            username,
            email,
            full_name,
            hashed_password,
            salt,
            is_active,
            created_at,
            modified_at,
            last_login
        ) VALUES (
            v_username,
            NEW.email,
            v_full_name,
            'SUPABASE_AUTH', -- Placeholder as auth is handled by Supabase
            'SUPABASE_AUTH', -- Placeholder as auth is handled by Supabase
            TRUE,
            NEW.created_at,
            NEW.updated_at,
            NEW.last_sign_in_at
        )
        RETURNING id INTO v_app_user_id;
        
        -- Create mapping
        INSERT INTO auth.user_mappings (auth_user_id, app_user_id)
        VALUES (NEW.id, v_app_user_id);
        
        -- Create user profile
        INSERT INTO public.user_profiles (
            user_id,
            profile_image_url,
            job_title,
            bio,
            contact_email,
            created_at,
            modified_at
        ) VALUES (
            v_app_user_id,
            NEW.raw_user_meta_data->>'avatar_url',
            NEW.raw_user_meta_data->>'job_title',
            NEW.raw_user_meta_data->>'bio',
            NEW.email,
            NEW.created_at,
            NEW.updated_at
        );
    ELSE
        -- Update existing application user
        UPDATE public.users
        SET
            email = NEW.email,
            full_name = v_full_name,
            is_active = (NEW.deleted_at IS NULL),
            modified_at = NEW.updated_at,
            last_login = NEW.last_sign_in_at
        WHERE id = v_app_user_id;
        
        -- Update user profile
        UPDATE public.user_profiles
        SET
            profile_image_url = NEW.raw_user_meta_data->>'avatar_url',
            job_title = NEW.raw_user_meta_data->>'job_title',
            bio = NEW.raw_user_meta_data->>'bio',
            contact_email = NEW.email,
            modified_at = NEW.updated_at
        WHERE user_id = v_app_user_id;
    END IF;
    
    RETURN NEW;
END;
$$;

-- Create trigger to sync users
CREATE TRIGGER trg_sync_user_from_auth
AFTER INSERT OR UPDATE ON auth.users
FOR EACH ROW
EXECUTE FUNCTION auth.sync_user_from_auth();

-- Create function to handle user deletion
CREATE OR REPLACE FUNCTION auth.handle_user_deletion()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_app_user_id UUID;
BEGIN
    -- Get application user ID
    SELECT app_user_id INTO v_app_user_id
    FROM auth.user_mappings
    WHERE auth_user_id = OLD.id;
    
    IF v_app_user_id IS NOT NULL THEN
        -- Mark application user as inactive
        UPDATE public.users
        SET
            is_active = FALSE,
            modified_at = NOW()
        WHERE id = v_app_user_id;
    END IF;
    
    RETURN OLD;
END;
$$;

-- Create trigger to handle user deletion
CREATE TRIGGER trg_handle_user_deletion
BEFORE DELETE ON auth.users
FOR EACH ROW
EXECUTE FUNCTION auth.handle_user_deletion();