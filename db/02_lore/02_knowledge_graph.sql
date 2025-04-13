-- Lore module - Knowledge graph

-- Knowledge graph entities
CREATE TABLE lore.entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lore.entities IS 'Entities in the knowledge graph';

-- Knowledge graph relationships
CREATE TABLE lore.relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_entity_id UUID NOT NULL REFERENCES lore.entities(id) ON DELETE CASCADE,
    target_entity_id UUID NOT NULL REFERENCES lore.entities(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}',
    confidence FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lore.relationships IS 'Relationships between entities in the knowledge graph';

-- Entity types
CREATE TABLE lore.entity_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lore.entity_types IS 'Types of entities in the knowledge graph';

-- Relationship types
CREATE TABLE lore.relationship_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    source_types TEXT[] DEFAULT '{}',
    target_types TEXT[] DEFAULT '{}',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lore.relationship_types IS 'Types of relationships in the knowledge graph';

-- Entity-document associations
CREATE TABLE lore.entity_document_associations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES lore.entities(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES lore.documents(id) ON DELETE CASCADE,
    confidence FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(entity_id, document_id)
);

COMMENT ON TABLE lore.entity_document_associations IS 'Mapping between entities and their source documents';

-- Entity mentions in documents
CREATE TABLE lore.entity_mentions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES lore.entities(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES lore.documents(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES lore.document_chunks(id) ON DELETE CASCADE,
    start_offset INTEGER,
    end_offset INTEGER,
    mention_text TEXT NOT NULL,
    confidence FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lore.entity_mentions IS 'Specific mentions of entities within documents';

-- Create indexes
CREATE INDEX idx_entities_entity_type ON lore.entities(entity_type);
CREATE INDEX idx_relationships_source_entity_id ON lore.relationships(source_entity_id);
CREATE INDEX idx_relationships_target_entity_id ON lore.relationships(target_entity_id);
CREATE INDEX idx_relationships_relationship_type ON lore.relationships(relationship_type);
CREATE INDEX idx_entity_document_associations_entity_id ON lore.entity_document_associations(entity_id);
CREATE INDEX idx_entity_document_associations_document_id ON lore.entity_document_associations(document_id);
CREATE INDEX idx_entity_mentions_entity_id ON lore.entity_mentions(entity_id);
CREATE INDEX idx_entity_mentions_document_id ON lore.entity_mentions(document_id);
CREATE INDEX idx_entity_mentions_chunk_id ON lore.entity_mentions(chunk_id);

-- Create a HNSW index for entity embeddings
CREATE INDEX ON lore.entities USING hnsw (embedding vector_cosine_ops);

-- Insert default entity types
INSERT INTO lore.entity_types (name, description, properties)
VALUES
    ('Person', 'A person or individual', '{"attributes": ["name", "title", "organization", "expertise"]}'),
    ('Organization', 'A company, institution, or group', '{"attributes": ["name", "industry", "location", "size"]}'),
    ('Concept', 'An abstract idea or notion', '{"attributes": ["name", "domain", "definition"]}'),
    ('Technology', 'A technology, tool, or platform', '{"attributes": ["name", "category", "version", "vendor"]}'),
    ('Process', 'A business process or workflow', '{"attributes": ["name", "domain", "steps", "owner"]}'),
    ('Location', 'A physical or virtual location', '{"attributes": ["name", "type", "coordinates"]}');

-- Insert default relationship types
INSERT INTO lore.relationship_types (name, description, source_types, target_types)
VALUES
    ('WORKS_FOR', 'Employment relationship', ARRAY['Person'], ARRAY['Organization']),
    ('KNOWS', 'Knowledge or expertise in a subject', ARRAY['Person'], ARRAY['Concept', 'Technology', 'Process']),
    ('PART_OF', 'Component or membership relationship', ARRAY['Person', 'Organization', 'Concept', 'Process'], ARRAY['Organization', 'Concept', 'Process']),
    ('USES', 'Usage relationship', ARRAY['Person', 'Organization', 'Process'], ARRAY['Technology', 'Process']),
    ('LOCATED_IN', 'Physical or logical location', ARRAY['Person', 'Organization'], ARRAY['Location']),
    ('RELATED_TO', 'General relationship', NULL, NULL);
