import frappe
from cauldron_operations_core.custom_fields import setup as setup_custom_fields
from cauldron_operations_core.workflows.order_approval_workflow import setup_workflows
from cauldron_operations_core.roles import setup as setup_roles
from cauldron_operations_core.role_profiles import setup as setup_role_profiles
from cauldron_operations_core.doctype.cauldron_settings.cauldron_settings import setup_field_permissions

def setup():
    """Setup all components for Cauldron Operations Core"""
    print("Setting up Cauldron Operations Core...")

    # Setup roles and permissions
    print("Setting up roles and permissions...")
    setup_roles()

    # Setup role profiles
    print("Setting up role profiles...")
    setup_role_profiles()

    # Setup custom fields
    print("Setting up custom fields...")
    setup_custom_fields()

    # Setup workflows
    print("Setting up workflows...")
    setup_workflows()

    # Setup field-level permissions
    print("Setting up field-level permissions...")
    setup_field_permissions()

    print("Cauldron Operations Core setup complete!")

def after_install():
    """Run after app installation"""
    setup()