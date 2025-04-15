"""
Synapse module configuration
"""

from frappe import _

def get_data():
    return [
        {
            "label": _("Data Fabric"),
            "icon": "fa fa-database",
            "items": [
                {
                    "type": "doctype",
                    "name": "DataSource",
                    "description": _("Configure data sources for analytics"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "DataPipeline",
                    "description": _("Define ETL processes and schedules"),
                },
                {
                    "type": "doctype",
                    "name": "DataModel",
                    "description": _("Define semantic data models"),
                },
                {
                    "type": "doctype",
                    "name": "AnalyticsMetric",
                    "description": _("Define business KPIs and metrics"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "DataQuality",
                    "description": _("Data quality metrics and rules"),
                },
            ]
        },
        {
            "label": _("Predictive Analytics"),
            "icon": "fa fa-line-chart",
            "items": [
                {
                    "type": "doctype",
                    "name": "Forecast",
                    "description": _("Time-series forecasts and predictions"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Anomaly",
                    "description": _("Detected anomalies and outliers"),
                },
                {
                    "type": "doctype",
                    "name": "PredictiveModel",
                    "description": _("Model configurations and metadata"),
                },
                {
                    "type": "doctype",
                    "name": "ModelTraining",
                    "description": _("Training job configurations and history"),
                },
                {
                    "type": "doctype",
                    "name": "ModelPerformance",
                    "description": _("Model accuracy and performance metrics"),
                },
            ]
        },
        {
            "label": _("Business Simulation"),
            "icon": "fa fa-flask",
            "items": [
                {
                    "type": "doctype",
                    "name": "BusinessScenario",
                    "description": _("What-if scenario definitions"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Simulation",
                    "description": _("Simulation configurations and results"),
                },
                {
                    "type": "doctype",
                    "name": "SimulationAgent",
                    "description": _("Agent definitions for agent-based modeling"),
                },
                {
                    "type": "doctype",
                    "name": "ScenarioParameter",
                    "description": _("Parameter definitions for simulations"),
                },
            ]
        },
        {
            "label": _("Strategic Advisor"),
            "icon": "fa fa-lightbulb-o",
            "items": [
                {
                    "type": "doctype",
                    "name": "Recommendation",
                    "description": _("Prescriptive recommendations"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "DecisionRecord",
                    "description": _("Decisions made based on insights"),
                },
                {
                    "type": "doctype",
                    "name": "AutomatedAction",
                    "description": _("Configured automated responses"),
                },
                {
                    "type": "doctype",
                    "name": "AIInsight",
                    "description": _("AI-generated insights and explanations"),
                },
            ]
        },
        {
            "label": _("Visualization"),
            "icon": "fa fa-pie-chart",
            "items": [
                {
                    "type": "doctype",
                    "name": "Dashboard",
                    "description": _("Custom dashboard configurations"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Report",
                    "description": _("Report definitions and parameters"),
                },
                {
                    "type": "doctype",
                    "name": "Alert",
                    "description": _("Alert configurations and history"),
                },
                {
                    "type": "page",
                    "name": "synapse-analytics",
                    "label": _("Analytics Hub"),
                    "description": _("Central analytics dashboard"),
                    "onboard": 1,
                },
            ]
        },
        {
            "label": _("Knowledge Management"),
            "icon": "fa fa-book",
            "items": [
                {
                    "type": "doctype",
                    "name": "BusinessOntology",
                    "description": _("Business concept relationships and hierarchies"),
                },
                {
                    "type": "doctype",
                    "name": "CausalGraph",
                    "description": _("Cause-effect relationships between metrics"),
                },
                {
                    "type": "doctype",
                    "name": "BusinessContext",
                    "description": _("Contextual information about business domains"),
                },
                {
                    "type": "doctype",
                    "name": "AnalyticsGlossary",
                    "description": _("Definitions of analytics terms and concepts"),
                },
            ]
        },
        {
            "label": _("Settings"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "SynapseSettings",
                    "description": _("Global settings for Synapse module"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "IntegrationSettings",
                    "description": _("Configure integrations with other modules"),
                },
                {
                    "type": "doctype",
                    "name": "AIModelSettings",
                    "description": _("Configure AI model settings"),
                },
            ]
        },
    ]"""
Synapse module configuration
"""

from frappe import _

def get_data():
    return [
        {
            "label": _("Data Fabric"),
            "icon": "fa fa-database",
            "items": [
                {
                    "type": "doctype",
                    "name": "DataSource",
                    "description": _("Configure data sources for analytics"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "DataPipeline",
                    "description": _("Define ETL processes and schedules"),
                },
                {
                    "type": "doctype",
                    "name": "DataModel",
                    "description": _("Define semantic data models"),
                },
                {
                    "type": "doctype",
                    "name": "AnalyticsMetric",
                    "description": _("Define business KPIs and metrics"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "DataQuality",
                    "description": _("Data quality metrics and rules"),
                },
            ]
        },
        {
            "label": _("Predictive Analytics"),
            "icon": "fa fa-line-chart",
            "items": [
                {
                    "type": "doctype",
                    "name": "Forecast",
                    "description": _("Time-series forecasts and predictions"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Anomaly",
                    "description": _("Detected anomalies and outliers"),
                },
                {
                    "type": "doctype",
                    "name": "PredictiveModel",
                    "description": _("Model configurations and metadata"),
                },
                {
                    "type": "doctype",
                    "name": "ModelTraining",
                    "description": _("Training job configurations and history"),
                },
                {
                    "type": "doctype",
                    "name": "ModelPerformance",
                    "description": _("Model accuracy and performance metrics"),
                },
            ]
        },
        {
            "label": _("Business Simulation"),
            "icon": "fa fa-flask",
            "items": [
                {
                    "type": "doctype",
                    "name": "BusinessScenario",
                    "description": _("What-if scenario definitions"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Simulation",
                    "description": _("Simulation configurations and results"),
                },
                {
                    "type": "doctype",
                    "name": "SimulationAgent",
                    "description": _("Agent definitions for agent-based modeling"),
                },
                {
                    "type": "doctype",
                    "name": "ScenarioParameter",
                    "description": _("Parameter definitions for simulations"),
                },
            ]
        },
        {
            "label": _("Strategic Advisor"),
            "icon": "fa fa-lightbulb-o",
            "items": [
                {
                    "type": "doctype",
                    "name": "Recommendation",
                    "description": _("Prescriptive recommendations"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "DecisionRecord",
                    "description": _("Decisions made based on insights"),
                },
                {
                    "type": "doctype",
                    "name": "AutomatedAction",
                    "description": _("Configured automated responses"),
                },
                {
                    "type": "doctype",
                    "name": "AIInsight",
                    "description": _("AI-generated insights and explanations"),
                },
            ]
        },
        {
            "label": _("Visualization"),
            "icon": "fa fa-pie-chart",
            "items": [
                {
                    "type": "doctype",
                    "name": "Dashboard",
                    "description": _("Custom dashboard configurations"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Report",
                    "description": _("Report definitions and parameters"),
                },
                {
                    "type": "doctype",
                    "name": "Alert",
                    "description": _("Alert configurations and history"),
                },
                {
                    "type": "page",
                    "name": "synapse-analytics",
                    "label": _("Analytics Hub"),
                    "description": _("Central analytics dashboard"),
                    "onboard": 1,
                },
            ]
        },
        {
            "label": _("Knowledge Management"),
            "icon": "fa fa-book",
            "items": [
                {
                    "type": "doctype",
                    "name": "BusinessOntology",
                    "description": _("Business concept relationships and hierarchies"),
                },
                {
                    "type": "doctype",
                    "name": "CausalGraph",
                    "description": _("Cause-effect relationships between metrics"),
                },
                {
                    "type": "doctype",
                    "name": "BusinessContext",
                    "description": _("Contextual information about business domains"),
                },
                {
                    "type": "doctype",
                    "name": "AnalyticsGlossary",
                    "description": _("Definitions of analytics terms and concepts"),
                },
            ]
        },
        {
            "label": _("Settings"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "SynapseSettings",
                    "description": _("Global settings for Synapse module"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "IntegrationSettings",
                    "description": _("Configure integrations with other modules"),
                },
                {
                    "type": "doctype",
                    "name": "AIModelSettings",
                    "description": _("Configure AI model settings"),
                },
            ]
        },
    ]