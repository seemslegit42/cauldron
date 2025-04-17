import frappe
from frappe import _

def get_context(context):
    context.no_cache = 1
    context.show_sidebar = True
    context.title = _("Cauldron Dashboard")
    
    # Add your context data here
    context.data = {
        "sample_key": "sample_value"
    }
    
    return context