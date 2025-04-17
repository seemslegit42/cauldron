import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.utils import now_datetime

def update_agent_status(doctype, docname, status_code, agent_id=None, task_id=None):
    """Update the agent status for a document

    Args:
        doctype (str): The DocType of the document
        docname (str): The name of the document
        status_code (str): The status code to set (must exist in Agent Status DocType)
        agent_id (str, optional): The ID of the agent. Defaults to None.
        task_id (str, optional): The task ID. Defaults to None.

    Returns:
        dict: The updated document
    """
    if not frappe.db.exists("Agent Status", status_code):
        frappe.throw(f"Invalid agent status: {status_code}")

    doc = frappe.get_doc(doctype, docname)

    # Update agent fields if provided
    if agent_id and not doc.managing_agent:
        doc.managing_agent = agent_id

    if task_id and not doc.agent_task_id:
        doc.agent_task_id = task_id

    # Set agent managed flag if not already set
    if not doc.agent_managed:
        doc.agent_managed = 1

    # Update status fields
    doc.agent_status = status_code
    doc.agent_status_updated = now_datetime()

    # Save the document
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    # Log the status change
    status_doc = frappe.get_doc("Agent Status", status_code)
    log_message = f"Status changed to {status_doc.status_name}"

    # Add action log entry if the document has agent_action_log field
    if hasattr(doc, 'agent_action_log'):
        doc.append("agent_action_log", {
            "action_timestamp": now_datetime(),
            "action_type": "Update",
            "action_description": log_message,
            "agent_id": agent_id or doc.managing_agent,
            "task_id": task_id or doc.agent_task_id,
            "human_review_required": status_doc.requires_attention
        })
        doc.save(ignore_permissions=True)
        frappe.db.commit()

    return doc

def get_documents_requiring_attention(doctype=None, user=None):
    """Get documents that require human attention based on their agent status

    Args:
        doctype (str, optional): Filter by specific DocType. Defaults to None.
        user (str, optional): Filter by specific user. Defaults to None.

    Returns:
        list: List of documents requiring attention
    """
    # Get statuses that require attention
    attention_statuses = frappe.get_all(
        "Agent Status",
        filters={"requires_attention": 1},
        pluck="name"
    )

    if not attention_statuses:
        return []

    # Build the query to find documents with these statuses
    doctypes_with_agent_status = [
        "Sales Order", "Purchase Order", "Journal Entry", "Item", "Customer"
    ]

    if doctype:
        if doctype not in doctypes_with_agent_status:
            frappe.throw(f"DocType {doctype} does not support agent status tracking")
        doctypes_to_check = [doctype]
    else:
        doctypes_to_check = doctypes_with_agent_status

    results = []

    for dt in doctypes_to_check:
        filters = {
            "agent_managed": 1,
            "agent_status": ["in", attention_statuses]
        }

        # Add user filter if specified
        if user:
            # This assumes there's a way to link documents to users
            # You might need to adjust this based on your actual data model
            if dt == "Sales Order":
                filters["owner"] = user
            elif dt == "Purchase Order":
                filters["owner"] = user
            # Add other DocType-specific user filters as needed

        docs = frappe.get_all(
            dt,
            filters=filters,
            fields=["name", "agent_status", "agent_status_updated", "managing_agent"]
        )

        for doc in docs:
            doc["doctype"] = dt
            results.append(doc)

    # Sort by status update time, newest first
    results.sort(key=lambda x: x.get("agent_status_updated") or "", reverse=True)

    return results

def get_agent_status_history(doctype, docname):
    """Get the status history for a document from its agent action log

    Args:
        doctype (str): The DocType of the document
        docname (str): The name of the document

    Returns:
        list: List of status changes with timestamps
    """
    doc = frappe.get_doc(doctype, docname)

    if not doc.agent_managed:
        return []

    # Check if the document has an action log
    if not hasattr(doc, 'agent_action_log'):
        # If no action log, just return the current status
        return [{
            "timestamp": doc.agent_status_updated or doc.modified,
            "status": doc.agent_status,
            "status_name": frappe.get_value("Agent Status", doc.agent_status, "status_name") if doc.agent_status else "Unknown",
            "agent": doc.managing_agent,
            "description": "Current status"
        }]

    # Get status changes from the action log
    status_history = []

    for log in doc.agent_action_log:
        if "Status changed to" in log.action_description:
            status_name = log.action_description.replace("Status changed to ", "")
            status_code = None

            # Find the status code from the status name
            statuses = frappe.get_all(
                "Agent Status",
                filters={"status_name": status_name},
                fields=["name"]
            )

            if statuses:
                status_code = statuses[0].name

            status_history.append({
                "timestamp": log.action_timestamp,
                "status": status_code,
                "status_name": status_name,
                "agent": log.agent_id,
                "description": log.action_description,
                "human_review_required": log.human_review_required
            })

    # Add the current status if it's not in the history
    if not status_history or status_history[0]["status"] != doc.agent_status:
        status_history.insert(0, {
            "timestamp": doc.agent_status_updated or doc.modified,
            "status": doc.agent_status,
            "status_name": frappe.get_value("Agent Status", doc.agent_status, "status_name") if doc.agent_status else "Unknown",
            "agent": doc.managing_agent,
            "description": "Current status"
        })

    # Sort by timestamp, newest first
    status_history.sort(key=lambda x: x["timestamp"], reverse=True)

    return status_history

