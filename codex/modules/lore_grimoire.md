# Module Grimoire: Lore™ (Collective Intelligence) V1.0

**Document Version:** 1.0
**Status:** Foundational Draft
**Module Owner:** (To Be Assigned)
**Related Frappe App:** `cauldron_lore`

## 1. Introduction & Purpose

`Lore™` serves as the central hub for Collective Intelligence and Knowledge Synthesis within the Cauldron™ sEOS. Its primary purpose is to ingest, process, index, and retrieve information from designated knowledge sources, making organizational knowledge readily accessible and actionable through advanced AI techniques like Retrieval-Augmented Generation (RAG).

`Lore` aims to function as the "Ambient Organizational Memory," providing contextual answers, proactively surfacing relevant information, mapping expertise, and (in later phases, with strict ethical oversight) synthesizing novel insights from the collective data stream.

## 2. Core Technology

* **Framework:** Built as a **custom Frappe Application** (`cauldron_lore`) within the Frappe Framework (Version 15+).
* **Primary Language:** Python.
* **Key Libraries:** Heavy use of NLP libraries (Hugging Face `transformers`, `sentence-transformers`), text processing libraries, Vector Database clients (`qdrant-client`, `pgvector`), LLM client libraries (`openai`, `anthropic`). Frameworks like LangChain/LlamaIndex might be used.
* **Database:** Utilizes shared PostgreSQL via Frappe ORM. Relies heavily on a dedicated **Vector Database** (`Obsidian Index`).

## 3. Scope & Boundaries

* **In Scope:** Knowledge source configuration, document ingestion/chunking/embedding, Vector DB (`Obsidian Index`) management, RAG query processing, contextual info surfacing, insight synthesis coordination (via agents), skill mapping logic, publishing/consuming relevant `Mythos` events.
* **Out of Scope:** Being the primary document storage (relies on sources like Nextcloud), agent orchestrator (`AetherCore`), BI engine (`Synapse`), security analysis (`Aegis`).

## 4. Key Features & Functionality (Phased Vision)

* **Phase 1 (Foundation - "Ambient Organizational Memory" v1):** Core RAG pipeline (Ingest from Nextcloud, embed, store in VectorDB, `/query` API for Q&A using LLM synthesis), basic `Manifold` integration for queries.
* **Phase 2 (Context & Synthesis v1):** Contextual awareness hook for `Manifold` (proactive info surfacing), initial "Emergent Insight Synthesis" agent (pattern detection on *non-sensitive, aggregated* metadata - requires ethical review), initial "Dynamic Skill Mapping" (based on ERPNext data).
* **Phase 3+ Goals (Advanced Insights & Proactivity):** Enhanced RAG (better retrieval, multi-source fusion), more sophisticated Insight Synthesis (requires *strict* ethical review/consent if analyzing communications), improved proactive surfacing, refined Skill Mapping (more data sources).

## 5. Key Components & Logic (in `cauldron_lore`)

* **Custom DocTypes:** `KnowledgeSource`, `IngestedDocument`, `EmbeddingModelConfig`, `VectorDBConfig`, `KnowledgeQueryLog`, `SynthesizedInsight`, `SkillProfile`, `ExpertiseMapping`.
* **Custom Scripts (Python):** Ingestion Pipeline (fetch, parse, chunk, embed, store), RAG Query Handler (`/query` API logic), Contextual Hook Logic (`/contextual_info` API), Insight Analysis Trigger (prepares data, triggers agent), Skill Mapping Engine.
* **`Relics` (Connectors):** `NextcloudRelic` (mandatory), potentially others (Confluence, SharePoint, etc.).

## 6. Data Models

* Stores config/metadata in custom DocTypes (Section 5) in PostgreSQL.
* Relies heavily on the **Vector Database** (`Obsidian Index`) for text embeddings.
* Reads contextual data from ERPNext (`User`, `Project`, `Task`).

## 7. Agent Interactions

* **Lore Initiates Tasks (via `Mythos` -> `AetherCore`):** Triggers `InsightSynthesisAgent`, `SkillAnalysisAgent`, potentially `KnowledgeGraphAgent`. Provides data pointers/parameters.
* **Lore Consumes Agent Responses (via `Mythos`):** Updates `SynthesizedInsight` or `ExpertiseMapping` based on agent results.
* **Other Agents Utilize Lore (via API):** Call `/query` API for RAG capabilities or skill lookups.

## 8. Integration Points

* **APIs Exposed:** REST API for RAG queries (`/query`), contextual info (`/contextual_info`), document ingestion (`/documents`), skill lookups. Used by `Manifold` and other agents.
* **APIs Consumed:** Nextcloud API (via `NextcloudRelic`), LLM APIs (OpenAI, Anthropic, etc.), potentially ERPNext/C&C/HR APIs for skill data.
* **EDA (`Mythos`) Events:** Publishes `document.indexed`, `insight.generated`, `skill_map.updated`. Publishes tasks for agents. Consumes events indicating new knowledge sources, agent results.
* **`AetherCore`:** Indirect interaction via EDA.
* **`Manifold`:** Provides RAG query UI, displays contextual info, insights, skills. Data served via Lore API.
* **Databases:** Heavy interaction with Vector DB. Reads/Writes metadata to PostgreSQL.

## 9. Non-Functional Requirements

* **Scalability:** Ingestion pipeline and Vector DB must scale.
* **Accuracy:** RAG results must be relevant and accurate.
* **Privacy & Ethics:** CRITICAL. Strict adherence required, especially for insight synthesis. Requires Ethics Council oversight.
* **Performance:** Low latency RAG queries needed for interactive use.
* **Maintainability:** RAG pipelines/models need ongoing evaluation.

---

*This Grimoire details `Lore™`. Its success hinges on effective RAG implementation, robust data pipelines, Vector DB management, and unwavering attention to privacy and ethics.*
