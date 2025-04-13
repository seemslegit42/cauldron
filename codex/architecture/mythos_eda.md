# Cauldron™ API Codex V1.0 - Foundations

**Purpose:** This document defines the standards, conventions, structure, and initial known endpoints for the synchronous APIs (primarily RESTful) within the Cauldron™ Sentient Enterprise Operating System (sEOS). It serves as the foundational guide for developers building or consuming these APIs.

**Scope:** This initial version focuses on establishing standards and outlining the core APIs identified in Phase 1 of development. Detailed endpoint specifications (request/response schemas, parameters) will be added iteratively as APIs are implemented, ideally using OpenAPI Specification (OAS) V3.x.

**Audience:** Developers (Backend, Frontend, Agent), AI Agents, System Architects, Integrators.

---

## 1. API Standards & Conventions

* **Specification:** All RESTful APIs MUST be documented using the **OpenAPI Specification (OAS) V3.x**. Schema definitions should accompany endpoint definitions. These specs should ideally be auto-generated from code annotations where possible (e.g., via FastAPI, Frappe integrations) and stored alongside the service code or in `/codex/apis/specs/`.
* **Data Format:** All API request and response bodies MUST use **JSON** (`application/json`).
* **Naming Conventions:**
    * Endpoints paths SHOULD use `kebab-case` (lowercase, hyphen-separated).
    * JSON property names SHOULD use `snake_case` (lowercase, underscore-separated).
    * Resource paths SHOULD represent nouns (e.g., `/tasks`, `/documents`).
    * Use standard HTTP verbs appropriately (GET, POST, PUT, PATCH, DELETE).
* **Error Handling:** APIs MUST return standard HTTP status codes to indicate success or failure. Error responses SHOULD follow a consistent JSON structure, including at minimum an `error_code` (machine-readable string) and an `error_message` (human-readable string). Example:
    ```json
    {
      "error_code": "INVALID_INPUT",
      "error_message": "Task ID format is incorrect.",
      "details": { ... } // Optional additional context
    }
    ```
* **Idempotency:** For `PUT` and `DELETE` requests, strive for idempotency. For `POST` requests that create resources, consider mechanisms to prevent duplicate creation if necessary (though often handled by client logic or unique constraints).

---

## 2. Authentication & Authorization

* **Primary Mechanism:** All protected API endpoints MUST be secured using **JWT Bearer Token** authentication.
* **Token Source:** Tokens are issued by **Supabase Auth**.
* **Transmission:** Clients MUST include the JWT in the `Authorization` HTTP header using the `Bearer` scheme:
    `Authorization: Bearer <your_supabase_jwt>`
* **Enforcement:** Authentication MUST be enforced at the **API Gateway** level. Backend services receive validated user identity information (e.g., user ID, roles) from the Gateway or directly validate the passed token using Supabase's public keys.
* **Authorization:** Fine-grained authorization (determining *what* an authenticated user can do) SHOULD be handled within the service logic, potentially leveraging centrally managed policies (e.g., via OPA integration) based on user roles or attributes passed from the authentication layer.

---

## 3. API Versioning

* All Cauldron™ APIs MUST be versioned to allow for backward-incompatible changes without breaking existing clients.
* **Strategy:** Use **URL path versioning**. All API endpoints will be prefixed with `/api/v{version_number}`.
* **Initial Version:** The initial version for all APIs will be **v1**.
* **Example:** `https://api.cauldron.tld/api/v1/aether/tasks`

---

## 4. Codex Structure

* This document (`codex/apis/README.md` or similar) serves as the entry point and defines global standards.
* Detailed specifications for each service's API will reside in separate files within `/codex/apis/` or be linked from here.
* **Example Structure:**
    * `/codex/apis/README.md` (This file)
    * `/codex/apis/aether_core_api.md` (Or link to OpenAPI spec)
    * `/codex/apis/lore_api.md` (Or link to OpenAPI spec)
    * `/codex/apis/synapse_api.md` (Or link to OpenAPI spec)
    * `/codex/apis/erpnext_core_api.md` (Reference guide for relevant ERPNext endpoints)
    * `/codex/apis/specs/` (Optional: Directory for storing generated OAS files)

