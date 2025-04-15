import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

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
    setup_custom_fields()