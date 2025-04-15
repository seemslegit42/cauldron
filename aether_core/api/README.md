# AetherCore API

This directory contains the API endpoints for AetherCore, the agent orchestration system for Cauldron.

## API Structure

The API is organized into the following modules:

- `main.py`: Main FastAPI application entry point
- `agent_api.py`: Endpoints for agent management
- `task_api.py`: Endpoints for task management
- `hitl_api.py`: Endpoints for human-in-the-loop interactions
- `knowledge_api.py`: Endpoints for knowledge management
- `metrics_api.py`: Endpoints for metrics and monitoring

## Human-in-the-Loop (HITL) API

The HITL API provides endpoints for human-in-the-loop interactions, allowing agents to request human input when needed.

### Endpoints

#### Create HITL Request

```
POST /api/v1/hitl/requests
```

Create a new human-in-the-loop request.

**Request Body:**
```json
{
  "task_id": "string",
  "request_type": "string",
  "request_description": "string",
  "options": [
    {
      "option_id": "string",
      "option_text": "string",
      "option_details": {}
    }
  ],
  "timeout_seconds": 3600,
  "urgency": "normal"
}
```

**Response:**
```json
{
  "request_id": "string",
  "task_id": "string",
  "request_type": "string",
  "request_description": "string",
  "options": [],
  "status": "pending",
  "response": null,
  "response_details": {},
  "human_id": null,
  "created_at": "string",
  "updated_at": "string",
  "completed_at": null
}
```

#### Get HITL Requests

```
GET /api/v1/hitl/requests
```

Get all HITL requests.

**Query Parameters:**
- `limit` (integer, default: 100): Maximum number of requests to return
- `offset` (integer, default: 0): Number of requests to skip

**Response:**
```json
[
  {
    "request_id": "string",
    "task_id": "string",
    "request_type": "string",
    "request_description": "string",
    "options": [],
    "status": "string",
    "response": "string",
    "response_details": {},
    "human_id": "string",
    "created_at": "string",
    "updated_at": "string",
    "completed_at": "string"
  }
]
```

#### Get HITL Request

```
GET /api/v1/hitl/requests/{request_id}
```

Get a specific HITL request by ID.

**Path Parameters:**
- `request_id` (string): The ID of the HITL request to retrieve

**Response:**
```json
{
  "request_id": "string",
  "task_id": "string",
  "request_type": "string",
  "request_description": "string",
  "options": [],
  "status": "string",
  "response": "string",
  "response_details": {},
  "human_id": "string",
  "created_at": "string",
  "updated_at": "string",
  "completed_at": "string"
}
```

#### Respond to HITL Request

```
POST /api/v1/hitl/requests/{request_id}/respond
```

Provide a human response to a HITL request.

**Path Parameters:**
- `request_id` (string): The ID of the HITL request to respond to

**Request Body:**
```json
{
  "response": "string",
  "response_details": {},
  "human_id": "string"
}
```

**Response:**
```json
{
  "request_id": "string",
  "task_id": "string",
  "request_type": "string",
  "request_description": "string",
  "options": [],
  "status": "completed",
  "response": "string",
  "response_details": {},
  "human_id": "string",
  "created_at": "string",
  "updated_at": "string",
  "completed_at": "string"
}
```

#### Get HITL Requests for a Task

```
GET /api/v1/hitl/requests/task/{task_id}
```

Get all HITL requests for a specific task.

**Path Parameters:**
- `task_id` (string): The ID of the task

**Query Parameters:**
- `limit` (integer, default: 100): Maximum number of requests to return
- `offset` (integer, default: 0): Number of requests to skip

**Response:**
```json
[
  {
    "request_id": "string",
    "task_id": "string",
    "request_type": "string",
    "request_description": "string",
    "options": [],
    "status": "string",
    "response": "string",
    "response_details": {},
    "human_id": "string",
    "created_at": "string",
    "updated_at": "string",
    "completed_at": "string"
  }
]
```

#### Get HITL Requests by Status

```
GET /api/v1/hitl/requests/status/{status}
```

Get all HITL requests with a specific status.

**Path Parameters:**
- `status` (string): The status of the HITL requests to retrieve (e.g., "pending", "completed")

**Query Parameters:**
- `limit` (integer, default: 100): Maximum number of requests to return
- `offset` (integer, default: 0): Number of requests to skip

**Response:**
```json
[
  {
    "request_id": "string",
    "task_id": "string",
    "request_type": "string",
    "request_description": "string",
    "options": [],
    "status": "string",
    "response": "string",
    "response_details": {},
    "human_id": "string",
    "created_at": "string",
    "updated_at": "string",
    "completed_at": "string"
  }
]
```

#### Get HITL Requests by Type

```
GET /api/v1/hitl/requests/type/{request_type}
```

Get all HITL requests with a specific type.

**Path Parameters:**
- `request_type` (string): The type of the HITL requests to retrieve

**Query Parameters:**
- `limit` (integer, default: 100): Maximum number of requests to return
- `offset` (integer, default: 0): Number of requests to skip

**Response:**
```json
[
  {
    "request_id": "string",
    "task_id": "string",
    "request_type": "string",
    "request_description": "string",
    "options": [],
    "status": "string",
    "response": "string",
    "response_details": {},
    "human_id": "string",
    "created_at": "string",
    "updated_at": "string",
    "completed_at": "string"
  }
]
```

## Request Types

The HITL API supports various request types, including:

- `approval`: Request approval for an action
- `information`: Request additional information
- `clarification`: Request clarification on a task
- `decision`: Request a decision between options
- `feedback`: Request feedback on a result
- `custom`: Custom request type

## Integration with Agent Orchestration

The HITL API is integrated with the Agent Orchestration Service, which manages the lifecycle of HITL requests. When an agent needs human input, it creates a HITL request through the Agent Orchestration Service, which then publishes a message to the message broker. The HITL API provides endpoints for humans to view and respond to these requests.

## WebSocket Support

In addition to the REST API, AetherCore provides WebSocket support for real-time notifications of HITL requests. Clients can subscribe to the WebSocket endpoint to receive notifications when new HITL requests are created or when existing requests are updated.

```
WebSocket: /ws/hitl
```

## Example Usage

### Creating a HITL Request

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/hitl/requests",
    json={
        "task_id": "123e4567-e89b-12d3-a456-426614174000",
        "request_type": "approval",
        "request_description": "Please approve the following action: Delete user account",
        "options": [
            {
                "option_id": "approve",
                "option_text": "Approve",
                "option_details": {"action": "delete_user", "user_id": "user123"}
            },
            {
                "option_id": "reject",
                "option_text": "Reject",
                "option_details": {"reason": "This action cannot be undone"}
            }
        ],
        "timeout_seconds": 3600,
        "urgency": "high"
    }
)

print(response.json())
```

### Responding to a HITL Request

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/hitl/requests/123e4567-e89b-12d3-a456-426614174000/respond",
    json={
        "response": "approve",
        "response_details": {"notes": "Approved after verifying user identity"},
        "human_id": "admin"
    }
)

print(response.json())
```