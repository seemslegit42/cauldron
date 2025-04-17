import frappe
from frappe.workflow.doctype.workflow.workflow import Workflow

def create_order_approval_workflow():
    """Create the Order Approval Workflow with agent integration"""

    # Check if workflow already exists
    if frappe.db.exists("Workflow", "Order Approval Workflow"):
        return

    # Create workflow states
    states = [
        {
            "state": "Draft",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronOperatorRole",
        },
        {
            "state": "Pending Agent Review",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronAgentRole",
        },
        {
            "state": "Agent Approved",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronAgentRole",
        },
        {
            "state": "Agent Rejected",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronAgentRole",
        },
        {
            "state": "Pending Human Review",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronOperatorRole",
        },
        {
            "state": "Approved",
            "doc_status": 1,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronOperatorRole",
        },
        {
            "state": "Rejected",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronOperatorRole",
        },
        {
            "state": "Cancelled",
            "doc_status": 2,
            "is_active_workflow_state": 0,
            "allow_edit": "CauldronOperatorRole",
        },
    ]

    # Create workflow transitions
    transitions = [
        {
            "state": "Draft",
            "action": "Submit for Agent Review",
            "next_state": "Pending Agent Review",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
            "condition": "doc.docstatus == 0",
        },
        {
            "state": "Pending Agent Review",
            "action": "Agent Approve",
            "next_state": "Agent Approved",
            "allowed": "CauldronAgentRole",
            "allow_self_approval": 1,
            "condition": "doc.agent_managed == 1",
        },
        {
            "state": "Pending Agent Review",
            "action": "Agent Reject",
            "next_state": "Agent Rejected",
            "allowed": "CauldronAgentRole",
            "allow_self_approval": 1,
            "condition": "doc.agent_managed == 1",
        },
        {
            "state": "Agent Approved",
            "action": "Submit for Human Review",
            "next_state": "Pending Human Review",
            "allowed": "CauldronAgentRole",
            "allow_self_approval": 1,
            "condition": "doc.agent_confidence < 0.95",
        },
        {
            "state": "Agent Approved",
            "action": "Auto Approve",
            "next_state": "Approved",
            "allowed": "CauldronAgentRole",
            "allow_self_approval": 1,
            "condition": "doc.agent_confidence >= 0.95 and doc.grand_total <= 1000",
        },
        {
            "state": "Agent Rejected",
            "action": "Return to Draft",
            "next_state": "Draft",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
        },
        {
            "state": "Pending Human Review",
            "action": "Human Approve",
            "next_state": "Approved",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
        },
        {
            "state": "Pending Human Review",
            "action": "Human Reject",
            "next_state": "Rejected",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
        },
        {
            "state": "Approved",
            "action": "Cancel",
            "next_state": "Cancelled",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
            "condition": "doc.docstatus == 1",
        },
        {
            "state": "Rejected",
            "action": "Return to Draft",
            "next_state": "Draft",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
        },
    ]

    # Create the workflow
    workflow = frappe.new_doc("Workflow")
    workflow.name = "Order Approval Workflow"
    workflow.document_type = "Sales Order"
    workflow.workflow_state_field = "workflow_state"
    workflow.is_active = 1
    workflow.send_email_alert = 1

    # Add states
    for state in states:
        workflow.append("states", {
            "state": state["state"],
            "doc_status": state["doc_status"],
            "is_active_workflow_state": state["is_active_workflow_state"],
            "allow_edit": state["allow_edit"],
        })

    # Add transitions
    for transition in transitions:
        workflow.append("transitions", {
            "state": transition["state"],
            "action": transition["action"],
            "next_state": transition["next_state"],
            "allowed": transition["allowed"],
            "allow_self_approval": transition["allow_self_approval"],
            "condition": transition.get("condition", ""),
        })

    workflow.insert(ignore_permissions=True)
    frappe.db.commit()

