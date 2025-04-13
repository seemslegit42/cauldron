# Cauldron™ Utility Scripts

This directory contains utility shell scripts for common development, build, deployment, or operational tasks related to the Cauldron™ sEOS project.

## Scripts

* **`setup_frappe.sh`**:
    * **Purpose:** Performs the initial setup of the Frappe Bench environment, site creation, and installation of ERPNext and custom Cauldron apps within the Codespaces container. Designed to be idempotent (safe to run multiple times).
    * **Usage:** Typically called automatically by the `postCreateCommand` in `.devcontainer/devcontainer.json`. Requires specific environment variables (e.g., `DB_ROOT_PASSWORD`, `ADMIN_PASSWORD`) to be set via Codespaces secrets.
* **(Other Scripts - Examples)**
    * `invoke-local.sh`: (Placeholder) Could be used to start all services locally via Docker Compose.
    * `build-images.sh`: (Placeholder) Could be used to build custom Docker images for services.
    * `deploy-infra.sh`: (Placeholder) Could wrap Terraform commands for infrastructure deployment.
    * `seed-data.sh`: (Placeholder) Could be used to populate the system with initial test or demo data.

*(Add documentation for new scripts here as they are created.)*

## Usage Notes

* Ensure scripts are executable (`chmod +x <script_name>.sh`). This is handled automatically for `setup_frappe.sh` in the current `devcontainer.json`.
* Refer to comments within each script for specific usage instructions and required environment variables.
