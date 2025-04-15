# Human-in-the-Loop (HITL) Interface

The Human-in-the-Loop (HITL) Interface is a component of the Cauldron™ system that enables human intervention and collaboration with the agent hierarchy. This document provides an overview of the HITL system, its architecture, and how to use it.

## Overview

The HITL Interface allows agents to request human input, approval, or guidance during task execution. This is particularly useful for:

- Obtaining approval for sensitive actions
- Gathering additional information that the agent cannot access
- Making critical decisions that require human judgment
- Resolving ambiguities or uncertainties
- Providing feedback to improve agent performance

## Architecture

The HITL system consists of the following components:

1. **Backend API**: Provides endpoints for creating, retrieving, and responding to HITL requests
2. **Database Models**: Stores HITL requests and their status
3. **WebSocket Service**: Enables real-time notifications and updates
4. **Frontend Interface**: A React-based UI for human operators to interact with HITL requests

### Backend Components

- `HITLService`: Service layer for managing HITL requests
- `HITLAPI`: API endpoints for HITL operations
- `WebSocketManager`: Manages WebSocket connections for real-time updates
- `HITLRequest`: Database model for storing HITL requests

### Frontend Components

- `HITLInterface.jsx`: Main React component for the HITL interface
- WebSocket connection for real-time updates
- Material UI components for a responsive and user-friendly interface

## API Endpoints

The HITL API provides the following endpoints:

- `POST /api/v1/hitl/requests`: Create a new HITL request
- `GET /api/v1/hitl/requests`: Get all HITL requests
- `GET /api/v1/hitl/requests/{request_id}`: Get a specific HITL request
- `POST /api/v1/hitl/requests/{request_id}/respond`: Respond to a HITL request
- `GET /api/v1/hitl/requests/status/{status}`: Get HITL requests by status
- `GET /api/v1/hitl/requests/type/{request_type}`: Get HITL requests by type
- `GET /api/v1/hitl/requests/task/{task_id}`: Get HITL requests for a specific task
- `WebSocket /ws/hitl`: WebSocket endpoint for real-time updates

## Request Types

The HITL system supports various types of requests:

1. **Approval**: Request approval for an action
2. **Information**: Request additional information
3. **Guidance**: Request guidance on how to proceed
4. **Feedback**: Request feedback on a completed action
5. **Exception**: Report an exception that requires human attention

## Usage

### Creating a HITL Request

Agents can create HITL requests when they need human input:

```python
# Example: Agent code creating a HITL request
hitl_request = agent_orchestration_service.create_hitl_request(
    task_id="task-123",
    request_type="approval",
    request_description="Please approve this sensitive operation",
    options=[
        {"value": "approve", "label": "Approve"},
        {"value": "reject", "label": "Reject"}
    ],
    urgency="high"
)
```

### Responding to a HITL Request

Human operators can respond to HITL requests through the web interface or API:

```python
# Example: API call to respond to a HITL request
response = requests.post(
    f"{API_URL}/api/v1/hitl/requests/{request_id}/respond",
    json={
        "response": "approve",
        "response_details": {"notes": "Approved after review"},
        "human_id": "operator-456"
    }
)
```

## WebSocket Communication

The HITL system uses WebSockets for real-time communication:

1. **New Request Notification**: When a new HITL request is created
2. **Request Update Notification**: When a HITL request is updated or responded to
3. **Initial Data**: When a client connects, it receives all pending HITL requests

## Frontend Interface

The frontend interface provides the following features:

- Real-time updates of HITL requests
- Filtering by status (pending, completed)
- Detailed view of request information
- Response submission with optional notes
- Urgency indicators for high-priority requests

## Integration with Agent Hierarchy

The HITL system integrates with the agent hierarchy in the following ways:

1. **Task Pausing**: Tasks can be paused while waiting for human input
2. **Agent Coordination**: Agents can coordinate their actions based on human responses
3. **Learning from Feedback**: Agents can learn from human feedback to improve future performance

## Security Considerations

The HITL system includes several security features:

- Authentication and authorization for human operators
- Logging of all HITL interactions
- Timeout mechanisms for requests that are not responded to
- Validation of request and response data

## Future Enhancements

Planned enhancements for the HITL system include:

- Support for multimedia content in requests (images, audio, video)
- Integration with notification systems (email, SMS, mobile push)
- Advanced filtering and search capabilities
- Analytics dashboard for HITL interactions
- Role-based access control for different types of operators