def create_purchase_order_approval_workflow():
    """Create the Purchase Order Approval Workflow with agent integration"""

    # Check if workflow already exists
    if frappe.db.exists("Workflow", "Purchase Order Approval Workflow"):
        return

    # Create workflow states
    states = [
        {
            "state": "Draft",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronOperatorRole",
        },
        {
            "state": "Pending Agent Review",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronAgentRole",
        },
        {
            "state": "Agent Approved",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronAgentRole",
        },
        {
            "state": "Agent Rejected",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronAgentRole",
        },
        {
            "state": "Pending Human Review",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronOperatorRole",
        },
        {
            "state": "Approved",
            "doc_status": 1,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronOperatorRole",
        },
        {
            "state": "Rejected",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronOperatorRole",
        },
        {
            "state": "Cancelled",
            "doc_status": 2,
            "is_active_workflow_state": 0,
            "allow_edit": "CauldronOperatorRole",
        },
    ]

    # Create workflow transitions
    transitions = [
        {
            "state": "Draft",
            "action": "Submit for Agent Review",
            "next_state": "Pending Agent Review",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
            "condition": "doc.docstatus == 0",
        },
        {
            "state": "Draft",
            "action": "Auto-Submit for Agent Review",
            "next_state": "Pending Agent Review",
            "allowed": "CauldronAgentRole",
            "allow_self_approval": 1,
            "condition": "doc.docstatus == 0 and doc.agent_managed == 1",
        },
        {
            "state": "Pending Agent Review",
            "action": "Agent Approve",
            "next_state": "Agent Approved",
            "allowed": "CauldronAgentRole",
            "allow_self_approval": 1,
            "condition": "doc.agent_managed == 1",
        },
        {
            "state": "Pending Agent Review",
            "action": "Agent Reject",
            "next_state": "Agent Rejected",
            "allowed": "CauldronAgentRole",
            "allow_self_approval": 1,
            "condition": "doc.agent_managed == 1",
        },
        {
            "state": "Agent Approved",
            "action": "Submit for Human Review",
            "next_state": "Pending Human Review",
            "allowed": "CauldronAgentRole",
            "allow_self_approval": 1,
            "condition": "doc.agent_confidence < 0.95 or doc.grand_total > 5000",
        },
        {
            "state": "Agent Approved",
            "action": "Auto Approve",
            "next_state": "Approved",
            "allowed": "CauldronAgentRole",
            "allow_self_approval": 1,
            "condition": "doc.agent_confidence >= 0.95 and doc.grand_total <= 5000",
        },
        {
            "state": "Agent Rejected",
            "action": "Return to Draft",
            "next_state": "Draft",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
        },
        {
            "state": "Pending Human Review",
            "action": "Human Approve",
            "next_state": "Approved",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
        },
        {
            "state": "Pending Human Review",
            "action": "Human Reject",
            "next_state": "Rejected",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
        },
        {
            "state": "Approved",
            "action": "Cancel",
            "next_state": "Cancelled",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
            "condition": "doc.docstatus == 1",
        },
        {
            "state": "Rejected",
            "action": "Return to Draft",
            "next_state": "Draft",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
        },
    ]

    # Create the workflow
    workflow = frappe.new_doc("Workflow")
    workflow.name = "Purchase Order Approval Workflow"
    workflow.document_type = "Purchase Order"
    workflow.workflow_state_field = "workflow_state"
    workflow.is_active = 1
    workflow.send_email_alert = 1

    # Add states
    for state in states:
        workflow.append("states", {
            "state": state["state"],
            "doc_status": state["doc_status"],
            "is_active_workflow_state": state["is_active_workflow_state"],
            "allow_edit": state["allow_edit"],
        })

    # Add transitions
    for transition in transitions:
        workflow.append("transitions", {
            "state": transition["state"],
            "action": transition["action"],
            "next_state": transition["next_state"],
            "allowed": transition["allowed"],
            "allow_self_approval": transition["allow_self_approval"],
            "condition": transition.get("condition", ""),
        })

    workflow.insert(ignore_permissions=True)
    frappe.db.commit()

