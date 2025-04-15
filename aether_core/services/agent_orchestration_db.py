"""
Agent Orchestration Service with Database Support for AetherCore

This service manages the lifecycle and coordination of agents in the hierarchy,
including task assignment, status tracking, and human-in-the-loop workflows.
It uses a database for persistent storage of tasks and HITL requests.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session

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
from ..models.database_models import (
    Task as DBTask,
    HITLRequest as DBHITLRequest
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
    
    @classmethod
    def from_db_model(cls, db_task: DBTask) -> 'Task':
        """Create task from database model"""
        return cls(
            task_id=str(db_task.id),
            task_type=db_task.task_type,
            task_description=db_task.task_description,
            assigned_agent_id=str(db_task.agent_id) if db_task.agent_id else None,
            assigned_agent_level=db_task.agent_level,
            status=db_task.status,
            priority=db_task.priority,
            input_data=db_task.input_data,
            result_data=db_task.result_data,
            error_data=db_task.error_data,
            created_at=db_task.created_at.isoformat(),
            updated_at=db_task.updated_at.isoformat(),
            completed_at=db_task.completed_at.isoformat() if db_task.completed_at else None,
            parent_task_id=str(db_task.parent_task_id) if db_task.parent_task_id else None,
            subtask_ids=db_task.subtasks,
            hitl_requests=[
                {
                    "request_id": str(req.id),
                    "request_type": req.request_type,
                    "request_description": req.request_description,
                    "options": req.options,
                    "status": req.status,
                    "response": req.response,
                    "response_details": req.response_details,
                    "human_id": req.human_id,
                    "created_at": req.created_at.isoformat(),
                    "updated_at": req.updated_at.isoformat(),
                    "completed_at": req.completed_at.isoformat() if req.completed_at else None
                }
                for req in db_task.hitl_requests
            ],
            retry_count=db_task.retry_count,
            max_retries=db_task.max_retries
        )
    
    def to_db_model(self) -> DBTask:
        """Convert task to database model"""
        return DBTask(
            id=uuid.UUID(self.task_id),
            task_type=self.task_type,
            task_description=self.task_description,
            agent_id=uuid.UUID(self.assigned_agent_id) if self.assigned_agent_id else None,
            agent_level=self.assigned_agent_level,
            status=self.status,
            priority=self.priority,
            input_data=self.input_data,
            result_data=self.result_data,
            error_data=self.error_data,
            parent_task_id=uuid.UUID(self.parent_task_id) if self.parent_task_id else None,
            retry_count=self.retry_count,
            max_retries=self.max_retries
        )


class AgentOrchestrationService:
    """Service for orchestrating agents in the hierarchy"""
    
    def __init__(
        self,
        agent_manager: HierarchicalAgentManager,
        message_broker: MessageBroker,
        db_session: Optional[Session] = None
    ):
        """Initialize the agent orchestration service"""
        self.agent_manager = agent_manager
        self.message_broker = message_broker
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
        
        # Task registry (in-memory cache)
        self.tasks = {}  # task_id -> Task
        
        # HITL request registry (in-memory cache)
        self.hitl_requests = {}  # request_id -> Dict
        
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
            if not task_id:
                self.logger.warning("Status update missing task_id")
                return
            
            # Get task
            task = self.get_task(task_id)
            if not task:
                self.logger.warning(f"Status update for unknown task: {task_id}")
                return
            
            # Update task status
            status_str = message.payload.get("status")
            if status_str:
                try:
                    status = TaskStatus(status_str)
                    self.update_task_status(
                        task_id=task_id,
                        status=status,
                        progress=message.payload.get("progress"),
                        details=message.payload.get("details")
                    )
                except ValueError:
                    self.logger.warning(f"Invalid task status: {status_str}")
            
        except Exception as e:
            self.logger.error(f"Error handling status update: {str(e)}")
    
    def _handle_result(self, message: ResultMessage):
        """Handle result messages"""
        try:
            task_id = message.payload.get("task_id")
            if not task_id:
                self.logger.warning("Result message missing task_id")
                return
            
            # Get task
            task = self.get_task(task_id)
            if not task:
                self.logger.warning(f"Result for unknown task: {task_id}")
                return
            
            # Update task result
            self.update_task_result(
                task_id=task_id,
                result_data=message.payload.get("result_data", {}),
                execution_time_ms=message.payload.get("execution_time_ms"),
                metrics=message.payload.get("metrics", {})
            )
            
        except Exception as e:
            self.logger.error(f"Error handling result: {str(e)}")
    
    def _handle_error(self, message: ErrorMessage):
        """Handle error messages"""
        try:
            task_id = message.payload.get("task_id")
            if not task_id:
                self.logger.warning("Error message missing task_id")
                return
            
            # Get task
            task = self.get_task(task_id)
            if not task:
                self.logger.warning(f"Error for unknown task: {task_id}")
                return
            
            # Update task error
            self.update_task_error(
                task_id=task_id,
                error_type=message.payload.get("error_type", "unknown"),
                error_message=message.payload.get("error_message", "Unknown error"),
                error_details=message.payload.get("error_details", {}),
                retry=task.retry_count < task.max_retries
            )
            
        except Exception as e:
            self.logger.error(f"Error handling error message: {str(e)}")
    
    def _handle_hitl_request(self, message: HITLRequestMessage):
        """Handle HITL request messages"""
        try:
            task_id = message.payload.get("task_id")
            if not task_id:
                self.logger.warning("HITL request missing task_id")
                return
            
            # Get task
            task = self.get_task(task_id)
            if not task:
                self.logger.warning(f"HITL request for unknown task: {task_id}")
                return
            
            # Create HITL request
            self.create_hitl_request(
                task_id=task_id,
                request_type=message.payload.get("request_type", "approval"),
                request_description=message.payload.get("request_description", ""),
                options=message.payload.get("options", []),
                timeout_seconds=message.payload.get("timeout_seconds", 3600),
                urgency=message.payload.get("urgency", "normal")
            )
            
        except Exception as e:
            self.logger.error(f"Error handling HITL request: {str(e)}")
    
    def _handle_hitl_response(self, message: HITLResponseMessage):
        """Handle HITL response messages"""
        try:
            request_id = message.payload.get("request_id")
            if not request_id:
                self.logger.warning("HITL response missing request_id")
                return
            
            # Get HITL request
            hitl_request = self.get_hitl_request(request_id)
            if not hitl_request:
                self.logger.warning(f"HITL response for unknown request: {request_id}")
                return
            
            # Respond to HITL request
            self.respond_to_hitl_request(
                request_id=request_id,
                response=message.payload.get("response", ""),
                response_details=message.payload.get("response_details", {}),
                human_id=message.payload.get("human_id", "unknown")
            )
            
        except Exception as e:
            self.logger.error(f"Error handling HITL response: {str(e)}")
    
    def create_task(
        self,
        task_type: str,
        task_description: str,
        assigned_agent_id: str = None,
        assigned_agent_level: AgentLevel = None,
        priority: int = 5,
        input_data: Dict[str, Any] = None,
        parent_task_id: str = None,
        max_retries: int = 3
    ) -> Task:
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
                input_data=input_data or {},
                parent_task_id=parent_task_id,
                max_retries=max_retries
            )
            
            # Add to registry
            self.tasks[task.task_id] = task
            
            # Save to database if available
            if self.db_session:
                db_task = task.to_db_model()
                self.db_session.add(db_task)
                self.db_session.commit()
            
            # If parent task exists, add this task as a subtask
            if parent_task_id:
                parent_task = self.get_task(parent_task_id)
                if parent_task:
                    parent_task.subtask_ids.append(task.task_id)
                    
                    # Update parent task in database if available
                    if self.db_session:
                        db_parent_task = self.db_session.query(DBTask).filter(DBTask.id == uuid.UUID(parent_task_id)).first()
                        if db_parent_task:
                            db_parent_task.subtasks = parent_task.subtask_ids
                            self.db_session.commit()
            
            # If agent is assigned, send task assignment message
            if assigned_agent_id:
                # Create task assignment message
                message = TaskAssignmentMessage(
                    task_id=task.task_id,
                    task_type=task.task_type,
                    task_description=task.task_description,
                    priority=task.priority,
                    input_data=task.input_data,
                    max_retries=task.max_retries,
                    sender_id="agent_orchestration_service",
                    recipient_id=task.assigned_agent_id,
                    recipient_level=task.assigned_agent_level
                )
                
                # Publish message
                topic = f"cauldron.agent.task.assign.{task.assigned_agent_id}"
                self.message_broker.publish(topic, message)
                
                self.logger.info(f"Assigned task {task.task_id} to agent {task.assigned_agent_id}")
            
            return task
            
        except Exception as e:
            self.logger.error(f"Error creating task: {str(e)}")
            raise
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        try:
            # Check in-memory cache first
            if task_id in self.tasks:
                return self.tasks[task_id]
            
            # Check database if available
            if self.db_session:
                db_task = self.db_session.query(DBTask).filter(DBTask.id == uuid.UUID(task_id)).first()
                if db_task:
                    # Convert to Task object
                    task = Task.from_db_model(db_task)
                    
                    # Add to in-memory cache
                    self.tasks[task_id] = task
                    
                    return task
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting task: {str(e)}")
            return None
    
    def get_tasks(self, limit: int = 100, offset: int = 0) -> List[Task]:
        """Get all tasks"""
        try:
            # If database is available, use it
            if self.db_session:
                db_tasks = self.db_session.query(DBTask).order_by(DBTask.created_at.desc()).limit(limit).offset(offset).all()
                
                tasks = []
                for db_task in db_tasks:
                    # Convert to Task object
                    task = Task.from_db_model(db_task)
                    
                    # Add to in-memory cache
                    self.tasks[task.task_id] = task
                    
                    tasks.append(task)
                
                return tasks
            
            # Otherwise, use in-memory cache
            return list(self.tasks.values())[offset:offset+limit]
            
        except Exception as e:
            self.logger.error(f"Error getting tasks: {str(e)}")
            return []
    
    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        progress: float = None,
        details: str = None
    ) -> Optional[Task]:
        """Update task status"""
        try:
            # Get task
            task = self.get_task(task_id)
            if not task:
                self.logger.warning(f"Task {task_id} not found")
                return None
            
            # Update task status
            task.status = status
            
            # Update task updated_at
            task.updated_at = datetime.now().isoformat()
            
            # If task is completed, set completed_at
            if status == TaskStatus.COMPLETED:
                task.completed_at = task.updated_at
            
            # Update in database if available
            if self.db_session:
                db_task = self.db_session.query(DBTask).filter(DBTask.id == uuid.UUID(task_id)).first()
                if db_task:
                    db_task.status = status
                    db_task.updated_at = datetime.now()
                    
                    if status == TaskStatus.COMPLETED:
                        db_task.completed_at = db_task.updated_at
                    
                    self.db_session.commit()
            
            # Publish status update message
            message = StatusUpdateMessage(
                task_id=task.task_id,
                status=status,
                progress=progress,
                details=details,
                sender_id=task.assigned_agent_id,
                recipient_id="agent_orchestration_service"
            )
            
            topic = "cauldron.agent.status.update"
            self.message_broker.publish(topic, message)
            
            self.logger.info(f"Updated task {task_id} status to {status.value}")
            
            return task
            
        except Exception as e:
            self.logger.error(f"Error updating task status: {str(e)}")
            return None
    
    def update_task_result(
        self,
        task_id: str,
        result_data: Dict[str, Any],
        execution_time_ms: int = None,
        metrics: Dict[str, Any] = None
    ) -> Optional[Task]:
        """Update task result"""
        try:
            # Get task
            task = self.get_task(task_id)
            if not task:
                self.logger.warning(f"Task {task_id} not found")
                return None
            
            # Update task result
            task.result_data = result_data
            
            # Update task status
            task.status = TaskStatus.COMPLETED
            
            # Update task updated_at and completed_at
            task.updated_at = datetime.now().isoformat()
            task.completed_at = task.updated_at
            
            # Update in database if available
            if self.db_session:
                db_task = self.db_session.query(DBTask).filter(DBTask.id == uuid.UUID(task_id)).first()
                if db_task:
                    db_task.result_data = result_data
                    db_task.status = TaskStatus.COMPLETED
                    db_task.updated_at = datetime.now()
                    db_task.completed_at = db_task.updated_at
                    
                    self.db_session.commit()
            
            # Publish result message
            message = ResultMessage(
                task_id=task.task_id,
                result_data=result_data,
                execution_time_ms=execution_time_ms,
                metrics=metrics or {},
                sender_id=task.assigned_agent_id,
                recipient_id="agent_orchestration_service"
            )
            
            topic = "cauldron.agent.result.success"
            self.message_broker.publish(topic, message)
            
            self.logger.info(f"Updated task {task_id} result")
            
            # Process parent task if this is a subtask
            if task.parent_task_id:
                self._process_parent_task(task.parent_task_id)
            
            return task
            
        except Exception as e:
            self.logger.error(f"Error updating task result: {str(e)}")
            return None
    
    def update_task_error(
        self,
        task_id: str,
        error_type: str,
        error_message: str,
        error_details: Dict[str, Any] = None,
        retry: bool = False
    ) -> Optional[Task]:
        """Update task error"""
        try:
            # Get task
            task = self.get_task(task_id)
            if not task:
                self.logger.warning(f"Task {task_id} not found")
                return None
            
            # Update task error
            task.error_data = {
                "error_type": error_type,
                "error_message": error_message,
                "error_details": error_details or {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Check if retry is possible
            if retry and task.retry_count < task.max_retries:
                # Update retry count
                task.retry_count += 1
                
                # Update task status
                task.status = TaskStatus.RETRYING
                
                # Update in database if available
                if self.db_session:
                    db_task = self.db_session.query(DBTask).filter(DBTask.id == uuid.UUID(task_id)).first()
                    if db_task:
                        db_task.error_data = task.error_data
                        db_task.retry_count = task.retry_count
                        db_task.status = TaskStatus.RETRYING
                        db_task.updated_at = datetime.now()
                        
                        self.db_session.commit()
                
                # Reassign task
                self._reassign_task(task)
            else:
                # Update task status
                task.status = TaskStatus.FAILED
                
                # Update in database if available
                if self.db_session:
                    db_task = self.db_session.query(DBTask).filter(DBTask.id == uuid.UUID(task_id)).first()
                    if db_task:
                        db_task.error_data = task.error_data
                        db_task.status = TaskStatus.FAILED
                        db_task.updated_at = datetime.now()
                        
                        self.db_session.commit()
            
            # Update task updated_at
            task.updated_at = datetime.now().isoformat()
            
            # Publish error message
            message = ErrorMessage(
                task_id=task.task_id,
                error_type=error_type,
                error_message=error_message,
                error_details=error_details or {},
                retry_count=task.retry_count,
                sender_id=task.assigned_agent_id,
                recipient_id="agent_orchestration_service"
            )
            
            topic = "cauldron.agent.error.occurred"
            self.message_broker.publish(topic, message)
            
            self.logger.info(f"Updated task {task_id} error: {error_message}")
            
            # Process parent task if this is a subtask
            if task.parent_task_id:
                self._process_parent_task(task.parent_task_id)
            
            return task
            
        except Exception as e:
            self.logger.error(f"Error updating task error: {str(e)}")
            return None
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        try:
            # Check if task exists
            task = self.get_task(task_id)
            if not task:
                return False
            
            # Delete from in-memory cache
            if task_id in self.tasks:
                del self.tasks[task_id]
            
            # Delete from database if available
            if self.db_session:
                db_task = self.db_session.query(DBTask).filter(DBTask.id == uuid.UUID(task_id)).first()
                if db_task:
                    self.db_session.delete(db_task)
                    self.db_session.commit()
            
            self.logger.info(f"Deleted task {task_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting task: {str(e)}")
            return False
    
    def get_agent_tasks(self, agent_id: str, limit: int = 100, offset: int = 0) -> List[Task]:
        """Get tasks for an agent"""
        try:
            # If database is available, use it
            if self.db_session:
                db_tasks = self.db_session.query(DBTask).filter(DBTask.agent_id == uuid.UUID(agent_id)).order_by(DBTask.created_at.desc()).limit(limit).offset(offset).all()
                
                tasks = []
                for db_task in db_tasks:
                    # Convert to Task object
                    task = Task.from_db_model(db_task)
                    
                    # Add to in-memory cache
                    self.tasks[task.task_id] = task
                    
                    tasks.append(task)
                
                return tasks
            
            # Otherwise, use in-memory cache
            return [task for task in self.tasks.values() if task.assigned_agent_id == agent_id][offset:offset+limit]
            
        except Exception as e:
            self.logger.error(f"Error getting agent tasks: {str(e)}")
            return []
    
    def get_tasks_by_status(self, status: TaskStatus, limit: int = 100, offset: int = 0) -> List[Task]:
        """Get tasks by status"""
        try:
            # If database is available, use it
            if self.db_session:
                db_tasks = self.db_session.query(DBTask).filter(DBTask.status == status).order_by(DBTask.created_at.desc()).limit(limit).offset(offset).all()
                
                tasks = []
                for db_task in db_tasks:
                    # Convert to Task object
                    task = Task.from_db_model(db_task)
                    
                    # Add to in-memory cache
                    self.tasks[task.task_id] = task
                    
                    tasks.append(task)
                
                return tasks
            
            # Otherwise, use in-memory cache
            return [task for task in self.tasks.values() if task.status == status][offset:offset+limit]
            
        except Exception as e:
            self.logger.error(f"Error getting tasks by status: {str(e)}")
            return []
    
    def get_subtasks(self, task_id: str, limit: int = 100, offset: int = 0) -> List[Task]:
        """Get subtasks of a task"""
        try:
            # Get task
            task = self.get_task(task_id)
            if not task:
                self.logger.warning(f"Task {task_id} not found")
                return []
            
            # If database is available, use it
            if self.db_session:
                db_tasks = self.db_session.query(DBTask).filter(DBTask.parent_task_id == uuid.UUID(task_id)).order_by(DBTask.created_at.desc()).limit(limit).offset(offset).all()
                
                tasks = []
                for db_task in db_tasks:
                    # Convert to Task object
                    subtask = Task.from_db_model(db_task)
                    
                    # Add to in-memory cache
                    self.tasks[subtask.task_id] = subtask
                    
                    tasks.append(subtask)
                
                return tasks
            
            # Otherwise, use in-memory cache
            subtasks = []
            for subtask_id in task.subtask_ids[offset:offset+limit]:
                subtask = self.get_task(subtask_id)
                if subtask:
                    subtasks.append(subtask)
            
            return subtasks
            
        except Exception as e:
            self.logger.error(f"Error getting subtasks: {str(e)}")
            return []
    
    def create_hitl_request(
        self,
        task_id: str,
        request_type: str,
        request_description: str,
        options: List[Dict[str, Any]] = None,
        timeout_seconds: int = 3600,
        urgency: str = "normal"
    ) -> Dict[str, Any]:
        """Create a HITL request"""
        try:
            # Get task
            task = self.get_task(task_id)
            if not task:
                self.logger.warning(f"Task {task_id} not found")
                raise ValueError(f"Task {task_id} not found")
            
            # Create request ID
            request_id = str(uuid.uuid4())
            
            # Create HITL request
            hitl_request = {
                "request_id": request_id,
                "task_id": task_id,
                "request_type": request_type,
                "request_description": request_description,
                "options": options or [],
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Store HITL request
            self.hitl_requests[request_id] = hitl_request
            
            # Add request to task
            task.hitl_requests.append(hitl_request)
            
            # Update task status
            task.status = TaskStatus.AWAITING_HITL
            
            # Update task updated_at
            task.updated_at = datetime.now().isoformat()
            
            # Update in database if available
            if self.db_session:
                # Update task
                db_task = self.db_session.query(DBTask).filter(DBTask.id == uuid.UUID(task_id)).first()
                if db_task:
                    db_task.status = TaskStatus.AWAITING_HITL
                    db_task.updated_at = datetime.now()
                
                # Create HITL request
                db_hitl_request = DBHITLRequest(
                    id=uuid.UUID(request_id),
                    task_id=uuid.UUID(task_id),
                    request_type=request_type,
                    request_description=request_description,
                    options=options or [],
                    status="pending"
                )
                
                self.db_session.add(db_hitl_request)
                self.db_session.commit()
            
            # Publish HITL request message
            message = HITLRequestMessage(
                task_id=task_id,
                request_type=request_type,
                request_description=request_description,
                options=options or [],
                timeout_seconds=timeout_seconds,
                urgency=urgency,
                sender_id=task.assigned_agent_id,
                recipient_id="human_interface"
            )
            
            topic = "cauldron.agent.hitl.request"
            self.message_broker.publish(topic, message)
            
            self.logger.info(f"Created HITL request {request_id} for task {task_id}")
            
            return hitl_request
            
        except Exception as e:
            self.logger.error(f"Error creating HITL request: {str(e)}")
            raise
    
    def get_hitl_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get a HITL request by ID"""
        try:
            # Check in-memory cache first
            if request_id in self.hitl_requests:
                return self.hitl_requests[request_id]
            
            # Check database if available
            if self.db_session:
                db_hitl_request = self.db_session.query(DBHITLRequest).filter(DBHITLRequest.id == uuid.UUID(request_id)).first()
                if db_hitl_request:
                    # Convert to dictionary
                    hitl_request = {
                        "request_id": str(db_hitl_request.id),
                        "task_id": str(db_hitl_request.task_id),
                        "request_type": db_hitl_request.request_type,
                        "request_description": db_hitl_request.request_description,
                        "options": db_hitl_request.options,
                        "status": db_hitl_request.status,
                        "response": db_hitl_request.response,
                        "response_details": db_hitl_request.response_details,
                        "human_id": db_hitl_request.human_id,
                        "created_at": db_hitl_request.created_at.isoformat(),
                        "updated_at": db_hitl_request.updated_at.isoformat(),
                        "completed_at": db_hitl_request.completed_at.isoformat() if db_hitl_request.completed_at else None
                    }
                    
                    # Add to in-memory cache
                    self.hitl_requests[request_id] = hitl_request
                    
                    return hitl_request
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting HITL request: {str(e)}")
            return None
    
    def get_hitl_requests(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all HITL requests"""
        try:
            # If database is available, use it
            if self.db_session:
                db_hitl_requests = self.db_session.query(DBHITLRequest).order_by(DBHITLRequest.created_at.desc()).limit(limit).offset(offset).all()
                
                hitl_requests = []
                for db_hitl_request in db_hitl_requests:
                    # Convert to dictionary
                    hitl_request = {
                        "request_id": str(db_hitl_request.id),
                        "task_id": str(db_hitl_request.task_id),
                        "request_type": db_hitl_request.request_type,
                        "request_description": db_hitl_request.request_description,
                        "options": db_hitl_request.options,
                        "status": db_hitl_request.status,
                        "response": db_hitl_request.response,
                        "response_details": db_hitl_request.response_details,
                        "human_id": db_hitl_request.human_id,
                        "created_at": db_hitl_request.created_at.isoformat(),
                        "updated_at": db_hitl_request.updated_at.isoformat(),
                        "completed_at": db_hitl_request.completed_at.isoformat() if db_hitl_request.completed_at else None
                    }
                    
                    # Add to in-memory cache
                    self.hitl_requests[str(db_hitl_request.id)] = hitl_request
                    
                    hitl_requests.append(hitl_request)
                
                return hitl_requests
            
            # Otherwise, use in-memory cache
            return list(self.hitl_requests.values())[offset:offset+limit]
            
        except Exception as e:
            self.logger.error(f"Error getting HITL requests: {str(e)}")
            return []
    
    def respond_to_hitl_request(
        self,
        request_id: str,
        response: str,
        response_details: Dict[str, Any] = None,
        human_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """Respond to a HITL request"""
        try:
            # Get HITL request
            hitl_request = self.get_hitl_request(request_id)
            if not hitl_request:
                self.logger.warning(f"HITL request {request_id} not found")
                return None
            
            # Get task
            task_id = hitl_request["task_id"]
            task = self.get_task(task_id)
            if not task:
                self.logger.warning(f"Task {task_id} not found")
                return None
            
            # Update HITL request
            hitl_request["status"] = "completed"
            hitl_request["response"] = response
            hitl_request["response_details"] = response_details or {}
            hitl_request["human_id"] = human_id
            hitl_request["completed_at"] = datetime.now().isoformat()
            hitl_request["updated_at"] = hitl_request["completed_at"]
            
            # Update in database if available
            if self.db_session:
                db_hitl_request = self.db_session.query(DBHITLRequest).filter(DBHITLRequest.id == uuid.UUID(request_id)).first()
                if db_hitl_request:
                    db_hitl_request.status = "completed"
                    db_hitl_request.response = response
                    db_hitl_request.response_details = response_details or {}
                    db_hitl_request.human_id = human_id
                    db_hitl_request.completed_at = datetime.now()
                    db_hitl_request.updated_at = db_hitl_request.completed_at
                    
                    self.db_session.commit()
            
            # Update task HITL request
            for req in task.hitl_requests:
                if req["request_id"] == request_id:
                    req["status"] = "completed"
                    req["response"] = response
                    req["response_details"] = response_details or {}
                    req["human_id"] = human_id
                    req["completed_at"] = hitl_request["completed_at"]
                    req["updated_at"] = hitl_request["updated_at"]
            
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            
            # Update task updated_at
            task.updated_at = datetime.now().isoformat()
            
            # Update task in database if available
            if self.db_session:
                db_task = self.db_session.query(DBTask).filter(DBTask.id == uuid.UUID(task_id)).first()
                if db_task:
                    db_task.status = TaskStatus.IN_PROGRESS
                    db_task.updated_at = datetime.now()
                    
                    self.db_session.commit()
            
            # Publish HITL response message
            message = HITLResponseMessage(
                task_id=task_id,
                request_id=request_id,
                response=response,
                response_details=response_details or {},
                human_id=human_id,
                sender_id="human_interface",
                recipient_id=task.assigned_agent_id
            )
            
            topic = "cauldron.agent.hitl.response"
            self.message_broker.publish(topic, message)
            
            # Forward response to agent
            agent_topic = f"cauldron.agent.hitl.response.{task.assigned_agent_id}"
            self.message_broker.publish(agent_topic, message)
            
            self.logger.info(f"Responded to HITL request {request_id}")
            
            return hitl_request
            
        except Exception as e:
            self.logger.error(f"Error responding to HITL request: {str(e)}")
            return None
    
    def get_task_hitl_requests(self, task_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get HITL requests for a task"""
        try:
            # If database is available, use it
            if self.db_session:
                db_hitl_requests = self.db_session.query(DBHITLRequest).filter(DBHITLRequest.task_id == uuid.UUID(task_id)).order_by(DBHITLRequest.created_at.desc()).limit(limit).offset(offset).all()
                
                hitl_requests = []
                for db_hitl_request in db_hitl_requests:
                    # Convert to dictionary
                    hitl_request = {
                        "request_id": str(db_hitl_request.id),
                        "task_id": str(db_hitl_request.task_id),
                        "request_type": db_hitl_request.request_type,
                        "request_description": db_hitl_request.request_description,
                        "options": db_hitl_request.options,
                        "status": db_hitl_request.status,
                        "response": db_hitl_request.response,
                        "response_details": db_hitl_request.response_details,
                        "human_id": db_hitl_request.human_id,
                        "created_at": db_hitl_request.created_at.isoformat(),
                        "updated_at": db_hitl_request.updated_at.isoformat(),
                        "completed_at": db_hitl_request.completed_at.isoformat() if db_hitl_request.completed_at else None
                    }
                    
                    # Add to in-memory cache
                    self.hitl_requests[str(db_hitl_request.id)] = hitl_request
                    
                    hitl_requests.append(hitl_request)
                
                return hitl_requests
            
            # Otherwise, use in-memory cache
            return [req for req in self.hitl_requests.values() if req["task_id"] == task_id][offset:offset+limit]
            
        except Exception as e:
            self.logger.error(f"Error getting task HITL requests: {str(e)}")
            return []
    
    def get_hitl_requests_by_status(self, status: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get HITL requests by status"""
        try:
            # If database is available, use it
            if self.db_session:
                db_hitl_requests = self.db_session.query(DBHITLRequest).filter(DBHITLRequest.status == status).order_by(DBHITLRequest.created_at.desc()).limit(limit).offset(offset).all()
                
                hitl_requests = []
                for db_hitl_request in db_hitl_requests:
                    # Convert to dictionary
                    hitl_request = {
                        "request_id": str(db_hitl_request.id),
                        "task_id": str(db_hitl_request.task_id),
                        "request_type": db_hitl_request.request_type,
                        "request_description": db_hitl_request.request_description,
                        "options": db_hitl_request.options,
                        "status": db_hitl_request.status,
                        "response": db_hitl_request.response,
                        "response_details": db_hitl_request.response_details,
                        "human_id": db_hitl_request.human_id,
                        "created_at": db_hitl_request.created_at.isoformat(),
                        "updated_at": db_hitl_request.updated_at.isoformat(),
                        "completed_at": db_hitl_request.completed_at.isoformat() if db_hitl_request.completed_at else None
                    }
                    
                    # Add to in-memory cache
                    self.hitl_requests[str(db_hitl_request.id)] = hitl_request
                    
                    hitl_requests.append(hitl_request)
                
                return hitl_requests
            
            # Otherwise, use in-memory cache
            return [req for req in self.hitl_requests.values() if req["status"] == status][offset:offset+limit]
            
        except Exception as e:
            self.logger.error(f"Error getting HITL requests by status: {str(e)}")
            return []
    
    def get_hitl_requests_by_type(self, request_type: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get HITL requests by type"""
        try:
            # If database is available, use it
            if self.db_session:
                db_hitl_requests = self.db_session.query(DBHITLRequest).filter(DBHITLRequest.request_type == request_type).order_by(DBHITLRequest.created_at.desc()).limit(limit).offset(offset).all()
                
                hitl_requests = []
                for db_hitl_request in db_hitl_requests:
                    # Convert to dictionary
                    hitl_request = {
                        "request_id": str(db_hitl_request.id),
                        "task_id": str(db_hitl_request.task_id),
                        "request_type": db_hitl_request.request_type,
                        "request_description": db_hitl_request.request_description,
                        "options": db_hitl_request.options,
                        "status": db_hitl_request.status,
                        "response": db_hitl_request.response,
                        "response_details": db_hitl_request.response_details,
                        "human_id": db_hitl_request.human_id,
                        "created_at": db_hitl_request.created_at.isoformat(),
                        "updated_at": db_hitl_request.updated_at.isoformat(),
                        "completed_at": db_hitl_request.completed_at.isoformat() if db_hitl_request.completed_at else None
                    }
                    
                    # Add to in-memory cache
                    self.hitl_requests[str(db_hitl_request.id)] = hitl_request
                    
                    hitl_requests.append(hitl_request)
                
                return hitl_requests
            
            # Otherwise, use in-memory cache
            return [req for req in self.hitl_requests.values() if req["request_type"] == request_type][offset:offset+limit]
            
        except Exception as e:
            self.logger.error(f"Error getting HITL requests by type: {str(e)}")
            return []
    
    def _reassign_task(self, task: Task):
        """Reassign a task to an agent"""
        try:
            # Update task status
            task.status = TaskStatus.RECEIVED
            
            # Update task updated_at
            task.updated_at = datetime.now().isoformat()
            
            # Update in database if available
            if self.db_session:
                db_task = self.db_session.query(DBTask).filter(DBTask.id == uuid.UUID(task.task_id)).first()
                if db_task:
                    db_task.status = TaskStatus.RECEIVED
                    db_task.updated_at = datetime.now()
                    
                    self.db_session.commit()
            
            # Create task assignment message
            message = TaskAssignmentMessage(
                task_id=task.task_id,
                task_type=task.task_type,
                task_description=task.task_description,
                priority=task.priority,
                input_data=task.input_data,
                max_retries=task.max_retries,
                sender_id="agent_orchestration_service",
                recipient_id=task.assigned_agent_id,
                recipient_level=task.assigned_agent_level
            )
            
            # Add retry information
            message.payload["retry_count"] = task.retry_count
            message.payload["previous_error"] = task.error_data
            
            # Publish message
            topic = f"cauldron.agent.task.assign.{task.assigned_agent_id}"
            self.message_broker.publish(topic, message)
            
            self.logger.info(f"Reassigned task {task.task_id} to agent {task.assigned_agent_id} (retry {task.retry_count})")
            
        except Exception as e:
            self.logger.error(f"Error reassigning task: {str(e)}")
            
            # Update task status
            task.status = TaskStatus.FAILED
            
            # Update task error
            task.error_data = {
                "error_type": "reassignment_error",
                "error_message": f"Failed to reassign task: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            
            # Update task updated_at
            task.updated_at = datetime.now().isoformat()
            
            # Update in database if available
            if self.db_session:
                db_task = self.db_session.query(DBTask).filter(DBTask.id == uuid.UUID(task.task_id)).first()
                if db_task:
                    db_task.status = TaskStatus.FAILED
                    db_task.error_data = task.error_data
                    db_task.updated_at = datetime.now()
                    
                    self.db_session.commit()
    
    def _process_parent_task(self, parent_task_id: str):
        """Process parent task after subtask completion"""
        try:
            # Get parent task
            parent_task = self.get_task(parent_task_id)
            if not parent_task:
                self.logger.warning(f"Parent task {parent_task_id} not found")
                return
            
            # Get subtasks
            subtasks = self.get_subtasks(parent_task_id)
            
            # Check if all subtasks are completed
            all_completed = True
            any_failed = False
            
            for subtask in subtasks:
                if subtask.status != TaskStatus.COMPLETED:
                    all_completed = False
                    if subtask.status == TaskStatus.FAILED:
                        any_failed = True
                    break
            
            if all_completed:
                # All subtasks completed successfully
                # Aggregate results
                aggregated_results = {
                    "subtask_results": {}
                }
                
                for subtask in subtasks:
                    aggregated_results["subtask_results"][subtask.task_id] = subtask.result_data
                
                # Update parent task
                self.update_task_result(
                    task_id=parent_task_id,
                    result_data=aggregated_results
                )
                
                self.logger.info(f"All subtasks completed for parent task {parent_task_id}")
                
            elif any_failed:
                # At least one subtask failed
                # Update parent task
                self.update_task_error(
                    task_id=parent_task_id,
                    error_type="subtask_failure",
                    error_message="One or more subtasks failed",
                    error_details={
                        "failed_subtasks": [
                            subtask.task_id for subtask in subtasks
                            if subtask.status == TaskStatus.FAILED
                        ]
                    }
                )
                
                self.logger.info(f"One or more subtasks failed for parent task {parent_task_id}")
            
        except Exception as e:
            self.logger.error(f"Error processing parent task: {str(e)}")