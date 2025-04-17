#!/usr/bin/env python3
"""
Script to set up initial RBAC roles for the Cauldron project.
This script defines and creates the core roles with appropriate permissions.
"""

import frappe
import json
from frappe.permissions import add_permission, update_permission_property

# Define the roles and their descriptions
ROLES = [
    {
        "name": "Cauldron Admin",
        "desk_access": 1,
        "description": "Full administrative access to all Cauldron features and settings",
        "is_custom": 1,
        "restrict_to_domain": "Cauldron",
        "two_factor_auth": 0
    },
    {
        "name": "Cauldron Finance User",
        "desk_access": 1,
        "description": "Access to financial modules including invoices, payments, and reports",
        "is_custom": 1,
        "restrict_to_domain": "Cauldron",
        "two_factor_auth": 0
    },
    {
        "name": "Cauldron Dev User",
        "desk_access": 1,
        "description": "Access to development tools and configuration settings",
        "is_custom": 1,
        "restrict_to_domain": "Cauldron",
        "two_factor_auth": 0
    },
    {
        "name": "Cauldron Operator",
        "desk_access": 1,
        "description": "Day-to-day operational access for managing workflows and tasks",
        "is_custom": 1,
        "restrict_to_domain": "Cauldron",
        "two_factor_auth": 0
    },
    {
        "name": "Cauldron Agent",
        "desk_access": 0,
        "description": "Limited API access for automated agents and integrations",
        "is_custom": 1,
        "restrict_to_domain": "Cauldron",
        "two_factor_auth": 0
    },
    {
        "name": "Cauldron Read Only",
        "desk_access": 1,
        "description": "Read-only access to view data without modification rights",
        "is_custom": 1,
        "restrict_to_domain": "Cauldron",
        "two_factor_auth": 0
    },
    {
        "name": "Cauldron Customer",
        "desk_access": 0,
        "description": "Limited access for external customers via portal",
        "is_custom": 1,
        "restrict_to_domain": "Cauldron",
        "two_factor_auth": 0
    },
    {
        "name": "Cauldron Supplier",
        "desk_access": 0,
        "description": "Limited access for suppliers via portal",
        "is_custom": 1,
        "restrict_to_domain": "Cauldron",
        "two_factor_auth": 0
    }
]

# Define role permissions for core DocTypes
ROLE_PERMISSIONS = {
    "Cauldron Admin": {
        "all": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 1,
            "cancel": 1,
            "amend": 1,
            "report": 1,
            "import": 1,
            "export": 1,
            "print": 1,
            "email": 1,
            "share": 1,
            "set_user_permissions": 1
        }
    },
    "Cauldron Finance User": {
        "Invoice": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "submit": 1,
            "cancel": 1,
            "amend": 1,
            "report": 1,
            "import": 1,
            "export": 1,
            "print": 1,
            "email": 1,
            "share": 1
        },
        "Purchase Order": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "submit": 1,
            "cancel": 1,
            "amend": 1,
            "report": 1,
            "import": 1,
            "export": 1,
            "print": 1,
            "email": 1,
            "share": 1
        },
        "Customer": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "report": 1,
            "import": 1,
            "export": 1,
            "print": 1,
            "email": 1,
            "share": 1
        },
        "Supplier": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "report": 1,
            "import": 1,
            "export": 1,
            "print": 1,
            "email": 1,
            "share": 1
        }
    },
    "Cauldron Dev User": {
        "Custom Field": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "import": 1,
            "export": 1
        },
        "Custom Script": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "import": 1,
            "export": 1
        },
        "Server Script": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "import": 1,
            "export": 1
        },
        "Client Script": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "import": 1,
            "export": 1
        },
        "Workflow": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "import": 1,
            "export": 1
        }
    },
    "Cauldron Operator": {
        "Invoice": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "submit": 1,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "print": 1,
            "email": 1
        },
        "Purchase Order": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "submit": 1,
            "cancel": 0,
            "amend": 0,
            "report": 1,
            "export": 1,
            "print": 1,
            "email": 1
        },
        "Customer": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "report": 1,
            "export": 1
        },
        "Supplier": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "report": 1,
            "export": 1
        }
    },
    "Cauldron Agent": {
        "Invoice": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "submit": 0,
            "report": 1,
            "export": 1
        },
        "Purchase Order": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "submit": 0,
            "report": 1,
            "export": 1
        },
        "Customer": {
            "read": 1,
            "write": 0,
            "create": 0,
            "report": 1
        },
        "Supplier": {
            "read": 1,
            "write": 0,
            "create": 0,
            "report": 1
        }
    },
    "Cauldron Read Only": {
        "Invoice": {
            "read": 1,
            "report": 1,
            "export": 1
        },
        "Purchase Order": {
            "read": 1,
            "report": 1,
            "export": 1
        },
        "Customer": {
            "read": 1,
            "report": 1,
            "export": 1
        },
        "Supplier": {
            "read": 1,
            "report": 1,
            "export": 1
        }
    },
    "Cauldron Customer": {
        "Invoice": {
            "read": 1,
            "print": 1
        },
        "Purchase Order": {
            "read": 0
        },
        "Customer": {
            "read": 0
        },
        "Supplier": {
            "read": 0
        }
    },
    "Cauldron Supplier": {
        "Invoice": {
            "read": 0
        },
        "Purchase Order": {
            "read": 1,
            "print": 1
        },
        "Customer": {
            "read": 0
        },
        "Supplier": {
            "read": 0
        }
    }
}