def setup_custom_fields():
    """Setup custom fields for standard ERPNext DocTypes to support agent integration"""

    custom_fields = {
        "Sales Order": [
            {
                "fieldname": "agent_section",
                "label": "Agent Management",
                "fieldtype": "Section Break",
                "insert_after": "subscription_section",
                "collapsible": 1,
            },
            {
                "fieldname": "agent_managed",
                "label": "Agent Managed",
                "fieldtype": "Check",
                "insert_after": "agent_section",
                "default": "0",
            },
            {
                "fieldname": "managing_agent",
                "label": "Managing Agent",
                "fieldtype": "Link",
                "options": "Agent",
                "insert_after": "agent_managed",
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_task_id",
                "label": "Agent Task ID",
                "fieldtype": "Data",
                "insert_after": "managing_agent",
                "read_only": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_status",
                "label": "Agent Status",
                "fieldtype": "Link",
                "options": "Agent Status",
                "insert_after": "agent_task_id",
                "read_only": 1,
                "in_list_view": 1,
                "in_standard_filter": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_status_updated",
                "label": "Status Updated",
                "fieldtype": "Datetime",
                "insert_after": "agent_status",
                "read_only": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "hitl_request_id",
                "label": "HITL Request ID",
                "fieldtype": "Data",
                "insert_after": "agent_status_updated",
                "read_only": 1,
                "hidden": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_confidence",
                "label": "Agent Confidence",
                "fieldtype": "Float",
                "insert_after": "agent_task_id",
                "read_only": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_action_log",
                "label": "Agent Action Log",
                "fieldtype": "Table",
                "options": "Agent Action Log",
                "insert_after": "agent_confidence",
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_notes",
                "label": "Agent Notes",
                "fieldtype": "Small Text",
                "insert_after": "agent_action_log",
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_explanation",
                "label": "Agent Explanation",
                "fieldtype": "Long Text",
                "insert_after": "agent_notes",
                "depends_on": "eval:doc.agent_managed == 1",
            },
        ],
        "Purchase Order": [
            {
                "fieldname": "agent_section",
                "label": "Agent Management",
                "fieldtype": "Section Break",
                "insert_after": "terms_section_break",
                "collapsible": 1,
            },
            {
                "fieldname": "agent_managed",
                "label": "Agent Managed",
                "fieldtype": "Check",
                "insert_after": "agent_section",
                "default": "0",
            },
            {
                "fieldname": "managing_agent",
                "label": "Managing Agent",
                "fieldtype": "Link",
                "options": "Agent",
                "insert_after": "agent_managed",
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_task_id",
                "label": "Agent Task ID",
                "fieldtype": "Data",
                "insert_after": "managing_agent",
                "read_only": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_status",
                "label": "Agent Status",
                "fieldtype": "Link",
                "options": "Agent Status",
                "insert_after": "agent_task_id",
                "read_only": 1,
                "in_list_view": 1,
                "in_standard_filter": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_status_updated",
                "label": "Status Updated",
                "fieldtype": "Datetime",
                "insert_after": "agent_status",
                "read_only": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "hitl_request_id",
                "label": "HITL Request ID",
                "fieldtype": "Data",
                "insert_after": "agent_status_updated",
                "read_only": 1,
                "hidden": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_confidence",
                "label": "Agent Confidence",
                "fieldtype": "Float",
                "insert_after": "agent_task_id",
                "read_only": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_action_log",
                "label": "Agent Action Log",
                "fieldtype": "Table",
                "options": "Agent Action Log",
                "insert_after": "agent_confidence",
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_notes",
                "label": "Agent Notes",
                "fieldtype": "Small Text",
                "insert_after": "agent_action_log",
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_explanation",
                "label": "Agent Explanation",
                "fieldtype": "Long Text",
                "insert_after": "agent_notes",
                "depends_on": "eval:doc.agent_managed == 1",
            },
        ],
        "Journal Entry": [
            {
                "fieldname": "agent_section",
                "label": "Agent Management",
                "fieldtype": "Section Break",
                "insert_after": "reference_section",
                "collapsible": 1,
            },
            {
                "fieldname": "agent_managed",
                "label": "Agent Managed",
                "fieldtype": "Check",
                "insert_after": "agent_section",
                "default": "0",
            },
            {
                "fieldname": "managing_agent",
                "label": "Managing Agent",
                "fieldtype": "Link",
                "options": "Agent",
                "insert_after": "agent_managed",
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_task_id",
                "label": "Agent Task ID",
                "fieldtype": "Data",
                "insert_after": "managing_agent",
                "read_only": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_status",
                "label": "Agent Status",
                "fieldtype": "Link",
                "options": "Agent Status",
                "insert_after": "agent_task_id",
                "read_only": 1,
                "in_list_view": 1,
                "in_standard_filter": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_status_updated",
                "label": "Status Updated",
                "fieldtype": "Datetime",
                "insert_after": "agent_status",
                "read_only": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "hitl_request_id",
                "label": "HITL Request ID",
                "fieldtype": "Data",
                "insert_after": "agent_status_updated",
                "read_only": 1,
                "hidden": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_confidence",
                "label": "Agent Confidence",
                "fieldtype": "Float",
                "insert_after": "agent_task_id",
                "read_only": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_action_log",
                "label": "Agent Action Log",
                "fieldtype": "Table",
                "options": "Agent Action Log",
                "insert_after": "agent_confidence",
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_notes",
                "label": "Agent Notes",
                "fieldtype": "Small Text",
                "insert_after": "agent_action_log",
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_explanation",
                "label": "Agent Explanation",
                "fieldtype": "Long Text",
                "insert_after": "agent_notes",
                "depends_on": "eval:doc.agent_managed == 1",
            },
        ],
        "Item": [
            {
                "fieldname": "agent_section",
                "label": "Agent Management",
                "fieldtype": "Section Break",
                "insert_after": "hub_publishing_sb",
                "collapsible": 1,
            },
            {
                "fieldname": "agent_managed",
                "label": "Agent Managed",
                "fieldtype": "Check",
                "insert_after": "agent_section",
                "default": "0",
            },
            {
                "fieldname": "managing_agent",
                "label": "Managing Agent",
                "fieldtype": "Link",
                "options": "Agent",
                "insert_after": "agent_managed",
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_task_id",
                "label": "Agent Task ID",
                "fieldtype": "Data",
                "insert_after": "managing_agent",
                "read_only": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_status",
                "label": "Agent Status",
                "fieldtype": "Link",
                "options": "Agent Status",
                "insert_after": "agent_task_id",
                "read_only": 1,
                "in_list_view": 1,
                "in_standard_filter": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_status_updated",
                "label": "Status Updated",
                "fieldtype": "Datetime",
                "insert_after": "agent_status",
                "read_only": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "hitl_request_id",
                "label": "HITL Request ID",
                "fieldtype": "Data",
                "insert_after": "agent_status_updated",
                "read_only": 1,
                "hidden": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_confidence",
                "label": "Agent Confidence",
                "fieldtype": "Float",
                "insert_after": "agent_task_id",
                "read_only": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_action_log",
                "label": "Agent Action Log",
                "fieldtype": "Table",
                "options": "Agent Action Log",
                "insert_after": "agent_confidence",
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_notes",
                "label": "Agent Notes",
                "fieldtype": "Small Text",
                "insert_after": "agent_action_log",
                "depends_on": "eval:doc.agent_managed == 1",
            },
        ],
        "Customer": [
            {
                "fieldname": "agent_section",
                "label": "Agent Management",
                "fieldtype": "Section Break",
                "insert_after": "default_currency",
                "collapsible": 1,
            },
            {
                "fieldname": "agent_managed",
                "label": "Agent Managed",
                "fieldtype": "Check",
                "insert_after": "agent_section",
                "default": "0",
            },
            {
                "fieldname": "managing_agent",
                "label": "Managing Agent",
                "fieldtype": "Link",
                "options": "Agent",
                "insert_after": "agent_managed",
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_task_id",
                "label": "Agent Task ID",
                "fieldtype": "Data",
                "insert_after": "managing_agent",
                "read_only": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_status",
                "label": "Agent Status",
                "fieldtype": "Link",
                "options": "Agent Status",
                "insert_after": "agent_task_id",
                "read_only": 1,
                "in_list_view": 1,
                "in_standard_filter": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_status_updated",
                "label": "Status Updated",
                "fieldtype": "Datetime",
                "insert_after": "agent_status",
                "read_only": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "hitl_request_id",
                "label": "HITL Request ID",
                "fieldtype": "Data",
                "insert_after": "agent_status_updated",
                "read_only": 1,
                "hidden": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_confidence",
                "label": "Agent Confidence",
                "fieldtype": "Float",
                "insert_after": "agent_task_id",
                "read_only": 1,
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_action_log",
                "label": "Agent Action Log",
                "fieldtype": "Table",
                "options": "Agent Action Log",
                "insert_after": "agent_confidence",
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_notes",
                "label": "Agent Notes",
                "fieldtype": "Small Text",
                "insert_after": "agent_action_log",
                "depends_on": "eval:doc.agent_managed == 1",
            },
            {
                "fieldname": "agent_insights",
                "label": "Agent Insights",
                "fieldtype": "Long Text",
                "insert_after": "agent_notes",
                "depends_on": "eval:doc.agent_managed == 1",
            },
        ],
    }

    create_custom_fields(custom_fields)
    frappe.db.commit()

