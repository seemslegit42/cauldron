"""
Hooks for Synapse module
"""

app_name = "cauldron_synapse"
app_title = "Synapse"
app_publisher = "Your Organization"
app_description = "Predictive & Prescriptive Business Intelligence Module"
app_icon = "octicon octicon-graph"
app_color = "blue"
app_email = "your-email@example.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/cauldron_synapse/css/synapse.css"
app_include_js = "/assets/cauldron_synapse/js/synapse.js"

# include js, css files in header of web template
web_include_css = "/assets/cauldron_synapse/css/synapse_web.css"
web_include_js = "/assets/cauldron_synapse/js/synapse_web.js"

# include custom scss in every website theme (without file extension ".scss")
website_theme_scss = "cauldron_synapse/public/scss/website"

# include js, css files in header of web form
webform_include_js = {"doctype": "public/js/doctype.js"}
webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
page_js = {"analytics-hub": "public/js/analytics_hub.js"}

# include js in doctype views
doctype_js = {
    "DataSource": "public/js/data_source.js",
    "Dashboard": "public/js/dashboard.js",
    "Forecast": "public/js/forecast.js",
    "BusinessScenario": "public/js/business_scenario.js",
    "Recommendation": "public/js/recommendation.js"
}

doctype_list_js = {
    "DataSource": "public/js/data_source_list.js",
    "Dashboard": "public/js/dashboard_list.js",
    "Forecast": "public/js/forecast_list.js"
}

# Home Pages
# ----------

# application home page (will override Website Settings)
home_page = "synapse-home"

# website user home page (by Role)
role_home_page = {
    "Analytics Manager": "synapse-analytics",
    "Analytics User": "synapse-analytics"
}

# Generators
# ----------

# automatically create page for each record of this doctype
website_generators = ["Dashboard"]

# Installation
# ------------

# before_install = "cauldron_synapse.install.before_install"
# after_install = "cauldron_synapse.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

notification_config = "cauldron_synapse.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
    "Dashboard": "cauldron_synapse.permissions.get_dashboard_permission_query_conditions",
    "Forecast": "cauldron_synapse.permissions.get_forecast_permission_query_conditions"
}

has_permission = {
    "Dashboard": "cauldron_synapse.permissions.has_dashboard_permission",
    "Forecast": "cauldron_synapse.permissions.has_forecast_permission"
}

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    "Dashboard": "cauldron_synapse.overrides.CustomDashboard"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "DataSource": {
        "after_insert": "cauldron_synapse.data_fabric.data_source.after_insert",
        "on_update": "cauldron_synapse.data_fabric.data_source.on_update",
        "on_cancel": "cauldron_synapse.data_fabric.data_source.on_cancel",
        "on_trash": "cauldron_synapse.data_fabric.data_source.on_trash"
    },
    "Forecast": {
        "after_insert": "cauldron_synapse.predictive_analytics.forecast.after_insert",
        "on_update": "cauldron_synapse.predictive_analytics.forecast.on_update"
    },
    "Anomaly": {
        "after_insert": "cauldron_synapse.predictive_analytics.anomaly.after_insert"
    },
    "BusinessScenario": {
        "after_insert": "cauldron_synapse.business_simulation.scenario.after_insert",
        "on_update": "cauldron_synapse.business_simulation.scenario.on_update"
    },
    "Recommendation": {
        "after_insert": "cauldron_synapse.strategic_advisor.recommendation.after_insert"
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "all": [
        "cauldron_synapse.tasks.all"
    ],
    "daily": [
        "cauldron_synapse.tasks.daily"
    ],
    "hourly": [
        "cauldron_synapse.tasks.hourly"
    ],
    "weekly": [
        "cauldron_synapse.tasks.weekly"
    ],
    "monthly": [
        "cauldron_synapse.tasks.monthly"
    ],
    "cron": {
        # Run data pipeline jobs
        "*/15 * * * *": [
            "cauldron_synapse.data_fabric.pipeline.run_scheduled_pipelines"
        ],
        # Run forecasting models
        "0 1 * * *": [
            "cauldron_synapse.predictive_analytics.forecasting.run_scheduled_forecasts"
        ],
        # Run anomaly detection
        "*/30 * * * *": [
            "cauldron_synapse.predictive_analytics.anomaly_detection.detect_anomalies"
        ]
    }
}

