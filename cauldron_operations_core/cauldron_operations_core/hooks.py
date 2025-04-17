from . import __version__ as app_version

app_name = "cauldron_operations_core"
app_title = "Cauldron Operations Core"
app_publisher = "Cauldron"
app_description = "Operations Core for Cauldron sEOS"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@cauldron.ai"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/cauldron_operations_core/css/cauldron_operations_core.css"
# app_include_js = "/assets/cauldron_operations_core/js/cauldron_operations_core.js"

# include js, css files in header of web template
# web_include_css = "/assets/cauldron_operations_core/css/cauldron_operations_core_web.css"
# web_include_js = "/assets/cauldron_operations_core/js/cauldron_operations_core_web.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "cauldron_operations_core/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "cauldron_operations_core.install.before_install"
after_install = "cauldron_operations_core.setup.after_install"

# Uninstallation
# ------------

# before_uninstall = "cauldron_operations_core.uninstall.before_uninstall"
# after_uninstall = "cauldron_operations_core.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "cauldron_operations_core.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Order": {
        "on_update": "cauldron_operations_core.workflows.workflow_handlers.handle_workflow_transition",
    },
    "Purchase Order": {
        "on_update": "cauldron_operations_core.workflows.workflow_handlers.handle_workflow_transition",
    },
    "Journal Entry": {
        "on_update": "cauldron_operations_core.workflows.workflow_handlers.handle_workflow_transition",
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"cauldron_operations_core.tasks.all"
# 	],
# 	"daily": [
# 		"cauldron_operations_core.tasks.daily"
# 	],
# 	"hourly": [
# 		"cauldron_operations_core.tasks.hourly"
# 	],
# 	"weekly": [
# 		"cauldron_operations_core.tasks.weekly"
# 	]
# 	"monthly": [
# 		"cauldron_operations_core.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "cauldron_operations_core.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "cauldron_operations_core.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "cauldron_operations_core.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
    {
        "doctype": "{doctype}",
        "filter_by": "{filter_by}",
        "redact_fields": ["{field1}", "{field2}"],
        "partial": 1,
    },
    {
        "doctype": "{doctype}",
        "filter_by": "{filter_by}",
        "partial": 0,
    },
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"cauldron_operations_core.auth.validate"
# ]

# Webhooks
# --------

webhooks = [
    {
        "doctype": "Webhook",
        "webhook_doctype": "HITL Response",
        "webhook_docevent": "on_submit",
        "request_url": "/api/method/cauldron_operations_core.api.hitl_webhook.hitl_response_webhook",
        "condition": "doc.status == 'Pending'",
        "request_method": "POST",
        "request_structure": "Form URL-Encoded",
        "webhook_headers": [
            {
                "key": "Content-Type",
                "value": "application/json"
            }
        ],
        "webhook_data": [
            {
                "fieldname": "hitl_request_id",
                "key": "hitl_request_id"
            },
            {
                "fieldname": "response",
                "key": "response"
            },
            {
                "fieldname": "response_details",
                "key": "response_details"
            },
            {
                "fieldname": "human_id",
                "key": "human_id"
            }
        ]
    }
]

# AetherCore Integration
# ---------------------

aethercore_integration = {
    "hitl_webhook_endpoint": "/api/method/cauldron_operations_core.api.hitl_webhook.hitl_response_webhook"
}