def create_agent_status_doctype():
    """Create the Agent Status DocType for tracking agent task status"""
    if frappe.db.exists("DocType", "Agent Status"):
        return

    doc = frappe.new_doc("DocType")
    doc.name = "Agent Status"
    doc.module = "Operations Core"
    doc.istable = 0
    doc.editable_grid = 0
    doc.track_changes = 1
    doc.naming_rule = "Expression"
    doc.autoname = "field:status_code"

    doc.fields = [
        {
            "fieldname": "status_code",
            "fieldtype": "Data",
            "label": "Status Code",
            "in_list_view": 1,
            "reqd": 1,
            "unique": 1,
        },
        {
            "fieldname": "status_name",
            "fieldtype": "Data",
            "label": "Status Name",
            "in_list_view": 1,
            "reqd": 1,
        },
        {
            "fieldname": "description",
            "fieldtype": "Small Text",
            "label": "Description",
            "in_list_view": 1,
        },
        {
            "fieldname": "color",
            "fieldtype": "Color",
            "label": "Color",
            "in_list_view": 1,
        },
        {
            "fieldname": "icon",
            "fieldtype": "Data",
            "label": "Icon",
            "description": "Font Awesome icon name (e.g., fa-check, fa-clock-o)",
        },
        {
            "fieldname": "requires_attention",
            "fieldtype": "Check",
            "label": "Requires Human Attention",
            "default": "0",
        },
        {
            "fieldname": "is_terminal_state",
            "fieldtype": "Check",
            "label": "Is Terminal State",
            "default": "0",
            "description": "Indicates if this is a final status that requires no further action",
        },
        {
            "fieldname": "sort_order",
            "fieldtype": "Int",
            "label": "Sort Order",
            "default": "0",
        },
    ]

    doc.permissions = [
        {
            "role": "System Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
        },
        {
            "role": "Operations Manager",
            "read": 1,
        },
        {
            "role": "Agent Manager",
            "read": 1,
        }
    ]

    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    # Create default statuses
    create_default_agent_statuses()

