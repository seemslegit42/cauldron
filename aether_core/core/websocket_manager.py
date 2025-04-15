"""
WebSocket Manager for AetherCore

This module provides a WebSocket manager for handling real-time communication
between the server and clients.
"""

import json
import logging
from typing import Dict, List, Any, Set
from fastapi import WebSocket


class WebSocketManager:
    """WebSocket manager for handling real-time communication"""
    
    def __init__(self):
        """Initialize the WebSocket manager"""
        self.active_connections: Set[WebSocket] = set()
        self.logger = logging.getLogger(__name__)
    
    async def connect(self, websocket: WebSocket):
        """Connect a WebSocket client"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.logger.info(f"WebSocket client connected. Active connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client"""
        self.active_connections.remove(websocket)
        self.logger.info(f"WebSocket client disconnected. Active connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            self.logger.error(f"Error sending personal message: {str(e)}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        disconnected_clients = set()
        
        for websocket in self.active_connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                self.logger.error(f"Error broadcasting message: {str(e)}")
                disconnected_clients.add(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected_clients:
            self.disconnect(websocket)
    
    async def broadcast_to_group(self, message: Dict[str, Any], group: List[WebSocket]):
        """Broadcast a message to a group of clients"""
        disconnected_clients = set()
        
        for websocket in group:
            if websocket in self.active_connections:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    self.logger.error(f"Error broadcasting message to group: {str(e)}")
                    disconnected_clients.add(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected_clients:
            self.disconnect(websocket)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)