def create_journal_entry_approval_workflow():
    """Create the Journal Entry Approval Workflow with agent integration"""

    # Check if workflow already exists
    if frappe.db.exists("Workflow", "Journal Entry Approval Workflow"):
        return

    # Create workflow states
    states = [
        {
            "state": "Draft",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronOperatorRole",
        },
        {
            "state": "Pending Agent Review",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronAgentRole",
        },
        {
            "state": "Agent Approved",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronAgentRole",
        },
        {
            "state": "Agent Rejected",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronAgentRole",
        },
        {
            "state": "Pending Human Review",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronOperatorRole",
        },
        {
            "state": "Approved",
            "doc_status": 1,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronOperatorRole",
        },
        {
            "state": "Rejected",
            "doc_status": 0,
            "is_active_workflow_state": 1,
            "allow_edit": "CauldronOperatorRole",
        },
        {
            "state": "Cancelled",
            "doc_status": 2,
            "is_active_workflow_state": 0,
            "allow_edit": "CauldronOperatorRole",
        },
    ]

    # Create workflow transitions
    transitions = [
        {
            "state": "Draft",
            "action": "Submit for Agent Review",
            "next_state": "Pending Agent Review",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
            "condition": "doc.docstatus == 0",
        },
        {
            "state": "Draft",
            "action": "Auto-Submit for Agent Review",
            "next_state": "Pending Agent Review",
            "allowed": "CauldronAgentRole",
            "allow_self_approval": 1,
            "condition": "doc.docstatus == 0 and doc.agent_managed == 1",
        },
        {
            "state": "Pending Agent Review",
            "action": "Agent Approve",
            "next_state": "Agent Approved",
            "allowed": "CauldronAgentRole",
            "allow_self_approval": 1,
            "condition": "doc.agent_managed == 1",
        },
        {
            "state": "Pending Agent Review",
            "action": "Agent Reject",
            "next_state": "Agent Rejected",
            "allowed": "CauldronAgentRole",
            "allow_self_approval": 1,
            "condition": "doc.agent_managed == 1",
        },
        {
            "state": "Agent Approved",
            "action": "Submit for Human Review",
            "next_state": "Pending Human Review",
            "allowed": "CauldronAgentRole",
            "allow_self_approval": 1,
            "condition": "doc.agent_confidence < 0.95 or doc.total_debit > 10000",
        },
        {
            "state": "Agent Approved",
            "action": "Auto Approve",
            "next_state": "Approved",
            "allowed": "CauldronAgentRole",
            "allow_self_approval": 1,
            "condition": "doc.agent_confidence >= 0.95 and doc.total_debit <= 10000",
        },
        {
            "state": "Agent Rejected",
            "action": "Return to Draft",
            "next_state": "Draft",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
        },
        {
            "state": "Pending Human Review",
            "action": "Human Approve",
            "next_state": "Approved",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
        },
        {
            "state": "Pending Human Review",
            "action": "Human Reject",
            "next_state": "Rejected",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
        },
        {
            "state": "Approved",
            "action": "Cancel",
            "next_state": "Cancelled",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
            "condition": "doc.docstatus == 1",
        },
        {
            "state": "Rejected",
            "action": "Return to Draft",
            "next_state": "Draft",
            "allowed": "CauldronOperatorRole",
            "allow_self_approval": 1,
        },
    ]

    # Create the workflow
    workflow = frappe.new_doc("Workflow")
    workflow.name = "Journal Entry Approval Workflow"
    workflow.document_type = "Journal Entry"
    workflow.workflow_state_field = "workflow_state"
    workflow.is_active = 1
    workflow.send_email_alert = 1

    # Add states
    for state in states:
        workflow.append("states", {
            "state": state["state"],
            "doc_status": state["doc_status"],
            "is_active_workflow_state": state["is_active_workflow_state"],
            "allow_edit": state["allow_edit"],
        })

    # Add transitions
    for transition in transitions:
        workflow.append("transitions", {
            "state": transition["state"],
            "action": transition["action"],
            "next_state": transition["next_state"],
            "allowed": transition["allowed"],
            "allow_self_approval": transition["allow_self_approval"],
            "condition": transition.get("condition", ""),
        })

    workflow.insert(ignore_permissions=True)
    frappe.db.commit()

def setup_workflows():
    """Setup all workflows"""
    create_order_approval_workflow()
    create_purchase_order_approval_workflow()
    create_journal_entry_approval_workflow()