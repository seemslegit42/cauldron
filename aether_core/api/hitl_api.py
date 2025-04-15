"""
HITL API for AetherCore

This module provides the API endpoints for human-in-the-loop interactions,
including creating, retrieving, and responding to HITL requests.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Local imports
from ..config.database import get_db
from ..services.agent_orchestration_db import AgentOrchestrationService
from .websocket import websocket_api


# Pydantic models for API requests and responses
class HITLRequestCreate(BaseModel):
    """Model for creating a HITL request"""
    task_id: str
    request_type: str
    request_description: str
    options: List[Dict[str, Any]] = []
    timeout_seconds: int = 3600
    urgency: str = "normal"


class HITLRequestResponse(BaseModel):
    """Model for HITL request response"""
    request_id: str
    task_id: str
    request_type: str
    request_description: str
    options: List[Dict[str, Any]] = []
    status: str
    response: Optional[str] = None
    response_details: Dict[str, Any] = {}
    human_id: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None


class HITLResponseCreate(BaseModel):
    """Model for creating a HITL response"""
    response: str
    response_details: Dict[str, Any] = {}
    human_id: str


class HITLAPI:
    """API for human-in-the-loop interactions"""
    
    def __init__(self, agent_orchestration_service: AgentOrchestrationService):
        """Initialize the HITL API"""
        self.agent_orchestration_service = agent_orchestration_service
        self.logger = logging.getLogger(__name__)
        
        # Create router
        self.router = APIRouter(prefix="/api/v1/hitl", tags=["hitl"])
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register API routes"""
        # HITL request management
        self.router.post(
            "/requests",
            response_model=HITLRequestResponse,
            summary="Create a HITL request",
            description="Create a new human-in-the-loop request"
        )(self.create_hitl_request)
        
        self.router.get(
            "/requests",
            response_model=List[HITLRequestResponse],
            summary="Get all HITL requests",
            description="Retrieve all human-in-the-loop requests"
        )(self.get_hitl_requests)
        
        self.router.get(
            "/requests/{request_id}",
            response_model=HITLRequestResponse,
            summary="Get a HITL request",
            description="Retrieve a specific human-in-the-loop request by ID"
        )(self.get_hitl_request)
        
        self.router.post(
            "/requests/{request_id}/respond",
            response_model=HITLRequestResponse,
            summary="Respond to a HITL request",
            description="Provide a human response to a HITL request"
        )(self.respond_to_hitl_request)
        
        # HITL request filtering
        self.router.get(
            "/requests/task/{task_id}",
            response_model=List[HITLRequestResponse],
            summary="Get HITL requests for a task",
            description="Retrieve all HITL requests for a specific task"
        )(self.get_task_hitl_requests)
        
        self.router.get(
            "/requests/status/{status}",
            response_model=List[HITLRequestResponse],
            summary="Get HITL requests by status",
            description="Retrieve all HITL requests with a specific status"
        )(self.get_hitl_requests_by_status)
        
        self.router.get(
            "/requests/type/{request_type}",
            response_model=List[HITLRequestResponse],
            summary="Get HITL requests by type",
            description="Retrieve all HITL requests with a specific type"
        )(self.get_hitl_requests_by_type)
    
    async def create_hitl_request(self, request_data: HITLRequestCreate, db: Session = Depends(get_db)):
        """Create a HITL request"""
        try:
            # Create HITL request
            hitl_request = self.agent_orchestration_service.create_hitl_request(
                task_id=request_data.task_id,
                request_type=request_data.request_type,
                request_description=request_data.request_description,
                options=request_data.options,
                timeout_seconds=request_data.timeout_seconds,
                urgency=request_data.urgency
            )
            
            # Convert to response model
            response = HITLRequestResponse(
                request_id=hitl_request.get("request_id"),
                task_id=hitl_request.get("task_id"),
                request_type=hitl_request.get("request_type"),
                request_description=hitl_request.get("request_description"),
                options=hitl_request.get("options", []),
                status=hitl_request.get("status"),
                response=hitl_request.get("response"),
                response_details=hitl_request.get("response_details", {}),
                human_id=hitl_request.get("human_id"),
                created_at=hitl_request.get("created_at"),
                updated_at=hitl_request.get("updated_at"),
                completed_at=hitl_request.get("completed_at")
            )
            
            # Notify WebSocket clients
            await websocket_api.notify_hitl_request_created(response.dict())
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error creating HITL request: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_hitl_requests(self, limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
        """Get all HITL requests"""
        try:
            # Get HITL requests from service
            hitl_requests = self.agent_orchestration_service.get_hitl_requests(limit=limit, offset=offset)
            
            # Convert to response models
            responses = []
            for hitl_request in hitl_requests:
                responses.append(
                    HITLRequestResponse(
                        request_id=hitl_request.get("request_id"),
                        task_id=hitl_request.get("task_id"),
                        request_type=hitl_request.get("request_type"),
                        request_description=hitl_request.get("request_description"),
                        options=hitl_request.get("options", []),
                        status=hitl_request.get("status"),
                        response=hitl_request.get("response"),
                        response_details=hitl_request.get("response_details", {}),
                        human_id=hitl_request.get("human_id"),
                        created_at=hitl_request.get("created_at"),
                        updated_at=hitl_request.get("updated_at"),
                        completed_at=hitl_request.get("completed_at")
                    )
                )
            
            return responses
            
        except Exception as e:
            self.logger.error(f"Error getting HITL requests: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_hitl_request(self, request_id: str = Path(..., description="The ID of the HITL request to retrieve")):
        """Get a HITL request by ID"""
        try:
            # Get HITL request from service
            hitl_request = self.agent_orchestration_service.get_hitl_request(request_id)
            
            if not hitl_request:
                raise HTTPException(status_code=404, detail=f"HITL request {request_id} not found")
            
            # Convert to response model
            response = HITLRequestResponse(
                request_id=hitl_request.get("request_id"),
                task_id=hitl_request.get("task_id"),
                request_type=hitl_request.get("request_type"),
                request_description=hitl_request.get("request_description"),
                options=hitl_request.get("options", []),
                status=hitl_request.get("status"),
                response=hitl_request.get("response"),
                response_details=hitl_request.get("response_details", {}),
                human_id=hitl_request.get("human_id"),
                created_at=hitl_request.get("created_at"),
                updated_at=hitl_request.get("updated_at"),
                completed_at=hitl_request.get("completed_at")
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error getting HITL request: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def respond_to_hitl_request(
        self,
        request_id: str = Path(..., description="The ID of the HITL request to respond to"),
        response_data: HITLResponseCreate = Body(...),
        db: Session = Depends(get_db)
    ):
        """Respond to a HITL request"""
        try:
            # Get HITL request from service
            hitl_request = self.agent_orchestration_service.get_hitl_request(request_id)
            
            if not hitl_request:
                raise HTTPException(status_code=404, detail=f"HITL request {request_id} not found")
            
            # Check if request is already completed
            if hitl_request.get("status") == "completed":
                raise HTTPException(status_code=400, detail=f"HITL request {request_id} is already completed")
            
            # Respond to HITL request
            updated_request = self.agent_orchestration_service.respond_to_hitl_request(
                request_id=request_id,
                response=response_data.response,
                response_details=response_data.response_details,
                human_id=response_data.human_id
            )
            
            # Convert to response model
            response = HITLRequestResponse(
                request_id=updated_request.get("request_id"),
                task_id=updated_request.get("task_id"),
                request_type=updated_request.get("request_type"),
                request_description=updated_request.get("request_description"),
                options=updated_request.get("options", []),
                status=updated_request.get("status"),
                response=updated_request.get("response"),
                response_details=updated_request.get("response_details", {}),
                human_id=updated_request.get("human_id"),
                created_at=updated_request.get("created_at"),
                updated_at=updated_request.get("updated_at"),
                completed_at=updated_request.get("completed_at")
            )
            
            # Notify WebSocket clients
            await websocket_api.notify_hitl_request_updated(response.dict())
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error responding to HITL request: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_task_hitl_requests(
        self,
        task_id: str = Path(..., description="The ID of the task"),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0)
    ):
        """Get HITL requests for a task"""
        try:
            # Get HITL requests from service
            hitl_requests = self.agent_orchestration_service.get_task_hitl_requests(
                task_id=task_id,
                limit=limit,
                offset=offset
            )
            
            # Convert to response models
            responses = []
            for hitl_request in hitl_requests:
                responses.append(
                    HITLRequestResponse(
                        request_id=hitl_request.get("request_id"),
                        task_id=hitl_request.get("task_id"),
                        request_type=hitl_request.get("request_type"),
                        request_description=hitl_request.get("request_description"),
                        options=hitl_request.get("options", []),
                        status=hitl_request.get("status"),
                        response=hitl_request.get("response"),
                        response_details=hitl_request.get("response_details", {}),
                        human_id=hitl_request.get("human_id"),
                        created_at=hitl_request.get("created_at"),
                        updated_at=hitl_request.get("updated_at"),
                        completed_at=hitl_request.get("completed_at")
                    )
                )
            
            return responses
            
        except Exception as e:
            self.logger.error(f"Error getting task HITL requests: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_hitl_requests_by_status(
        self,
        status: str = Path(..., description="The status of the HITL requests to retrieve"),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0)
    ):
        """Get HITL requests by status"""
        try:
            # Validate status
            if status not in ["pending", "completed"]:
                raise HTTPException(status_code=400, detail=f"Invalid HITL request status: {status}")
            
            # Get HITL requests from service
            hitl_requests = self.agent_orchestration_service.get_hitl_requests_by_status(
                status=status,
                limit=limit,
                offset=offset
            )
            
            # Convert to response models
            responses = []
            for hitl_request in hitl_requests:
                responses.append(
                    HITLRequestResponse(
                        request_id=hitl_request.get("request_id"),
                        task_id=hitl_request.get("task_id"),
                        request_type=hitl_request.get("request_type"),
                        request_description=hitl_request.get("request_description"),
                        options=hitl_request.get("options", []),
                        status=hitl_request.get("status"),
                        response=hitl_request.get("response"),
                        response_details=hitl_request.get("response_details", {}),
                        human_id=hitl_request.get("human_id"),
                        created_at=hitl_request.get("created_at"),
                        updated_at=hitl_request.get("updated_at"),
                        completed_at=hitl_request.get("completed_at")
                    )
                )
            
            return responses
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error getting HITL requests by status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_hitl_requests_by_type(
        self,
        request_type: str = Path(..., description="The type of the HITL requests to retrieve"),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0)
    ):
        """Get HITL requests by type"""
        try:
            # Get HITL requests from service
            hitl_requests = self.agent_orchestration_service.get_hitl_requests_by_type(
                request_type=request_type,
                limit=limit,
                offset=offset
            )
            
            # Convert to response models
            responses = []
            for hitl_request in hitl_requests:
                responses.append(
                    HITLRequestResponse(
                        request_id=hitl_request.get("request_id"),
                        task_id=hitl_request.get("task_id"),
                        request_type=hitl_request.get("request_type"),
                        request_description=hitl_request.get("request_description"),
                        options=hitl_request.get("options", []),
                        status=hitl_request.get("status"),
                        response=hitl_request.get("response"),
                        response_details=hitl_request.get("response_details", {}),
                        human_id=hitl_request.get("human_id"),
                        created_at=hitl_request.get("created_at"),
                        updated_at=hitl_request.get("updated_at"),
                        completed_at=hitl_request.get("completed_at")
                    )
                )
            
            return responses
            
        except Exception as e:
            self.logger.error(f"Error getting HITL requests by type: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))