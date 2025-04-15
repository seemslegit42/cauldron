"""
WebSocket API for AetherCore

This module provides WebSocket endpoints for real-time communication with AetherCore,
including HITL request notifications.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..models.database_models import HITLRequest

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        """Initialize connection manager"""
        self.active_connections: Dict[str, List[WebSocket]] = {
            "hitl": []
        }
    
    async def connect(self, websocket: WebSocket, client_type: str):
        """Connect a client"""
        await websocket.accept()
        if client_type not in self.active_connections:
            self.active_connections[client_type] = []
        self.active_connections[client_type].append(websocket)
        logger.info(f"Client connected to {client_type} WebSocket")
    
    def disconnect(self, websocket: WebSocket, client_type: str):
        """Disconnect a client"""
        if client_type in self.active_connections:
            if websocket in self.active_connections[client_type]:
                self.active_connections[client_type].remove(websocket)
                logger.info(f"Client disconnected from {client_type} WebSocket")
    
    async def broadcast(self, message: Dict[str, Any], client_type: str):
        """Broadcast a message to all connected clients of a type"""
        if client_type not in self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections[client_type]:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to client: {str(e)}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, client_type)
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific client"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message to client: {str(e)}")


# Create connection manager
manager = ConnectionManager()


class WebSocketAPI:
    """WebSocket API for AetherCore"""
    
    def __init__(self):
        """Initialize WebSocket API"""
        self.manager = manager
        self.logger = logging.getLogger(__name__)
    
    async def hitl_endpoint(self, websocket: WebSocket, db: Session = Depends(get_db)):
        """WebSocket endpoint for HITL notifications"""
        await self.manager.connect(websocket, "hitl")
        
        try:
            # Send initial data
            hitl_requests = db.query(HITLRequest).order_by(HITLRequest.created_at.desc()).limit(10).all()
            
            initial_data = {
                "type": "initial_data",
                "requests": [
                    {
                        "request_id": str(req.id),
                        "task_id": str(req.task_id),
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
                    for req in hitl_requests
                ]
            }
            
            await self.manager.send_personal_message(initial_data, websocket)
            
            # Wait for messages
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle client messages
                if message.get("type") == "ping":
                    await self.manager.send_personal_message({"type": "pong"}, websocket)
                
        except WebSocketDisconnect:
            self.manager.disconnect(websocket, "hitl")
        except Exception as e:
            self.logger.error(f"Error in HITL WebSocket: {str(e)}")
            self.manager.disconnect(websocket, "hitl")
    
    async def notify_hitl_request_created(self, hitl_request: Dict[str, Any]):
        """Notify clients of a new HITL request"""
        message = {
            "type": "new_request",
            "request": hitl_request
        }
        
        await self.manager.broadcast(message, "hitl")
    
    async def notify_hitl_request_updated(self, hitl_request: Dict[str, Any]):
        """Notify clients of an updated HITL request"""
        message = {
            "type": "update_request",
            "request": hitl_request
        }
        
        await self.manager.broadcast(message, "hitl")


# Create WebSocket API
websocket_api = WebSocketAPI()