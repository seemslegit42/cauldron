"""
HITL Service for AetherCore

This module provides the service layer for managing human-in-the-loop (HITL) requests,
including creating, retrieving, and responding to requests.
"""

import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

# Local imports
from ..models.database_models import HITLRequest as HITLRequestModel
from ..models.database_models import Task as TaskModel


class HITLRequest:
    """HITL request data class"""
    
    def __init__(
        self,
        request_id: str,
        task_id: str,
        request_type: str,
        request_description: str,
        options: List[Dict[str, Any]],
        status: str,
        response: Optional[str] = None,
        response_details: Optional[Dict[str, Any]] = None,
        human_id: Optional[str] = None,
        created_at: str = None,
        updated_at: str = None,
        completed_at: Optional[str] = None,
        timeout_seconds: int = 3600,
        urgency: str = "normal"
    ):
        self.request_id = request_id
        self.task_id = task_id
        self.request_type = request_type
        self.request_description = request_description
        self.options = options
        self.status = status
        self.response = response
        self.response_details = response_details
        self.human_id = human_id
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
        self.completed_at = completed_at
        self.timeout_seconds = timeout_seconds
        self.urgency = urgency


class HITLService:
    """Service for managing HITL requests"""
    
    def __init__(self, db_session: Session):
        """Initialize the HITL service"""
        self.db = db_session
        self.logger = logging.getLogger(__name__)
    
    def create_hitl_request(
        self,
        task_id: str,
        request_type: str,
        request_description: str,
        options: List[Dict[str, Any]] = None,
        timeout_seconds: int = 3600,
        urgency: str = "normal"
    ) -> HITLRequest:
        """Create a new HITL request"""
        try:
            # Create HITL request model
            hitl_request_model = HITLRequestModel(
                id=uuid.uuid4(),
                task_id=uuid.UUID(task_id),
                request_type=request_type,
                request_description=request_description,
                options=options or [],
                status="pending",
                timeout_seconds=timeout_seconds,
                urgency=urgency
            )
            
            # Add to database
            self.db.add(hitl_request_model)
            self.db.commit()
            self.db.refresh(hitl_request_model)
            
            # Convert to data class
            hitl_request = self._convert_to_data_class(hitl_request_model)
            
            return hitl_request
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating HITL request: {str(e)}")
            raise
    
    def get_hitl_request(self, request_id: str) -> Optional[HITLRequest]:
        """Get a HITL request by ID"""
        try:
            # Query database
            hitl_request_model = self.db.query(HITLRequestModel).filter(
                HITLRequestModel.id == uuid.UUID(request_id)
            ).first()
            
            if not hitl_request_model:
                return None
            
            # Convert to data class
            hitl_request = self._convert_to_data_class(hitl_request_model)
            
            return hitl_request
            
        except Exception as e:
            self.logger.error(f"Error getting HITL request: {str(e)}")
            raise
    
    def get_hitl_requests(self, limit: int = 100, offset: int = 0) -> List[HITLRequest]:
        """Get all HITL requests"""
        try:
            # Query database
            hitl_request_models = self.db.query(HITLRequestModel).order_by(
                desc(HITLRequestModel.created_at)
            ).limit(limit).offset(offset).all()
            
            # Convert to data classes
            hitl_requests = [self._convert_to_data_class(model) for model in hitl_request_models]
            
            return hitl_requests
            
        except Exception as e:
            self.logger.error(f"Error getting HITL requests: {str(e)}")
            raise
    
    def get_hitl_requests_by_status(self, status: str, limit: int = 100, offset: int = 0) -> List[HITLRequest]:
        """Get HITL requests by status"""
        try:
            # Query database
            hitl_request_models = self.db.query(HITLRequestModel).filter(
                HITLRequestModel.status == status
            ).order_by(
                desc(HITLRequestModel.created_at)
            ).limit(limit).offset(offset).all()
            
            # Convert to data classes
            hitl_requests = [self._convert_to_data_class(model) for model in hitl_request_models]
            
            return hitl_requests
            
        except Exception as e:
            self.logger.error(f"Error getting HITL requests by status: {str(e)}")
            raise
    
    def get_hitl_requests_by_type(self, request_type: str, limit: int = 100, offset: int = 0) -> List[HITLRequest]:
        """Get HITL requests by type"""
        try:
            # Query database
            hitl_request_models = self.db.query(HITLRequestModel).filter(
                HITLRequestModel.request_type == request_type
            ).order_by(
                desc(HITLRequestModel.created_at)
            ).limit(limit).offset(offset).all()
            
            # Convert to data classes
            hitl_requests = [self._convert_to_data_class(model) for model in hitl_request_models]
            
            return hitl_requests
            
        except Exception as e:
            self.logger.error(f"Error getting HITL requests by type: {str(e)}")
            raise
    
    def get_hitl_requests_by_task(self, task_id: str, limit: int = 100, offset: int = 0) -> List[HITLRequest]:
        """Get HITL requests for a task"""
        try:
            # Query database
            hitl_request_models = self.db.query(HITLRequestModel).filter(
                HITLRequestModel.task_id == uuid.UUID(task_id)
            ).order_by(
                desc(HITLRequestModel.created_at)
            ).limit(limit).offset(offset).all()
            
            # Convert to data classes
            hitl_requests = [self._convert_to_data_class(model) for model in hitl_request_models]
            
            return hitl_requests
            
        except Exception as e:
            self.logger.error(f"Error getting HITL requests by task: {str(e)}")
            raise
    
    def update_hitl_request(
        self,
        request_id: str,
        status: Optional[str] = None,
        response: Optional[str] = None,
        response_details: Optional[Dict[str, Any]] = None,
        human_id: Optional[str] = None,
        completed_at: Optional[str] = None
    ) -> Optional[HITLRequest]:
        """Update a HITL request"""
        try:
            # Query database
            hitl_request_model = self.db.query(HITLRequestModel).filter(
                HITLRequestModel.id == uuid.UUID(request_id)
            ).first()
            
            if not hitl_request_model:
                return None
            
            # Update fields
            if status is not None:
                hitl_request_model.status = status
            
            if response is not None:
                hitl_request_model.response = response
            
            if response_details is not None:
                hitl_request_model.response_details = response_details
            
            if human_id is not None:
                hitl_request_model.human_id = human_id
            
            if completed_at is not None:
                hitl_request_model.completed_at = completed_at
            
            # Update timestamp
            hitl_request_model.updated_at = datetime.utcnow()
            
            # Commit changes
            self.db.commit()
            self.db.refresh(hitl_request_model)
            
            # Convert to data class
            hitl_request = self._convert_to_data_class(hitl_request_model)
            
            return hitl_request
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating HITL request: {str(e)}")
            raise
    
    def delete_hitl_request(self, request_id: str) -> bool:
        """Delete a HITL request"""
        try:
            # Query database
            hitl_request_model = self.db.query(HITLRequestModel).filter(
                HITLRequestModel.id == uuid.UUID(request_id)
            ).first()
            
            if not hitl_request_model:
                return False
            
            # Delete from database
            self.db.delete(hitl_request_model)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error deleting HITL request: {str(e)}")
            raise
    
    def _convert_to_data_class(self, hitl_request_model: HITLRequestModel) -> HITLRequest:
        """Convert a HITL request model to a data class"""
        return HITLRequest(
            request_id=str(hitl_request_model.id),
            task_id=str(hitl_request_model.task_id),
            request_type=hitl_request_model.request_type,
            request_description=hitl_request_model.request_description,
            options=hitl_request_model.options,
            status=hitl_request_model.status,
            response=hitl_request_model.response,
            response_details=hitl_request_model.response_details,
            human_id=hitl_request_model.human_id,
            created_at=hitl_request_model.created_at.isoformat() if hitl_request_model.created_at else None,
            updated_at=hitl_request_model.updated_at.isoformat() if hitl_request_model.updated_at else None,
            completed_at=hitl_request_model.completed_at.isoformat() if hitl_request_model.completed_at else None,
            timeout_seconds=hitl_request_model.timeout_seconds,
            urgency=hitl_request_model.urgency
        )