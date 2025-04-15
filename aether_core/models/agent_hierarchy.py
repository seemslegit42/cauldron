"""
Agent Hierarchy Models for AetherCore

This module defines the data models for the multi-level agent hierarchy in Cauldron™,
including Domain Regents, Task Masters, and Minions.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class AgentLevel(str, Enum):
    """Enumeration of agent hierarchy levels"""
    CORE_SENTIENCE = "core_sentience"  # Level 0
    DOMAIN_REGENT = "domain_regent"    # Level 1
    TASK_MASTER = "task_master"        # Level 2
    MINION = "minion"                  # Level 3


class AgentDomain(str, Enum):
    """Enumeration of agent domains"""
    OPERATIONS = "operations"
    INTELLIGENCE = "intelligence"
    SECURITY = "security"
    KNOWLEDGE = "knowledge"
    DEVELOPMENT = "development"
    SYSTEM = "system"  # For Core Sentience agents


class AgentStatus(str, Enum):
    """Enumeration of agent statuses"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    TERMINATED = "terminated"
    ERROR = "error"


class AgentCapability(BaseModel):
    """Model representing an agent capability"""
    name: str
    description: str
    tools: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AgentConstraint(BaseModel):
    """Model representing an ethical constraint or guardrail for an agent"""
    name: str
    description: str
    constraint_type: str  # e.g., "approval_required", "forbidden", "limited"
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AgentBase(BaseModel):
    """Base model for all agents in the hierarchy"""
    id: str
    name: str
    description: str
    level: AgentLevel
    domain: AgentDomain
    status: AgentStatus = AgentStatus.INITIALIZING
    capabilities: List[AgentCapability] = Field(default_factory=list)
    constraints: List[AgentConstraint] = Field(default_factory=list)
    model_config: Dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class CoreSentienceAgent(AgentBase):
    """Model for Level 0 Core Sentience agents"""
    level: AgentLevel = AgentLevel.CORE_SENTIENCE
    domain: AgentDomain = AgentDomain.SYSTEM
    system_role: str  # e.g., "coordinator", "resource_manager", "ethics_guardian"
    oversight_domains: List[AgentDomain] = Field(default_factory=list)


class DomainRegent(AgentBase):
    """Model for Level 1 Domain Regent agents"""
    level: AgentLevel = AgentLevel.DOMAIN_REGENT
    strategic_goals: List[str] = Field(default_factory=list)
    performance_metrics: List[str] = Field(default_factory=list)
    task_master_ids: List[str] = Field(default_factory=list)


class TaskMaster(AgentBase):
    """Model for Level 2 Task Master agents"""
    level: AgentLevel = AgentLevel.TASK_MASTER
    specialty: str
    domain_regent_id: str
    minion_ids: List[str] = Field(default_factory=list)
    expertise_areas: List[str] = Field(default_factory=list)


class Minion(AgentBase):
    """Model for Level 3 Minion agents"""
    level: AgentLevel = AgentLevel.MINION
    task_master_id: str
    function_type: str  # e.g., "data", "process", "interaction", "technical"
    specific_function: str  # e.g., "data_collector", "task_executor", "query_responder"


class AgentHierarchy(BaseModel):
    """Model representing the complete agent hierarchy"""
    core_sentience_agents: List[CoreSentienceAgent] = Field(default_factory=list)
    domain_regents: List[DomainRegent] = Field(default_factory=list)
    task_masters: List[TaskMaster] = Field(default_factory=list)
    minions: List[Minion] = Field(default_factory=list)

    def get_agent_by_id(self, agent_id: str) -> Optional[Union[CoreSentienceAgent, DomainRegent, TaskMaster, Minion]]:
        """Retrieve an agent by its ID"""
        for agent in self.core_sentience_agents:
            if agent.id == agent_id:
                return agent
                
        for agent in self.domain_regents:
            if agent.id == agent_id:
                return agent
                
        for agent in self.task_masters:
            if agent.id == agent_id:
                return agent
                
        for agent in self.minions:
            if agent.id == agent_id:
                return agent
                
        return None

    def get_agents_by_domain(self, domain: AgentDomain) -> List[Union[CoreSentienceAgent, DomainRegent, TaskMaster, Minion]]:
        """Retrieve all agents in a specific domain"""
        agents = []
        
        for agent in self.core_sentience_agents:
            if agent.domain == domain:
                agents.append(agent)
                
        for agent in self.domain_regents:
            if agent.domain == domain:
                agents.append(agent)
                
        for agent in self.task_masters:
            if agent.domain == domain:
                agents.append(agent)
                
        for agent in self.minions:
            if agent.domain == domain:
                agents.append(agent)
                
        return agents

    def get_regent_task_masters(self, regent_id: str) -> List[TaskMaster]:
        """Retrieve all Task Masters under a specific Domain Regent"""
        return [tm for tm in self.task_masters if tm.domain_regent_id == regent_id]
        
    def get_task_master_minions(self, task_master_id: str) -> List[Minion]:
        """Retrieve all Minions under a specific Task Master"""
        return [m for m in self.minions if m.task_master_id == task_master_id]