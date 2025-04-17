# Core Frappe Permissions Documentation

## Overview

This document describes the permissions assigned to core Frappe DocTypes for the initial roles in the Cauldron project. These permissions follow the principle of least privilege, ensuring that each role has only the permissions necessary to perform its intended functions.

## Core DocTypes

The following core Frappe DocTypes have been assigned permissions:

- **User**: User accounts and profiles
- **Role**: Role definitions for permissions
- **DocType**: Document type definitions
- **DocField**: Field definitions for DocTypes
- **Custom Field**: Custom field definitions
- **Workflow**: Workflow definitions
- **Workflow State**: Workflow state definitions
- **Workflow Action**: Workflow action definitions
- **File**: File attachments and uploads
- **Report**: Report definitions
- **Page**: Page definitions
- **Module Def**: Module definitions
- **System Settings**: System configuration
- **Print Format**: Print format definitions
- **Email Template**: Email template definitions
- **Notification**: Notification definitions
- **Client Script**: Client-side JavaScript customizations
- **Server Script**: Server-side Python customizations
- **Custom DocPerm**: Custom permission rules
- **Property Setter**: Property customizations
- **Translation**: Translation entries
- **Language**: Language definitions
- **Web Page**: Web page content
- **Web Form**: Web form definitions
- **Web Template**: Web template definitions
- **Dashboard**: Dashboard definitions
- **Dashboard Chart**: Dashboard chart definitions
- **Dashboard Chart Source**: Dashboard chart data sources
- **Document Naming Rule**: Document naming rules
- **Auto Email Report**: Automated email report configurations
- **Scheduled Job Type**: Scheduled job definitions
- **Error Log**: Error log entries
- **Error Snapshot**: Error snapshot details
- **Event Producer**: Event producer configurations
- **Event Consumer**: Event consumer configurations
- **Event Update Log**: Event update log entries
- **Event Sync Log**: Event synchronization log entries

## Role Permissions

### Cauldron Admin

**Description**: Full administrative access to all Cauldron features and settings.

**Permissions**:
- Full access to all core DocTypes (read, write, create, delete, submit, cancel, amend)
- Can import and export data
- Can set user permissions
- Can access all reports and dashboards

### Cauldron Finance User

**Description**: Access to financial modules including invoices, payments, and reports.

**Permissions**:
- Read-only access to User DocType
- Read/write/create access to File DocType
- Read-only access to Report, Dashboard, Dashboard Chart DocTypes
- Read-only access to Print Format and Email Template DocTypes

### Cauldron Dev User

**Description**: Access to development tools and configuration settings.

**Permissions**:
- Read-only access to User and Role DocTypes
- Read/write/create access to DocType and DocField DocTypes
- Full access to Custom Field, Workflow, Workflow State, and Workflow Action DocTypes
- Full access to Client Script, Server Script, Custom DocPerm, and Property Setter DocTypes
- Full access to Translation, Print Format, and Report DocTypes

### Cauldron Operator

**Description**: Day-to-day operational access.

**Permissions**:
- Read-only access to User DocType
- Read/write/create access to File DocType
- Read-only access to Report, Dashboard, Print Format, Email Template, and Notification DocTypes

### Cauldron Agent

**Description**: Limited API access for automated agents.

**Permissions**:
- Read/write/create access to File DocType
- Read-only access to Report DocType

### Cauldron Read Only

**Description**: Read-only access to view data.

**Permissions**:
- Read-only access to all core DocTypes
- Can export and print data
- Cannot write, create, delete, email, or share data

### Cauldron Customer

**Description**: Limited access for external customers via portal.

**Permissions**:
- Read-only access to File DocType (only if owner)

### Cauldron Supplier

**Description**: Limited access for suppliers via portal.

**Permissions**:
- Read-only access to File DocType (only if owner)

## Implementation

The permissions are implemented using the `setup-core-permissions.py` script, which:

1. Defines the core roles and DocTypes
2. Defines the permission levels for each role on each DocType
3. Checks if the roles exist
4. Applies the permissions to the DocTypes

The script can be run using the `setup-core-permissions.sh` shell script, which:

1. Copies the Python script to the Frappe container
2. Makes the script executable
3. Runs the script in the container
4. Cleans up temporary files

## Maintenance

To modify the permissions:

1. Edit the `CORE_PERMISSIONS` dictionary in `setup-core-permissions.py`
2. Run the `setup-core-permissions.sh` script again

To add permissions for new DocTypes:

1. Add the DocType to the `CORE_DOCTYPES` list in `setup-core-permissions.py`
2. Add the permissions for each role in the `CORE_PERMISSIONS` dictionary
3. Run the `setup-core-permissions.sh` script again
