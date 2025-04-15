"""
Database Models for AetherCore

This module defines the SQLAlchemy database models for AetherCore,
including agents, tasks, and messages.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from ..config.database import Base
from .agent_hierarchy import AgentLevel, AgentDomain, AgentStatus
from ..core.agent_communication import MessageType, TaskStatus


class Agent(Base):
    """Database model for agents"""
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(Enum(AgentLevel), nullable=False)
    domain = Column(Enum(AgentDomain), nullable=False)
    status = Column(Enum(AgentStatus), nullable=False, default=AgentStatus.INITIALIZING)
    capabilities = Column(JSON, nullable=True)
    constraints = Column(JSON, nullable=True)
    model_config = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = relationship("Task", back_populates="agent")
    messages_sent = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    messages_received = relationship("Message", back_populates="recipient", foreign_keys="Message.recipient_id")
    
    # Type-specific fields
    system_role = Column(String(255), nullable=True)  # For Core Sentience
    oversight_domains = Column(JSON, nullable=True)  # For Core Sentience
    strategic_goals = Column(JSON, nullable=True)  # For Domain Regent
    performance_metrics = Column(JSON, nullable=True)  # For Domain Regent
    task_master_ids = Column(JSON, nullable=True)  # For Domain Regent
    specialty = Column(String(255), nullable=True)  # For Task Master
    domain_regent_id = Column(UUID(as_uuid=True), nullable=True)  # For Task Master
    minion_ids = Column(JSON, nullable=True)  # For Task Master
    expertise_areas = Column(JSON, nullable=True)  # For Task Master
    task_master_id = Column(UUID(as_uuid=True), nullable=True)  # For Minion
    function_type = Column(String(255), nullable=True)  # For Minion
    specific_function = Column(String(255), nullable=True)  # For Minion


class Task(Base):
    """Database model for tasks"""
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_type = Column(String(255), nullable=False)
    task_description = Column(Text, nullable=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    agent_level = Column(Enum(AgentLevel), nullable=True)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.RECEIVED)
    priority = Column(Integer, nullable=False, default=5)
    input_data = Column(JSON, nullable=True)
    result_data = Column(JSON, nullable=True)
    error_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)
    
    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    subtasks = relationship("Task", backref=ForeignKey("tasks.parent_task_id"))
    hitl_requests = relationship("HITLRequest", back_populates="task")


class HITLRequest(Base):
    """Database model for HITL requests"""
    __tablename__ = "hitl_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    request_type = Column(String(255), nullable=False)
    request_description = Column(Text, nullable=True)
    options = Column(JSON, nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    response = Column(Text, nullable=True)
    response_details = Column(JSON, nullable=True)
    human_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="hitl_requests")


class Message(Base):
    """Database model for messages"""
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_type = Column(Enum(MessageType), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    sender_level = Column(Enum(AgentLevel), nullable=True)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    recipient_level = Column(Enum(AgentLevel), nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    sender = relationship("Agent", back_populates="messages_sent", foreign_keys=[sender_id])
    recipient = relationship("Agent", back_populates="messages_received", foreign_keys=[recipient_id])