# Cauldron Monorepo Structure

This document outlines the standard monorepo structure for the Cauldron project.

## Directory Structure

```
cauldron/
├── frappe-bench/         # Frappe Bench setup and applications
├── microservices/        # Microservices architecture components
├── frontend/             # Frontend applications and components
├── infra/                # Infrastructure as code and deployment configurations
├── docs/                 # Documentation and guides
├── scripts/              # Utility scripts for development and deployment
└── tests/                # Integration and end-to-end tests
```

## Directory Purposes

### frappe-bench/
Contains the Frappe Bench setup, which is the foundation for the Frappe applications used in Cauldron. This includes ERPNext and custom Frappe apps developed for the project.

### microservices/
Houses the microservices that make up the Cauldron ecosystem. Each microservice is self-contained with its own source code, configuration, and tests.

### frontend/
Contains all frontend applications and components, including the main UI (Manifold) and any other user interfaces.

### infra/
Infrastructure as code (IaC) configurations, Kubernetes manifests, Terraform scripts, and other deployment-related files.

### docs/
Comprehensive documentation for the project, including architecture diagrams, setup guides, API references, and governance protocols.

### scripts/
Utility scripts for development, deployment, testing, and other operational tasks.

### tests/
Integration tests, end-to-end tests, and other test suites that span multiple components of the system.

## Development Guidelines

1. **Component Isolation**: Each component should be self-contained with clear boundaries.
2. **Consistent Structure**: Follow the established patterns within each directory.
3. **Documentation**: Include README files in each directory explaining its purpose and structure.
4. **Testing**: Write tests for all components and ensure they can be run both individually and as part of the larger test suite.
5. **Dependencies**: Clearly document dependencies between components.

## Workflow

For development workflow and contribution guidelines, please refer to the `CONTRIBUTING.md` file in the root directory.# Cauldron Monorepo Structure

This document outlines the standard monorepo structure for the Cauldron project.

## Directory Structure

```
cauldron/
├── frappe-bench/         # Frappe Bench setup and applications
├── microservices/        # Microservices architecture components
├── frontend/             # Frontend applications and components
├── infra/                # Infrastructure as code and deployment configurations
├── docs/                 # Documentation and guides
├── scripts/              # Utility scripts for development and deployment
└── tests/                # Integration and end-to-end tests
```

## Directory Purposes

### frappe-bench/
Contains the Frappe Bench setup, which is the foundation for the Frappe applications used in Cauldron. This includes ERPNext and custom Frappe apps developed for the project.

### microservices/
Houses the microservices that make up the Cauldron ecosystem. Each microservice is self-contained with its own source code, configuration, and tests.

### frontend/
Contains all frontend applications and components, including the main UI (Manifold) and any other user interfaces.

### infra/
Infrastructure as code (IaC) configurations, Kubernetes manifests, Terraform scripts, and other deployment-related files.

### docs/
Comprehensive documentation for the project, including architecture diagrams, setup guides, API references, and governance protocols.

### scripts/
Utility scripts for development, deployment, testing, and other operational tasks.

### tests/
Integration tests, end-to-end tests, and other test suites that span multiple components of the system.

## Development Guidelines

1. **Component Isolation**: Each component should be self-contained with clear boundaries.
2. **Consistent Structure**: Follow the established patterns within each directory.
3. **Documentation**: Include README files in each directory explaining its purpose and structure.
4. **Testing**: Write tests for all components and ensure they can be run both individually and as part of the larger test suite.
5. **Dependencies**: Clearly document dependencies between components.

## Workflow

For development workflow and contribution guidelines, please refer to the `CONTRIBUTING.md` file in the root directory.