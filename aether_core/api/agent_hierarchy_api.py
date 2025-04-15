"""
Agent Hierarchy API for AetherCore

This module provides the API endpoints for managing the agent hierarchy,
including creating, retrieving, updating, and deleting agents at different levels.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from pydantic import BaseModel

# Local imports
from ..models.agent_hierarchy import (
    AgentLevel, AgentDomain, AgentStatus, AgentBase,
    CoreSentienceAgent, DomainRegent, TaskMaster, Minion,
    AgentCapability, AgentConstraint
)
from ..services.agent_factory import AgentFactory
from ..core.superagi_integration import (
    SuperAGIAgentFactory, HierarchicalAgentManager
)


# Pydantic models for API requests and responses
class AgentCapabilityCreate(BaseModel):
    """Model for creating an agent capability"""
    name: str
    description: str
    tools: List[str] = []
    parameters: Dict[str, Any] = {}


class AgentConstraintCreate(BaseModel):
    """Model for creating an agent constraint"""
    name: str
    description: str
    constraint_type: str
    parameters: Dict[str, Any] = {}


class CoreSentienceAgentCreate(BaseModel):
    """Model for creating a Core Sentience agent"""
    name: str
    description: str
    system_role: str
    oversight_domains: List[AgentDomain] = []
    capabilities: List[AgentCapabilityCreate] = []
    constraints: List[AgentConstraintCreate] = []
    model_config: Dict[str, Any] = {}


class DomainRegentCreate(BaseModel):
    """Model for creating a Domain Regent agent"""
    name: str
    description: str
    domain: AgentDomain
    strategic_goals: List[str] = []
    performance_metrics: List[str] = []
    capabilities: List[AgentCapabilityCreate] = []
    constraints: List[AgentConstraintCreate] = []
    model_config: Dict[str, Any] = {}


class TaskMasterCreate(BaseModel):
    """Model for creating a Task Master agent"""
    name: str
    description: str
    domain: AgentDomain
    specialty: str
    domain_regent_id: str
    expertise_areas: List[str] = []
    capabilities: List[AgentCapabilityCreate] = []
    constraints: List[AgentConstraintCreate] = []
    model_config: Dict[str, Any] = {}


class MinionCreate(BaseModel):
    """Model for creating a Minion agent"""
    name: str
    description: str
    domain: AgentDomain
    function_type: str
    specific_function: str
    task_master_id: str
    capabilities: List[AgentCapabilityCreate] = []
    constraints: List[AgentConstraintCreate] = []
    model_config: Dict[str, Any] = {}


class AgentResponse(BaseModel):
    """Model for agent response"""
    id: str
    name: str
    description: str
    level: str
    domain: str
    status: str
    created_at: str
    updated_at: str


class CoreSentienceAgentResponse(AgentResponse):
    """Model for Core Sentience agent response"""
    system_role: str
    oversight_domains: List[str]


class DomainRegentResponse(AgentResponse):
    """Model for Domain Regent agent response"""
    strategic_goals: List[str]
    performance_metrics: List[str]
    task_master_ids: List[str]


class TaskMasterResponse(AgentResponse):
    """Model for Task Master agent response"""
    specialty: str
    domain_regent_id: str
    minion_ids: List[str]
    expertise_areas: List[str]


class MinionResponse(AgentResponse):
    """Model for Minion agent response"""
    function_type: str
    specific_function: str
    task_master_id: str


class AgentHierarchyResponse(BaseModel):
    """Model for agent hierarchy response"""
    core_sentience_agents: List[CoreSentienceAgentResponse]
    domain_regents: List[DomainRegentResponse]
    task_masters: List[TaskMasterResponse]
    minions: List[MinionResponse]


class AgentHierarchyAPI:
    """API for managing the agent hierarchy"""
    
    def __init__(
        self,
        agent_factory: AgentFactory,
        agent_manager: HierarchicalAgentManager
    ):
        """Initialize the agent hierarchy API"""
        self.agent_factory = agent_factory
        self.agent_manager = agent_manager
        self.logger = logging.getLogger(__name__)
        
        # Create router
        self.router = APIRouter(prefix="/api/v1/agents", tags=["agents"])
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register API routes"""
        # Core Sentience agents
        self.router.post(
            "/core-sentience",
            response_model=CoreSentienceAgentResponse,
            summary="Create a Core Sentience agent",
            description="Create a new Core Sentience agent in the hierarchy"
        )(self.create_core_sentience_agent)
        
        self.router.get(
            "/core-sentience",
            response_model=List[CoreSentienceAgentResponse],
            summary="Get all Core Sentience agents",
            description="Retrieve all Core Sentience agents in the hierarchy"
        )(self.get_core_sentience_agents)
        
        self.router.get(
            "/core-sentience/{agent_id}",
            response_model=CoreSentienceAgentResponse,
            summary="Get a Core Sentience agent",
            description="Retrieve a specific Core Sentience agent by ID"
        )(self.get_core_sentience_agent)
        
        # Domain Regent agents
        self.router.post(
            "/domain-regents",
            response_model=DomainRegentResponse,
            summary="Create a Domain Regent agent",
            description="Create a new Domain Regent agent in the hierarchy"
        )(self.create_domain_regent)
        
        self.router.get(
            "/domain-regents",
            response_model=List[DomainRegentResponse],
            summary="Get all Domain Regent agents",
            description="Retrieve all Domain Regent agents in the hierarchy"
        )(self.get_domain_regents)
        
        self.router.get(
            "/domain-regents/{agent_id}",
            response_model=DomainRegentResponse,
            summary="Get a Domain Regent agent",
            description="Retrieve a specific Domain Regent agent by ID"
        )(self.get_domain_regent)
        
        # Task Master agents
        self.router.post(
            "/task-masters",
            response_model=TaskMasterResponse,
            summary="Create a Task Master agent",
            description="Create a new Task Master agent in the hierarchy"
        )(self.create_task_master)
        
        self.router.get(
            "/task-masters",
            response_model=List[TaskMasterResponse],
            summary="Get all Task Master agents",
            description="Retrieve all Task Master agents in the hierarchy"
        )(self.get_task_masters)
        
        self.router.get(
            "/task-masters/{agent_id}",
            response_model=TaskMasterResponse,
            summary="Get a Task Master agent",
            description="Retrieve a specific Task Master agent by ID"
        )(self.get_task_master)
        
        self.router.get(
            "/domain-regents/{regent_id}/task-masters",
            response_model=List[TaskMasterResponse],
            summary="Get Task Masters for a Domain Regent",
            description="Retrieve all Task Master agents under a specific Domain Regent"
        )(self.get_regent_task_masters)
        
        # Minion agents
        self.router.post(
            "/minions",
            response_model=MinionResponse,
            summary="Create a Minion agent",
            description="Create a new Minion agent in the hierarchy"
        )(self.create_minion)
        
        self.router.get(
            "/minions",
            response_model=List[MinionResponse],
            summary="Get all Minion agents",
            description="Retrieve all Minion agents in the hierarchy"
        )(self.get_minions)
        
        self.router.get(
            "/minions/{agent_id}",
            response_model=MinionResponse,
            summary="Get a Minion agent",
            description="Retrieve a specific Minion agent by ID"
        )(self.get_minion)
        
        self.router.get(
            "/task-masters/{task_master_id}/minions",
            response_model=List[MinionResponse],
            summary="Get Minions for a Task Master",
            description="Retrieve all Minion agents under a specific Task Master"
        )(self.get_task_master_minions)
        
        # Hierarchy operations
        self.router.get(
            "/hierarchy",
            response_model=AgentHierarchyResponse,
            summary="Get the complete agent hierarchy",
            description="Retrieve the complete agent hierarchy"
        )(self.get_hierarchy)
        
        self.router.post(
            "/hierarchy/initialize",
            response_model=AgentHierarchyResponse,
            summary="Initialize the agent hierarchy",
            description="Initialize the agent hierarchy with default agents"
        )(self.initialize_hierarchy)
        
        self.router.get(
            "/domains/{domain}",
            response_model=AgentHierarchyResponse,
            summary="Get agents by domain",
            description="Retrieve all agents in a specific domain"
        )(self.get_agents_by_domain)
    
    async def create_core_sentience_agent(self, agent_data: CoreSentienceAgentCreate):
        """Create a Core Sentience agent"""
        try:
            # Convert capabilities and constraints
            capabilities = [
                AgentCapability(
                    name=cap.name,
                    description=cap.description,
                    tools=cap.tools,
                    parameters=cap.parameters
                )
                for cap in agent_data.capabilities
            ]
            
            constraints = [
                AgentConstraint(
                    name=con.name,
                    description=con.description,
                    constraint_type=con.constraint_type,
                    parameters=con.parameters
                )
                for con in agent_data.constraints
            ]
            
            # Create agent
            agent = self.agent_factory.create_core_sentience_agent(
                name=agent_data.name,
                description=agent_data.description,
                system_role=agent_data.system_role,
                oversight_domains=agent_data.oversight_domains,
                capabilities=capabilities,
                constraints=constraints,
                model_config=agent_data.model_config
            )
            
            # Register agent with manager
            self.agent_manager.create_agent(agent)
            
            # Convert to response model
            response = CoreSentienceAgentResponse(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                level=agent.level.value,
                domain=agent.domain.value,
                status=agent.status.value,
                created_at=agent.created_at,
                updated_at=agent.updated_at,
                system_role=agent.system_role,
                oversight_domains=[domain.value for domain in agent.oversight_domains]
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error creating Core Sentience agent: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_core_sentience_agents(self):
        """Get all Core Sentience agents"""
        try:
            # Get agents from manager
            agents = self.agent_manager.get_all_agents().get("core_sentience", [])
            
            # Convert to response models
            responses = []
            for agent in agents:
                responses.append(
                    CoreSentienceAgentResponse(
                        id=agent.id,
                        name=agent.name,
                        description=agent.description,
                        level=agent.level.value,
                        domain=agent.domain.value,
                        status=agent.status.value,
                        created_at=agent.created_at,
                        updated_at=agent.updated_at,
                        system_role=agent.system_role,
                        oversight_domains=[domain.value for domain in agent.oversight_domains]
                    )
                )
            
            return responses
            
        except Exception as e:
            self.logger.error(f"Error getting Core Sentience agents: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_core_sentience_agent(self, agent_id: str):
        """Get a Core Sentience agent by ID"""
        try:
            # Get agent from manager
            agent = self.agent_manager.get_agent(agent_id, AgentLevel.CORE_SENTIENCE)
            
            if not agent:
                raise HTTPException(status_code=404, detail=f"Core Sentience agent {agent_id} not found")
            
            # Convert to response model
            response = CoreSentienceAgentResponse(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                level=agent.level.value,
                domain=agent.domain.value,
                status=agent.status.value,
                created_at=agent.created_at,
                updated_at=agent.updated_at,
                system_role=agent.system_role,
                oversight_domains=[domain.value for domain in agent.oversight_domains]
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error getting Core Sentience agent: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def create_domain_regent(self, agent_data: DomainRegentCreate):
        """Create a Domain Regent agent"""
        try:
            # Convert capabilities and constraints
            capabilities = [
                AgentCapability(
                    name=cap.name,
                    description=cap.description,
                    tools=cap.tools,
                    parameters=cap.parameters
                )
                for cap in agent_data.capabilities
            ]
            
            constraints = [
                AgentConstraint(
                    name=con.name,
                    description=con.description,
                    constraint_type=con.constraint_type,
                    parameters=con.parameters
                )
                for con in agent_data.constraints
            ]
            
            # Create agent
            agent = self.agent_factory.create_domain_regent(
                name=agent_data.name,
                description=agent_data.description,
                domain=agent_data.domain,
                strategic_goals=agent_data.strategic_goals,
                performance_metrics=agent_data.performance_metrics,
                capabilities=capabilities,
                constraints=constraints,
                model_config=agent_data.model_config
            )
            
            # Register agent with manager
            self.agent_manager.create_agent(agent)
            
            # Convert to response model
            response = DomainRegentResponse(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                level=agent.level.value,
                domain=agent.domain.value,
                status=agent.status.value,
                created_at=agent.created_at,
                updated_at=agent.updated_at,
                strategic_goals=agent.strategic_goals,
                performance_metrics=agent.performance_metrics,
                task_master_ids=agent.task_master_ids
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error creating Domain Regent agent: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_domain_regents(self):
        """Get all Domain Regent agents"""
        try:
            # Get agents from manager
            agents = self.agent_manager.get_all_agents().get("domain_regents", [])
            
            # Convert to response models
            responses = []
            for agent in agents:
                responses.append(
                    DomainRegentResponse(
                        id=agent.id,
                        name=agent.name,
                        description=agent.description,
                        level=agent.level.value,
                        domain=agent.domain.value,
                        status=agent.status.value,
                        created_at=agent.created_at,
                        updated_at=agent.updated_at,
                        strategic_goals=agent.strategic_goals,
                        performance_metrics=agent.performance_metrics,
                        task_master_ids=agent.task_master_ids
                    )
                )
            
            return responses
            
        except Exception as e:
            self.logger.error(f"Error getting Domain Regent agents: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_domain_regent(self, agent_id: str):
        """Get a Domain Regent agent by ID"""
        try:
            # Get agent from manager
            agent = self.agent_manager.get_agent(agent_id, AgentLevel.DOMAIN_REGENT)
            
            if not agent:
                raise HTTPException(status_code=404, detail=f"Domain Regent agent {agent_id} not found")
            
            # Convert to response model
            response = DomainRegentResponse(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                level=agent.level.value,
                domain=agent.domain.value,
                status=agent.status.value,
                created_at=agent.created_at,
                updated_at=agent.updated_at,
                strategic_goals=agent.strategic_goals,
                performance_metrics=agent.performance_metrics,
                task_master_ids=agent.task_master_ids
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error getting Domain Regent agent: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def create_task_master(self, agent_data: TaskMasterCreate):
        """Create a Task Master agent"""
        try:
            # Convert capabilities and constraints
            capabilities = [
                AgentCapability(
                    name=cap.name,
                    description=cap.description,
                    tools=cap.tools,
                    parameters=cap.parameters
                )
                for cap in agent_data.capabilities
            ]
            
            constraints = [
                AgentConstraint(
                    name=con.name,
                    description=con.description,
                    constraint_type=con.constraint_type,
                    parameters=con.parameters
                )
                for con in agent_data.constraints
            ]
            
            # Create agent
            agent = self.agent_factory.create_task_master(
                name=agent_data.name,
                description=agent_data.description,
                domain=agent_data.domain,
                specialty=agent_data.specialty,
                domain_regent_id=agent_data.domain_regent_id,
                expertise_areas=agent_data.expertise_areas,
                capabilities=capabilities,
                constraints=constraints,
                model_config=agent_data.model_config
            )
            
            # Register agent with manager
            self.agent_manager.create_agent(agent)
            
            # Update Domain Regent
            regent = self.agent_manager.get_agent(agent_data.domain_regent_id, AgentLevel.DOMAIN_REGENT)
            if regent:
                regent.task_master_ids.append(agent.id)
                self.agent_manager.update_agent(regent)
            
            # Convert to response model
            response = TaskMasterResponse(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                level=agent.level.value,
                domain=agent.domain.value,
                status=agent.status.value,
                created_at=agent.created_at,
                updated_at=agent.updated_at,
                specialty=agent.specialty,
                domain_regent_id=agent.domain_regent_id,
                minion_ids=agent.minion_ids,
                expertise_areas=agent.expertise_areas
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error creating Task Master agent: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_task_masters(self):
        """Get all Task Master agents"""
        try:
            # Get agents from manager
            agents = self.agent_manager.get_all_agents().get("task_masters", [])
            
            # Convert to response models
            responses = []
            for agent in agents:
                responses.append(
                    TaskMasterResponse(
                        id=agent.id,
                        name=agent.name,
                        description=agent.description,
                        level=agent.level.value,
                        domain=agent.domain.value,
                        status=agent.status.value,
                        created_at=agent.created_at,
                        updated_at=agent.updated_at,
                        specialty=agent.specialty,
                        domain_regent_id=agent.domain_regent_id,
                        minion_ids=agent.minion_ids,
                        expertise_areas=agent.expertise_areas
                    )
                )
            
            return responses
            
        except Exception as e:
            self.logger.error(f"Error getting Task Master agents: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_task_master(self, agent_id: str):
        """Get a Task Master agent by ID"""
        try:
            # Get agent from manager
            agent = self.agent_manager.get_agent(agent_id, AgentLevel.TASK_MASTER)
            
            if not agent:
                raise HTTPException(status_code=404, detail=f"Task Master agent {agent_id} not found")
            
            # Convert to response model
            response = TaskMasterResponse(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                level=agent.level.value,
                domain=agent.domain.value,
                status=agent.status.value,
                created_at=agent.created_at,
                updated_at=agent.updated_at,
                specialty=agent.specialty,
                domain_regent_id=agent.domain_regent_id,
                minion_ids=agent.minion_ids,
                expertise_areas=agent.expertise_areas
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error getting Task Master agent: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_regent_task_masters(self, regent_id: str):
        """Get all Task Master agents under a Domain Regent"""
        try:
            # Get all Task Masters
            all_task_masters = self.agent_manager.get_all_agents().get("task_masters", [])
            
            # Filter by Domain Regent ID
            regent_task_masters = [tm for tm in all_task_masters if tm.domain_regent_id == regent_id]
            
            # Convert to response models
            responses = []
            for agent in regent_task_masters:
                responses.append(
                    TaskMasterResponse(
                        id=agent.id,
                        name=agent.name,
                        description=agent.description,
                        level=agent.level.value,
                        domain=agent.domain.value,
                        status=agent.status.value,
                        created_at=agent.created_at,
                        updated_at=agent.updated_at,
                        specialty=agent.specialty,
                        domain_regent_id=agent.domain_regent_id,
                        minion_ids=agent.minion_ids,
                        expertise_areas=agent.expertise_areas
                    )
                )
            
            return responses
            
        except Exception as e:
            self.logger.error(f"Error getting Task Masters for Domain Regent: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def create_minion(self, agent_data: MinionCreate):
        """Create a Minion agent"""
        try:
            # Convert capabilities and constraints
            capabilities = [
                AgentCapability(
                    name=cap.name,
                    description=cap.description,
                    tools=cap.tools,
                    parameters=cap.parameters
                )
                for cap in agent_data.capabilities
            ]
            
            constraints = [
                AgentConstraint(
                    name=con.name,
                    description=con.description,
                    constraint_type=con.constraint_type,
                    parameters=con.parameters
                )
                for con in agent_data.constraints
            ]
            
            # Create agent
            agent = self.agent_factory.create_minion(
                name=agent_data.name,
                description=agent_data.description,
                domain=agent_data.domain,
                function_type=agent_data.function_type,
                specific_function=agent_data.specific_function,
                task_master_id=agent_data.task_master_id,
                capabilities=capabilities,
                constraints=constraints,
                model_config=agent_data.model_config
            )
            
            # Register agent with manager
            self.agent_manager.create_agent(agent)
            
            # Update Task Master
            task_master = self.agent_manager.get_agent(agent_data.task_master_id, AgentLevel.TASK_MASTER)
            if task_master:
                task_master.minion_ids.append(agent.id)
                self.agent_manager.update_agent(task_master)
            
            # Convert to response model
            response = MinionResponse(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                level=agent.level.value,
                domain=agent.domain.value,
                status=agent.status.value,
                created_at=agent.created_at,
                updated_at=agent.updated_at,
                function_type=agent.function_type,
                specific_function=agent.specific_function,
                task_master_id=agent.task_master_id
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error creating Minion agent: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_minions(self):
        """Get all Minion agents"""
        try:
            # Get agents from manager
            agents = self.agent_manager.get_all_agents().get("minions", [])
            
            # Convert to response models
            responses = []
            for agent in agents:
                responses.append(
                    MinionResponse(
                        id=agent.id,
                        name=agent.name,
                        description=agent.description,
                        level=agent.level.value,
                        domain=agent.domain.value,
                        status=agent.status.value,
                        created_at=agent.created_at,
                        updated_at=agent.updated_at,
                        function_type=agent.function_type,
                        specific_function=agent.specific_function,
                        task_master_id=agent.task_master_id
                    )
                )
            
            return responses
            
        except Exception as e:
            self.logger.error(f"Error getting Minion agents: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_minion(self, agent_id: str):
        """Get a Minion agent by ID"""
        try:
            # Get agent from manager
            agent = self.agent_manager.get_agent(agent_id, AgentLevel.MINION)
            
            if not agent:
                raise HTTPException(status_code=404, detail=f"Minion agent {agent_id} not found")
            
            # Convert to response model
            response = MinionResponse(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                level=agent.level.value,
                domain=agent.domain.value,
                status=agent.status.value,
                created_at=agent.created_at,
                updated_at=agent.updated_at,
                function_type=agent.function_type,
                specific_function=agent.specific_function,
                task_master_id=agent.task_master_id
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error getting Minion agent: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_task_master_minions(self, task_master_id: str):
        """Get all Minion agents under a Task Master"""
        try:
            # Get all Minions
            all_minions = self.agent_manager.get_all_agents().get("minions", [])
            
            # Filter by Task Master ID
            task_master_minions = [m for m in all_minions if m.task_master_id == task_master_id]
            
            # Convert to response models
            responses = []
            for agent in task_master_minions:
                responses.append(
                    MinionResponse(
                        id=agent.id,
                        name=agent.name,
                        description=agent.description,
                        level=agent.level.value,
                        domain=agent.domain.value,
                        status=agent.status.value,
                        created_at=agent.created_at,
                        updated_at=agent.updated_at,
                        function_type=agent.function_type,
                        specific_function=agent.specific_function,
                        task_master_id=agent.task_master_id
                    )
                )
            
            return responses
            
        except Exception as e:
            self.logger.error(f"Error getting Minions for Task Master: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_hierarchy(self):
        """Get the complete agent hierarchy"""
        try:
            # Get all agents
            all_agents = self.agent_manager.get_all_agents()
            
            # Convert to response models
            core_sentience_responses = []
            for agent in all_agents.get("core_sentience", []):
                core_sentience_responses.append(
                    CoreSentienceAgentResponse(
                        id=agent.id,
                        name=agent.name,
                        description=agent.description,
                        level=agent.level.value,
                        domain=agent.domain.value,
                        status=agent.status.value,
                        created_at=agent.created_at,
                        updated_at=agent.updated_at,
                        system_role=agent.system_role,
                        oversight_domains=[domain.value for domain in agent.oversight_domains]
                    )
                )
            
            domain_regent_responses = []
            for agent in all_agents.get("domain_regents", []):
                domain_regent_responses.append(
                    DomainRegentResponse(
                        id=agent.id,
                        name=agent.name,
                        description=agent.description,
                        level=agent.level.value,
                        domain=agent.domain.value,
                        status=agent.status.value,
                        created_at=agent.created_at,
                        updated_at=agent.updated_at,
                        strategic_goals=agent.strategic_goals,
                        performance_metrics=agent.performance_metrics,
                        task_master_ids=agent.task_master_ids
                    )
                )
            
            task_master_responses = []
            for agent in all_agents.get("task_masters", []):
                task_master_responses.append(
                    TaskMasterResponse(
                        id=agent.id,
                        name=agent.name,
                        description=agent.description,
                        level=agent.level.value,
                        domain=agent.domain.value,
                        status=agent.status.value,
                        created_at=agent.created_at,
                        updated_at=agent.updated_at,
                        specialty=agent.specialty,
                        domain_regent_id=agent.domain_regent_id,
                        minion_ids=agent.minion_ids,
                        expertise_areas=agent.expertise_areas
                    )
                )
            
            minion_responses = []
            for agent in all_agents.get("minions", []):
                minion_responses.append(
                    MinionResponse(
                        id=agent.id,
                        name=agent.name,
                        description=agent.description,
                        level=agent.level.value,
                        domain=agent.domain.value,
                        status=agent.status.value,
                        created_at=agent.created_at,
                        updated_at=agent.updated_at,
                        function_type=agent.function_type,
                        specific_function=agent.specific_function,
                        task_master_id=agent.task_master_id
                    )
                )
            
            # Create hierarchy response
            hierarchy_response = AgentHierarchyResponse(
                core_sentience_agents=core_sentience_responses,
                domain_regents=domain_regent_responses,
                task_masters=task_master_responses,
                minions=minion_responses
            )
            
            return hierarchy_response
            
        except Exception as e:
            self.logger.error(f"Error getting agent hierarchy: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def initialize_hierarchy(self):
        """Initialize the agent hierarchy with default agents"""
        try:
            # Create Core Sentience agents
            core_sentience_agents = self.agent_factory.create_default_core_sentience_agents()
            for agent in core_sentience_agents:
                self.agent_manager.create_agent(agent)
            
            # Create Domain Regent agents
            domain_regents = self.agent_factory.create_default_domain_regents()
            domain_regent_ids = {}
            for agent in domain_regents:
                self.agent_manager.create_agent(agent)
                domain_regent_ids[agent.domain] = agent.id
            
            # Create Task Master agents
            task_masters = self.agent_factory.create_default_task_masters(domain_regent_ids)
            task_master_ids = {}
            for agent in task_masters:
                self.agent_manager.create_agent(agent)
                task_master_ids[agent.name] = agent.id
                
                # Update Domain Regent
                regent = self.agent_manager.get_agent(agent.domain_regent_id, AgentLevel.DOMAIN_REGENT)
                if regent:
                    regent.task_master_ids.append(agent.id)
                    self.agent_manager.update_agent(regent)
            
            # Create Minion agents
            minions = self.agent_factory.create_default_minions(task_master_ids)
            for agent in minions:
                self.agent_manager.create_agent(agent)
                
                # Update Task Master
                task_master = self.agent_manager.get_agent(agent.task_master_id, AgentLevel.TASK_MASTER)
                if task_master:
                    task_master.minion_ids.append(agent.id)
                    self.agent_manager.update_agent(task_master)
            
            # Return the complete hierarchy
            return await self.get_hierarchy()
            
        except Exception as e:
            self.logger.error(f"Error initializing agent hierarchy: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_agents_by_domain(self, domain: str):
        """Get all agents in a specific domain"""
        try:
            # Convert domain string to enum
            try:
                domain_enum = AgentDomain(domain)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid domain: {domain}")
            
            # Get all agents
            all_agents = self.agent_manager.get_all_agents()
            
            # Filter by domain
            core_sentience_agents = [a for a in all_agents.get("core_sentience", []) if a.domain == domain_enum]
            domain_regents = [a for a in all_agents.get("domain_regents", []) if a.domain == domain_enum]
            task_masters = [a for a in all_agents.get("task_masters", []) if a.domain == domain_enum]
            minions = [a for a in all_agents.get("minions", []) if a.domain == domain_enum]
            
            # Convert to response models
            core_sentience_responses = []
            for agent in core_sentience_agents:
                core_sentience_responses.append(
                    CoreSentienceAgentResponse(
                        id=agent.id,
                        name=agent.name,
                        description=agent.description,
                        level=agent.level.value,
                        domain=agent.domain.value,
                        status=agent.status.value,
                        created_at=agent.created_at,
                        updated_at=agent.updated_at,
                        system_role=agent.system_role,
                        oversight_domains=[domain.value for domain in agent.oversight_domains]
                    )
                )
            
            domain_regent_responses = []
            for agent in domain_regents:
                domain_regent_responses.append(
                    DomainRegentResponse(
                        id=agent.id,
                        name=agent.name,
                        description=agent.description,
                        level=agent.level.value,
                        domain=agent.domain.value,
                        status=agent.status.value,
                        created_at=agent.created_at,
                        updated_at=agent.updated_at,
                        strategic_goals=agent.strategic_goals,
                        performance_metrics=agent.performance_metrics,
                        task_master_ids=agent.task_master_ids
                    )
                )
            
            task_master_responses = []
            for agent in task_masters:
                task_master_responses.append(
                    TaskMasterResponse(
                        id=agent.id,
                        name=agent.name,
                        description=agent.description,
                        level=agent.level.value,
                        domain=agent.domain.value,
                        status=agent.status.value,
                        created_at=agent.created_at,
                        updated_at=agent.updated_at,
                        specialty=agent.specialty,
                        domain_regent_id=agent.domain_regent_id,
                        minion_ids=agent.minion_ids,
                        expertise_areas=agent.expertise_areas
                    )
                )
            
            minion_responses = []
            for agent in minions:
                minion_responses.append(
                    MinionResponse(
                        id=agent.id,
                        name=agent.name,
                        description=agent.description,
                        level=agent.level.value,
                        domain=agent.domain.value,
                        status=agent.status.value,
                        created_at=agent.created_at,
                        updated_at=agent.updated_at,
                        function_type=agent.function_type,
                        specific_function=agent.specific_function,
                        task_master_id=agent.task_master_id
                    )
                )
            
            # Create hierarchy response
            hierarchy_response = AgentHierarchyResponse(
                core_sentience_agents=core_sentience_responses,
                domain_regents=domain_regent_responses,
                task_masters=task_master_responses,
                minions=minion_responses
            )
            
            return hierarchy_response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error getting agents by domain: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))