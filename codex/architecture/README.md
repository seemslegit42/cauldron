# Cauldron™ Nexus Map V1.0 (Integration Mapping)

This document outlines the primary integration points and communication pathways between the core components of the Cauldron™ sEOS. It serves as a high-level map of how different parts of the system interact.

*(Note: A visual Mermaid diagram representation is planned for future iterations)*

## Core Interaction Patterns:

1.  **Manifold <> Backend Services (API Gateway / Direct):**
    *   The **Manifold UI** (React Frontend) primarily interacts with backend services via a central **API Gateway** (e.g., managed by `Command & Cauldron`).
    *   These interactions use synchronous **RESTful APIs** (defined in the `/codex/apis/`) for fetching data to display, submitting user commands, and triggering actions.
    *   Key interactions include fetching operational data from **Operations Core**, BI data from **Synapse**, knowledge from **Lore**, security status from **Aegis Protocol**, and DevOps info from **Command & Cauldron**. It also interacts with **AetherCore** to monitor/manage agents.
    *   Authentication is typically handled via JWT provided after login (e.g., via Supabase Auth).

2.  **Mythos EDA (Asynchronous Communication):**
    *   **Mythos** (Kafka/RabbitMQ) serves as the central nervous system for asynchronous communication. Modules and agents publish events to specific topics, and interested parties subscribe to consume them.
    *   **Operations Core** publishes events for significant business actions (e.g., `order.created`, `invoice.paid`).
    *   **Synapse** consumes operational events for analysis and publishes insights/forecasts/anomalies (e.g., `anomaly.detected`, `forecast.updated`).
    *   **Aegis Protocol** consumes events from various sources (Ops Core, C&C, external security tools via integrations) and publishes security alerts/incidents (e.g., `security.alert.high`, `incident.created`).
    *   **Lore** consumes events indicating new information sources and publishes events when knowledge summaries/insights are generated (e.g., `knowledge.summary.ready`).
    *   **Command & Cauldron** consumes events related to code commits, build statuses, deployment events and publishes pipeline statuses/results (e.g., `build.succeeded`, `deployment.failed`).
    *   **AetherCore** publishes agent status updates (`agent.status.updated`) and task assignments (`agent.task.assigned`) and consumes task completion/failure events (`agent.task.completed`, `agent.task.failed`).
    *   **AI Agents (Constructs)** subscribe to their assigned task topics on Mythos and publish status updates, results, or requests for HITL back via specific Mythos topics monitored by AetherCore and potentially Manifold.

3.  **AetherCore <> AI Agents:**
    *   **AetherCore** manages the lifecycle and tasking of **AI Agents**.
    *   Task assignment and status reporting primarily occur asynchronously via **Mythos**.
    *   Direct API calls might exist for specific agent management functions if needed, but EDA is preferred for decoupling.

4.  **Module <> Module (Internal APIs):**
    *   While EDA is preferred, some modules might expose internal REST APIs for specific synchronous data requests from other *authorized* modules if absolutely necessary (e.g., Synapse might directly query Lore for specific structured data needed for a forecast). These should be minimized to maintain loose coupling.

5.  **Data Layer Interaction:**
    *   Each primary module interacts with its designated data storage:
        *   **Operations Core, Synapse, Aegis Protocol, Command & Cauldron:** Primarily interact with the **Frappe Database** (MariaDB/Postgres underlying ERPNext).
        *   **Lore:** Primarily interacts with the **Vector Database** (e.g., Qdrant, Weaviate) for RAG indexes and potentially the Frappe DB for metadata.
        *   **AetherCore:** Interacts with its own database (likely **PostgreSQL via Supabase**) for agent state, task queues, etc.
        *   Time-sensitive data (e.g., system metrics, security events) might be pushed to a **Time-Series Database** (e.g., TimescaleDB, InfluxDB) by relevant modules (Aegis, C&C).

6.  **External Integrations (n8n / Custom):**
    *   Modules like **Aegis Protocol**, **Synapse**, or **Operations Core** may need to interact with external systems.
    *   **n8n** is planned as a primary tool for connecting to external SaaS APIs (e.g., sending Slack alerts, pulling data from external sources).
    *   Custom integration code within modules might be necessary for bespoke external systems.

This map highlights the centrality of the Mythos EDA for decoupling and asynchronous flow, complemented by synchronous APIs for direct requests, particularly from the Manifold UI. AetherCore acts as the agent hub, primarily interacting via Mythos.