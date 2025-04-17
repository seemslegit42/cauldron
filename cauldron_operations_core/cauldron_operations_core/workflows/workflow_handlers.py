import frappe
import json
import requests
from datetime import datetime
from cauldron_operations_core.custom_fields import update_agent_status

# AetherCore API endpoint for HITL requests
AETHERCORE_API_ENDPOINT = frappe.get_value("Cauldron Settings", None, "aethercore_api_endpoint") or "http://aethercore:8000/api/v1"

def handle_workflow_transition(doc, method=None):
    """Handle workflow transitions and create HITL requests when needed
    
    This function is called when a document's workflow state changes.
    It updates the agent status field to match the workflow state and
    creates HITL requests when human review is needed.
    
    Args:
        doc: The document that triggered the workflow transition
        method: The method that triggered the workflow transition (not used)
    """
    # Skip if document doesn't have workflow state
    if not hasattr(doc, 'workflow_state'):
        return
    
    # Skip if document is not agent managed
    if not hasattr(doc, 'agent_managed') or not doc.agent_managed:
        return
    
    # Map workflow states to agent statuses
    workflow_to_status_map = {
        "Draft": "RECEIVED",
        "Pending Agent Review": "IN_PROGRESS",
        "Agent Approved": "COMPLETED",
        "Agent Rejected": "FAILED",
        "Pending Human Review": "AWAITING_HITL",
        "Approved": "COMPLETED",
        "Rejected": "FAILED",
        "Cancelled": "CANCELLED"
    }
    
    # Update agent status based on workflow state
    if doc.workflow_state in workflow_to_status_map:
        update_agent_status(
            doc.doctype, 
            doc.name, 
            workflow_to_status_map[doc.workflow_state],
            agent_id=doc.managing_agent,
            task_id=doc.agent_task_id
        )
    
    # Create HITL request if workflow state is "Pending Human Review"
    if doc.workflow_state == "Pending Human Review":
        create_hitl_request_for_document(doc)

