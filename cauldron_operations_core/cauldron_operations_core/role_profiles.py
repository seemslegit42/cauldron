import frappe
from frappe import _

def create_role_profiles():
    """Create role profiles for different user types
    
    Role profiles make it easier to assign multiple roles to users based on their job function.
    This function creates the following role profiles:
    - Cauldron Operator: For human operators who oversee agent actions
    - Cauldron Warden: For administrators with high-level oversight
    - Cauldron Agent Manager: For users who manage agent configurations
    - Cauldron Analyst: For users who analyze data but don't approve operations
    - Cauldron Auditor: For users who audit system operations
    - Knowledge Manager: For users who manage the knowledge base
    """
    # Define role profiles
    role_profiles = [
        {
            "role_profile": "Cauldron Operator",
            "roles": [
                "CauldronOperatorRole",
                "Knowledge User"
            ],
            "description": _("Role profile for human operators who oversee and approve agent actions")
        },
        {
            "role_profile": "Cauldron Warden",
            "roles": [
                "CauldronWardenRole",
                "CauldronOperatorRole",
                "CauldronAgentManagerRole",
                "CauldronWorkflowDesignerRole",
                "Knowledge Manager"
            ],
            "description": _("Role profile for administrators with high-level oversight of the Cauldron system")
        },
        {
            "role_profile": "Cauldron Agent Manager",
            "roles": [
                "CauldronAgentManagerRole",
                "CauldronOperatorRole",
                "Knowledge Contributor"
            ],
            "description": _("Role profile for users who manage agent configurations and monitor performance")
        },
        {
            "role_profile": "Cauldron Analyst",
            "roles": [
                "CauldronAnalystRole",
                "Knowledge User"
            ],
            "description": _("Role profile for users who analyze data but don't approve operations")
        },
        {
            "role_profile": "Cauldron Auditor",
            "roles": [
                "CauldronAuditorRole",
                "Knowledge User"
            ],
            "description": _("Role profile for users who audit system operations and agent actions")
        },
        {
            "role_profile": "Knowledge Manager",
            "roles": [
                "Knowledge Manager",
                "Knowledge Contributor",
                "Knowledge User"
            ],
            "description": _("Role profile for users who manage the knowledge base")
        }
    ]
    
    # Create role profiles
    for profile in role_profiles:
        # Check if role profile already exists
        if not frappe.db.exists("Role Profile", profile["role_profile"]):
            # Create role profile
            doc = frappe.new_doc("Role Profile")
            doc.role_profile = profile["role_profile"]
            
            # Add roles
            for role in profile["roles"]:
                doc.append("roles", {"role": role})
                
            # Set description
            doc.description = profile["description"]
            
            # Save role profile
            doc.insert(ignore_permissions=True)
    
    frappe.db.commit()

def setup():
    """Setup role profiles"""
    create_role_profiles()
