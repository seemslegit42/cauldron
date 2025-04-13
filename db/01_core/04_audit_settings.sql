-- Audit logs and system settings

-- Audit logs
CREATE TABLE public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.audit_logs IS 'System-wide audit trail of user actions';

-- System settings
CREATE TABLE public.system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(180) NOT NULL UNIQUE,
    value JSONB NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.system_settings IS 'Global system configuration settings';

-- Organization settings
CREATE TABLE public.organization_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    key VARCHAR(180) NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, key)
);

COMMENT ON TABLE public.organization_settings IS 'Organization-specific configuration settings';

-- User settings
CREATE TABLE public.user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    key VARCHAR(180) NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, key)
);

COMMENT ON TABLE public.user_settings IS 'User-specific configuration settings';

-- Schema migrations
CREATE TABLE public.schema_migrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    applied_by VARCHAR(100)
);

COMMENT ON TABLE public.schema_migrations IS 'Database schema version tracking';

-- Create indexes
CREATE INDEX idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON public.audit_logs(action);
CREATE INDEX idx_audit_logs_entity_type_id ON public.audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON public.audit_logs(created_at);
CREATE INDEX idx_organization_settings_organization_id ON public.organization_settings(organization_id);
CREATE INDEX idx_user_settings_user_id ON public.user_settings(user_id);

-- Insert initial system settings
INSERT INTO public.system_settings (key, value, description, is_system)
VALUES
    ('system.name', '"Cauldron sEOS"', 'System name displayed in UI', TRUE),
    ('system.version', '"1.0.0"', 'Current system version', TRUE),
    ('auth.password_policy', '{"min_length": 8, "require_uppercase": true, "require_number": true, "require_special": true}', 'Password policy settings', TRUE),
    ('auth.session_timeout', '86400', 'Session timeout in seconds (24 hours)', TRUE),
    ('email.enabled', 'true', 'Whether email notifications are enabled', TRUE),
    ('lore.embedding_model', '"text-embedding-ada-002"', 'Default embedding model for knowledge management', TRUE),
    ('lore.embedding_dimensions', '1536', 'Dimensions for vector embeddings', TRUE),
    ('agent.default_model', '"gpt-4"', 'Default LLM for agent operations', TRUE);

-- Record initial migration
INSERT INTO public.schema_migrations (version, description, applied_by)
VALUES ('20230101000000', 'Initial schema creation', 'setup');