def create_hitl_request_for_document(doc):
    """Create a HITL request for a document
    
    Args:
        doc: The document that needs human review
    
    Returns:
        dict: The HITL request response or None if request failed
    """
    # Skip if document doesn't have required fields
    if not hasattr(doc, 'agent_task_id') or not doc.agent_task_id:
        frappe.log_error(
            f"Cannot create HITL request for {doc.doctype} {doc.name}: Missing agent_task_id",
            "HITL Request Error"
        )
        return None
    
    # Prepare request data
    request_data = {
        "task_id": doc.agent_task_id,
        "request_type": "approval",
        "request_description": f"Please review {doc.doctype} {doc.name} for approval",
        "options": [
            {
                "id": "approve",
                "label": "Approve",
                "description": "Approve the document"
            },
            {
                "id": "reject",
                "label": "Reject",
                "description": "Reject the document"
            }
        ],
        "timeout_seconds": 86400,  # 24 hours
        "urgency": "normal"
    }
    
    # Add document-specific details
    if doc.doctype == "Sales Order":
        request_data["request_description"] = f"Please review Sales Order {doc.name} for customer {doc.customer_name} with total amount {doc.grand_total}"
        request_data["document_details"] = {
            "doctype": doc.doctype,
            "name": doc.name,
            "customer": doc.customer_name,
            "grand_total": doc.grand_total,
            "delivery_date": str(doc.delivery_date) if hasattr(doc, 'delivery_date') else None
        }
    elif doc.doctype == "Purchase Order":
        request_data["request_description"] = f"Please review Purchase Order {doc.name} for supplier {doc.supplier_name} with total amount {doc.grand_total}"
        request_data["document_details"] = {
            "doctype": doc.doctype,
            "name": doc.name,
            "supplier": doc.supplier_name,
            "grand_total": doc.grand_total,
            "schedule_date": str(doc.schedule_date) if hasattr(doc, 'schedule_date') else None
        }
    elif doc.doctype == "Journal Entry":
        request_data["request_description"] = f"Please review Journal Entry {doc.name} with total debit amount {doc.total_debit}"
        request_data["document_details"] = {
            "doctype": doc.doctype,
            "name": doc.name,
            "posting_date": str(doc.posting_date),
            "total_debit": doc.total_debit,
            "total_credit": doc.total_credit,
            "user_remark": doc.user_remark if hasattr(doc, 'user_remark') else None
        }
    
    # Call AetherCore API to create HITL request
    try:
        response = requests.post(
            f"{AETHERCORE_API_ENDPOINT}/hitl/requests",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            hitl_request = response.json()
            
            # Log the HITL request creation
            frappe.log_error(
                f"Created HITL request for {doc.doctype} {doc.name}: {hitl_request['id']}",
                "HITL Request Created"
            )
            
            # Store HITL request ID in document
            doc.hitl_request_id = hitl_request['id']
            doc.save(ignore_permissions=True)
            
            return hitl_request
        else:
            frappe.log_error(
                f"Failed to create HITL request for {doc.doctype} {doc.name}: {response.text}",
                "HITL Request Error"
            )
            return None
            
    except Exception as e:
        frappe.log_error(
            f"Error creating HITL request for {doc.doctype} {doc.name}: {str(e)}",
            "HITL Request Error"
        )
        return None

def handle_hitl_response(hitl_request_id, response, response_details=None):
    """Handle HITL response from AetherCore
    
    This function is called when a HITL request receives a response.
    It updates the document's workflow state based on the response.
    
    Args:
        hitl_request_id: The ID of the HITL request
        response: The response from the human (approve/reject)
        response_details: Additional details about the response
    
    Returns:
        bool: True if the response was handled successfully, False otherwise
    """
    # Find documents with this HITL request ID
    docs = frappe.get_all(
        "Sales Order",
        filters={"hitl_request_id": hitl_request_id},
        fields=["name"]
    )
    
    if not docs:
        docs = frappe.get_all(
            "Purchase Order",
            filters={"hitl_request_id": hitl_request_id},
            fields=["name"]
        )
    
    if not docs:
        docs = frappe.get_all(
            "Journal Entry",
            filters={"hitl_request_id": hitl_request_id},
            fields=["name"]
        )
    
    if not docs:
        frappe.log_error(
            f"No document found with HITL request ID {hitl_request_id}",
            "HITL Response Error"
        )
        return False
    
    # Get the document
    doc_name = docs[0].name
    doctype = None
    
    # Determine the doctype
    for dt in ["Sales Order", "Purchase Order", "Journal Entry"]:
        if frappe.db.exists(dt, doc_name):
            doctype = dt
            break
    
    if not doctype:
        frappe.log_error(
            f"Could not determine doctype for document {doc_name} with HITL request ID {hitl_request_id}",
            "HITL Response Error"
        )
        return False
    
    # Get the document
    doc = frappe.get_doc(doctype, doc_name)
    
    # Update workflow state based on response
    if response == "approve":
        # Apply the "Human Approve" action
        workflow = frappe.get_doc("Workflow", {"document_type": doctype})
        transitions = [t for t in workflow.transitions if t.state == "Pending Human Review" and t.action == "Human Approve"]
        
        if transitions:
            doc.workflow_state = transitions[0].next_state
            doc.add_comment("Workflow", f"Human approved via HITL request {hitl_request_id}")
            
            # If the next state is "Approved", submit the document
            if doc.workflow_state == "Approved" and doc.docstatus == 0:
                doc.submit()
            else:
                doc.save(ignore_permissions=True)
                
            # Update agent status
            update_agent_status(
                doctype, 
                doc_name, 
                "COMPLETED",
                agent_id=doc.managing_agent,
                task_id=doc.agent_task_id
            )
            
            return True
    
    elif response == "reject":
        # Apply the "Human Reject" action
        workflow = frappe.get_doc("Workflow", {"document_type": doctype})
        transitions = [t for t in workflow.transitions if t.state == "Pending Human Review" and t.action == "Human Reject"]
        
        if transitions:
            doc.workflow_state = transitions[0].next_state
            
            # Add rejection reason if provided
            rejection_reason = "No reason provided"
            if response_details and "reason" in response_details:
                rejection_reason = response_details["reason"]
                
            doc.add_comment("Workflow", f"Human rejected via HITL request {hitl_request_id}. Reason: {rejection_reason}")
            doc.save(ignore_permissions=True)
            
            # Update agent status
            update_agent_status(
                doctype, 
                doc_name, 
                "FAILED",
                agent_id=doc.managing_agent,
                task_id=doc.agent_task_id
            )
            
            return True
    
    frappe.log_error(
        f"Invalid response '{response}' for HITL request {hitl_request_id}",
        "HITL Response Error"
    )
    return False
