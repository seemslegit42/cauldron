#!/usr/bin/env python3
# Script to install DocTypes in a Frappe application

import os
import json
import argparse
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the output"""
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {command}")
        print(f"Error: {result.stderr}")
        return None
    return result.stdout.strip()

def create_app(app_name, bench_path):
    """Create a new Frappe app if it doesn't exist"""
    apps_path = os.path.join(bench_path, 'apps')
    if not os.path.exists(os.path.join(apps_path, app_name)):
        print(f"Creating new app: {app_name}")
        result = run_command(f"bench new-app {app_name}", cwd=bench_path)
        if not result:
            print(f"Failed to create app {app_name}")
            return False
        print(f"App {app_name} created successfully")
    else:
        print(f"App {app_name} already exists")
    return True

def install_app(app_name, site_name, bench_path):
    """Install the app on the site if not already installed"""
    print(f"Checking if {app_name} is installed on {site_name}")
    installed_apps = run_command(f"bench --site {site_name} list-apps", cwd=bench_path)
    if installed_apps and app_name in installed_apps:
        print(f"App {app_name} is already installed on {site_name}")
        return True
    
    print(f"Installing app {app_name} on site {site_name}")
    result = run_command(f"bench --site {site_name} install-app {app_name}", cwd=bench_path)
    if not result:
        print(f"Failed to install app {app_name} on site {site_name}")
        return False
    print(f"App {app_name} installed successfully on {site_name}")
    return True

def create_module(app_name, module_name, bench_path):
    """Create a new module in the app if it doesn't exist"""
    app_path = os.path.join(bench_path, 'apps', app_name)
    module_path = os.path.join(app_path, app_name, module_name.lower().replace(' ', '_'))
    
    if not os.path.exists(module_path):
        print(f"Creating module: {module_name}")
        os.makedirs(module_path, exist_ok=True)
        
        # Create __init__.py
        with open(os.path.join(module_path, '__init__.py'), 'w') as f:
            f.write('')
        
        # Update modules.txt
        modules_file = os.path.join(app_path, app_name, 'modules.txt')
        modules = []
        if os.path.exists(modules_file):
            with open(modules_file, 'r') as f:
                modules = [line.strip() for line in f.readlines() if line.strip()]
        
        if module_name not in modules:
            modules.append(module_name)
            with open(modules_file, 'w') as f:
                f.write('\n'.join(modules))
        
        print(f"Module {module_name} created successfully")
    else:
        print(f"Module {module_name} already exists")
    
    return module_path

def install_doctype(doctype_file, app_name, module_name, bench_path):
    """Install a DocType from a JSON file"""
    doctype_name = os.path.splitext(os.path.basename(doctype_file))[0]
    print(f"Installing DocType: {doctype_name}")
    
    # Read the DocType JSON
    with open(doctype_file, 'r') as f:
        doctype_json = json.load(f)
    
    # Update module name
    doctype_json['module'] = module_name
    
    # Create module directory if it doesn't exist
    module_path = create_module(app_name, module_name, bench_path)
    
    # Create doctype directory
    doctype_path = os.path.join(module_path, 'doctype')
    os.makedirs(doctype_path, exist_ok=True)
    
    # Create doctype subdirectory
    doctype_subdir = os.path.join(doctype_path, doctype_name.lower().replace(' ', '_'))
    os.makedirs(doctype_subdir, exist_ok=True)
    
    # Write the JSON file
    json_file = os.path.join(doctype_subdir, f'{doctype_name.lower().replace(" ", "_")}.json')
    with open(json_file, 'w') as f:
        json.dump(doctype_json, f, indent=1)
    
    # Create __init__.py
    with open(os.path.join(doctype_subdir, '__init__.py'), 'w') as f:
        f.write('')
    
    print(f"DocType {doctype_name} installed successfully")
    return True

def main():
    parser = argparse.ArgumentParser(description='Install DocTypes in a Frappe application')
    parser.add_argument('--app', required=True, help='App name')
    parser.add_argument('--module', required=True, help='Module name')
    parser.add_argument('--site', required=True, help='Site name')
    parser.add_argument('--bench-path', required=True, help='Path to Frappe bench')
    parser.add_argument('--doctypes-dir', required=True, help='Directory containing DocType JSON files')
    
    args = parser.parse_args()
    
    # Validate bench path
    if not os.path.exists(os.path.join(args.bench_path, 'apps')):
        print(f"Invalid bench path: {args.bench_path}")
        return False
    
    # Validate doctypes directory
    if not os.path.exists(args.doctypes_dir):
        print(f"Invalid doctypes directory: {args.doctypes_dir}")
        return False
    
    # Create app if it doesn't exist
    if not create_app(args.app, args.bench_path):
        return False
    
    # Install app on site
    if not install_app(args.app, args.site, args.bench_path):
        return False
    
    # Install DocTypes
    doctypes_dir = Path(args.doctypes_dir)
    for doctype_file in doctypes_dir.glob('*.json'):
        install_doctype(doctype_file, args.app, args.module, args.bench_path)
    
    # Migrate to update the database
    print("Migrating site to update database...")
    run_command(f"bench --site {args.site} migrate", cwd=args.bench_path)
    
    print("DocTypes installation completed successfully!")
    return True

if __name__ == "__main__":
    main()
