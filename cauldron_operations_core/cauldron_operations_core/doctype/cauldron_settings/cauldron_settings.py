import frappe
from frappe.model.document import Document

class CauldronSettings(Document):
    """Settings for Cauldron Operations Core"""

    def validate(self):
        """Validate settings"""
        # Validate AetherCore API endpoint
        if self.enable_hitl_integration and not self.aethercore_api_endpoint:
            frappe.throw("AetherCore API Endpoint is required when HITL Integration is enabled")

        # Validate default agent confidence
        if self.default_agent_confidence < 0 or self.default_agent_confidence > 1:
            frappe.throw("Default Agent Confidence must be between 0 and 1")

        # Validate webhook secret
        if self.enable_hitl_integration and not self.hitl_webhook_secret:
            frappe.msgprint("It is recommended to set a HITL Webhook Secret for security", indicator="yellow")

def setup_field_permissions():
    """Setup field-level permissions for sensitive fields in Cauldron Settings

    This function sets up field-level permissions for sensitive fields in the Cauldron Settings DocType.
    Fields like API keys, webhook secrets, and other sensitive configuration are protected with
    permlevel=1 to ensure only authorized roles can modify them.
    """
    # Define sensitive fields that should have permlevel=1
    sensitive_fields = [
        "hitl_webhook_secret",
        "aethercore_api_endpoint",
    ]

    # Get the DocType
    if not frappe.db.exists("DocType", "Cauldron Settings"):
        return

    doctype = frappe.get_doc("DocType", "Cauldron Settings")

    # Update field permissions
    for field in doctype.fields:
        if field.fieldname in sensitive_fields:
            field.permlevel = 1

    # Save the DocType
    doctype.save(ignore_permissions=True)
    frappe.db.commit()

    frappe.clear_cache(doctype="Cauldron Settings")
