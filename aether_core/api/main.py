"""
Main API Application for AetherCore

This module provides the main FastAPI application for AetherCore,
integrating all API endpoints and services.
"""

import os
import logging
from fastapi import FastAPI, Depends, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Local imports
from ..config.database import get_db, engine, Base
from ..core.superagi_integration import SuperAGIAgentFactory, HierarchicalAgentManager
from ..core.agent_communication import MessageBroker
from ..core.websocket_manager import WebSocketManager
from ..services.agent_factory import AgentFactory
from ..services.agent_orchestration_db import AgentOrchestrationService
from ..services.hitl_service import HITLService
from .agent_hierarchy_api import AgentHierarchyAPI
from .task_api import TaskAPI
from .hitl_api import HITLAPI
from .websocket import websocket_api


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Create database tables
def setup_database():
    """Set up database tables"""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


# Create FastAPI application
app = FastAPI(
    title="AetherCore API",
    description="API for managing the agent hierarchy in Cauldron™",
    version="1.0.0"
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize services
def initialize_services():
    """Initialize AetherCore services"""
    try:
        # Initialize SuperAGI factory
        superagi_factory = SuperAGIAgentFactory(
            config_path=os.environ.get("SUPERAGI_CONFIG_PATH")
        )
        
        # Initialize agent manager
        agent_manager = HierarchicalAgentManager(superagi_factory)
        
        # Initialize message broker
        broker_type = os.environ.get("MESSAGE_BROKER_TYPE", "memory")
        broker_config = {}
        
        if broker_type == "kafka":
            broker_config = {
                "bootstrap_servers": os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
                "group_id": os.environ.get("KAFKA_GROUP_ID", "aether_core")
            }
        elif broker_type == "rabbitmq":
            broker_config = {
                "host": os.environ.get("RABBITMQ_HOST", "localhost"),
                "port": int(os.environ.get("RABBITMQ_PORT", "5672")),
                "virtual_host": os.environ.get("RABBITMQ_VHOST", "/"),
                "username": os.environ.get("RABBITMQ_USERNAME", "guest"),
                "password": os.environ.get("RABBITMQ_PASSWORD", "guest")
            }
            
        message_broker = MessageBroker(
            broker_type=broker_type,
            config=broker_config
        )
        
        # Initialize WebSocket manager
        websocket_manager = WebSocketManager()
        
        # Initialize agent factory
        agent_factory = AgentFactory()
        
        # Initialize agent orchestration service
        agent_orchestration_service = AgentOrchestrationService(
            agent_manager=agent_manager,
            message_broker=message_broker,
            db_session=next(get_db())
        )
        
        # Initialize HITL service
        hitl_service = HITLService(
            db_session=next(get_db())
        )
        
        # Initialize APIs
        agent_hierarchy_api = AgentHierarchyAPI(
            agent_factory=agent_factory,
            agent_manager=agent_manager
        )
        
        task_api = TaskAPI(
            agent_orchestration_service=agent_orchestration_service
        )
        
        hitl_api = HITLAPI(
            agent_orchestration_service=agent_orchestration_service,
            hitl_service=hitl_service,
            websocket_manager=websocket_manager
        )
        
        # Include routers
        app.include_router(agent_hierarchy_api.router)
        app.include_router(task_api.router)
        app.include_router(hitl_api.router)
        
        logger.info("AetherCore services initialized successfully")
        
        return {
            "superagi_factory": superagi_factory,
            "agent_manager": agent_manager,
            "message_broker": message_broker,
            "websocket_manager": websocket_manager,
            "agent_factory": agent_factory,
            "agent_orchestration_service": agent_orchestration_service,
            "hitl_service": hitl_service
        }
        
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        raise


# Setup on startup
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    try:
        # Set up database
        setup_database()
        
        # Initialize services
        app.state.services = initialize_services()
        
        logger.info("AetherCore API started successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise


# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    try:
        # Close message broker connections
        if hasattr(app.state, "services") and "message_broker" in app.state.services:
            app.state.services["message_broker"].close()
            
        logger.info("AetherCore API shut down successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint for AetherCore API"""
    return {
        "message": "Welcome to AetherCore API",
        "version": "1.0.0",
        "status": "operational"
    }


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for AetherCore API"""
    try:
        # Check database connection
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "operational"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "error"
    
    # Check message broker
    broker_status = "operational"
    if hasattr(app.state, "services") and "message_broker" in app.state.services:
        broker_type = app.state.services["message_broker"].broker_type
    else:
        broker_type = "unknown"
        broker_status = "not_initialized"
    
    # Check WebSocket manager
    websocket_status = "operational"
    if hasattr(app.state, "services") and "websocket_manager" in app.state.services:
        websocket_connections = app.state.services["websocket_manager"].get_connection_count()
    else:
        websocket_status = "not_initialized"
        websocket_connections = 0
    
    # Check HITL service
    hitl_status = "operational" if hasattr(app.state, "services") and "hitl_service" in app.state.services else "not_initialized"
    
    return {
        "status": "healthy" if db_status == "operational" and broker_status == "operational" else "unhealthy",
        "services": {
            "database": db_status,
            "message_broker": {
                "status": broker_status,
                "type": broker_type
            },
            "websocket": {
                "status": websocket_status,
                "connections": websocket_connections
            },
            "agent_manager": "operational" if hasattr(app.state, "services") and "agent_manager" in app.state.services else "not_initialized",
            "agent_factory": "operational" if hasattr(app.state, "services") and "agent_factory" in app.state.services else "not_initialized",
            "agent_orchestration": "operational" if hasattr(app.state, "services") and "agent_orchestration_service" in app.state.services else "not_initialized",
            "hitl_service": hitl_status
        }
    }


# WebSocket endpoints
@app.websocket("/ws/hitl")
async def hitl_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for HITL notifications"""
    if hasattr(app.state, "services") and "hitl_service" in app.state.services and "websocket_manager" in app.state.services:
        hitl_service = app.state.services["hitl_service"]
        websocket_manager = app.state.services["websocket_manager"]
        
        await websocket_manager.connect(websocket)
        
        try:
            # Send initial data
            hitl_requests = hitl_service.get_hitl_requests(limit=100, offset=0)
            responses = [
                {
                    "request_id": req.request_id,
                    "task_id": req.task_id,
                    "request_type": req.request_type,
                    "request_description": req.request_description,
                    "options": req.options,
                    "status": req.status,
                    "response": req.response,
                    "response_details": req.response_details,
                    "human_id": req.human_id,
                    "created_at": req.created_at,
                    "updated_at": req.updated_at,
                    "completed_at": req.completed_at,
                    "timeout_seconds": req.timeout_seconds,
                    "urgency": req.urgency
                }
                for req in hitl_requests
            ]
            
            await websocket.send_json(
                {
                    "type": "initial_data",
                    "requests": responses
                }
            )
            
            # Keep connection alive and handle messages
            while True:
                data = await websocket.receive_text()
                # Process any client messages if needed
                if data == "ping":
                    await websocket.send_text("pong")
                
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
            websocket_manager.disconnect(websocket)
    else:
        # Services not initialized
        await websocket.accept()
        await websocket.send_json({"error": "Services not initialized"})
        await websocket.close()


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "error": "Internal server error",
        "status_code": 500
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", 8000)),
        reload=os.environ.get("DEBUG", "False").lower() == "true"
    )