def create_default_agent_statuses():
    """Create default agent statuses"""
    default_statuses = [
        {
            "status_code": "RECEIVED",
            "status_name": "Received",
            "description": "Task has been received by the agent but processing has not yet begun",
            "color": "#d3d3d3",  # Light gray
            "icon": "fa-inbox",
            "requires_attention": 0,
            "is_terminal_state": 0,
            "sort_order": 10
        },
        {
            "status_code": "IN_PROGRESS",
            "status_name": "In Progress",
            "description": "Agent is actively working on the task",
            "color": "#1e90ff",  # Dodger blue
            "icon": "fa-spinner",
            "requires_attention": 0,
            "is_terminal_state": 0,
            "sort_order": 20
        },
        {
            "status_code": "AWAITING_HITL",
            "status_name": "Awaiting Human Input",
            "description": "Task requires human review or input to proceed",
            "color": "#ffa500",  # Orange
            "icon": "fa-user-clock",
            "requires_attention": 1,
            "is_terminal_state": 0,
            "sort_order": 30
        },
        {
            "status_code": "COMPLETED",
            "status_name": "Completed",
            "description": "Task has been successfully completed",
            "color": "#32cd32",  # Lime green
            "icon": "fa-check-circle",
            "requires_attention": 0,
            "is_terminal_state": 1,
            "sort_order": 40
        },
        {
            "status_code": "FAILED",
            "status_name": "Failed",
            "description": "Task has failed and cannot be completed",
            "color": "#ff0000",  # Red
            "icon": "fa-times-circle",
            "requires_attention": 1,
            "is_terminal_state": 1,
            "sort_order": 50
        },
        {
            "status_code": "RETRYING",
            "status_name": "Retrying",
            "description": "Task encountered an issue and is being retried",
            "color": "#ffff00",  # Yellow
            "icon": "fa-redo",
            "requires_attention": 0,
            "is_terminal_state": 0,
            "sort_order": 60
        },
        {
            "status_code": "CANCELLED",
            "status_name": "Cancelled",
            "description": "Task was cancelled before completion",
            "color": "#808080",  # Gray
            "icon": "fa-ban",
            "requires_attention": 0,
            "is_terminal_state": 1,
            "sort_order": 70
        },
        {
            "status_code": "PENDING_APPROVAL",
            "status_name": "Pending Approval",
            "description": "Task is complete but requires approval before proceeding",
            "color": "#9370db",  # Medium purple
            "icon": "fa-clipboard-check",
            "requires_attention": 1,
            "is_terminal_state": 0,
            "sort_order": 80
        }
    ]

    for status in default_statuses:
        if not frappe.db.exists("Agent Status", status["status_code"]):
            doc = frappe.new_doc("Agent Status")
            for key, value in status.items():
                doc.set(key, value)
            doc.insert(ignore_permissions=True)

    frappe.db.commit()