# Testing
# -------

# before_tests = "cauldron_synapse.install.before_tests"

# Overriding Methods
# ------------------------------

# override_whitelisted_methods = {
#     "frappe.desk.doctype.event.event.get_events": "cauldron_synapse.event.get_events"
# }

# Mythos EDA Event Handlers
# -------------------------

mythos_event_handlers = {
    "operations.sales.order.created": "cauldron_synapse.integrations.mythos.handle_sales_order_created",
    "operations.inventory.level.changed": "cauldron_synapse.integrations.mythos.handle_inventory_level_changed",
    "operations.production.completed": "cauldron_synapse.integrations.mythos.handle_production_completed",
    "operations.finance.transaction.recorded": "cauldron_synapse.integrations.mythos.handle_finance_transaction_recorded"
}

# Mythos EDA Event Publishers
# --------------------------

mythos_event_publishers = [
    "cauldron_synapse.integrations.mythos.publish_forecast_updated",
    "cauldron_synapse.integrations.mythos.publish_anomaly_detected",
    "cauldron_synapse.integrations.mythos.publish_recommendation_created",
    "cauldron_synapse.integrations.mythos.publish_insight_generated"
]

# AetherCore Agent Tasks
# ---------------------

aethercore_agent_tasks = {
    "synapse.analyze_trend": "cauldron_synapse.integrations.aethercore.analyze_trend",
    "synapse.generate_forecast": "cauldron_synapse.integrations.aethercore.generate_forecast",
    "synapse.detect_anomalies": "cauldron_synapse.integrations.aethercore.detect_anomalies",
    "synapse.recommend_actions": "cauldron_synapse.integrations.aethercore.recommend_actions",
    "synapse.explain_insight": "cauldron_synapse.integrations.aethercore.explain_insight"
}

# Each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
    "Sales Order": "cauldron_synapse.overrides.dashboards.get_sales_order_dashboard",
    "Item": "cauldron_synapse.overrides.dashboards.get_item_dashboard",
    "Customer": "cauldron_synapse.overrides.dashboards.get_customer_dashboard"
}"""
Hooks for Synapse module
"""

app_name = "cauldron_synapse"
app_title = "Synapse"
app_publisher = "Your Organization"
app_description = "Predictive & Prescriptive Business Intelligence Module"
app_icon = "octicon octicon-graph"
app_color = "blue"
app_email = "your-email@example.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/cauldron_synapse/css/synapse.css"
app_include_js = "/assets/cauldron_synapse/js/synapse.js"

# include js, css files in header of web template
web_include_css = "/assets/cauldron_synapse/css/synapse_web.css"
web_include_js = "/assets/cauldron_synapse/js/synapse_web.js"

# include custom scss in every website theme (without file extension ".scss")
website_theme_scss = "cauldron_synapse/public/scss/website"

# include js, css files in header of web form
webform_include_js = {"doctype": "public/js/doctype.js"}
webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
page_js = {"analytics-hub": "public/js/analytics_hub.js"}

# include js in doctype views
doctype_js = {
    "DataSource": "public/js/data_source.js",
    "Dashboard": "public/js/dashboard.js",
    "Forecast": "public/js/forecast.js",
    "BusinessScenario": "public/js/business_scenario.js",
    "Recommendation": "public/js/recommendation.js"
}

doctype_list_js = {
    "DataSource": "public/js/data_source_list.js",
    "Dashboard": "public/js/dashboard_list.js",
    "Forecast": "public/js/forecast_list.js"
}

# Home Pages
# ----------

# application home page (will override Website Settings)
home_page = "synapse-home"

# website user home page (by Role)
role_home_page = {
    "Analytics Manager": "synapse-analytics",
    "Analytics User": "synapse-analytics"
}

# Generators
# ----------

# automatically create page for each record of this doctype
website_generators = ["Dashboard"]

# Installation
# ------------

# before_install = "cauldron_synapse.install.before_install"
# after_install = "cauldron_synapse.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

notification_config = "cauldron_synapse.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
    "Dashboard": "cauldron_synapse.permissions.get_dashboard_permission_query_conditions",
    "Forecast": "cauldron_synapse.permissions.get_forecast_permission_query_conditions"
}

