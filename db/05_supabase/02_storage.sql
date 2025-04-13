-- Supabase integration - Storage functionality

-- Create schema for Supabase Storage (if not already created)
CREATE SCHEMA IF NOT EXISTS storage;
COMMENT ON SCHEMA storage IS 'Supabase Storage functionality';

-- Storage buckets table
CREATE TABLE storage.buckets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    owner UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    public BOOLEAN DEFAULT FALSE,
    avif_autodetection BOOLEAN DEFAULT FALSE,
    file_size_limit BIGINT,
    allowed_mime_types TEXT[]
);

COMMENT ON TABLE storage.buckets IS 'Supabase Storage buckets';

-- Storage objects table
CREATE TABLE storage.objects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket_id TEXT NOT NULL REFERENCES storage.buckets(id),
    name TEXT NOT NULL,
    owner UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    path_tokens TEXT[] GENERATED ALWAYS AS (string_to_array(name, '/')) STORED,
    UNIQUE(bucket_id, name)
);

COMMENT ON TABLE storage.objects IS 'Supabase Storage objects';

-- Storage versions table (for versioning)
CREATE TABLE storage.versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    object_id UUID NOT NULL REFERENCES storage.objects(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    size BIGINT,
    metadata JSONB,
    UNIQUE(object_id, version_number)
);

COMMENT ON TABLE storage.versions IS 'Supabase Storage object versions';

-- Create application-specific file metadata table
CREATE TABLE storage.file_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    object_id UUID NOT NULL REFERENCES storage.objects(id) ON DELETE CASCADE,
    title TEXT,
    description TEXT,
    tags TEXT[],
    entity_type VARCHAR(100),
    entity_id UUID,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    is_archived BOOLEAN DEFAULT FALSE,
    custom_metadata JSONB DEFAULT '{}'
);

COMMENT ON TABLE storage.file_metadata IS 'Application-specific metadata for storage objects';

-- Create table for access control
CREATE TABLE storage.access_controls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    object_id UUID REFERENCES storage.objects(id) ON DELETE CASCADE,
    bucket_id TEXT REFERENCES storage.buckets(id) ON DELETE CASCADE,
    entity_type VARCHAR(20) NOT NULL, -- 'user', 'role', 'team', 'organization'
    entity_id UUID NOT NULL,
    permission VARCHAR(20) NOT NULL, -- 'read', 'write', 'full'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    CHECK (object_id IS NOT NULL OR bucket_id IS NOT NULL),
    UNIQUE(object_id, entity_type, entity_id),
    UNIQUE(bucket_id, entity_type, entity_id)
);

COMMENT ON TABLE storage.access_controls IS 'Access control for storage objects and buckets';

-- Create indexes for efficient querying
CREATE INDEX idx_storage_objects_bucket_id ON storage.objects (bucket_id);
CREATE INDEX idx_storage_objects_owner ON storage.objects (owner);
CREATE INDEX idx_storage_objects_created_at ON storage.objects (created_at);
CREATE INDEX idx_storage_objects_path_tokens ON storage.objects USING GIN (path_tokens);

CREATE INDEX idx_storage_versions_object_id ON storage.versions (object_id);
CREATE INDEX idx_storage_versions_created_at ON storage.versions (created_at);
CREATE INDEX idx_storage_versions_created_by ON storage.versions (created_by);

CREATE INDEX idx_storage_file_metadata_object_id ON storage.file_metadata (object_id);
CREATE INDEX idx_storage_file_metadata_entity ON storage.file_metadata (entity_type, entity_id);
CREATE INDEX idx_storage_file_metadata_organization_id ON storage.file_metadata (organization_id);
CREATE INDEX idx_storage_file_metadata_created_by ON storage.file_metadata (created_by);
CREATE INDEX idx_storage_file_metadata_tags ON storage.file_metadata USING GIN (tags);
CREATE INDEX idx_storage_file_metadata_custom_metadata ON storage.file_metadata USING GIN (custom_metadata);

CREATE INDEX idx_storage_access_controls_object_id ON storage.access_controls (object_id);
CREATE INDEX idx_storage_access_controls_bucket_id ON storage.access_controls (bucket_id);
CREATE INDEX idx_storage_access_controls_entity ON storage.access_controls (entity_type, entity_id);

-- Create default buckets
INSERT INTO storage.buckets (id, name, public)
VALUES
    ('documents', 'Documents', FALSE),
    ('images', 'Images', TRUE),
    ('avatars', 'User Avatars', TRUE),
    ('backups', 'System Backups', FALSE),
    ('temp', 'Temporary Files', FALSE);

-- Create function to handle file uploads
CREATE OR REPLACE FUNCTION storage.handle_file_upload()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Create default file metadata
    INSERT INTO storage.file_metadata (
        object_id,
        title,
        created_by,
        organization_id
    )
    SELECT
        NEW.id,
        NEW.name,
        NEW.owner,
        (
            SELECT organization_id
            FROM public.organization_users ou
            JOIN auth.user_mappings um ON um.app_user_id = ou.user_id
            WHERE um.auth_user_id = NEW.owner
            LIMIT 1
        );
    
    RETURN NEW;
