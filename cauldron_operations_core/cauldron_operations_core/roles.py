import frappe

def create_cauldron_roles():
    """Create custom roles for Cauldron system"""
    
    # Define roles to create
    roles = [
        {
            "role_name": "CauldronAgentRole",
            "desk_access": 1,
            "two_factor_auth": 0,
            "restrict_to_domain": "",
            "desk_access": 1,
            "disabled": 0,
            "is_custom": 1,
            "description": "Role for AI Agents to perform operations within the system"
        },
        {
            "role_name": "CauldronOperatorRole",
            "desk_access": 1,
            "two_factor_auth": 1,
            "restrict_to_domain": "",
            "desk_access": 1,
            "disabled": 0,
            "is_custom": 1,
            "description": "Role for human operators who oversee and approve agent actions"
        },
        {
            "role_name": "CauldronWardenRole",
            "desk_access": 1,
            "two_factor_auth": 1,
            "restrict_to_domain": "",
            "desk_access": 1,
            "disabled": 0,
            "is_custom": 1,
            "description": "Role for Wardens who have high-level oversight of the Cauldron system"
        },
        {
            "role_name": "CauldronAnalystRole",
            "desk_access": 1,
            "two_factor_auth": 1,
            "restrict_to_domain": "",
            "desk_access": 1,
            "disabled": 0,
            "is_custom": 1,
            "description": "Role for analysts who work with data and insights but don't approve operations"
        },
        {
            "role_name": "CauldronAuditorRole",
            "desk_access": 1,
            "two_factor_auth": 1,
            "restrict_to_domain": "",
            "desk_access": 1,
            "disabled": 0,
            "is_custom": 1,
            "description": "Role for auditors who review system operations and agent actions"
        },
        {
            "role_name": "Knowledge Manager",
            "desk_access": 1,
            "two_factor_auth": 1,
            "restrict_to_domain": "",
            "desk_access": 1,
            "disabled": 0,
            "is_custom": 1,
            "description": "Role for managing knowledge base entries and categories"
        },
        {
            "role_name": "Knowledge Contributor",
            "desk_access": 1,
            "two_factor_auth": 1,
            "restrict_to_domain": "",
            "desk_access": 1,
            "disabled": 0,
            "is_custom": 1,
            "description": "Role for creating and editing knowledge base entries"
        },
        {
            "role_name": "Knowledge User",
            "desk_access": 1,
            "two_factor_auth": 0,
            "restrict_to_domain": "",
            "desk_access": 1,
            "disabled": 0,
            "is_custom": 1,
            "description": "Role for viewing and using knowledge base entries"
        },
    ]
    
    # Create roles if they don't exist
    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role = frappe.new_doc("Role")
            for key, value in role_data.items():
                setattr(role, key, value)
            role.insert(ignore_permissions=True)
    
    frappe.db.commit()

def setup_role_permissions():
    """Setup permissions for custom roles"""
    
    # Define permissions for standard DocTypes
    permissions = {
        "Sales Order": [
            {
                "role": "CauldronAgentRole",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 1,
                "share": 0,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
            {
                "role": "CauldronOperatorRole",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "submit": 1,
                "cancel": 1,
                "amend": 1,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
            {
                "role": "CauldronWardenRole",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "submit": 1,
                "cancel": 1,
                "amend": 1,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
            {
                "role": "CauldronAnalystRole",
                "permlevel": 0,
                "read": 1,
                "write": 0,
                "create": 0,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 1,
                "share": 0,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
            {
                "role": "CauldronAuditorRole",
                "permlevel": 0,
                "read": 1,
                "write": 0,
                "create": 0,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 1,
                "share": 0,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
        ],
        "Purchase Order": [
            {
                "role": "CauldronAgentRole",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 1,
                "share": 0,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
            {
                "role": "CauldronOperatorRole",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "submit": 1,
                "cancel": 1,
                "amend": 1,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
            {
                "role": "CauldronWardenRole",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "submit": 1,
                "cancel": 1,
                "amend": 1,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
            {
                "role": "CauldronAnalystRole",
                "permlevel": 0,
                "read": 1,
                "write": 0,
                "create": 0,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 1,
                "share": 0,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
            {
                "role": "CauldronAuditorRole",
                "permlevel": 0,
                "read": 1,
                "write": 0,
                "create": 0,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 1,
                "share": 0,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
        ],
        "Journal Entry": [
            {
                "role": "CauldronAgentRole",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 1,
                "share": 0,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
            {
                "role": "CauldronOperatorRole",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "submit": 1,
                "cancel": 1,
                "amend": 1,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
        ],
        "Item": [
            {
                "role": "CauldronAgentRole",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 1,
                "share": 0,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
        ],
        "Customer": [
            {
                "role": "CauldronAgentRole",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 1,
                "share": 0,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
        ],
        "Knowledge Base Entry": [
            {
                "role": "CauldronAgentRole",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 1,
                "share": 0,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
            {
                "role": "Knowledge Manager",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
            {
                "role": "Knowledge Contributor",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 1,
                "share": 1,
                "print": 1,
                "email": 1,
                "if_owner": 1,
            },
            {
                "role": "Knowledge User",
                "permlevel": 0,
                "read": 1,
                "write": 0,
                "create": 0,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 1,
                "share": 0,
                "print": 1,
                "email": 1,
                "if_owner": 0,
            },
        ],
    }
    
    # Apply permissions
    for doctype, perms in permissions.items():
        if frappe.db.exists("DocType", doctype):
            for perm in perms:
                # Check if permission already exists
                existing_perm = frappe.db.exists(
                    "Custom DocPerm",
                    {
                        "parent": doctype,
                        "role": perm["role"],
                        "permlevel": perm["permlevel"],
                    },
                )
                
                if existing_perm:
                    # Update existing permission
                    doc = frappe.get_doc("Custom DocPerm", existing_perm)
                    for key, value in perm.items():
                        setattr(doc, key, value)
                    doc.save(ignore_permissions=True)
                else:
                    # Create new permission
                    doc = frappe.new_doc("Custom DocPerm")
                    doc.parent = doctype
                    for key, value in perm.items():
                        setattr(doc, key, value)
                    doc.parenttype = "DocType"
                    doc.parentfield = "permissions"
                    doc.insert(ignore_permissions=True)
    
    frappe.db.commit()

def setup():
    """Setup all roles and permissions"""
    create_cauldron_roles()
    setup_role_permissions()