nscode"""
Task API for AetherCore

This module provides the API endpoints for managing tasks,
including creating, retrieving, updating, and deleting tasks.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from pydantic import BaseModel

# Local imports
from ..core.agent_communication import TaskStatus
from ..services.agent_orchestration_db import AgentOrchestrationService, Task


# Pydantic models for API requests and responses
class TaskCreate(BaseModel):
    """Model for creating a task"""
    task_type: str
    task_description: str
    assigned_agent_id: Optional[str] = None
    priority: int = 5
    input_data: Dict[str, Any] = {}
    parent_task_id: Optional[str] = None
    max_retries: int = 3


class TaskResponse(BaseModel):
    """Model for task response"""
    task_id: str
    task_type: str
    task_description: str
    assigned_agent_id: Optional[str] = None
    status: str
    priority: int
    input_data: Dict[str, Any] = {}
    result_data: Dict[str, Any] = {}
    error_data: Dict[str, Any] = {}
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    parent_task_id: Optional[str] = None
    subtask_ids: List[str] = []
    hitl_requests: List[Dict[str, Any]] = []
    retry_count: int = 0
    max_retries: int = 3


class TaskStatusUpdate(BaseModel):
    """Model for updating task status"""
    status: str
    progress: Optional[float] = None
    details: Optional[str] = None


class TaskResultUpdate(BaseModel):
    """Model for updating task result"""
    result_data: Dict[str, Any]
    execution_time_ms: Optional[int] = None
    metrics: Dict[str, Any] = {}


class TaskErrorUpdate(BaseModel):
    """Model for updating task error"""
    error_type: str
    error_message: str
    error_details: Dict[str, Any] = {}
    retry: bool = False


class TaskAPI:
    """API for managing tasks"""
    
    def __init__(self, agent_orchestration_service: AgentOrchestrationService):
        """Initialize the task API"""
        self.agent_orchestration_service = agent_orchestration_service
        self.logger = logging.getLogger(__name__)
        
        # Create router
        self.router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register API routes"""
        # Task management
        self.router.post(
            "/",
            response_model=TaskResponse,
            summary="Create a task",
            description="Create a new task for an agent"
        )(self.create_task)
        
        self.router.get(
            "/",
            response_model=List[TaskResponse],
            summary="Get all tasks",
            description="Retrieve all tasks"
        )(self.get_tasks)
        
        self.router.get(
            "/{task_id}",
            response_model=TaskResponse,
            summary="Get a task",
            description="Retrieve a specific task by ID"
        )(self.get_task)
        
        self.router.put(
            "/{task_id}/status",
            response_model=TaskResponse,
            summary="Update task status",
            description="Update the status of a task"
        )(self.update_task_status)
        
        self.router.put(
            "/{task_id}/result",
            response_model=TaskResponse,
            summary="Update task result",
            description="Update the result of a task"
        )(self.update_task_result)
        
        self.router.put(
            "/{task_id}/error",
            response_model=TaskResponse,
            summary="Update task error",
            description="Update the error of a task"
        )(self.update_task_error)
        
        self.router.delete(
            "/{task_id}",
            response_model=Dict[str, Any],
            summary="Delete a task",
            description="Delete a specific task by ID"
        )(self.delete_task)
        
        # Task filtering
        self.router.get(
            "/agent/{agent_id}",
            response_model=List[TaskResponse],
            summary="Get tasks for an agent",
            description="Retrieve all tasks assigned to a specific agent"
        )(self.get_agent_tasks)
        
        self.router.get(
            "/status/{status}",
            response_model=List[TaskResponse],
            summary="Get tasks by status",
            description="Retrieve all tasks with a specific status"
        )(self.get_tasks_by_status)
        
        self.router.get(
            "/{task_id}/subtasks",
            response_model=List[TaskResponse],
            summary="Get subtasks",
            description="Retrieve all subtasks of a specific task"
        )(self.get_subtasks)
    
    async def create_task(self, task_data: TaskCreate):
        """Create a task"""
        try:
            # Create task
            task = self.agent_orchestration_service.create_task(
                task_type=task_data.task_type,
                task_description=task_data.task_description,
                assigned_agent_id=task_data.assigned_agent_id,
                priority=task_data.priority,
                input_data=task_data.input_data,
                parent_task_id=task_data.parent_task_id,
                max_retries=task_data.max_retries
            )
            
            # Convert to response model
            response = TaskResponse(
                task_id=task.task_id,
                task_type=task.task_type,
                task_description=task.task_description,
                assigned_agent_id=task.assigned_agent_id,
                status=task.status.value if task.status else None,
                priority=task.priority,
                input_data=task.input_data,
                result_data=task.result_data,
                error_data=task.error_data,
                created_at=task.created_at,
                updated_at=task.updated_at,
                completed_at=task.completed_at,
                parent_task_id=task.parent_task_id,
                subtask_ids=task.subtask_ids,
                hitl_requests=task.hitl_requests,
                retry_count=task.retry_count,
                max_retries=task.max_retries
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error creating task: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_tasks(self, limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
        """Get all tasks"""
        try:
            # Get tasks from service
            tasks = self.agent_orchestration_service.get_tasks(limit=limit, offset=offset)
            
            # Convert to response models
            responses = []
            for task in tasks:
                responses.append(
                    TaskResponse(
                        task_id=task.task_id,
                        task_type=task.task_type,
                        task_description=task.task_description,
                        assigned_agent_id=task.assigned_agent_id,
                        status=task.status.value if task.status else None,
                        priority=task.priority,
                        input_data=task.input_data,
                        result_data=task.result_data,
                        error_data=task.error_data,
                        created_at=task.created_at,
                        updated_at=task.updated_at,
                        completed_at=task.completed_at,
                        parent_task_id=task.parent_task_id,
                        subtask_ids=task.subtask_ids,
                        hitl_requests=task.hitl_requests,
                        retry_count=task.retry_count,
                        max_retries=task.max_retries
                    )
                )
            
            return responses
            
        except Exception as e:
            self.logger.error(f"Error getting tasks: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_task(self, task_id: str = Path(..., description="The ID of the task to retrieve")):
        """Get a task by ID"""
        try:
            # Get task from service
            task = self.agent_orchestration_service.get_task(task_id)
            
            if not task:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
            # Convert to response model
            response = TaskResponse(
                task_id=task.task_id,
                task_type=task.task_type,
                task_description=task.task_description,
                assigned_agent_id=task.assigned_agent_id,
                status=task.status.value if task.status else None,
                priority=task.priority,
                input_data=task.input_data,
                result_data=task.result_data,
                error_data=task.error_data,
                created_at=task.created_at,
                updated_at=task.updated_at,
                completed_at=task.completed_at,
                parent_task_id=task.parent_task_id,
                subtask_ids=task.subtask_ids,
                hitl_requests=task.hitl_requests,
                retry_count=task.retry_count,
                max_retries=task.max_retries
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error getting task: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_task_status(
        self,
        task_id: str = Path(..., description="The ID of the task to update"),
        status_data: TaskStatusUpdate = Body(...)
    ):
        """Update task status"""
        try:
            # Get task from service
            task = self.agent_orchestration_service.get_task(task_id)
            
            if not task:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
            # Update task status
            try:
                task_status = TaskStatus(status_data.status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid task status: {status_data.status}")
            
            task = self.agent_orchestration_service.update_task_status(
                task_id=task_id,
                status=task_status,
                progress=status_data.progress,
                details=status_data.details
            )
            
            # Convert to response model
            response = TaskResponse(
                task_id=task.task_id,
                task_type=task.task_type,
                task_description=task.task_description,
                assigned_agent_id=task.assigned_agent_id,
                status=task.status.value if task.status else None,
                priority=task.priority,
                input_data=task.input_data,
                result_data=task.result_data,
                error_data=task.error_data,
                created_at=task.created_at,
                updated_at=task.updated_at,
                completed_at=task.completed_at,
                parent_task_id=task.parent_task_id,
                subtask_ids=task.subtask_ids,
                hitl_requests=task.hitl_requests,
                retry_count=task.retry_count,
                max_retries=task.max_retries
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error updating task status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_task_result(
        self,
        task_id: str = Path(..., description="The ID of the task to update"),
        result_data: TaskResultUpdate = Body(...)
    ):
        """Update task result"""
        try:
            # Get task from service
            task = self.agent_orchestration_service.get_task(task_id)
            
            if not task:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
            # Update task result
            task = self.agent_orchestration_service.update_task_result(
                task_id=task_id,
                result_data=result_data.result_data,
                execution_time_ms=result_data.execution_time_ms,
                metrics=result_data.metrics
            )
            
            # Convert to response model
            response = TaskResponse(
                task_id=task.task_id,
                task_type=task.task_type,
                task_description=task.task_description,
                assigned_agent_id=task.assigned_agent_id,
                status=task.status.value if task.status else None,
                priority=task.priority,
                input_data=task.input_data,
                result_data=task.result_data,
                error_data=task.error_data,
                created_at=task.created_at,
                updated_at=task.updated_at,
                completed_at=task.completed_at,
                parent_task_id=task.parent_task_id,
                subtask_ids=task.subtask_ids,
                hitl_requests=task.hitl_requests,
                retry_count=task.retry_count,
                max_retries=task.max_retries
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error updating task result: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_task_error(
        self,
        task_id: str = Path(..., description="The ID of the task to update"),
        error_data: TaskErrorUpdate = Body(...)
    ):
        """Update task error"""
        try:
            # Get task from service
            task = self.agent_orchestration_service.get_task(task_id)
            
            if not task:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
            # Update task error
            task = self.agent_orchestration_service.update_task_error(
                task_id=task_id,
                error_type=error_data.error_type,
                error_message=error_data.error_message,
                error_details=error_data.error_details,
                retry=error_data.retry
            )
            
            # Convert to response model
            response = TaskResponse(
                task_id=task.task_id,
                task_type=task.task_type,
                task_description=task.task_description,
                assigned_agent_id=task.assigned_agent_id,
                status=task.status.value if task.status else None,
                priority=task.priority,
                input_data=task.input_data,
                result_data=task.result_data,
                error_data=task.error_data,
                created_at=task.created_at,
                updated_at=task.updated_at,
                completed_at=task.completed_at,
                parent_task_id=task.parent_task_id,
                subtask_ids=task.subtask_ids,
                hitl_requests=task.hitl_requests,
                retry_count=task.retry_count,
                max_retries=task.max_retries
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error updating task error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def delete_task(self, task_id: str = Path(..., description="The ID of the task to delete")):
        """Delete a task"""
        try:
            # Get task from service
            task = self.agent_orchestration_service.get_task(task_id)
            
            if not task:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
            # Delete task
            success = self.agent_orchestration_service.delete_task(task_id)
            
            if not success:
                raise HTTPException(status_code=500, detail=f"Failed to delete task {task_id}")
            
            return {"message": f"Task {task_id} deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error deleting task: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_agent_tasks(
        self,
        agent_id: str = Path(..., description="The ID of the agent"),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0)
    ):
        """Get tasks for an agent"""
        try:
            # Get tasks from service
            tasks = self.agent_orchestration_service.get_agent_tasks(
                agent_id=agent_id,
                limit=limit,
                offset=offset
            )
            
            # Convert to response models
            responses = []
            for task in tasks:
                responses.append(
                    TaskResponse(
                        task_id=task.task_id,
                        task_type=task.task_type,
                        task_description=task.task_description,
                        assigned_agent_id=task.assigned_agent_id,
                        status=task.status.value if task.status else None,
                        priority=task.priority,
                        input_data=task.input_data,
                        result_data=task.result_data,
                        error_data=task.error_data,
                        created_at=task.created_at,
                        updated_at=task.updated_at,
                        completed_at=task.completed_at,
                        parent_task_id=task.parent_task_id,
                        subtask_ids=task.subtask_ids,
                        hitl_requests=task.hitl_requests,
                        retry_count=task.retry_count,
                        max_retries=task.max_retries
                    )
                )
            
            return responses
            
        except Exception as e:
            self.logger.error(f"Error getting agent tasks: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_tasks_by_status(
        self,
        status: str = Path(..., description="The status of the tasks to retrieve"),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0)
    ):
        """Get tasks by status"""
        try:
            # Convert status string to enum
            try:
                task_status = TaskStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid task status: {status}")
            
            # Get tasks from service
            tasks = self.agent_orchestration_service.get_tasks_by_status(
                status=task_status,
                limit=limit,
                offset=offset
            )
            
            # Convert to response models
            responses = []
            for task in tasks:
                responses.append(
                    TaskResponse(
                        task_id=task.task_id,
                        task_type=task.task_type,
                        task_description=task.task_description,
                        assigned_agent_id=task.assigned_agent_id,
                        status=task.status.value if task.status else None,
                        priority=task.priority,
                        input_data=task.input_data,
                        result_data=task.result_data,
                        error_data=task.error_data,
                        created_at=task.created_at,
                        updated_at=task.updated_at,
                        completed_at=task.completed_at,
                        parent_task_id=task.parent_task_id,
                        subtask_ids=task.subtask_ids,
                        hitl_requests=task.hitl_requests,
                        retry_count=task.retry_count,
                        max_retries=task.max_retries
                    )
                )
            
            return responses
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error getting tasks by status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_subtasks(
        self,
        task_id: str = Path(..., description="The ID of the parent task"),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0)
    ):
        """Get subtasks of a task"""
        try:
            # Get task from service
            task = self.agent_orchestration_service.get_task(task_id)
            
            if not task:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
            # Get subtasks from service
            subtasks = self.agent_orchestration_service.get_subtasks(
                task_id=task_id,
                limit=limit,
                offset=offset
            )
            
            # Convert to response models
            responses = []
            for subtask in subtasks:
                responses.append(
                    TaskResponse(
                        task_id=subtask.task_id,
                        task_type=subtask.task_type,
                        task_description=subtask.task_description,
                        assigned_agent_id=subtask.assigned_agent_id,
                        status=subtask.status.value if subtask.status else None,
                        priority=subtask.priority,
                        input_data=subtask.input_data,
                        result_data=subtask.result_data,
                        error_data=subtask.error_data,
                        created_at=subtask.created_at,
                        updated_at=subtask.updated_at,
                        completed_at=subtask.completed_at,
                        parent_task_id=subtask.parent_task_id,
                        subtask_ids=subtask.subtask_ids,
                        hitl_requests=subtask.hitl_requests,
                        retry_count=subtask.retry_count,
                        max_retries=subtask.max_retries
                    )
                )
            
            return responses
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error getting subtasks: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))