---

## 5. Core Service APIs (Phase 1 - Initial Endpoints)

This section outlines the initial key APIs identified during Phase 1 development. Detailed specifications will be added as they are built.

### 5.1. AetherCore API (`/api/v1/aether`)

* **Purpose:** Manages AI Agent tasks and orchestration.
* **Key Endpoints (Initial):**
    * `POST /tasks`: Submit a new task for agent execution.
    * `GET /tasks`: List existing tasks (with filtering/pagination).
    * `GET /tasks/{task_id}`: Get the status and details of a specific task.
    * `POST /tasks/{task_id}/approve`: (Warden Action) Approve a task awaiting HITL review.
    * `POST /tasks/{task_id}/reject`: (Warden Action) Reject a task awaiting HITL review.
    * `GET /agents`: List available/registered agents (TBD).
    * `GET /agents/{agent_id}`: Get details of a specific agent (TBD).

### 5.2. Lore API (`/api/v1/lore`)

* **Purpose:** Handles knowledge ingestion and Retrieval-Augmented Generation (RAG).
* **Key Endpoints (Initial):**
    * `POST /documents`: Ingest new document content for processing and embedding. Accepts file uploads or text content.
    * `POST /query`: Perform a RAG query. Takes a user query, retrieves relevant context from the Vector DB (`Obsidian Index`), and returns an LLM-synthesized answer.
    * `GET /documents/{document_id}`: Retrieve metadata or status of an ingested document (TBD).

### 5.3. Synapse API (`/api/v1/synapse`)

* **Purpose:** Serves processed Business Intelligence data and potentially predictive insights.
* **Key Endpoints (Initial):**
    * `GET /bi/sales_summary`: Example endpoint to retrieve aggregated sales data.
    * `GET /bi/customer_value/{customer_id}`: Example endpoint for customer-specific metrics.
    * *(More endpoints to be defined based on specific BI models and dashboard needs)*

### 5.4. ERPNext Core API (`/api/resource` or `/api/method` via Frappe)

* **Purpose:** Provides access to core ERP data and functions within ERPNext. Cauldron™ services will interact with these standard APIs.
* **Key Endpoints (Reference):** Cauldron™ will primarily use standard Frappe REST API endpoints:
    * `GET /api/resource/{Doctype}`: List records.
    * `POST /api/resource/{Doctype}`: Create a new record.
    * `GET /api/resource/{Doctype}/{name}`: Read a specific record.
    * `PUT /api/resource/{Doctype}/{name}`: Update a specific record.
    * `DELETE /api/resource/{Doctype}/{name}`: Delete a specific record.
    * `POST /api/method/{method_path}`: Call specific whitelisted server-side methods.
* **Documentation:** Refer to the official [Frappe REST API Documentation](https://frappeframework.com/docs/user/en/api/rest) and ERPNext specific DocTypes for details. Key DocTypes for Cauldron™ include `User`, `Item`, `Sales Order`, `Purchase Invoice`, `Customer`, `Supplier`, etc.

---

## 6. Asynchronous Communication (Mythos EDA)

* For asynchronous operations, status updates, and decoupled communication between services and agents, Cauldron™ uses the **`Mythos` Event-Driven Architecture** (Kafka/RabbitMQ).
* Refer to the **Agent Interaction Playbook** (`cauldron_agent_playbook_v1`) and the event schema definitions (likely in `/codex/architecture/event_schemas.md`) for details on asynchronous communication patterns and message formats. APIs should generally be used for synchronous request/response interactions, while EDA handles background processing triggers and broadcasts.

---

*This API Codex will evolve alongside Cauldron™. Ensure implementations adhere to these standards.*