END;
$$;

-- Create trigger for file uploads
CREATE TRIGGER trg_handle_file_upload
AFTER INSERT ON storage.objects
FOR EACH ROW
EXECUTE FUNCTION storage.handle_file_upload();

-- Create function to check access permissions
CREATE OR REPLACE FUNCTION storage.check_access(
    p_object_id UUID,
    p_user_id UUID,
    p_permission VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_app_user_id UUID;
    v_has_access BOOLEAN := FALSE;
    v_bucket_id TEXT;
    v_is_public BOOLEAN;
    v_organization_ids UUID[];
    v_team_ids UUID[];
    v_role_ids UUID[];
BEGIN
    -- Get application user ID
    SELECT app_user_id INTO v_app_user_id
    FROM auth.user_mappings
    WHERE auth_user_id = p_user_id;
    
    IF v_app_user_id IS NULL THEN
        RETURN FALSE;
    END IF;
    
    -- Check if user is system admin
    SELECT is_system_admin INTO v_has_access
    FROM public.users
    WHERE id = v_app_user_id;
    
    IF v_has_access THEN
        RETURN TRUE;
    END IF;
    
    -- Get bucket info
    SELECT o.bucket_id, b.public INTO v_bucket_id, v_is_public
    FROM storage.objects o
    JOIN storage.buckets b ON o.bucket_id = b.id
    WHERE o.id = p_object_id;
    
    -- If bucket is public and permission is 'read', grant access
    IF v_is_public AND p_permission = 'read' THEN
        RETURN TRUE;
    END IF;
    
    -- Get user's organizations
    SELECT array_agg(organization_id) INTO v_organization_ids
    FROM public.organization_users
    WHERE user_id = v_app_user_id;
    
    -- Get user's teams
    SELECT array_agg(team_id) INTO v_team_ids
    FROM public.team_members
    WHERE user_id = v_app_user_id;
    
    -- Get user's roles
    SELECT array_agg(role_id) INTO v_role_ids
    FROM public.user_roles
    WHERE user_id = v_app_user_id;
    
    -- Check direct object access
    SELECT EXISTS (
        SELECT 1
        FROM storage.access_controls
        WHERE object_id = p_object_id
        AND (
            (entity_type = 'user' AND entity_id = v_app_user_id) OR
            (entity_type = 'organization' AND entity_id = ANY(v_organization_ids)) OR
            (entity_type = 'team' AND entity_id = ANY(v_team_ids)) OR
            (entity_type = 'role' AND entity_id = ANY(v_role_ids))
        )
        AND (
            permission = p_permission OR
            permission = 'full'
        )
    ) INTO v_has_access;
    
    IF v_has_access THEN
        RETURN TRUE;
    END IF;
    
    -- Check bucket access
    SELECT EXISTS (
        SELECT 1
        FROM storage.access_controls
        WHERE bucket_id = v_bucket_id
        AND (
            (entity_type = 'user' AND entity_id = v_app_user_id) OR
            (entity_type = 'organization' AND entity_id = ANY(v_organization_ids)) OR
            (entity_type = 'team' AND entity_id = ANY(v_team_ids)) OR
            (entity_type = 'role' AND entity_id = ANY(v_role_ids))
        )
        AND (
            permission = p_permission OR
            permission = 'full'
        )
    ) INTO v_has_access;
    
    RETURN v_has_access;
END;
$$;

COMMENT ON FUNCTION storage.check_access IS 'Check if a user has access to a storage object';

-- Create RLS policies
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;
ALTER TABLE storage.buckets ENABLE ROW LEVEL SECURITY;
ALTER TABLE storage.file_metadata ENABLE ROW LEVEL SECURITY;

-- Policy for reading objects
CREATE POLICY read_objects ON storage.objects
    FOR SELECT
    USING (
        bucket_id IN (SELECT id FROM storage.buckets WHERE public = TRUE) OR
        storage.check_access(id, auth.uid(), 'read')
    );

-- Policy for inserting objects
CREATE POLICY insert_objects ON storage.objects
    FOR INSERT
    WITH CHECK (
        storage.check_access(NULL, auth.uid(), 'write') OR
        bucket_id IN (
            SELECT bucket_id 
            FROM storage.access_controls 
            WHERE entity_type = 'user' 
            AND entity_id = (
                SELECT app_user_id 
                FROM auth.user_mappings 
                WHERE auth_user_id = auth.uid()
            )
            AND (permission = 'write' OR permission = 'full')
        )
    );

-- Policy for updating objects
CREATE POLICY update_objects ON storage.objects
    FOR UPDATE
    USING (storage.check_access(id, auth.uid(), 'write'));

-- Policy for deleting objects
CREATE POLICY delete_objects ON storage.objects
    FOR DELETE
    USING (storage.check_access(id, auth.uid(), 'full'));