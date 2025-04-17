import frappe
from frappe import _

def create_cauldron_roles():
    """Create custom roles for Cauldron system based on the principle of least privilege

    This function creates the following roles:
    - CauldronAgentRole: Limited role for AI agents to perform operations
    - CauldronOperatorRole: Role for human operators who oversee agent actions
    - CauldronWardenRole: High-level oversight role with broader permissions
    - CauldronAnalystRole: Read-only access to data for analysis
    - CauldronAuditorRole: Read-only access for auditing purposes
    - Knowledge roles: For managing the knowledge base
    """

    # Define roles to create based on the principle of least privilege
    roles = [
        {
            "role_name": "CauldronAgentRole",
            "desk_access": 1,
            "two_factor_auth": 0,
            "restrict_to_domain": "",
            "disabled": 0,
            "is_custom": 1,
            "description": _("Role for AI Agents to perform operations within the system. Limited to create and update operations without delete or submit permissions.")
        },
        {
            "role_name": "CauldronOperatorRole",
            "desk_access": 1,
            "two_factor_auth": 1,
            "restrict_to_domain": "",
            "disabled": 0,
            "is_custom": 1,
            "description": _("Role for human operators who oversee and approve agent actions. Can submit, approve, and reject documents but with limited delete permissions.")
        },
        {
            "role_name": "CauldronWardenRole",
            "desk_access": 1,
            "two_factor_auth": 1,
            "restrict_to_domain": "",
            "disabled": 0,
            "is_custom": 1,
            "description": _("Role for Wardens who have high-level oversight of the Cauldron system. Has broader permissions including configuration management.")
        },
        {
            "role_name": "CauldronAnalystRole",
            "desk_access": 1,
            "two_factor_auth": 1,
            "restrict_to_domain": "",
            "disabled": 0,
            "is_custom": 1,
            "description": _("Role for analysts who work with data and insights. Read-only access to operational data with export and report capabilities.")
        },
        {
            "role_name": "CauldronAuditorRole",
            "desk_access": 1,
            "two_factor_auth": 1,
            "restrict_to_domain": "",
            "disabled": 0,
            "is_custom": 1,
            "description": _("Role for auditors who review system operations and agent actions. Read-only access with audit log visibility.")
        },
        {
            "role_name": "CauldronAgentManagerRole",
            "desk_access": 1,
            "two_factor_auth": 1,
            "restrict_to_domain": "",
            "disabled": 0,
            "is_custom": 1,
            "description": _("Role for managing agent configurations, tasks, and monitoring agent performance.")
        },
        {
            "role_name": "CauldronWorkflowDesignerRole",
            "desk_access": 1,
            "two_factor_auth": 1,
            "restrict_to_domain": "",
            "disabled": 0,
            "is_custom": 1,
            "description": _("Role for designing and configuring workflows, states, and transitions.")
        },
        {
            "role_name": "Knowledge Manager",
            "desk_access": 1,
            "two_factor_auth": 1,
            "restrict_to_domain": "",
            "disabled": 0,
            "is_custom": 1,
            "description": _("Role for managing knowledge base entries and categories. Full control over knowledge base structure.")
        },
        {
            "role_name": "Knowledge Contributor",
            "desk_access": 1,
            "two_factor_auth": 1,
            "restrict_to_domain": "",
            "disabled": 0,
            "is_custom": 1,
            "description": _("Role for creating and editing knowledge base entries. Can create and edit own entries but not delete.")
        },
        {
            "role_name": "Knowledge User",
            "desk_access": 1,
            "two_factor_auth": 0,
            "restrict_to_domain": "",
            "disabled": 0,
            "is_custom": 1,
            "description": _("Role for viewing and using knowledge base entries. Read-only access to knowledge base.")
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
    """Setup permissions for custom roles based on the principle of least privilege

    This function applies permissions for the following DocTypes:
    - Standard ERPNext DocTypes: Sales Order, Purchase Order, Journal Entry, Item, Customer
    - Custom DocTypes: Agent Status, Agent Action Log, Cauldron Settings, etc.
    - Knowledge DocTypes: Knowledge Base Entry

    Permissions are assigned following the principle of least privilege, where each role
    is given only the minimum permissions necessary to perform its intended functions.
    """

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
        "Agent Status": [
            {
                "role": "CauldronAgentRole",
                "permlevel": 0,
                "read": 1,
                "write": 0,
                "create": 0,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 0,
                "share": 0,
                "print": 0,
                "email": 0,
                "if_owner": 0,
            },
            {
                "role": "CauldronOperatorRole",
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
                "email": 0,
                "if_owner": 0,
            },
            {
                "role": "CauldronAgentManagerRole",
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
                "if_owner": 0,
            },
            {
                "role": "CauldronWardenRole",
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
        ],
        "Agent Action Log": [
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
                "report": 0,
                "export": 0,
                "share": 0,
                "print": 0,
                "email": 0,
                "if_owner": 0,
            },
            {
                "role": "CauldronOperatorRole",
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
                "email": 0,
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
        "Cauldron Settings": [
            {
                "role": "CauldronWardenRole",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 0,
                "export": 0,
                "share": 0,
                "print": 0,
                "email": 0,
                "if_owner": 0,
            },
            {
                "role": "CauldronAgentManagerRole",
                "permlevel": 0,
                "read": 1,
                "write": 1,
                "create": 0,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 0,
                "export": 0,
                "share": 0,
                "print": 0,
                "email": 0,
                "if_owner": 0,
            },
            {
                "role": "CauldronOperatorRole",
                "permlevel": 0,
                "read": 1,
                "write": 0,
                "create": 0,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 0,
                "export": 0,
                "share": 0,
                "print": 0,
                "email": 0,
                "if_owner": 0,
            },
        ],
        "Workflow": [
            {
                "role": "CauldronWorkflowDesignerRole",
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
                "role": "CauldronWardenRole",
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
                "role": "CauldronOperatorRole",
                "permlevel": 0,
                "read": 1,
                "write": 0,
                "create": 0,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 1,
                "export": 0,
                "share": 0,
                "print": 1,
                "email": 0,
                "if_owner": 0,
            },
        ],
    }

    # Define field-level permissions for sensitive fields
    field_level_permissions = {
        "Cauldron Settings": [
            {
                "role": "CauldronOperatorRole",
                "permlevel": 1,
                "read": 1,
                "write": 0,
                "create": 0,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 0,
                "export": 0,
                "share": 0,
                "print": 0,
                "email": 0,
                "if_owner": 0,
            },
            {
                "role": "CauldronAgentManagerRole",
                "permlevel": 1,
                "read": 1,
                "write": 1,
                "create": 0,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 0,
                "export": 0,
                "share": 0,
                "print": 0,
                "email": 0,
                "if_owner": 0,
            },
        ],
        "Sales Order": [
            {
                "role": "CauldronAgentRole",
                "permlevel": 1,
                "read": 1,
                "write": 0,
                "create": 0,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 0,
                "export": 0,
                "share": 0,
                "print": 0,
                "email": 0,
                "if_owner": 0,
            },
            {
                "role": "CauldronOperatorRole",
                "permlevel": 1,
                "read": 1,
                "write": 1,
                "create": 0,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 0,
                "export": 0,
                "share": 0,
                "print": 0,
                "email": 0,
                "if_owner": 0,
            },
        ],
        "Purchase Order": [
            {
                "role": "CauldronAgentRole",
                "permlevel": 1,
                "read": 1,
                "write": 0,
                "create": 0,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 0,
                "export": 0,
                "share": 0,
                "print": 0,
                "email": 0,
                "if_owner": 0,
            },
            {
                "role": "CauldronOperatorRole",
                "permlevel": 1,
                "read": 1,
                "write": 1,
                "create": 0,
                "delete": 0,
                "submit": 0,
                "cancel": 0,
                "amend": 0,
                "report": 0,
                "export": 0,
                "share": 0,
                "print": 0,
                "email": 0,
                "if_owner": 0,
            },
        ],
    }

    # Apply document-level permissions
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

    # Apply field-level permissions
    for doctype, perms in field_level_permissions.items():
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