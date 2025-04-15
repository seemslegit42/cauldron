# Human-in-the-Loop (HITL) System for Cauldron

This document provides an overview of the Human-in-the-Loop (HITL) system implemented for the Cauldron project.

## Overview

The HITL system enables agents in the Cauldron ecosystem to request human input when needed. This creates a collaborative environment where AI agents can leverage human expertise, judgment, and decision-making capabilities to enhance their performance and ensure safety.

## Components

The HITL system consists of the following components:

1. **HITL API**: RESTful API endpoints for creating, retrieving, and responding to HITL requests.
2. **WebSocket API**: Real-time communication channel for HITL notifications.
3. **Database Models**: Persistent storage for HITL requests and responses.
4. **Agent Orchestration Service**: Service that manages the lifecycle of HITL requests.
5. **UI Components**: User interface for humans to interact with HITL requests.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Agent    │     │   Agent     │     │    Agent    │
│             │     │Orchestration│     │             │
│             │◄────┤   Service   │◄────┤             │
└─────┬───────┘     └──────┬──────┘     └─────────────┘
      │                    │
      │ HITL Request       │ Store Request
      ▼                    ▼
┌─────────────┐     ┌─────────────┐
│  Message    │     │  Database   │
│   Broker    │     │             │
└─────┬───────┘     └──────┬──────┘
      │                    │
      │                    │ Query
      │                    ▼
      │              ┌─────────────┐
      │              │  HITL API   │
      │              │             │
      └─────────────►│             │◄────┐
                     └──────┬──────┘     │
                            │            │
                            │ WebSocket  │ REST API
                            ▼            │
                     ┌─────────────┐     │
                     │    HITL     │     │
                     │     UI      │◄────┘
                     │             │
                     └─────────────┘
```

## HITL Request Lifecycle

1. **Creation**: An agent creates a HITL request through the Agent Orchestration Service.
2. **Storage**: The request is stored in the database and published to the message broker.
3. **Notification**: The WebSocket API notifies connected clients of the new request.
4. **Display**: The HITL UI displays the request to human users.
5. **Response**: A human user responds to the request through the UI.
6. **Processing**: The response is stored in the database and published to the message broker.
7. **Notification**: The WebSocket API notifies connected clients of the updated request.
8. **Continuation**: The agent receives the response and continues its task.

## API Endpoints

### REST API

- `POST /api/v1/hitl/requests`: Create a new HITL request
- `GET /api/v1/hitl/requests`: Get all HITL requests
- `GET /api/v1/hitl/requests/{request_id}`: Get a specific HITL request
- `POST /api/v1/hitl/requests/{request_id}/respond`: Respond to a HITL request
- `GET /api/v1/hitl/requests/task/{task_id}`: Get HITL requests for a task
- `GET /api/v1/hitl/requests/status/{status}`: Get HITL requests by status
- `GET /api/v1/hitl/requests/type/{request_type}`: Get HITL requests by type

### WebSocket API

- `WebSocket /ws/hitl`: WebSocket endpoint for HITL notifications

## Request Types

The HITL system supports various request types, including:

- `approval`: Request approval for an action
- `information`: Request additional information
- `clarification`: Request clarification on a task
- `decision`: Request a decision between options
- `feedback`: Request feedback on a result
- `custom`: Custom request type

## Database Schema

### HITLRequest Table

| Column              | Type      | Description                           |
|---------------------|-----------|---------------------------------------|
| id                  | UUID      | Primary key                           |
| task_id             | UUID      | Foreign key to Task                   |
| request_type        | String    | Type of HITL request                  |
| request_description | Text      | Description of the request            |
| options             | JSON      | Options for the request               |
| status              | String    | Status of the request                 |
| response            | Text      | Human response                        |
| response_details    | JSON      | Additional response details           |
| human_id            | String    | ID of the human who responded         |
| created_at          | DateTime  | Creation timestamp                    |
| updated_at          | DateTime  | Last update timestamp                 |
| completed_at        | DateTime  | Completion timestamp                  |

## UI Components

The HITL UI provides the following features:

- Real-time display of HITL requests
- Filtering by status (pending, completed)
- Detailed view of request information
- Response form with options
- Notification of new requests

## Integration with Agent Orchestration

The HITL system is integrated with the Agent Orchestration Service, which manages the lifecycle of HITL requests. When an agent needs human input, it creates a HITL request through the Agent Orchestration Service, which then publishes a message to the message broker. The HITL API provides endpoints for humans to view and respond to these requests.

## Testing

A test script is provided in `tests/test_hitl_api.py` to test the HITL API endpoints. This script creates a HITL request, retrieves it, and responds to it, demonstrating the full lifecycle of a HITL request.

## Future Enhancements

1. **Authentication and Authorization**: Add user authentication and role-based access control for HITL requests.
2. **Request Prioritization**: Implement a priority system for HITL requests based on urgency and importance.
3. **Request Routing**: Route HITL requests to specific users or groups based on expertise and availability.
4. **Request Templates**: Create templates for common HITL request types to streamline the request creation process.
5. **Analytics**: Track metrics on HITL request volume, response time, and resolution rate.
6. **Mobile Support**: Develop a mobile app for responding to HITL requests on the go.
7. **Integration with External Systems**: Integrate with external communication channels like Slack, Microsoft Teams, or email.

## Conclusion

The HITL system provides a robust framework for human-AI collaboration in the Cauldron ecosystem. By enabling agents to request human input when needed, the system enhances the capabilities of the AI agents while ensuring human oversight and control.