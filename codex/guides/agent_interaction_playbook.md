# Cauldron™ Agent Interaction Playbook V1.0

**Purpose:** To define the standard protocols and patterns for communication and interaction for all AI Agents (`Constructs`) operating within the Cauldron™ Sentient Enterprise Operating System (sEOS). Adherence to this playbook ensures consistency, reliability, and effective orchestration via `AetherCore`.

**Audience:** AI Agent Developers, AI Agents (as operational context), System Architects, Wardens (for understanding expected behavior).

---

## 1. Core Principles

* **EDA First:** Primary communication (task assignments, status updates, results, errors) MUST occur asynchronously via the `Mythos` Event-Driven Architecture (EDA - Kafka/RabbitMQ) unless a synchronous API interaction is explicitly required and defined for a specific use case.
* **`AetherCore` as Hub:** Agents primarily interact with `AetherCore` (often indirectly via `Mythos`) for tasking, status reporting, and HITL coordination. Direct inter-agent communication should be avoided initially; use `Mythos` events or mediated requests through `AetherCore` if necessary.
* **Standard Schemas:** All communication via `Mythos` MUST adhere to the defined event schemas (refer to `codex/architecture/event_schemas.md`).
* **Statefulness:** Agents may maintain internal state for complex tasks but MUST report key status transitions via `Mythos`. `AetherCore` tracks the canonical state of tasks.
* **Clarity & Context:** All reports (status, results, errors) MUST include sufficient context, primarily the unique `task_id`.

---

## 2. Task Handling

1.  **Task Reception:**
    * Agents receive new tasks primarily by subscribing to a specific `Mythos` topic designated by `AetherCore` (e.g., `cauldron.agent.task.assigned.<agent_id>`).
    * The event payload will contain the task details, adhering to the `AgentTask` schema defined in `AetherCore` (including `task_id`, `input_data`, `priority`, etc.).
    * **Example Envelope Ref:** See `codex/architecture/event_schemas.md` for `cauldron.agent.task.assigned` details.

2.  **Task Acknowledgement:**
    * Upon successfully receiving and parsing a task assignment, the Agent SHOULD publish a status update event to `Mythos` with status `RECEIVED`.
    * **Topic:** `cauldron.agent.status.update`
    * **Payload Example Ref:** See `codex/architecture/event_schemas.md`. Key fields: `task_id`, `agent_id`, `timestamp`, `status: "RECEIVED"`, `details`.

---

## 3. Status Reporting

1.  **Mandatory Updates:** Agents MUST report status changes via `Mythos` events (`cauldron.agent.status.update`) for key state transitions.
2.  **Standard Statuses:** `RECEIVED`, `IN_PROGRESS`, `AWAITING_HITL`, `COMPLETED`, `FAILED`, `RETRYING`. (See Lexicon for definitions).
3.  **Update Frequency:** Report key transitions promptly. Intermediate `IN_PROGRESS` updates based on task duration/complexity.
4.  **Payload Content:** MUST include `task_id`, `agent_id`, `timestamp`, `status`. SHOULD include contextual `details`.

---

## 4. Result Reporting

1.  **Mechanism:** Final results for successfully completed tasks MUST be reported via a dedicated `Mythos` event (e.g., `cauldron.agent.result.success`).
2.  **Payload Content:** MUST include `task_id`, `agent_id`, `timestamp`, and `result_data` (task-specific output structure). See `event_schemas.md`.
3.  **Final Status:** Publish a `COMPLETED` status update alongside or just after the result event.

---

## 5. Human-in-the-Loop (HITL) Workflow

1.  **Triggering HITL:** Agent determines approval needed (config, confidence, guardrail). Publishes `AWAITING_HITL` status update event. `details` field explains proposal. May publish supplementary data via specific mechanism defined by `AetherCore`.
2.  **Pausing Execution:** Agent MUST pause relevant execution while `AWAITING_HITL`.
3.  **Receiving Decision:** Agent receives decision (Approve/Reject) via `Mythos` event from `AetherCore` (e.g., `cauldron.agent.hitl.response`).
4.  **Resuming Execution:** Proceed with approved action or handle rejection (alternative path, report `FAILED`, or await further guidance). Report subsequent status.

---

## 6. Error Handling & Reporting

1.  **Internal Handling:** Implement reasonable internal error handling (try/except). Attempt retries based on task metadata (`max_retries`), publishing `RETRYING` status.
2.  **Reporting Failure:** If task fails definitively, MUST publish `FAILED` status update AND a dedicated error event (e.g., `cauldron.agent.error.occurred`).
3.  **Error Event Content:** MUST include `task_id`, `agent_id`, `timestamp`, `error_message`, `error_type`. SHOULD include relevant `error_details` (context, safe stack trace snippet). See `event_schemas.md`.

---

## 7. Inter-Agent Communication (Phase 3+ Pattern)

* **Initial Approach:** Avoid direct agent-to-agent calls. Use `Mythos` events or request `AetherCore` to orchestrate tasks for other agents.
* **Future Pattern (If Needed):** Define standard request/response patterns over dedicated `Mythos` topics if direct interaction proves necessary (requires architectural approval).

---

## 8. Resource & Security Context

* **Resource Limits:** Operate within constraints communicated by `AetherCore` or environment.
* **Credentials:** DO NOT manage secrets. Credentials provided securely by platform (`AetherCore`/Vault/Codespaces Secrets) at runtime.

---

*Adherence to this playbook is mandatory for all agents integrated into the Cauldron™ sEOS.*
