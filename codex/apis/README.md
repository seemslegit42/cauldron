# Cauldron™ API Documentation

This directory contains specifications and documentation for the various synchronous APIs exposed by Cauldron™ services.

Understanding these APIs is crucial for:

*   Frontend (**Manifold UI**) development.
*   Inter-service communication (where synchronous calls are necessary).
*   Third-party integrations.

## Structure:

*   **Foundations (`api_codex_foundations_v1.md`):** Defines overall API standards, authentication methods, versioning strategy, and error handling guidelines. **Start here!**
*   **Service-Specific Specs:** Subdirectories or files (often OpenAPI/Swagger YAML/JSON, or Markdown descriptions) detailing the endpoints, request/response schemas, and usage for each service exposing an API (e.g., `aether_core_api.yaml`, `synapse_api.md`).

Adherence to the defined standards is mandatory for all new API development.