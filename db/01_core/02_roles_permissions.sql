-- Role-based access control

-- Roles
CREATE TABLE public.roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL UNIQUE,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.roles IS 'User roles for access control';

-- User-role assignments
CREATE TABLE public.user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, role_id)
);

COMMENT ON TABLE public.user_roles IS 'Mapping between users and their assigned roles';

-- Permissions
CREATE TABLE public.permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL UNIQUE,
    description TEXT,
    module VARCHAR(180) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.permissions IS 'Available permissions in the system';

-- Role-permission assignments
CREATE TABLE public.role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES public.permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(role_id, permission_id)
);

COMMENT ON TABLE public.role_permissions IS 'Mapping between roles and their assigned permissions';

-- Create indexes
CREATE INDEX idx_user_roles_user_id ON public.user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON public.user_roles(role_id);
CREATE INDEX idx_role_permissions_role_id ON public.role_permissions(role_id);
CREATE INDEX idx_permissions_module ON public.permissions(module);

-- Insert default roles
INSERT INTO public.roles (name, description, is_system_role)
VALUES 
    ('System Administrator', 'Full access to all system functions', TRUE),
    ('User', 'Standard user with basic access', TRUE),
    ('Manager', 'Access to manage teams and view reports', TRUE),
    ('Developer', 'Access to development tools and APIs', TRUE),
    ('Analyst', 'Access to analytics and reporting', TRUE);

-- Insert default permissions
INSERT INTO public.permissions (name, description, module)
VALUES
    ('user.create', 'Create new users', 'core'),
    ('user.read', 'View user information', 'core'),
    ('user.update', 'Update user information', 'core'),
    ('user.delete', 'Delete users', 'core'),
    ('role.manage', 'Manage roles and permissions', 'core'),
    ('settings.manage', 'Manage system settings', 'core'),
    ('api.access', 'Access API endpoints', 'core'),
    ('lore.read', 'Access knowledge base', 'lore'),
    ('lore.write', 'Create and update knowledge', 'lore'),
    ('lore.admin', 'Administer knowledge base', 'lore'),
    ('agent.create', 'Create new agents', 'superagi'),
    ('agent.execute', 'Execute agent workflows', 'superagi'),
    ('agent.manage', 'Manage agent configurations', 'superagi');

-- Assign permissions to roles
INSERT INTO public.role_permissions (role_id, permission_id)
SELECT 
    r.id, 
    p.id
FROM 
    public.roles r,
    public.permissions p
WHERE 
    r.name = 'System Administrator';

-- Assign basic permissions to User role
INSERT INTO public.role_permissions (role_id, permission_id)
SELECT 
    r.id, 
    p.id
FROM 
    public.roles r,
    public.permissions p
WHERE 
    r.name = 'User' AND
    p.name IN ('user.read', 'lore.read', 'agent.execute');
