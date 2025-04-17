#!/usr/bin/env python3
"""
Script to set up basic Frappe permissions for core DocTypes to initial roles.
This script defines and assigns permissions for essential Frappe DocTypes to the core roles.
"""

import frappe
import json
from frappe.permissions import add_permission, update_permission_property

# Define the core roles
CORE_ROLES = [
    "Cauldron Admin",
    "Cauldron Finance User",
    "Cauldron Dev User",
    "Cauldron Operator",
    "Cauldron Agent",
    "Cauldron Read Only",
    "Cauldron Customer",
    "Cauldron Supplier"
]

# Define core Frappe DocTypes that need permissions
CORE_DOCTYPES = [
    "User",
    "Role",
    "DocType",
    "DocField",
    "Custom Field",
    "Workflow",
    "Workflow State",
    "Workflow Action",
    "File",
    "Report",
    "Page",
    "Module Def",
    "System Settings",
    "Print Format",
    "Email Template",
    "Notification",
    "Client Script",
    "Server Script",
    "Custom DocPerm",
    "Property Setter",
    "Translation",
    "Language",
    "Web Page",
    "Web Form",
    "Web Template",
    "Dashboard",
    "Dashboard Chart",
    "Dashboard Chart Source",
    "Document Naming Rule",
    "Auto Email Report",
    "Scheduled Job Type",
    "Error Log",
    "Error Snapshot",
    "Event Producer",
    "Event Consumer",
    "Event Update Log",
    "Event Sync Log"
]

# Define role permissions for core DocTypes
CORE_PERMISSIONS = {
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
        "User": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "report": 1,
            "export": 1,
            "print": 1,
            "email": 1
        },
        "File": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "report": 1,
            "export": 1,
            "print": 1,
            "email": 1
        },
        "Report": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "report": 1,
            "export": 1,
            "print": 1,
            "email": 1
        },
        "Dashboard": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "report": 1,
            "export": 1,
            "print": 1,
            "email": 1
        },
        "Dashboard Chart": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "report": 1,
            "export": 1,
            "print": 1,
            "email": 1
        },
        "Print Format": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0
        },
        "Email Template": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0
        }
    },
    "Cauldron Dev User": {
        "User": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "report": 1,
            "export": 1
        },
        "Role": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "report": 1,
            "export": 1
        },
        "DocType": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "report": 1,
            "export": 1
        },
        "DocField": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "report": 1,
            "export": 1
        },
        "Custom Field": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "export": 1
        },
        "Workflow": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "export": 1
        },
        "Workflow State": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "export": 1
        },
        "Workflow Action": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "export": 1
        },
        "File": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "export": 1
        },
        "Client Script": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "export": 1
        },
        "Server Script": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "export": 1
        },
        "Custom DocPerm": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "export": 1
        },
        "Property Setter": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "export": 1
        },
        "Translation": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "export": 1
        },
        "Print Format": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "export": 1
        },
        "Report": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "export": 1
        }
    },
    "Cauldron Operator": {
        "User": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "report": 1,
            "export": 1
        },
        "File": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "report": 1,
            "export": 1
        },
        "Report": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "report": 1,
            "export": 1
        },
        "Dashboard": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "report": 1,
            "export": 1
        },
        "Print Format": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0
        },
        "Email Template": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0
        },
        "Notification": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0
        }
    },
    "Cauldron Agent": {
        "File": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 0,
            "report": 1,
            "export": 0
        },
        "Report": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "report": 1,
            "export": 0
        }
    },
    "Cauldron Read Only": {
        "all": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "report": 1,
            "export": 1,
            "print": 1,
            "email": 0,
            "share": 0
        }
    },
    "Cauldron Customer": {
        "File": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "if_owner": 1
        }
    },
    "Cauldron Supplier": {
        "File": {
            "read": 1,
            "write": 0,
            "create": 0,
            "delete": 0,
            "if_owner": 1
        }
    }
}

def check_roles_exist():
    """Check if the core roles exist, return False if any are missing"""
    for role in CORE_ROLES:
        if not frappe.db.exists("Role", role):
            print(f"Role {role} does not exist. Please run setup-rbac-roles.py first.")
            return False
    return True

def setup_core_permissions():
    """Set up permissions for core DocTypes"""
    for role, doctypes in CORE_PERMISSIONS.items():
        for doctype, permissions in doctypes.items():
            if doctype == "all":
                # Apply to all core DocTypes
                for dt in CORE_DOCTYPES:
                    apply_permissions(role, dt, permissions)
            else:
                # Apply to specific DocType
                if doctype in CORE_DOCTYPES:
                    apply_permissions(role, doctype, permissions)
                else:
                    print(f"DocType {doctype} is not in the core DocTypes list, skipping permissions for {role}")

def apply_permissions(role, doctype, permissions):
    """Apply the specified permissions for a role on a doctype"""
    try:
        # Check if DocType exists
        if not frappe.db.exists("DocType", doctype):
            print(f"DocType {doctype} does not exist, skipping permissions for {role}")
            return
            
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

def main():
    """Main function to set up core permissions"""
    print("Setting up core permissions for Frappe DocTypes...")
    
    # Check if roles exist
    if not check_roles_exist():
        return
    
    # Set up core permissions
    setup_core_permissions()
    
    print("Core permissions setup completed successfully!")

if __name__ == "__main__":
    main()