def create_agent_action_log_doctype():
    """Create the Agent Action Log DocType for tracking agent actions"""
    if frappe.db.exists("DocType", "Agent Action Log"):
        return

    doc = frappe.new_doc("DocType")
    doc.name = "Agent Action Log"
    doc.module = "Operations Core"
    doc.istable = 1
    doc.editable_grid = 1
    doc.track_changes = 0

    doc.fields = [
        {
            "fieldname": "action_timestamp",
            "fieldtype": "Datetime",
            "label": "Timestamp",
            "in_list_view": 1,
            "reqd": 1,
            "read_only": 1,
        },
        {
            "fieldname": "action_type",
            "fieldtype": "Select",
            "label": "Action Type",
            "options": "Create\nUpdate\nReview\nApprove\nReject\nAnalyze\nOther",
            "in_list_view": 1,
            "reqd": 1,
        },
        {
            "fieldname": "action_description",
            "fieldtype": "Small Text",
            "label": "Description",
            "in_list_view": 1,
            "reqd": 1,
        },
        {
            "fieldname": "agent_id",
            "fieldtype": "Link",
            "options": "Agent",
            "label": "Agent",
            "in_list_view": 1,
            "reqd": 1,
        },
        {
            "fieldname": "task_id",
            "fieldtype": "Data",
            "label": "Task ID",
            "in_list_view": 1,
        },
        {
            "fieldname": "confidence",
            "fieldtype": "Float",
            "label": "Confidence",
            "in_list_view": 1,
        },
        {
            "fieldname": "fields_modified",
            "fieldtype": "Small Text",
            "label": "Fields Modified",
        },
        {
            "fieldname": "human_review_required",
            "fieldtype": "Check",
            "label": "Human Review Required",
            "default": "0",
        },
        {
            "fieldname": "human_reviewer",
            "fieldtype": "Link",
            "options": "User",
            "label": "Human Reviewer",
            "depends_on": "eval:doc.human_review_required == 1",
        },
        {
            "fieldname": "review_status",
            "fieldtype": "Select",
            "label": "Review Status",
            "options": "Pending\nApproved\nRejected\nModified",
            "depends_on": "eval:doc.human_review_required == 1",
        },
        {
            "fieldname": "review_notes",
            "fieldtype": "Small Text",
            "label": "Review Notes",
            "depends_on": "eval:doc.human_review_required == 1",
        },
    ]

    doc.permissions = [
        {
            "role": "System Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
        }
    ]

    doc.insert(ignore_permissions=True)
    frappe.db.commit()

def setup():
    """Setup all custom fields and DocTypes"""
    create_agent_action_log_doctype()
    create_agent_status_doctype()
    setup_custom_fields()