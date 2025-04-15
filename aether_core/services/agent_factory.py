"""
Agent Factory Service for AetherCore

This service provides factory methods for creating different types of agents
in the hierarchy, including Core Sentience, Domain Regents, Task Masters, and Minions.
"""

import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Local imports
from ..models.agent_hierarchy import (
    AgentLevel, AgentDomain, AgentStatus, AgentBase,
    CoreSentienceAgent, DomainRegent, TaskMaster, Minion,
    AgentCapability, AgentConstraint
)


class AgentFactory:
    """Factory class for creating agents in the hierarchy"""
    
    def __init__(self):
        """Initialize the agent factory"""
        self.logger = logging.getLogger(__name__)
    
    def create_core_sentience_agent(
        self,
        name: str,
        description: str,
        system_role: str,
        oversight_domains: List[AgentDomain] = None,
        capabilities: List[AgentCapability] = None,
        constraints: List[AgentConstraint] = None,
        model_config: Dict[str, Any] = None
    ) -> CoreSentienceAgent:
        """Create a Core Sentience agent"""
        try:
            agent = CoreSentienceAgent(
                id=str(uuid.uuid4()),
                name=name,
                description=description,
                level=AgentLevel.CORE_SENTIENCE,
                domain=AgentDomain.SYSTEM,
                status=AgentStatus.INITIALIZING,
                system_role=system_role,
                oversight_domains=oversight_domains or [],
                capabilities=capabilities or [],
                constraints=constraints or [],
                model_config=model_config or {},
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.logger.info(f"Created Core Sentience agent: {name} ({agent.id})")
            
            return agent
            
        except Exception as e:
            self.logger.error(f"Error creating Core Sentience agent: {str(e)}")
            raise
    
    def create_domain_regent(
        self,
        name: str,
        description: str,
        domain: AgentDomain,
        strategic_goals: List[str] = None,
        performance_metrics: List[str] = None,
        capabilities: List[AgentCapability] = None,
        constraints: List[AgentConstraint] = None,
        model_config: Dict[str, Any] = None
    ) -> DomainRegent:
        """Create a Domain Regent agent"""
        try:
            agent = DomainRegent(
                id=str(uuid.uuid4()),
                name=name,
                description=description,
                level=AgentLevel.DOMAIN_REGENT,
                domain=domain,
                status=AgentStatus.INITIALIZING,
                strategic_goals=strategic_goals or [],
                performance_metrics=performance_metrics or [],
                task_master_ids=[],
                capabilities=capabilities or [],
                constraints=constraints or [],
                model_config=model_config or {},
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.logger.info(f"Created Domain Regent agent: {name} ({agent.id})")
            
            return agent
            
        except Exception as e:
            self.logger.error(f"Error creating Domain Regent agent: {str(e)}")
            raise
    
    def create_task_master(
        self,
        name: str,
        description: str,
        domain: AgentDomain,
        specialty: str,
        domain_regent_id: str,
        expertise_areas: List[str] = None,
        capabilities: List[AgentCapability] = None,
        constraints: List[AgentConstraint] = None,
        model_config: Dict[str, Any] = None
    ) -> TaskMaster:
        """Create a Task Master agent"""
        try:
            agent = TaskMaster(
                id=str(uuid.uuid4()),
                name=name,
                description=description,
                level=AgentLevel.TASK_MASTER,
                domain=domain,
                status=AgentStatus.INITIALIZING,
                specialty=specialty,
                domain_regent_id=domain_regent_id,
                minion_ids=[],
                expertise_areas=expertise_areas or [],
                capabilities=capabilities or [],
                constraints=constraints or [],
                model_config=model_config or {},
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.logger.info(f"Created Task Master agent: {name} ({agent.id})")
            
            return agent
            
        except Exception as e:
            self.logger.error(f"Error creating Task Master agent: {str(e)}")
            raise
    
    def create_minion(
        self,
        name: str,
        description: str,
        domain: AgentDomain,
        function_type: str,
        specific_function: str,
        task_master_id: str,
        capabilities: List[AgentCapability] = None,
        constraints: List[AgentConstraint] = None,
        model_config: Dict[str, Any] = None
    ) -> Minion:
        """Create a Minion agent"""
        try:
            agent = Minion(
                id=str(uuid.uuid4()),
                name=name,
                description=description,
                level=AgentLevel.MINION,
                domain=domain,
                status=AgentStatus.INITIALIZING,
                function_type=function_type,
                specific_function=specific_function,
                task_master_id=task_master_id,
                capabilities=capabilities or [],
                constraints=constraints or [],
                model_config=model_config or {},
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.logger.info(f"Created Minion agent: {name} ({agent.id})")
            
            return agent
            
        except Exception as e:
            self.logger.error(f"Error creating Minion agent: {str(e)}")
            raise
    
    def create_default_capability(
        self,
        name: str,
        description: str,
        tools: List[str] = None,
        parameters: Dict[str, Any] = None
    ) -> AgentCapability:
        """Create a default agent capability"""
        return AgentCapability(
            name=name,
            description=description,
            tools=tools or [],
            parameters=parameters or {}
        )
    
    def create_default_constraint(
        self,
        name: str,
        description: str,
        constraint_type: str,
        parameters: Dict[str, Any] = None
    ) -> AgentConstraint:
        """Create a default agent constraint"""
        return AgentConstraint(
            name=name,
            description=description,
            constraint_type=constraint_type,
            parameters=parameters or {}
        )
    
    def create_default_core_sentience_agents(self) -> List[CoreSentienceAgent]:
        """Create default Core Sentience agents"""
        agents = []
        
        # System Coordinator
        system_coordinator = self.create_core_sentience_agent(
            name="System Coordinator",
            description="Overall orchestration and emergent intelligence for the Cauldron™ system",
            system_role="coordinator",
            oversight_domains=[
                AgentDomain.OPERATIONS,
                AgentDomain.INTELLIGENCE,
                AgentDomain.SECURITY,
                AgentDomain.KNOWLEDGE,
                AgentDomain.DEVELOPMENT
            ],
            capabilities=[
                self.create_default_capability(
                    name="System Monitoring",
                    description="Monitor overall system health and performance",
                    tools=["system_monitor", "performance_analyzer"]
                ),
                self.create_default_capability(
                    name="Cross-Domain Coordination",
                    description="Coordinate activities across different domains",
                    tools=["coordination_planner", "resource_allocator"]
                )
            ],
            constraints=[
                self.create_default_constraint(
                    name="Strategic Alignment",
                    description="All actions must align with organizational strategic goals",
                    constraint_type="alignment_check"
                ),
                self.create_default_constraint(
                    name="Critical Decision Approval",
                    description="Critical system-wide decisions require human approval",
                    constraint_type="approval_required"
                )
            ]
        )
        agents.append(system_coordinator)
        
        # Resource Manager
        resource_manager = self.create_core_sentience_agent(
            name="Resource Manager",
            description="Optimizing agent resource allocation across the Cauldron™ system",
            system_role="resource_manager",
            oversight_domains=[
                AgentDomain.OPERATIONS,
                AgentDomain.INTELLIGENCE,
                AgentDomain.SECURITY,
                AgentDomain.KNOWLEDGE,
                AgentDomain.DEVELOPMENT
            ],
            capabilities=[
                self.create_default_capability(
                    name="Resource Monitoring",
                    description="Monitor resource utilization across the system",
                    tools=["resource_monitor", "utilization_analyzer"]
                ),
                self.create_default_capability(
                    name="Resource Allocation",
                    description="Allocate computational resources based on priority",
                    tools=["resource_allocator", "priority_scheduler"]
                )
            ],
            constraints=[
                self.create_default_constraint(
                    name="Fair Allocation",
                    description="Resources must be allocated fairly based on priority and need",
                    constraint_type="fairness_check"
                ),
                self.create_default_constraint(
                    name="Resource Limits",
                    description="Cannot exceed defined resource limits for any component",
                    constraint_type="limit_enforcement"
                )
            ]
        )
        agents.append(resource_manager)
        
        # Learning Coordinator
        learning_coordinator = self.create_core_sentience_agent(
            name="Learning Coordinator",
            description="Managing cross-agent learning and knowledge distribution",
            system_role="learning_coordinator",
            oversight_domains=[
                AgentDomain.OPERATIONS,
                AgentDomain.INTELLIGENCE,
                AgentDomain.SECURITY,
                AgentDomain.KNOWLEDGE,
                AgentDomain.DEVELOPMENT
            ],
            capabilities=[
                self.create_default_capability(
                    name="Learning Aggregation",
                    description="Aggregate learning across agents",
                    tools=["learning_aggregator", "pattern_recognizer"]
                ),
                self.create_default_capability(
                    name="Knowledge Distribution",
                    description="Distribute learned knowledge to relevant agents",
                    tools=["knowledge_distributor", "relevance_analyzer"]
                )
            ],
            constraints=[
                self.create_default_constraint(
                    name="Knowledge Validation",
                    description="New knowledge must be validated before distribution",
                    constraint_type="validation_required"
                ),
                self.create_default_constraint(
                    name="Privacy Protection",
                    description="Must protect sensitive information during knowledge sharing",
                    constraint_type="privacy_enforcement"
                )
            ]
        )
        agents.append(learning_coordinator)
        
        # Ethics Guardian
        ethics_guardian = self.create_core_sentience_agent(
            name="Ethics Guardian",
            description="Ensuring adherence to ethical guidelines across the Cauldron™ system",
            system_role="ethics_guardian",
            oversight_domains=[
                AgentDomain.OPERATIONS,
                AgentDomain.INTELLIGENCE,
                AgentDomain.SECURITY,
                AgentDomain.KNOWLEDGE,
                AgentDomain.DEVELOPMENT
            ],
            capabilities=[
                self.create_default_capability(
                    name="Ethical Monitoring",
                    description="Monitor agent actions for ethical compliance",
                    tools=["ethics_monitor", "action_analyzer"]
                ),
                self.create_default_capability(
                    name="Ethical Review",
                    description="Review potential ethical issues",
                    tools=["ethics_reviewer", "impact_analyzer"]
                )
            ],
            constraints=[
                self.create_default_constraint(
                    name="Ethical Principles",
                    description="All actions must adhere to defined ethical principles",
                    constraint_type="principle_enforcement"
                ),
                self.create_default_constraint(
                    name="Ethical Escalation",
                    description="Significant ethical concerns must be escalated to humans",
                    constraint_type="escalation_required"
                )
            ]
        )
        agents.append(ethics_guardian)
        
        # Human Interface
        human_interface = self.create_core_sentience_agent(
            name="Human Interface",
            description="Coordinating human-AI interaction across the Cauldron™ system",
            system_role="human_interface",
            oversight_domains=[
                AgentDomain.OPERATIONS,
                AgentDomain.INTELLIGENCE,
                AgentDomain.SECURITY,
                AgentDomain.KNOWLEDGE,
                AgentDomain.DEVELOPMENT
            ],
            capabilities=[
                self.create_default_capability(
                    name="Approval Management",
                    description="Manage approval workflows for human authorization",
                    tools=["approval_manager", "notification_system"]
                ),
                self.create_default_capability(
                    name="Feedback Processing",
                    description="Process and distribute human feedback",
                    tools=["feedback_processor", "sentiment_analyzer"]
                )
            ],
            constraints=[
                self.create_default_constraint(
                    name="Human Authority",
                    description="Human decisions override agent decisions in conflicts",
                    constraint_type="authority_enforcement"
                ),
                self.create_default_constraint(
                    name="Transparency",
                    description="Must provide clear explanations of agent actions to humans",
                    constraint_type="transparency_required"
                )
            ]
        )
        agents.append(human_interface)
        
        return agents
    
    def create_default_domain_regents(self) -> List[DomainRegent]:
        """Create default Domain Regent agents"""
        agents = []
        
        # Operations Regent
        operations_regent = self.create_domain_regent(
            name="Operations Regent",
            description="Strategic oversight for core business operations",
            domain=AgentDomain.OPERATIONS,
            strategic_goals=[
                "Optimize operational efficiency",
                "Reduce operational costs",
                "Improve resource utilization",
                "Enhance operational resilience"
            ],
            performance_metrics=[
                "Operational cost reduction",
                "Process efficiency improvement",
                "Resource utilization rate",
                "Operational incident reduction"
            ],
            capabilities=[
                self.create_default_capability(
                    name="Operational Analysis",
                    description="Analyze operational data for insights",
                    tools=["operations_analyzer", "process_optimizer"]
                ),
                self.create_default_capability(
                    name="Resource Optimization",
                    description="Optimize allocation of operational resources",
                    tools=["resource_optimizer", "capacity_planner"]
                )
            ],
            constraints=[
                self.create_default_constraint(
                    name="Operational Continuity",
                    description="Changes must not disrupt critical operations",
                    constraint_type="continuity_check"
                ),
                self.create_default_constraint(
                    name="Financial Limits",
                    description="Cannot exceed defined financial limits",
                    constraint_type="limit_enforcement"
                )
            ]
        )
        agents.append(operations_regent)
        
        # Intelligence Regent
        intelligence_regent = self.create_domain_regent(
            name="Intelligence Regent",
            description="Strategic oversight for business intelligence and analytics",
            domain=AgentDomain.INTELLIGENCE,
            strategic_goals=[
                "Enhance predictive capabilities",
                "Improve decision support",
                "Identify strategic opportunities",
                "Detect emerging trends"
            ],
            performance_metrics=[
                "Forecast accuracy",
                "Decision impact",
                "Insight generation rate",
                "Trend detection speed"
            ],
            capabilities=[
                self.create_default_capability(
                    name="Predictive Analytics",
                    description="Develop and manage predictive models",
                    tools=["predictive_modeler", "forecast_analyzer"]
                ),
                self.create_default_capability(
                    name="Business Simulation",
                    description="Simulate business scenarios for planning",
                    tools=["business_simulator", "scenario_planner"]
                )
            ],
            constraints=[
                self.create_default_constraint(
                    name="Data Quality",
                    description="Analysis must be based on high-quality data",
                    constraint_type="quality_check"
                ),
                self.create_default_constraint(
                    name="Confidence Transparency",
                    description="Must clearly communicate confidence levels in predictions",
                    constraint_type="transparency_required"
                )
            ]
        )
        agents.append(intelligence_regent)
        
        # Security Regent
        security_regent = self.create_domain_regent(
            name="Security Regent",
            description="Strategic oversight for cybersecurity operations",
            domain=AgentDomain.SECURITY,
            strategic_goals=[
                "Enhance threat detection capabilities",
                "Improve incident response",
                "Strengthen security posture",
                "Reduce security vulnerabilities"
            ],
            performance_metrics=[
                "Threat detection rate",
                "Incident response time",
                "Vulnerability remediation rate",
                "Security posture score"
            ],
            capabilities=[
                self.create_default_capability(
                    name="Threat Intelligence",
                    description="Gather and analyze threat intelligence",
                    tools=["threat_analyzer", "intelligence_aggregator"]
                ),
                self.create_default_capability(
                    name="Security Orchestration",
                    description="Coordinate security tools and responses",
                    tools=["security_orchestrator", "response_coordinator"]
                )
            ],
            constraints=[
                self.create_default_constraint(
                    name="Critical Response Approval",
                    description="Critical security responses require human approval",
                    constraint_type="approval_required"
                ),
                self.create_default_constraint(
                    name="Privacy Protection",
                    description="Security operations must protect privacy",
                    constraint_type="privacy_enforcement"
                )
            ]
        )
        agents.append(security_regent)
        
        # Knowledge Regent
        knowledge_regent = self.create_domain_regent(
            name="Knowledge Regent",
            description="Strategic oversight for knowledge management",
            domain=AgentDomain.KNOWLEDGE,
            strategic_goals=[
                "Enhance organizational knowledge capture",
                "Improve knowledge accessibility",
                "Generate valuable insights",
                "Map organizational expertise"
            ],
            performance_metrics=[
                "Knowledge capture rate",
                "Knowledge retrieval accuracy",
                "Insight generation quality",
                "Expertise mapping coverage"
            ],
            capabilities=[
                self.create_default_capability(
                    name="Knowledge Organization",
                    description="Organize and structure organizational knowledge",
                    tools=["knowledge_organizer", "taxonomy_manager"]
                ),
                self.create_default_capability(
                    name="Insight Synthesis",
                    description="Synthesize insights from knowledge",
                    tools=["insight_synthesizer", "pattern_recognizer"]
                )
            ],
            constraints=[
                self.create_default_constraint(
                    name="Knowledge Quality",
                    description="Must maintain high knowledge quality standards",
                    constraint_type="quality_check"
                ),
                self.create_default_constraint(
                    name="Intellectual Property",
                    description="Must respect intellectual property rights",
                    constraint_type="rights_enforcement"
                )
            ]
        )
        agents.append(knowledge_regent)
        
        # Development Regent
        development_regent = self.create_domain_regent(
            name="Development Regent",
            description="Strategic oversight for software development activities",
            domain=AgentDomain.DEVELOPMENT,
            strategic_goals=[
                "Enhance development efficiency",
                "Improve code quality",
                "Accelerate deployment cycles",
                "Reduce technical debt"
            ],
            performance_metrics=[
                "Development velocity",
                "Code quality metrics",
                "Deployment frequency",
                "Technical debt reduction"
            ],
            capabilities=[
                self.create_default_capability(
                    name="Development Coordination",
                    description="Coordinate development projects and resources",
                    tools=["project_coordinator", "resource_allocator"]
                ),
                self.create_default_capability(
                    name="Quality Management",
                    description="Manage code quality and testing",
                    tools=["quality_manager", "test_coordinator"]
                )
            ],
            constraints=[
                self.create_default_constraint(
                    name="Security Standards",
                    description="All code must meet security standards",
                    constraint_type="standard_enforcement"
                ),
                self.create_default_constraint(
                    name="Production Deployment Approval",
                    description="Production deployments require human approval",
                    constraint_type="approval_required"
                )
            ]
        )
        agents.append(development_regent)
        
        return agents
    
    def create_default_task_masters(self, domain_regents: Dict[AgentDomain, str]) -> List[TaskMaster]:
        """Create default Task Master agents"""
        agents = []
        
        # Operations Task Masters
        if AgentDomain.OPERATIONS in domain_regents:
            operations_regent_id = domain_regents[AgentDomain.OPERATIONS]
            
            # Financial Analyst
            financial_analyst = self.create_task_master(
                name="Financial Analyst",
                description="Financial planning, analysis, and optimization",
                domain=AgentDomain.OPERATIONS,
                specialty="Financial Analysis",
                domain_regent_id=operations_regent_id,
                expertise_areas=[
                    "Financial planning",
                    "Cost analysis",
                    "Budget optimization",
                    "Financial forecasting"
                ],
                capabilities=[
                    self.create_default_capability(
                        name="Financial Analysis",
                        description="Analyze financial data for insights",
                        tools=["financial_analyzer", "trend_detector"]
                    ),
                    self.create_default_capability(
                        name="Budget Optimization",
                        description="Optimize budget allocation",
                        tools=["budget_optimizer", "cost_analyzer"]
                    )
                ]
            )
            agents.append(financial_analyst)
            
            # Supply Chain Optimizer
            supply_chain_optimizer = self.create_task_master(
                name="Supply Chain Optimizer",
                description="Inventory, logistics, and supplier management",
                domain=AgentDomain.OPERATIONS,
                specialty="Supply Chain Management",
                domain_regent_id=operations_regent_id,
                expertise_areas=[
                    "Inventory optimization",
                    "Logistics planning",
                    "Supplier management",
                    "Supply chain resilience"
                ],
                capabilities=[
                    self.create_default_capability(
                        name="Inventory Management",
                        description="Optimize inventory levels",
                        tools=["inventory_optimizer", "stock_analyzer"]
                    ),
                    self.create_default_capability(
                        name="Logistics Planning",
                        description="Plan and optimize logistics operations",
                        tools=["logistics_planner", "route_optimizer"]
                    )
                ]
            )
            agents.append(supply_chain_optimizer)
        
        # Intelligence Task Masters
        if AgentDomain.INTELLIGENCE in domain_regents:
            intelligence_regent_id = domain_regents[AgentDomain.INTELLIGENCE]
            
            # Data Scientist
            data_scientist = self.create_task_master(
                name="Data Scientist",
                description="Advanced analytics and statistical modeling",
                domain=AgentDomain.INTELLIGENCE,
                specialty="Data Science",
                domain_regent_id=intelligence_regent_id,
                expertise_areas=[
                    "Statistical analysis",
                    "Machine learning",
                    "Data visualization",
                    "Feature engineering"
                ],
                capabilities=[
                    self.create_default_capability(
                        name="Statistical Analysis",
                        description="Perform statistical analysis on data",
                        tools=["statistical_analyzer", "hypothesis_tester"]
                    ),
                    self.create_default_capability(
                        name="Model Development",
                        description="Develop and evaluate machine learning models",
                        tools=["model_developer", "model_evaluator"]
                    )
                ]
            )
            agents.append(data_scientist)
            
            # Forecaster
            forecaster = self.create_task_master(
                name="Forecaster",
                description="Predictive modeling and scenario analysis",
                domain=AgentDomain.INTELLIGENCE,
                specialty="Forecasting",
                domain_regent_id=intelligence_regent_id,
                expertise_areas=[
                    "Time series forecasting",
                    "Scenario modeling",
                    "Predictive analytics",
                    "Uncertainty quantification"
                ],
                capabilities=[
                    self.create_default_capability(
                        name="Time Series Forecasting",
                        description="Forecast future values of time series data",
                        tools=["time_series_forecaster", "seasonality_analyzer"]
                    ),
                    self.create_default_capability(
                        name="Scenario Analysis",
                        description="Analyze different future scenarios",
                        tools=["scenario_analyzer", "sensitivity_tester"]
                    )
                ]
            )
            agents.append(forecaster)
        
        # Security Task Masters
        if AgentDomain.SECURITY in domain_regents:
            security_regent_id = domain_regents[AgentDomain.SECURITY]
            
            # Threat Hunter
            threat_hunter = self.create_task_master(
                name="Threat Hunter",
                description="Proactive threat identification and analysis",
                domain=AgentDomain.SECURITY,
                specialty="Threat Hunting",
                domain_regent_id=security_regent_id,
                expertise_areas=[
                    "Threat intelligence",
                    "Behavioral analysis",
                    "Indicator analysis",
                    "Attack pattern recognition"
                ],
                capabilities=[
                    self.create_default_capability(
                        name="Threat Intelligence Analysis",
                        description="Analyze threat intelligence data",
                        tools=["intelligence_analyzer", "ioc_detector"]
                    ),
                    self.create_default_capability(
                        name="Behavioral Analysis",
                        description="Analyze system behavior for anomalies",
                        tools=["behavior_analyzer", "anomaly_detector"]
                    )
                ]
            )
            agents.append(threat_hunter)
            
            # Incident Responder
            incident_responder = self.create_task_master(
                name="Incident Responder",
                description="Security incident investigation and remediation",
                domain=AgentDomain.SECURITY,
                specialty="Incident Response",
                domain_regent_id=security_regent_id,
                expertise_areas=[
                    "Incident investigation",
                    "Forensic analysis",
                    "Containment strategies",
                    "Remediation planning"
                ],
                capabilities=[
                    self.create_default_capability(
                        name="Incident Investigation",
                        description="Investigate security incidents",
                        tools=["incident_investigator", "evidence_collector"]
                    ),
                    self.create_default_capability(
                        name="Remediation Planning",
                        description="Plan incident remediation steps",
                        tools=["remediation_planner", "containment_strategist"]
                    )
                ]
            )
            agents.append(incident_responder)
        
        # Knowledge Task Masters
        if AgentDomain.KNOWLEDGE in domain_regents:
            knowledge_regent_id = domain_regents[AgentDomain.KNOWLEDGE]
            
            # Knowledge Curator
            knowledge_curator = self.create_task_master(
                name="Knowledge Curator",
                description="Content organization and quality management",
                domain=AgentDomain.KNOWLEDGE,
                specialty="Knowledge Curation",
                domain_regent_id=knowledge_regent_id,
                expertise_areas=[
                    "Content organization",
                    "Metadata management",
                    "Quality assessment",
                    "Information architecture"
                ],
                capabilities=[
                    self.create_default_capability(
                        name="Content Organization",
                        description="Organize and categorize content",
                        tools=["content_organizer", "taxonomy_manager"]
                    ),
                    self.create_default_capability(
                        name="Quality Assessment",
                        description="Assess and improve content quality",
                        tools=["quality_assessor", "improvement_recommender"]
                    )
                ]
            )
            agents.append(knowledge_curator)
            
            # Insight Generator
            insight_generator = self.create_task_master(
                name="Insight Generator",
                description="Pattern recognition and insight synthesis",
                domain=AgentDomain.KNOWLEDGE,
                specialty="Insight Generation",
                domain_regent_id=knowledge_regent_id,
                expertise_areas=[
                    "Pattern recognition",
                    "Insight synthesis",
                    "Knowledge connection",
                    "Trend identification"
                ],
                capabilities=[
                    self.create_default_capability(
                        name="Pattern Recognition",
                        description="Recognize patterns in knowledge",
                        tools=["pattern_recognizer", "connection_finder"]
                    ),
                    self.create_default_capability(
                        name="Insight Synthesis",
                        description="Synthesize insights from patterns",
                        tools=["insight_synthesizer", "implication_analyzer"]
                    )
                ]
            )
            agents.append(insight_generator)
        
        # Development Task Masters
        if AgentDomain.DEVELOPMENT in domain_regents:
            development_regent_id = domain_regents[AgentDomain.DEVELOPMENT]
            
            # Code Architect
            code_architect = self.create_task_master(
                name="Code Architect",
                description="Software design and architecture",
                domain=AgentDomain.DEVELOPMENT,
                specialty="Software Architecture",
                domain_regent_id=development_regent_id,
                expertise_areas=[
                    "System design",
                    "Architecture patterns",
                    "Technical debt management",
                    "Scalability planning"
                ],
                capabilities=[
                    self.create_default_capability(
                        name="Architecture Design",
                        description="Design software architecture",
                        tools=["architecture_designer", "pattern_implementer"]
                    ),
                    self.create_default_capability(
                        name="Technical Debt Management",
                        description="Identify and manage technical debt",
                        tools=["debt_analyzer", "refactoring_planner"]
                    )
                ]
            )
            agents.append(code_architect)
            
            # Quality Engineer
            quality_engineer = self.create_task_master(
                name="Quality Engineer",
                description="Testing and quality assurance",
                domain=AgentDomain.DEVELOPMENT,
                specialty="Quality Assurance",
                domain_regent_id=development_regent_id,
                expertise_areas=[
                    "Test strategy",
                    "Automated testing",
                    "Quality metrics",
                    "Defect analysis"
                ],
                capabilities=[
                    self.create_default_capability(
                        name="Test Strategy",
                        description="Develop comprehensive test strategies",
                        tools=["test_strategist", "coverage_analyzer"]
                    ),
                    self.create_default_capability(
                        name="Automated Testing",
                        description="Implement automated testing",
                        tools=["test_automator", "regression_tester"]
                    )
                ]
            )
            agents.append(quality_engineer)
        
        return agents
    
    def create_default_minions(self, task_masters: Dict[str, str]) -> List[Minion]:
        """Create default Minion agents"""
        agents = []
        
        # For each Task Master, create appropriate Minions
        for task_master_name, task_master_id in task_masters.items():
            # Data Minions
            if task_master_name in ["Data Scientist", "Forecaster", "Knowledge Curator"]:
                # Data Collector
                data_collector = self.create_minion(
                    name=f"Data Collector for {task_master_name}",
                    description="Gathering data from various sources",
                    domain=self._get_domain_for_task_master(task_master_name),
                    function_type="data",
                    specific_function="data_collector",
                    task_master_id=task_master_id,
                    capabilities=[
                        self.create_default_capability(
                            name="Data Collection",
                            description="Collect data from various sources",
                            tools=["data_collector", "source_connector"]
                        )
                    ]
                )
                agents.append(data_collector)
                
                # Data Transformer
                data_transformer = self.create_minion(
                    name=f"Data Transformer for {task_master_name}",
                    description="Converting data between formats",
                    domain=self._get_domain_for_task_master(task_master_name),
                    function_type="data",
                    specific_function="data_transformer",
                    task_master_id=task_master_id,
                    capabilities=[
                        self.create_default_capability(
                            name="Data Transformation",
                            description="Transform data between formats",
                            tools=["data_transformer", "format_converter"]
                        )
                    ]
                )
                agents.append(data_transformer)
            
            # Process Minions
            if task_master_name in ["Financial Analyst", "Supply Chain Optimizer", "Incident Responder"]:
                # Task Executor
                task_executor = self.create_minion(
                    name=f"Task Executor for {task_master_name}",
                    description="Running predefined processes",
                    domain=self._get_domain_for_task_master(task_master_name),
                    function_type="process",
                    specific_function="task_executor",
                    task_master_id=task_master_id,
                    capabilities=[
                        self.create_default_capability(
                            name="Process Execution",
                            description="Execute predefined processes",
                            tools=["process_executor", "workflow_runner"]
                        )
                    ]
                )
                agents.append(task_executor)
                
                # Notifier
                notifier = self.create_minion(
                    name=f"Notifier for {task_master_name}",
                    description="Sending alerts and notifications",
                    domain=self._get_domain_for_task_master(task_master_name),
                    function_type="process",
                    specific_function="notifier",
                    task_master_id=task_master_id,
                    capabilities=[
                        self.create_default_capability(
                            name="Notification",
                            description="Send alerts and notifications",
                            tools=["notifier", "alert_manager"]
                        )
                    ]
                )
                agents.append(notifier)
            
            # Interaction Minions
            if task_master_name in ["Insight Generator", "Threat Hunter", "Code Architect"]:
                # Query Responder
                query_responder = self.create_minion(
                    name=f"Query Responder for {task_master_name}",
                    description="Answering simple questions",
                    domain=self._get_domain_for_task_master(task_master_name),
                    function_type="interaction",
                    specific_function="query_responder",
                    task_master_id=task_master_id,
                    capabilities=[
                        self.create_default_capability(
                            name="Query Response",
                            description="Answer simple questions",
                            tools=["query_responder", "knowledge_retriever"]
                        )
                    ]
                )
                agents.append(query_responder)
                
                # Summarizer
                summarizer = self.create_minion(
                    name=f"Summarizer for {task_master_name}",
                    description="Creating concise summaries",
                    domain=self._get_domain_for_task_master(task_master_name),
                    function_type="interaction",
                    specific_function="summarizer",
                    task_master_id=task_master_id,
                    capabilities=[
                        self.create_default_capability(
                            name="Summarization",
                            description="Create concise summaries",
                            tools=["summarizer", "key_point_extractor"]
                        )
                    ]
                )
                agents.append(summarizer)
            
            # Technical Minions
            if task_master_name in ["Quality Engineer", "Code Architect"]:
                # Code Generator
                code_generator = self.create_minion(
                    name=f"Code Generator for {task_master_name}",
                    description="Creating simple code snippets",
                    domain=self._get_domain_for_task_master(task_master_name),
                    function_type="technical",
                    specific_function="code_generator",
                    task_master_id=task_master_id,
                    capabilities=[
                        self.create_default_capability(
                            name="Code Generation",
                            description="Generate simple code snippets",
                            tools=["code_generator", "template_implementer"]
                        )
                    ]
                )
                agents.append(code_generator)
                
                # Tester
                tester = self.create_minion(
                    name=f"Tester for {task_master_name}",
                    description="Running predefined tests",
                    domain=self._get_domain_for_task_master(task_master_name),
                    function_type="technical",
                    specific_function="tester",
                    task_master_id=task_master_id,
                    capabilities=[
                        self.create_default_capability(
                            name="Testing",
                            description="Run predefined tests",
                            tools=["test_runner", "result_analyzer"]
                        )
                    ]
                )
                agents.append(tester)
        
        return agents
    
    def _get_domain_for_task_master(self, task_master_name: str) -> AgentDomain:
        """Get the domain for a task master based on its name"""
        if task_master_name in ["Financial Analyst", "Supply Chain Optimizer"]:
            return AgentDomain.OPERATIONS
        elif task_master_name in ["Data Scientist", "Forecaster"]:
            return AgentDomain.INTELLIGENCE
        elif task_master_name in ["Threat Hunter", "Incident Responder"]:
            return AgentDomain.SECURITY
        elif task_master_name in ["Knowledge Curator", "Insight Generator"]:
            return AgentDomain.KNOWLEDGE
        elif task_master_name in ["Code Architect", "Quality Engineer"]:
            return AgentDomain.DEVELOPMENT
        else:
            return AgentDomain.SYSTEM