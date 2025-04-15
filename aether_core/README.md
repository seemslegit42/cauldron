# AetherCore: Agent Orchestration for Cauldron™

AetherCore is the central Agent Orchestration service for the Cauldron™ Sentient Enterprise Operating System (sEOS). It manages the lifecycle, communication, and coordination of AI agents within the system, leveraging the SuperAGI framework.

## Agent Hierarchy

AetherCore implements a multi-level agent hierarchy consisting of:

1. **Level 0: Core Sentience** - System-wide coordination and emergent intelligence
   - System Coordinator
   - Resource Manager
   - Learning Coordinator
   - Ethics Guardian
   - Human Interface

2. **Level 1: Domain Regents** - Strategic oversight for major functional domains
   - Operations Regent
   - Intelligence Regent
   - Security Regent
   - Knowledge Regent
   - Development Regent

3. **Level 2: Task Masters** - Specialized expertise for complex domain-specific tasks
   - Financial Analyst, Supply Chain Optimizer (Operations)
   - Data Scientist, Forecaster (Intelligence)
   - Threat Hunter, Incident Responder (Security)
   - Knowledge Curator, Insight Generator (Knowledge)
   - Code Architect, Quality Engineer (Development)

4. **Level 3: Minions** - Focused execution of specific atomic tasks
   - Data Minions (Data Collector, Data Transformer, etc.)
   - Process Minions (Task Executor, Notifier, etc.)
   - Interaction Minions (Query Responder, Summarizer, etc.)
   - Technical Minions (Code Generator, Tester, etc.)

## Architecture

AetherCore consists of the following components:

- **API Layer**: FastAPI-based REST API for managing agents and tasks
- **Core Layer**: Integration with SuperAGI and agent communication infrastructure
- **Services Layer**: Agent factory, orchestration, and task management
- **Models Layer**: Data models for agents, tasks, and messages

## Communication

Agents communicate through a standardized messaging system following the patterns defined in the Agent Interaction Playbook:

- **Task Assignment**: Assigning tasks to agents
- **Status Updates**: Reporting task progress
- **Results**: Reporting task completion
- **Errors**: Reporting task failures
- **HITL Requests**: Requesting human intervention
- **Knowledge Sharing**: Sharing insights between agents

## Human-in-the-Loop (HITL)

AetherCore implements robust HITL workflows to ensure human oversight of agent activities:

- **Approval Workflows**: Human approval for critical agent actions
- **Intervention Interfaces**: Tools for human guidance of agent activities
- **Explanation Generation**: Human-readable explanations of agent decisions
- **Feedback Mechanisms**: Capturing human feedback for agent learning

## Getting Started

### Prerequisites

- Python 3.8+
- SuperAGI
- FastAPI
- Uvicorn
- Pydantic

### Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables
4. Start the API server: `python -m aether_core.api.main`

### API Usage

The AetherCore API provides endpoints for managing the agent hierarchy:

- `/api/v1/agents/hierarchy`: Get the complete agent hierarchy
- `/api/v1/agents/hierarchy/initialize`: Initialize the agent hierarchy with default agents
- `/api/v1/agents/core-sentience`: Manage Core Sentience agents
- `/api/v1/agents/domain-regents`: Manage Domain Regent agents
- `/api/v1/agents/task-masters`: Manage Task Master agents
- `/api/v1/agents/minions`: Manage Minion agents

## Integration with Cauldron™

AetherCore integrates with other Cauldron™ components through:

- **Mythos EDA**: Event-driven communication via Kafka/RabbitMQ
- **API Gateway**: REST API access for other services
- **Manifold UI**: User interface for agent management and HITL workflows

## License

This project is licensed under the terms of the license provided with the Cauldron™ sEOS.