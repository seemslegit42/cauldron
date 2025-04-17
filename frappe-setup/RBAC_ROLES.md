# Cauldron RBAC Roles Documentation

## Overview

This document describes the Role-Based Access Control (RBAC) roles defined for the Cauldron project. These roles provide a structured approach to managing permissions across different user types in the system.

## Core Roles

### Cauldron Admin

**Description**: Full administrative access to all Cauldron features and settings.

**Permissions**:
- Full access to all DocTypes (read, write, create, delete, submit, cancel, amend)
- Can import and export data
- Can set user permissions
- Can access all reports and dashboards

**Use Cases**:
- System administrators
- IT managers
- Project owners

### Cauldron Finance User

**Description**: Access to financial modules including invoices, payments, and reports.

**Permissions**:
- Full access to financial DocTypes (Invoice, Purchase Order, etc.)
- Can create and modify customer and supplier records
- Can generate financial reports
- Cannot delete financial records (for audit purposes)

**Use Cases**:
- Finance managers
- Accountants
- Financial analysts

### Cauldron Dev User

**Description**: Access to development tools and configuration settings.

**Permissions**:
- Can create and modify custom fields, scripts, and workflows
- Can access system settings and configurations
- Can create and modify reports and dashboards
- Can export and import data for development purposes

**Use Cases**:
- Developers
- System customizers
- Technical consultants

### Cauldron Operator

**Description**: Day-to-day operational access for managing workflows and tasks.

**Permissions**:
- Can create and modify core business documents (invoices, orders, etc.)
- Can submit documents for approval
- Cannot cancel or amend submitted documents
- Limited access to system settings

**Use Cases**:
- Operations staff
- Customer service representatives
- Sales personnel

### Cauldron Agent

**Description**: Limited API access for automated agents and integrations.

**Permissions**:
- Read access to most DocTypes
- Limited write access to specific DocTypes
- Cannot submit or cancel documents
- Cannot access sensitive information

**Use Cases**:
- API integrations
- Automated processes
- AI agents

### Cauldron Read Only

**Description**: Read-only access to view data without modification rights.

**Permissions**:
- Read access to most DocTypes
- Can generate reports
- Cannot modify any data
- Cannot access sensitive information

**Use Cases**:
- Auditors
- Managers (for oversight)
- Stakeholders needing visibility

### Cauldron Customer

**Description**: Limited access for external customers via portal.

**Permissions**:
- Can view their own invoices and orders
- Cannot access other customers' data
- Cannot modify any data
- Limited to portal access (no desk access)

**Use Cases**:
- External customers
- Client representatives

### Cauldron Supplier

**Description**: Limited access for suppliers via portal.

**Permissions**:
- Can view purchase orders related to them
- Cannot access other suppliers' data
- Cannot modify any data
- Limited to portal access (no desk access)

**Use Cases**:
- External suppliers
- Vendor representatives

## Role Profiles

Role profiles combine multiple roles to create common user types:

### Cauldron Administrator

**Roles**:
- Cauldron Admin

**Use Case**: System administrators with full access to all features.

### Cauldron Finance Manager

**Roles**:
- Cauldron Finance User
- Cauldron Read Only

**Use Case**: Finance team members who need to manage financial data and view other business data.

### Cauldron Developer

**Roles**:
- Cauldron Dev User
- Cauldron Read Only

**Use Case**: Developers who need to customize the system and view business data.

### Cauldron Operations

**Roles**:
- Cauldron Operator
- Cauldron Read Only

**Use Case**: Operations staff who manage day-to-day business processes.

### Cauldron API Integration

**Roles**:
- Cauldron Agent

**Use Case**: API integrations and automated processes.

## Permission Matrix

The following table shows the permission levels for each role on key DocTypes:

| DocType | Cauldron Admin | Cauldron Finance User | Cauldron Dev User | Cauldron Operator | Cauldron Agent | Cauldron Read Only | Cauldron Customer | Cauldron Supplier |
|---------|----------------|----------------------|-------------------|-------------------|----------------|-------------------|-------------------|-------------------|
| Invoice | Full Access    | Create, Submit, Amend| Read              | Create, Submit    | Create, Read   | Read Only         | Read Own          | No Access         |
| Purchase Order | Full Access | Create, Submit, Amend | Read         | Create, Submit    | Create, Read   | Read Only         | No Access         | Read Own          |
| Customer | Full Access   | Create, Modify       | Read              | Create, Modify    | Read Only      | Read Only         | No Access         | No Access         |
| Supplier | Full Access   | Create, Modify       | Read              | Create, Modify    | Read Only      | Read Only         | No Access         | No Access         |
| Custom Field | Full Access | No Access          | Full Access       | No Access         | No Access      | No Access         | No Access         | No Access         |
| Workflow | Full Access   | No Access            | Full Access       | No Access         | No Access      | No Access         | No Access         | No Access         |
| User    | Full Access    | No Access            | No Access         | No Access         | No Access      | No Access         | No Access         | No Access         |

## Best Practices

### Role Assignment

1. **Principle of Least Privilege**: Assign users the minimum permissions needed for their job functions.
2. **Role Separation**: Separate duties by assigning different roles to different users.
3. **Regular Review**: Periodically review role assignments to ensure they remain appropriate.

### Custom Roles

When creating custom roles:

1. **Be Specific**: Create roles for specific job functions rather than generic access levels.
2. **Document Permissions**: Clearly document what permissions each role has.
3. **Test Thoroughly**: Test custom roles to ensure they have the appropriate access.

### Security Considerations

1. **Admin Access**: Limit the number of users with admin access.
2. **API Access**: Regularly rotate API keys for agent roles.
3. **Audit Logs**: Regularly review audit logs to detect unauthorized access.

## Extending the Role System

### Adding New Roles

To add a new role:

1. Create the role in the Frappe system
2. Define permissions for the role on relevant DocTypes
3. Update the role documentation

### Modifying Existing Roles

To modify an existing role:

1. Update the permissions in the Frappe system
2. Update the role documentation
3. Communicate changes to affected users

### Creating Custom Role Profiles

To create a custom role profile:

1. Identify the combination of roles needed
2. Create the role profile in the Frappe system
3. Document the new role profile

## Implementation Details

The RBAC roles are implemented using the following components:

1. **Role DocType**: Defines the roles in the system
2. **DocPerm DocType**: Defines permissions for roles on DocTypes
3. **Role Profile DocType**: Defines combinations of roles for common user types

The setup script (`setup-rbac-roles.py`) automates the creation of these components.

## References

- [Frappe Permissions Documentation](https://frappeframework.com/docs/user/en/basics/users-and-permissions)
- [Role-Based Access Control (RBAC) Overview](https://en.wikipedia.org/wiki/Role-based_access_control)
- [Principle of Least Privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege)
