"""
Agent Orchestration Service for AetherCore

This service manages the lifecycle and coordination of agents in the hierarchy,
including task assignment, status tracking, and human-in-the-loop workflows.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Local imports
from ..models.agent_hierarchy import (
    AgentLevel, AgentDomain, AgentStatus, AgentBase,
    CoreSentienceAgent, DomainRegent, TaskMaster, Minion,
    AgentHierarchy
)
from ..core.superagi_integration import (
    SuperAGIAgentFactory, HierarchicalAgentManager
)
from ..core.agent_communication import (
    MessageBroker, Message, TaskAssignmentMessage, StatusUpdateMessage,
    ResultMessage, ErrorMessage, HITLRequestMessage, HITLResponseMessage,
    KnowledgeSharingMessage, ResourceRequestMessage, CoordinationMessage,
    MessageType, TaskStatus
)


class Task:
    """Model representing a task in the system"""
    
    def __init__(
        self,
        task_id: str = None,
        task_type: str = None,
        task_description: str = None,
        assigned_agent_id: str = None,
        assigned_agent_level: AgentLevel = None,
        status: TaskStatus = TaskStatus.RECEIVED,
        priority: int = 5,
        input_data: Dict[str, Any] = None,
        result_data: Dict[str, Any] = None,
        error_data: Dict[str, Any] = None,
        created_at: str = None,
        updated_at: str = None,
        completed_at: str = None,
        parent_task_id: str = None,
        subtask_ids: List[str] = None,
        hitl_requests: List[Dict[str, Any]] = None,
        retry_count: int = 0,
        max_retries: int = 3
    ):
        self.task_id = task_id or str(uuid.uuid4())
        self.task_type = task_type
        self.task_description = task_description
        self.assigned_agent_id = assigned_agent_id
        self.assigned_agent_level = assigned_agent_level
        self.status = status
        self.priority = priority
        self.input_data = input_data or {}
        self.result_data = result_data or {}
        self.error_data = error_data or {}
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or self.created_at
        self.completed_at = completed_at
        self.parent_task_id = parent_task_id
        self.subtask_ids = subtask_ids or []
        self.hitl_requests = hitl_requests or []
        self.retry_count = retry_count
        self.max_retries = max_retries
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "task_description": self.task_description,
            "assigned_agent_id": self.assigned_agent_id,
            "assigned_agent_level": self.assigned_agent_level.value if self.assigned_agent_level else None,
            "status": self.status.value if self.status else None,
            "priority": self.priority,
            "input_data": self.input_data,
            "result_data": self.result_data,
            "error_data": self.error_data,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "parent_task_id": self.parent_task_id,
            "subtask_ids": self.subtask_ids,
            "hitl_requests": self.hitl_requests,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary"""
        return cls(
            task_id=data.get("task_id"),
            task_type=data.get("task_type"),
            task_description=data.get("task_description"),
            assigned_agent_id=data.get("assigned_agent_id"),
            assigned_agent_level=AgentLevel(data.get("assigned_agent_level")) if data.get("assigned_agent_level") else None,
            status=TaskStatus(data.get("status")) if data.get("status") else None,
            priority=data.get("priority"),
            input_data=data.get("input_data"),
            result_data=data.get("result_data"),
            error_data=data.get("error_data"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            completed_at=data.get("completed_at"),
            parent_task_id=data.get("parent_task_id"),
            subtask_ids=data.get("subtask_ids"),
            hitl_requests=data.get("hitl_requests"),
            retry_count=data.get("retry_count"),
            max_retries=data.get("max_retries")
        )


class AgentOrchestrationService:
    """Service for orchestrating agents in the hierarchy"""
    
    def __init__(
        self,
        agent_manager: HierarchicalAgentManager,
        message_broker: MessageBroker,
        db_session=None
    ):
        """Initialize the agent orchestration service"""
        self.agent_manager = agent_manager
        self.message_broker = message_broker
        self.logger = logging.getLogger(__name__)
        self.db_session = db_session
        
        # Task registry (in-memory cache)
        self.tasks = {}  # task_id -> Task
        
        # HITL request registry (in-memory cache)
        self.hitl_requests = {}  # request_id -> HITLRequestMessage
        
        # Set up message handlers
        self._setup_message_handlers()
    
    def _setup_message_handlers(self):
        """Set up handlers for different message types"""
        # Subscribe to status updates
        self.message_broker.subscribe(
            "cauldron.agent.status.update",
            self._handle_status_update
        )
        
        # Subscribe to results
        self.message_broker.subscribe(
            "cauldron.agent.result.success",
            self._handle_result
        )
        
        # Subscribe to errors
        self.message_broker.subscribe(
            "cauldron.agent.error.occurred",
            self._handle_error
        )
        
        # Subscribe to HITL requests
        self.message_broker.subscribe(
            "cauldron.agent.hitl.request",
            self._handle_hitl_request
        )
        
        # Subscribe to HITL responses
        self.message_broker.subscribe(
            "cauldron.agent.hitl.response",
            self._handle_hitl_response
        )
    
    def _handle_status_update(self, message: StatusUpdateMessage):
        """Handle status update messages"""
        try:
            task_id = message.payload.get("task_id")
            if not task_id or task_id not in self.tasks:
                self.logger.warning(f"Status update for unknown task: {task_id}")
                return
            
            task = self.tasks[task_id]
            
            # Update task status
            status_str = message.payload.get("status")
            if status_str:
                task.status = TaskStatus(status_str)
            
            # Update task updated_at
            task.updated_at = datetime.now().isoformat()
            
            # If task is completed, set completed_at
            if task.status == TaskStatus.COMPLETED:
                task.completed_at = task.updated_at
            
            self.logger.info(f"Updated task {task_id} status to {task.status.value}")
            
        except Exception as e:
            self.logger.error(f"Error handling status update: {str(e)}")
    
    def _handle_result(self, message: ResultMessage):
        """Handle result messages"""
        try:
            task_id = message.payload.get("task_id")
            if not task_id or task_id not in self.tasks:
                self.logger.warning(f"Result for unknown task: {task_id}")
                return
            
            task = self.tasks[task_id]
            
            # Update task result
            task.result_data = message.payload.get("result_data", {})
            
            # Update task status
            task.status = TaskStatus.COMPLETED
            
            # Update task updated_at and completed_at
            task.updated_at = datetime.now().isoformat()
            task.completed_at = task.updated_at
            
            self.logger.info(f"Received result for task {task_id}")
            
            # Process parent task if this is a subtask
            if task.parent_task_id and task.parent_task_id in self.tasks:
                self._process_parent_task(task.parent_task_id)
            
        except Exception as e:
            self.logger.error(f"Error handling result: {str(e)}")
    
    def _handle_error(self, message: ErrorMessage):
        """Handle error messages"""
        try:
            task_id = message.payload.get("task_id")
            if not task_id or task_id not in self.tasks:
                self.logger.warning(f"Error for unknown task: {task_id}")
                return
            
            task = self.tasks[task_id]
            
            # Update task error
            task.error_data = {
                "error_type": message.payload.get("error_type"),
                "error_message": message.payload.get("error_message"),
                "error_details": message.payload.get("error_details", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            # Check if retry is possible
            retry_count = message.payload.get("retry_count", 0)
            if retry_count < task.max_retries:
                # Update retry count
                task.retry_count = retry_count + 1
                
                # Update task status
                task.status = TaskStatus.RETRYING
                
                # Reassign task
                self._reassign_task(task)
            else:
                # Update task status
                task.status = TaskStatus.FAILED
            
            # Update task updated_at
            task.updated_at = datetime.now().isoformat()
            
            self.logger.info(f"Received error for task {task_id}: {message.payload.get('error_message')}")
            
            # Process parent task if this is a subtask
            if task.parent_task_id and task.parent_task_id in self.tasks:
                self._process_parent_task(task.parent_task_id)
            
        except Exception as e:
            self.logger.error(f"Error handling error message: {str(e)}")
    
    def _handle_hitl_request(self, message: HITLRequestMessage):
        """Handle HITL request messages"""
        try:
            task_id = message.payload.get("task_id")
            if not task_id or task_id not in self.tasks:
                self.logger.warning(f"HITL request for unknown task: {task_id}")
                return
            
            task = self.tasks[task_id]
            
            # Create HITL request
            request_id = str(uuid.uuid4())
            
            # Store HITL request
            self.hitl_requests[request_id] = message
            
            # Add request to task
            task.hitl_requests.append({
                "request_id": request_id,
                "request_type": message.payload.get("request_type"),
                "request_description": message.payload.get("request_description"),
                "options": message.payload.get("options", []),
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            })
            
            # Update task status
            task.status = TaskStatus.AWAITING_HITL
            
            # Update task updated_at
            task.updated_at = datetime.now().isoformat()
            
            self.logger.info(f"Received HITL request for task {task_id}")
            
            # Forward request to human interface
            # In a real implementation, this would notify the UI
            # For now, we'll just log it
            self.logger.info(f"HITL request {request_id} awaiting human response")
            
        except Exception as e:
            self.logger.error(f"Error handling HITL request: {str(e)}")
    
    def _handle_hitl_response(self, message: HITLResponseMessage):
        """Handle HITL response messages"""
        try:
            request_id = message.payload.get("request_id")
            if not request_id or request_id not in self.hitl_requests:
                self.logger.warning(f"HITL response for unknown request: {request_id}")
                return
            
            # Get original request
            request = self.hitl_requests[request_id]
            
            # Get task
            task_id = request.payload.get("task_id")
            if not task_id or task_id not in self.tasks:
                self.logger.warning(f"HITL response for unknown task: {task_id}")
                return
            
            task = self.tasks[task_id]
            
            # Update HITL request status
            for req in task.hitl_requests:
                if req["request_id"] == request_id:
                    req["status"] = "completed"
                    req["response"] = message.payload.get("response")
                    req["response_details"] = message.payload.get("response_details", {})
                    req["human_id"] = message.payload.get("human_id")
                    req["completed_at"] = datetime.now().isoformat()
            
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            
            # Update task updated_at
            task.updated_at = datetime.now().isoformat()
            
            self.logger.info(f"Received HITL response for request {request_id}")
            
            # Forward response to agent
            self._forward_hitl_response(task, request_id, message)
            
        except Exception as e:
            self.logger.error(f"Error handling HITL response: {str(e)}")
    
    def _forward_hitl_response(self, task: Task, request_id: str, response: HITLResponseMessage):
        """Forward HITL response to agent"""
        try:
            # Create topic
            topic = f"cauldron.agent.hitl.response.{task.assigned_agent_id}"
            
            # Publish response
            self.message_broker.publish(topic, response)
            
            self.logger.info(f"Forwarded HITL response for request {request_id} to agent {task.assigned_agent_id}")
            
        except Exception as e:
            self.logger.error(f"Error forwarding HITL response: {str(e)}")
    
    def _process_parent_task(self, parent_task_id: str):
        """Process parent task after subtask completion"""
        try:
            parent_task = self.tasks[parent_task_id]
            
            # Check if all subtasks are completed
            all_completed = True
            any_failed = False
            
            for subtask_id in parent_task.subtask_ids:
                if subtask_id not in self.tasks:
                    all_completed = False
                    break
                
                subtask = self.tasks[subtask_id]
                if subtask.status != TaskStatus.COMPLETED:
                    if subtask.status == TaskStatus.FAILED:
                        any_failed = True
                    all_completed = False
                    break
            
            if all_completed:
                # All subtasks completed successfully
                # Aggregate results
                aggregated_results = self._aggregate_subtask_results(parent_task)
                
                # Update parent task
                parent_task.result_data = aggregated_results
                parent_task.status = TaskStatus.COMPLETED
                parent_task.updated_at = datetime.now().isoformat()
                parent_task.completed_at = parent_task.updated_at
                
                self.logger.info(f"All subtasks completed for parent task {parent_task_id}")
                
                # Notify agent of completion
                self._notify_task_completion(parent_task)
                
            elif any_failed:
                # At least one subtask failed
                # Update parent task
                parent_task.status = TaskStatus.FAILED
                parent_task.error_data = {
                    "error_type": "subtask_failure",
                    "error_message": "One or more subtasks failed",
                    "error_details": {
                        "failed_subtasks": [
                            subtask_id for subtask_id in parent_task.subtask_ids
                            if subtask_id in self.tasks and self.tasks[subtask_id].status == TaskStatus.FAILED
                        ]
                    },
                    "timestamp": datetime.now().isoformat()
                }
                parent_task.updated_at = datetime.now().isoformat()
                
                self.logger.info(f"One or more subtasks failed for parent task {parent_task_id}")
                
                # Notify agent of failure
                self._notify_task_failure(parent_task)
            
        except Exception as e:
            self.logger.error(f"Error processing parent task: {str(e)}")
    
    def _aggregate_subtask_results(self, parent_task: Task) -> Dict[str, Any]:
        """Aggregate results from subtasks"""
        try:
            aggregated_results = {
                "subtask_results": {}
            }
            
            for subtask_id in parent_task.subtask_ids:
                if subtask_id in self.tasks:
                    subtask = self.tasks[subtask_id]
                    if subtask.status == TaskStatus.COMPLETED:
                        aggregated_results["subtask_results"][subtask_id] = subtask.result_data
            
            return aggregated_results
            
        except Exception as e:
            self.logger.error(f"Error aggregating subtask results: {str(e)}")
            return {"error": str(e)}
    
    def _notify_task_completion(self, task: Task):
        """Notify agent of task completion"""
        try:
            # Create result message
            result_message = ResultMessage(
                task_id=task.task_id,
                result_data=task.result_data,
                sender_id="aether_core",
                recipient_id=task.assigned_agent_id,
                recipient_level=task.assigned_agent_level
            )
            
            # Publish to agent-specific topic
            topic = f"cauldron.agent.result.{task.assigned_agent_id}"
            self.message_broker.publish(topic, result_message)
            
            self.logger.info(f"Notified agent {task.assigned_agent_id} of task {task.task_id} completion")
            
        except Exception as e:
            self.logger.error(f"Error notifying task completion: {str(e)}")
    
    def _notify_task_failure(self, task: Task):
        """Notify agent of task failure"""
        try:
            # Create error message
            error_message = ErrorMessage(
                task_id=task.task_id,
                error_type=task.error_data.get("error_type"),
                error_message=task.error_data.get("error_message"),
                error_details=task.error_data.get("error_details"),
                sender_id="aether_core",
                recipient_id=task.assigned_agent_id,
                recipient_level=task.assigned_agent_level
            )
            
            # Publish to agent-specific topic
            topic = f"cauldron.agent.error.{task.assigned_agent_id}"
            self.message_broker.publish(topic, error_message)
            
            self.logger.info(f"Notified agent {task.assigned_agent_id} of task {task.task_id} failure")
            
        except Exception as e:
            self.logger.error(f"Error notifying task failure: {str(e)}")
    
    def _reassign_task(self, task: Task):
        """Reassign a task for retry"""
        try:
            # Create task assignment message
            task_message = TaskAssignmentMessage(
                task_id=task.task_id,
                task_type=task.task_type,
                task_description=task.task_description,
                priority=task.priority,
                input_data=task.input_data,
                max_retries=task.max_retries,
                sender_id="aether_core",
                recipient_id=task.assigned_agent_id,
                recipient_level=task.assigned_agent_level
            )
            
            # Add retry information
            task_message.payload["retry_count"] = task.retry_count
            task_message.payload["previous_error"] = task.error_data
            
            # Publish to agent-specific topic
            topic = f"cauldron.agent.task.assigned.{task.assigned_agent_id}"
            self.message_broker.publish(topic, task_message)
            
            self.logger.info(f"Reassigned task {task.task_id} to agent {task.assigned_agent_id} (retry {task.retry_count})")
            
        except Exception as e:
            self.logger.error(f"Error reassigning task: {str(e)}")
    
    def create_task(
        self,
        task_type: str,
        task_description: str,
        input_data: Dict[str, Any],
        assigned_agent_id: str,
        assigned_agent_level: AgentLevel,
        priority: int = 5,
        max_retries: int = 3,
        parent_task_id: str = None
    ) -> str:
        """Create a new task"""
        try:
            # Create task
            task = Task(
                task_type=task_type,
                task_description=task_description,
                assigned_agent_id=assigned_agent_id,
                assigned_agent_level=assigned_agent_level,
                status=TaskStatus.RECEIVED,
                priority=priority,
                input_data=input_data,
                max_retries=max_retries,
                parent_task_id=parent_task_id
            )
            
            # Add to registry
            self.tasks[task.task_id] = task
            
            # If this is a subtask, add to parent
            if parent_task_id and parent_task_id in self.tasks:
                parent_task = self.tasks[parent_task_id]
                parent_task.subtask_ids.append(task.task_id)
            
            # Create task assignment message
            task_message = TaskAssignmentMessage(
                task_id=task.task_id,
                task_type=task.task_type,
                task_description=task.task_description,
                priority=task.priority,
                input_data=task.input_data,
                max_retries=task.max_retries,
                sender_id="aether_core",
                recipient_id=task.assigned_agent_id,
                recipient_level=task.assigned_agent_level
            )
            
            # Publish to agent-specific topic
            topic = f"cauldron.agent.task.assigned.{task.assigned_agent_id}"
            self.message_broker.publish(topic, task_message)
            
            self.logger.info(f"Created task {task.task_id} and assigned to agent {task.assigned_agent_id}")
            
            return task.task_id
            
        except Exception as e:
            self.logger.error(f"Error creating task: {str(e)}")
            raise
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_agent(self, agent_id: str) -> List[Task]:
        """Get all tasks assigned to an agent"""
        return [task for task in self.tasks.values() if task.assigned_agent_id == agent_id]
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status"""
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_pending_hitl_requests(self) -> List[Dict[str, Any]]:
        """Get all pending HITL requests"""
        pending_requests = []
        
        for task in self.tasks.values():
            for request in task.hitl_requests:
                if request["status"] == "pending":
                    pending_requests.append({
                        "request_id": request["request_id"],
                        "task_id": task.task_id,
                        "agent_id": task.assigned_agent_id,
                        "agent_level": task.assigned_agent_level.value if task.assigned_agent_level else None,
                        "request_type": request["request_type"],
                        "request_description": request["request_description"],
                        "options": request["options"],
                        "created_at": request["created_at"]
                    })
        
        return pending_requests
    
    def submit_hitl_response(
        self,
        request_id: str,
        response: str,
        response_details: Dict[str, Any] = None,
        human_id: str = None
    ) -> bool:
        """Submit a response to a HITL request"""
        try:
            # Check if request exists
            if request_id not in self.hitl_requests:
                self.logger.warning(f"HITL response for unknown request: {request_id}")
                return False
            
            # Get original request
            request = self.hitl_requests[request_id]
            
            # Get task
            task_id = request.payload.get("task_id")
            if not task_id or task_id not in self.tasks:
                self.logger.warning(f"HITL response for unknown task: {task_id}")
                return False
            
            task = self.tasks[task_id]
            
            # Create HITL response message
            response_message = HITLResponseMessage(
                task_id=task_id,
                request_id=request_id,
                response=response,
                response_details=response_details,
                human_id=human_id,
                sender_id="aether_core",
                recipient_id=task.assigned_agent_id,
                recipient_level=task.assigned_agent_level
            )
            
            # Publish to HITL response topic
            self.message_broker.publish("cauldron.agent.hitl.response", response_message)
            
            self.logger.info(f"Submitted HITL response for request {request_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error submitting HITL response: {str(e)}")
            return False