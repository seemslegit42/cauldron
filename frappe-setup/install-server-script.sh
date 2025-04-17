#!/bin/bash
# Script to install server scripts in a Frappe application

set -e

# Default values
CONTAINER_NAME="frappe-web"
SITE_NAME="cauldron.local"
APP_NAME="cauldron_operations_core"
MODULE_NAME="Accounts"
SCRIPT_NAME="invoice_server_script"
DOCTYPE="Invoice"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --container)
      CONTAINER_NAME="$2"
      shift
      shift
      ;;
    --site-name)
      SITE_NAME="$2"
      shift
      shift
      ;;
    --app-name)
      APP_NAME="$2"
      shift
      shift
      ;;
    --module-name)
      MODULE_NAME="$2"
      shift
      shift
      ;;
    --script-name)
      SCRIPT_NAME="$2"
      shift
      shift
      ;;
    --doctype)
      DOCTYPE="$2"
      shift
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --container NAME        Container name (default: frappe-web)"
      echo "  --site-name NAME        Site name (default: cauldron.local)"
      echo "  --app-name NAME         App name (default: cauldron_operations_core)"
      echo "  --module-name NAME      Module name (default: Accounts)"
      echo "  --script-name NAME      Server script name (default: invoice_server_script)"
      echo "  --doctype NAME          DocType to attach the script to (default: Invoice)"
      echo "  --help                  Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Installing server script with the following configuration:"
echo "  Container: $CONTAINER_NAME"
echo "  Site: $SITE_NAME"
echo "  App: $APP_NAME"
echo "  Module: $MODULE_NAME"
echo "  Script: $SCRIPT_NAME"
echo "  DocType: $DOCTYPE"
echo ""

# Copy the server script to the container
echo "Copying server script to container..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_SCRIPTS_DIR="$SCRIPT_DIR/server-scripts"
TEMP_DIR=$(mktemp -d)

# Create a Python script to install the server script
cat > "$TEMP_DIR/install_server_script.py" << EOF
#!/usr/bin/env python3
import os
import sys
import frappe

