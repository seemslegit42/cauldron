# Cauldron™ Codebase Context Guide for AI Agents

**Objective:** Provide essential context for AI agents analyzing, modifying, or generating code within the Cauldron™ Sentient Enterprise Operating System (sEOS) project. This guide outlines the core vision, architecture, structure, naming conventions, and key technologies.

**Version:** 1.0

---

## 1. Core Vision & Paradigm

* **Project:** Cauldron™ Sentient Enterprise Operating System (sEOS).
* **Goal:** An integrated, AI-driven platform that autonomously adapts and optimizes core business functions based on human strategic intent.
* **Paradigm:** Agent-First Design. Autonomous AI agents (based on SuperAGI core) are the primary orchestrators, coordinated by the `AetherCore` service. Humans provide goals and oversight.
* **Branding:** "Radical Arcana™" - Expect unique, thematic naming conventions (see Lexicon).

---

## 2. Core Architecture Overview

* **Foundation:** OpenSaaS, leveraging best-of-breed open-source components.
* **Backend:** Centered on the **Frappe Framework (Python)**.
    * **ERP Core:** Leverages standard **ERPNext** application (`frappe-bench/apps/erpnext`).
    * **Custom Cauldron™ Modules:** Implemented as **custom Frappe Applications** (`frappe-bench/apps/cauldron_*`) for domains like DevOps (`Command & Cauldron`), BI (`Synapse`), Security (`Aegis Protocol`), KM (`Lore`).
* **Database Layer (`HexaGrid` Concept):** PostgreSQL (Primary Relational), Supabase (BaaS/Auth), Vector DB (for `Lore`), Time-Series DB (for `Synapse`/`Aegis`).
* **Integration Fabric (`Mythos` EDA):** Event-Driven Architecture using **Kafka** or **RabbitMQ** for primary async communication. REST APIs supplement this. `n8n` for external/simple workflows.
* **Frontend (`Manifold` UI):** React framework with Ant Design Pro component library.
* **Agent Orchestration (`AetherCore`):** Dedicated service (likely Python/FastAPI) managing SuperAGI-based agents.
* **Developer Portal:** Backstage.io (planned).

---

## 3. Key Directory Structure (Root Level)

* `aether_core/`: Agent Orchestration service code.
* `domains/`: May hold non-Frappe helper logic related to modules (primary module code is in `frappe-bench/apps/`).
* `manifold/`: Frontend UI code (React/AntD Pro).
* `infra/`: Infrastructure as Code (Terraform).
* `codex/`: Project documentation (YOU ARE HERE!).
* `scripts/`: Utility shell scripts.
* `frappe-bench/`: Frappe Bench directory containing `apps/` (erpnext, frappe, cauldron_* apps) and `sites/`.

---

## 4. Core Modules & Services Purpose

* **ERPNext:** Standard ERP functions. Foundation for `Operations Core`.
* **`cauldron_operations_core`:** Extends ERPNext for Cauldron specifics.
* **`Synapse` (`cauldron_synapse`):** BI, prediction, recommendations.
* **`Aegis Protocol` (`cauldron_aegis_protocol`):** Cybersecurity detection, analysis, response coordination.
* **`Lore` (`cauldron_lore`):** Knowledge Management, RAG, insight synthesis.
* **`Command & Cauldron` (`cauldron_command_cauldron`):** DevOps orchestration, CI/CD integration.
* **`AetherCore`:** Manages agent lifecycle, tasks, HITL.
* **`Manifold`:** Primary UI, dashboards (`Runestone`), command palette, XAI (`Arcana`).
* **API Gateway:** Manages external API traffic, routing, auth.

---

## 5. Naming Conventions ("Radical Arcana™")

* Expect thematic names. Refer to `codex/lexicon.md` for definitions.
* Examples: `Mythos` (EDA), `Runestone` (Dashboard), `Relics` (Connectors), `Sigils` (Modules).

---

## 6. Technology Stack Summary

* **Backend:** Frappe/Python, ERPNext
* **Frontend:** React, Ant Design Pro
* **Agent Framework:** SuperAGI/Python
* **Agent Orchestration:** FastAPI/Python (likely)
* **Databases:** PostgreSQL, Supabase, Vector DB, Time-Series DB
* **EDA:** Kafka or RabbitMQ
* **Infrastructure:** Docker, Kubernetes, Terraform
* **Secrets:** Vault or Cloud Provider equivalent
* **Dev Portal:** Backstage.io

---

## 7. Integration Patterns

* **Async:** Primarily via `Mythos` EDA (Kafka/RabbitMQ). Refer to `Agent Interaction Playbook` and `event_schemas.md`.
* **Sync:** Via REST APIs (Frappe standard APIs, custom module APIs) managed through API Gateway. Refer to `API Codex`.
* **Database:** Direct Postgres interaction common. Supabase APIs for BaaS features. Avoid direct cross-service DB calls; use EDA/API.

---

## 8. Key Guiding Principles (Affecting Code)

* **Agent-First:** Logic often involves interacting with `AetherCore` or reacting to agent events via EDA.
* **API-First:** Expose functionality via APIs or EDA events.
* **Zero Trust:** Expect strict AuthN/AuthZ checks. Handle failures.
* **Ethical Guardrails:** High-risk agent operations require HITL checks or adherence to constraints (see `codex/governance/`).
* **Immutable Auditing:** Produce detailed, structured logs.

---

**Conclusion:** Use this guide for orientation. Refer to detailed documents in `/codex` for specifics.
