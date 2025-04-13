# Module Grimoire: Operations Core (ERPNext Extensions) V1.0

## 1. Overview & Purpose

The **Operations Core** module serves as the foundational layer for Cauldron™'s interaction with core enterprise resource planning (ERP) functions. It leverages the robust capabilities of **ERPNext** (built on the **Frappe Framework**) and extends them via a custom Frappe App (`cauldron_operations_core`) to integrate seamlessly with the broader sEOS vision, particularly enabling AI Agents to interact with and automate operational processes.

**Analogy:** The Engine Room – Provides the fundamental power and machinery for day-to-day business operations.

## 2. Scope & Boundaries

*   **In Scope:**
    *   Standard ERPNext functionalities (Finance, Accounting, Sales, Purchasing, Inventory, HR basics).
    *   Customizations within the `cauldron_operations_core` app to support sEOS integration (e.g., custom fields, workflows, API endpoints).
    *   Defining and exposing stable APIs (standard Frappe REST API + custom endpoints) for interaction by AI Agents and other modules.
    *   Publishing relevant business events to the **Mythos EDA**.
    *   Implementing necessary UI elements within ERPNext (via custom scripts/pages) or providing data for **Manifold** related to core operations.
*   **Out of Scope:**
    *   Advanced BI, prediction, simulation (Handled by **Synapse**).
    *   Knowledge management, RAG (Handled by **Lore**).
    *   Cybersecurity monitoring and response (Handled by **Aegis Protocol**).
    *   DevOps automation, CI/CD (Handled by **Command & Cauldron**).
    *   Agent orchestration (Handled by **AetherCore**).

## 3. Key Features & Functionalities (Phased Approach)

*   **Phase 1 (Foundation):**
    *   Stable deployment of core ERPNext modules.
    *   Basic configuration reflecting the target enterprise structure.
    *   Implementation of the `cauldron_operations_core` Frappe app structure.
    *   Defining initial custom fields needed for agent interaction or tracking (e.g., `agent_managed` flag, `last_agent_action_id`).
    *   Basic event publishing to Mythos for key transactions (e.g., `order.created`, `invoice.submitted`).
    *   Exposing standard Frappe REST API for basic CRUD operations by authorized agents/services.
*   **Phase 2 (Agent Assistance):**
    *   Developing custom API endpoints for specific, common agent tasks (e.g., API to trigger invoice payment run based on parameters).
    *   Implementing simple agent-driven workflows with mandatory HITL (e.g., Agent drafts purchase order based on low stock, requires Warden approval via Manifold before submission).
    *   Enriching Mythos events with more contextual data.
    *   Adding custom dashboards/views within ERPNext or providing data for Manifold showing agent activity related to operations.
*   **Phase 3+ (Towards Autonomy - High Risk/Complexity):**
    *   **"Self-Driving" Finance (Conceptual Goal):** Agents performing tasks like automated invoice processing, payment matching, GL reconciliation, potentially basic financial reporting generation (with heavy oversight and validation).
    *   **Adaptive Supply Chain (Conceptual Goal):** Agents analyzing inventory levels, sales forecasts (from Synapse), lead times, and automatically suggesting or (with approval) creating purchase orders, stock transfers, or production orders.
    *   **Automated HR Processes (Conceptual Goal):** Agents assisting with onboarding task checklists, leave request processing (within defined rules).
    *   **Requires:** Advanced agent capabilities, robust guardrails, sophisticated XAI, mature governance, reliable data feeds. Requires rigorous validation.

## 4. Technical Architecture & Implementation

*   **Framework:** Frappe Framework (Python).
*   **Base Application:** ERPNext.
*   **Custom Code:** Resides within the `cauldron_operations_core` Frappe App located in `frappe-bench/apps/`.
*   **Key Components:**
    *   **Custom DocTypes:** If needed beyond standard ERPNext DocTypes (minimize where possible).
    *   **Custom Fields:** Added to existing ERPNext DocTypes via "Customize Form" or fixtures.
    *   **Server Scripts (Python):** Implement custom business logic, validation rules, triggered on DocType events (Save, Submit, Cancel).
    *   **API Endpoints (Python):** Defined using Frappe's `@frappe.whitelist()` decorator for custom REST API endpoints.
    *   **Scheduled Jobs (Python):** For background processing or periodic tasks related to operations.
    *   **Client Scripts (JavaScript):** For UI customizations within the standard ERPNext interface (use sparingly, prefer Manifold for major UI).
    *   **Event Producers (Python):** Code within Server Scripts or hooks to publish standardized events to Mythos.

## 5. Data Model

*   Primarily leverages the extensive **standard DocTypes** provided by ERPNext (e.g., `Sales Order`, `Purchase Invoice`, `Journal Entry`, `Item`, `Customer`, `Supplier`, `Employee`).
*   Custom fields will be added to these standard DocTypes as needed for sEOS integration.
*   Avoid creating redundant custom DocTypes if an existing ERPNext DocType can be adapted.

## 6. Integration Points

*   **Manifold UI:** Via REST APIs (standard Frappe API + custom endpoints exposed by `cauldron_operations_core`).
*   **AI Agents (via AetherCore):** Primarily via REST APIs for performing actions (CRUD, custom actions).
*   **Mythos EDA:** Publishes business events; may consume limited events if needed for specific operational triggers (use with caution to avoid tight coupling).
*   **Synapse:** Consumes operational events from Mythos for analysis.
*   **Aegis Protocol:** Consumes operational events relevant to security/fraud monitoring.

## 7. Security & Governance Considerations

*   **Permissions:** Relies heavily on Frappe's built-in Role-Based Permissions system. Ensure agent service accounts have appropriately restricted permissions.
*   **API Security:** Standard Frappe API authentication + authorization applies. Custom endpoints must implement permission checks (`frappe.has_permission`).
*   **HITL:** Mandatory HITL checkpoints must be implemented (either in agent logic or via Frappe workflows requiring specific roles) before agents perform high-impact financial or operational actions.
*   **Auditing:** Leverage Frappe's built-in audit trails (`_version` table) and supplement with detailed event publishing to Mythos.

The Operations Core provides the essential operational foundation upon which Cauldron's intelligence is built. Stability, clear APIs, and robust eventing are paramount.