def install_server_script():
    """Install the server script in the Frappe application"""
    
    # Parameters
    app_name = "$APP_NAME"
    module_name = "$MODULE_NAME"
    script_name = "$SCRIPT_NAME"
    doctype = "$DOCTYPE"
    
    # Get the script content
    script_path = "/tmp/server_scripts/$SCRIPT_NAME.py"
    with open(script_path, "r") as f:
        script_content = f.read()
    
    # Create the module directory if it doesn't exist
    app_path = os.path.join(frappe.get_app_path(app_name))
    module_path = os.path.join(app_path, app_name.replace("-", "_"), module_name.lower().replace(" ", "_"))
    os.makedirs(module_path, exist_ok=True)
    
    # Create the server scripts directory if it doesn't exist
    server_scripts_path = os.path.join(module_path, "server_scripts")
    os.makedirs(server_scripts_path, exist_ok=True)
    
    # Create __init__.py files
    if not os.path.exists(os.path.join(module_path, "__init__.py")):
        with open(os.path.join(module_path, "__init__.py"), "w") as f:
            f.write("")
    
    if not os.path.exists(os.path.join(server_scripts_path, "__init__.py")):
        with open(os.path.join(server_scripts_path, "__init__.py"), "w") as f:
            f.write("")
    
    # Save the script
    script_file_path = os.path.join(server_scripts_path, f"{script_name}.py")
    with open(script_file_path, "w") as f:
        f.write(script_content)
    
    print(f"Server script saved to {script_file_path}")
    
    # Create hooks to attach the script to the DocType
    hooks_path = os.path.join(app_path, app_name.replace("-", "_"), "hooks.py")
    
    # Read the current hooks file
    with open(hooks_path, "r") as f:
        hooks_content = f.read()
    
    # Check if the hooks already exist
    hook_name = f"doc_events"
    if hook_name not in hooks_content:
        # Add the hook section
        hooks_content += f"\n\n# Document Events\n{hook_name} = {{}}\n"
    
    # Find the position to insert the hook
    import re
    hook_pattern = re.compile(f"{hook_name} = {{(.*?)}}", re.DOTALL)
    match = hook_pattern.search(hooks_content)
    
    if match:
        # Extract the current hook content
        hook_content = match.group(1)
        
        # Check if the DocType is already in the hooks
        doctype_pattern = re.compile(f'"{doctype}"\\s*:\\s*{{(.*?)}}', re.DOTALL)
        doctype_match = doctype_pattern.search(hook_content)
        
        if doctype_match:
            # DocType already exists, update the events
            doctype_content = doctype_match.group(1)
            
            # Check if the events are already defined
            events = ["validate", "on_submit", "on_cancel", "on_update_after_submit"]
            for event in events:
                event_pattern = re.compile(f'"{event}"\\s*:\\s*"[^"]*"')
                if not event_pattern.search(doctype_content):
                    # Add the event
                    doctype_content = doctype_content.rstrip() + f'\n\t\t"{event}": "{app_name}.{module_name.lower().replace(" ", "_")}.server_scripts.{script_name}.{event}",'
            
            # Update the DocType content
            new_doctype_content = f'"{doctype}": {{{doctype_content}\n\t}}'
            new_hook_content = hook_pattern.sub(f"{hook_name} = {{{hook_content.replace(doctype_match.group(0), new_doctype_content)}}}", hooks_content)
        else:
            # DocType doesn't exist, add it
            new_doctype_content = f'\n\t"{doctype}": {{\n\t\t"validate": "{app_name}.{module_name.lower().replace(" ", "_")}.server_scripts.{script_name}.validate",\n\t\t"on_submit": "{app_name}.{module_name.lower().replace(" ", "_")}.server_scripts.{script_name}.on_submit",\n\t\t"on_cancel": "{app_name}.{module_name.lower().replace(" ", "_")}.server_scripts.{script_name}.on_cancel",\n\t\t"on_update_after_submit": "{app_name}.{module_name.lower().replace(" ", "_")}.server_scripts.{script_name}.on_update_after_submit"\n\t}},'
            new_hook_content = hook_pattern.sub(f"{hook_name} = {{{hook_content}{new_doctype_content}}}", hooks_content)
    else:
        # Hook section not found, create it
        new_doctype_content = f'\n\t"{doctype}": {{\n\t\t"validate": "{app_name}.{module_name.lower().replace(" ", "_")}.server_scripts.{script_name}.validate",\n\t\t"on_submit": "{app_name}.{module_name.lower().replace(" ", "_")}.server_scripts.{script_name}.on_submit",\n\t\t"on_cancel": "{app_name}.{module_name.lower().replace(" ", "_")}.server_scripts.{script_name}.on_cancel",\n\t\t"on_update_after_submit": "{app_name}.{module_name.lower().replace(" ", "_")}.server_scripts.{script_name}.on_update_after_submit"\n\t}}'
        new_hook_content = hooks_content + f"\n\n# Document Events\n{hook_name} = {{{new_doctype_content}\n}}"
    
    # Write the updated hooks file
    with open(hooks_path, "w") as f:
        f.write(new_hook_content)
    
    print(f"Hooks updated in {hooks_path}")
    
    # Update the app.py file to include the new module
    app_py_path = os.path.join(app_path, app_name.replace("-", "_"), "app.py")
    
    # Read the current app.py file
    with open(app_py_path, "r") as f:
        app_py_content = f.read()
    
    # Check if the module is already in the app.py file
    module_pattern = re.compile(f'"{module_name.lower().replace(" ", "_")}"')
    if not module_pattern.search(app_py_content):
        # Add the module to the app.py file
        modules_pattern = re.compile(r"modules\s*=\s*\[(.*?)\]", re.DOTALL)
        modules_match = modules_pattern.search(app_py_content)
        
        if modules_match:
            # Extract the current modules
            modules_content = modules_match.group(1)
            
            # Add the new module
            new_modules_content = modules_content.rstrip() + f',\n\t"{module_name.lower().replace(" ", "_")}"'
            new_app_py_content = modules_pattern.sub(f"modules = [{new_modules_content}]", app_py_content)
            
            # Write the updated app.py file
            with open(app_py_path, "w") as f:
                f.write(new_app_py_content)
            
            print(f"Module added to {app_py_path}")
    
    print(f"Server script installation completed successfully!")
    return True

if __name__ == "__main__":
    frappe.init(site="$SITE_NAME")
    frappe.connect()
    
    try:
        result = install_server_script()
        if result:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    finally:
        frappe.destroy()
EOF

# Copy the server script to the temp directory
mkdir -p "$TEMP_DIR/server_scripts"
cp "$SERVER_SCRIPTS_DIR/$SCRIPT_NAME.py" "$TEMP_DIR/server_scripts/"

# Copy the files to the container
docker cp "$TEMP_DIR" "$CONTAINER_NAME:/tmp/server_scripts"

# Make the script executable
docker exec "$CONTAINER_NAME" bash -c "chmod +x /tmp/server_scripts/install_server_script.py"

# Run the script in the container
echo "Installing server script in the container..."
docker exec -u frappe "$CONTAINER_NAME" bash -c "cd /home/frappe/frappe-bench && python /tmp/server_scripts/install_server_script.py"

# Clean up
rm -rf "$TEMP_DIR"

echo "Server script installation completed successfully!"
echo ""
echo "The server script has been installed and attached to the $DOCTYPE DocType."
echo "It will be triggered on the following events:"
echo "  - validate: When the document is saved"
echo "  - on_submit: When the document is submitted"
echo "  - on_cancel: When the document is cancelled"
echo "  - on_update_after_submit: When the document is updated after submission"
