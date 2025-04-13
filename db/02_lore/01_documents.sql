-- Lore module - Document management with vector embeddings

-- Knowledge documents
CREATE TABLE lore.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    source_url TEXT,
    source_type VARCHAR(50),
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    is_archived BOOLEAN DEFAULT FALSE
);

COMMENT ON TABLE lore.documents IS 'Knowledge documents in the Lore module';

-- Document chunks for embedding
CREATE TABLE lore.document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES lore.documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536), -- Dimension depends on embedding model
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

COMMENT ON TABLE lore.document_chunks IS 'Chunked documents with vector embeddings for semantic search';

-- Document categories
CREATE TABLE lore.document_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL UNIQUE,
    description TEXT,
    parent_id UUID REFERENCES lore.document_categories(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lore.document_categories IS 'Categories for organizing documents';

-- Document-category associations
CREATE TABLE lore.document_category_associations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES lore.documents(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES lore.document_categories(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, category_id)
);

COMMENT ON TABLE lore.document_category_associations IS 'Mapping between documents and categories';

-- Document tags
CREATE TABLE lore.document_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lore.document_tags IS 'Tags for documents';

-- Document-tag associations
CREATE TABLE lore.document_tag_associations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES lore.documents(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES lore.document_tags(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, tag_id)
);

COMMENT ON TABLE lore.document_tag_associations IS 'Mapping between documents and tags';

-- Document teams (for access control)
CREATE TABLE lore.document_teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES lore.documents(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES public.teams(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, team_id)
);

COMMENT ON TABLE lore.document_teams IS 'Teams with access to specific documents';

-- Document versions
CREATE TABLE lore.document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES lore.documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, version_number)
);

COMMENT ON TABLE lore.document_versions IS 'Historical versions of documents';

-- Create indexes
CREATE INDEX idx_documents_created_at ON lore.documents(created_at);
CREATE INDEX idx_documents_created_by ON lore.documents(created_by);
CREATE INDEX idx_document_chunks_document_id ON lore.document_chunks(document_id);
CREATE INDEX idx_document_category_associations_document_id ON lore.document_category_associations(document_id);
CREATE INDEX idx_document_category_associations_category_id ON lore.document_category_associations(category_id);
CREATE INDEX idx_document_tag_associations_document_id ON lore.document_tag_associations(document_id);
CREATE INDEX idx_document_tag_associations_tag_id ON lore.document_tag_associations(tag_id);
CREATE INDEX idx_document_teams_document_id ON lore.document_teams(document_id);
CREATE INDEX idx_document_teams_team_id ON lore.document_teams(team_id);
CREATE INDEX idx_document_versions_document_id ON lore.document_versions(document_id);

-- Create a HNSW index for fast similarity search
CREATE INDEX ON lore.document_chunks USING hnsw (embedding vector_cosine_ops);

-- Full-text search index
CREATE INDEX idx_documents_fts ON lore.documents USING GIN (to_tsvector('english', title || ' ' || content));