def create_roles():
    """Create the defined roles if they don't exist"""
    for role_data in ROLES:
        role_name = role_data["name"]
        if not frappe.db.exists("Role", role_name):
            role = frappe.new_doc("Role")
            for key, value in role_data.items():
                setattr(role, key, value)
            role.save()
            print(f"Created role: {role_name}")
        else:
            print(f"Role already exists: {role_name}")

def setup_role_permissions():
    """Set up permissions for each role"""
    for role, doctypes in ROLE_PERMISSIONS.items():
        for doctype, permissions in doctypes.items():
            if doctype == "all":
                # Apply to all DocTypes
                all_doctypes = frappe.get_all("DocType", filters={"istable": 0, "issingle": 0})
                for dt in all_doctypes:
                    apply_permissions(role, dt.name, permissions)
            else:
                # Apply to specific DocType
                if frappe.db.exists("DocType", doctype):
                    apply_permissions(role, doctype, permissions)
                else:
                    print(f"DocType {doctype} does not exist, skipping permissions for {role}")

def apply_permissions(role, doctype, permissions):
    """Apply the specified permissions for a role on a doctype"""
    try:
        # Check if permission already exists
        if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role}):
            # Add new permission
            add_permission(doctype, role, 0)
            print(f"Added permission for {role} on {doctype}")
        
        # Update permission properties
        for perm_type, value in permissions.items():
            update_permission_property(doctype, role, 0, perm_type, value)
        
        print(f"Updated permissions for {role} on {doctype}")
    except Exception as e:
        print(f"Error setting permissions for {role} on {doctype}: {str(e)}")

def create_role_profiles():
    """Create role profiles for common user types"""
    role_profiles = [
        {
            "name": "Cauldron Administrator",
            "roles": ["Cauldron Admin"]
        },
        {
            "name": "Cauldron Finance Manager",
            "roles": ["Cauldron Finance User", "Cauldron Read Only"]
        },
        {
            "name": "Cauldron Developer",
            "roles": ["Cauldron Dev User", "Cauldron Read Only"]
        },
        {
            "name": "Cauldron Operations",
            "roles": ["Cauldron Operator", "Cauldron Read Only"]
        },
        {
            "name": "Cauldron API Integration",
            "roles": ["Cauldron Agent"]
        }
    ]
    
    for profile_data in role_profiles:
        profile_name = profile_data["name"]
        if not frappe.db.exists("Role Profile", profile_name):
            profile = frappe.new_doc("Role Profile")
            profile.role_profile = profile_name
            
            for role in profile_data["roles"]:
                profile.append("roles", {"role": role})
            
            profile.save()
            print(f"Created role profile: {profile_name}")
        else:
            print(f"Role profile already exists: {profile_name}")

def main():
    """Main function to set up RBAC roles"""
    print("Setting up RBAC roles for Cauldron...")
    
    # Create roles
    create_roles()
    
    # Set up permissions
    setup_role_permissions()
    
    # Create role profiles
    create_role_profiles()
    
    print("RBAC roles setup completed successfully!")

if __name__ == "__main__":
    main()