has_permission = {
    "Dashboard": "cauldron_synapse.permissions.has_dashboard_permission",
    "Forecast": "cauldron_synapse.permissions.has_forecast_permission"
}

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    "Dashboard": "cauldron_synapse.overrides.CustomDashboard"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "DataSource": {
        "after_insert": "cauldron_synapse.data_fabric.data_source.after_insert",
        "on_update": "cauldron_synapse.data_fabric.data_source.on_update",
        "on_cancel": "cauldron_synapse.data_fabric.data_source.on_cancel",
        "on_trash": "cauldron_synapse.data_fabric.data_source.on_trash"
    },
    "Forecast": {
        "after_insert": "cauldron_synapse.predictive_analytics.forecast.after_insert",
        "on_update": "cauldron_synapse.predictive_analytics.forecast.on_update"
    },
    "Anomaly": {
        "after_insert": "cauldron_synapse.predictive_analytics.anomaly.after_insert"
    },
    "BusinessScenario": {
        "after_insert": "cauldron_synapse.business_simulation.scenario.after_insert",
        "on_update": "cauldron_synapse.business_simulation.scenario.on_update"
    },
    "Recommendation": {
        "after_insert": "cauldron_synapse.strategic_advisor.recommendation.after_insert"
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "all": [
        "cauldron_synapse.tasks.all"
    ],
    "daily": [
        "cauldron_synapse.tasks.daily"
    ],
    "hourly": [
        "cauldron_synapse.tasks.hourly"
    ],
    "weekly": [
        "cauldron_synapse.tasks.weekly"
    ],
    "monthly": [
        "cauldron_synapse.tasks.monthly"
    ],
    "cron": {
        # Run data pipeline jobs
        "*/15 * * * *": [
            "cauldron_synapse.data_fabric.pipeline.run_scheduled_pipelines"
        ],
        # Run forecasting models
        "0 1 * * *": [
            "cauldron_synapse.predictive_analytics.forecasting.run_scheduled_forecasts"
        ],
        # Run anomaly detection
        "*/30 * * * *": [
            "cauldron_synapse.predictive_analytics.anomaly_detection.detect_anomalies"
        ]
    }
}

# Testing
# -------

# before_tests = "cauldron_synapse.install.before_tests"

# Overriding Methods
# ------------------------------

# override_whitelisted_methods = {
#     "frappe.desk.doctype.event.event.get_events": "cauldron_synapse.event.get_events"
# }

# Mythos EDA Event Handlers
# -------------------------

mythos_event_handlers = {
    "operations.sales.order.created": "cauldron_synapse.integrations.mythos.handle_sales_order_created",
    "operations.inventory.level.changed": "cauldron_synapse.integrations.mythos.handle_inventory_level_changed",
    "operations.production.completed": "cauldron_synapse.integrations.mythos.handle_production_completed",
    "operations.finance.transaction.recorded": "cauldron_synapse.integrations.mythos.handle_finance_transaction_recorded"
}

# Mythos EDA Event Publishers
# --------------------------

mythos_event_publishers = [
    "cauldron_synapse.integrations.mythos.publish_forecast_updated",
    "cauldron_synapse.integrations.mythos.publish_anomaly_detected",
    "cauldron_synapse.integrations.mythos.publish_recommendation_created",
    "cauldron_synapse.integrations.mythos.publish_insight_generated"
]

# AetherCore Agent Tasks
# ---------------------

aethercore_agent_tasks = {
    "synapse.analyze_trend": "cauldron_synapse.integrations.aethercore.analyze_trend",
    "synapse.generate_forecast": "cauldron_synapse.integrations.aethercore.generate_forecast",
    "synapse.detect_anomalies": "cauldron_synapse.integrations.aethercore.detect_anomalies",
    "synapse.recommend_actions": "cauldron_synapse.integrations.aethercore.recommend_actions",
    "synapse.explain_insight": "cauldron_synapse.integrations.aethercore.explain_insight"
}

# Each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
    "Sales Order": "cauldron_synapse.overrides.dashboards.get_sales_order_dashboard",
    "Item": "cauldron_synapse.overrides.dashboards.get_item_dashboard",
    "Customer": "cauldron_synapse.overrides.dashboards.get_customer_dashboard"
}