import frappe
import json
from frappe.utils import cint
from cauldron_operations_core.workflows.workflow_handlers import handle_hitl_response

@frappe.whitelist(allow_guest=True)
def hitl_response_webhook():
    """Webhook endpoint for AetherCore HITL responses
    
    This endpoint receives HITL responses from AetherCore and processes them.
    It expects a JSON payload with the following structure:
    {
        "hitl_request_id": "uuid-string",
        "response": "approve|reject",
        "response_details": {
            "reason": "Optional reason for rejection",
            "notes": "Optional notes from the human reviewer"
        },
        "human_id": "user-id",
        "timestamp": "ISO-8601 timestamp"
    }
    
    Returns:
        dict: A response indicating success or failure
    """
    # Verify webhook secret if configured
    webhook_secret = frappe.get_value("Cauldron Settings", None, "hitl_webhook_secret")
    if webhook_secret:
        if frappe.request.headers.get("X-Webhook-Secret") != webhook_secret:
            frappe.throw("Invalid webhook secret", frappe.AuthenticationError)
    
    # Parse request data
    try:
        if frappe.request.data:
            data = json.loads(frappe.request.data)
        else:
            data = frappe.request.form
            
        # Validate required fields
        if not data.get("hitl_request_id"):
            frappe.throw("Missing hitl_request_id")
            
        if not data.get("response"):
            frappe.throw("Missing response")
            
        # Process the HITL response
        success = handle_hitl_response(
            data.get("hitl_request_id"),
            data.get("response"),
            data.get("response_details")
        )
        
        if success:
            return {"success": True, "message": "HITL response processed successfully"}
        else:
            return {"success": False, "message": "Failed to process HITL response"}
            
    except Exception as e:
        frappe.log_error(f"Error processing HITL webhook: {str(e)}", "HITL Webhook Error")
        return {"success": False, "message": str(e)}
