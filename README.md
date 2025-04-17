# Cauldron Project

Cauldron is a modular application built on the Frappe Framework, designed to provide a comprehensive suite of tools for various operations.

## Project Structure

- `frappe-bench/` - The Frappe bench directory containing all applications and configurations
- `download-frappe-bench.ps1` - Script to download and set up the Frappe bench
- `setup-frappe-site.ps1` - Script to set up a new site in the Frappe bench
- `create-cauldron-apps.ps1` - Script to create custom Cauldron apps

## Custom Apps

The Cauldron project consists of the following custom apps:

1. **Cauldron Operations Core** (`cauldron_operations_core`) - Core operations module
2. **Cauldron Synapse** (`cauldron_synapse`) - Integration and connectivity module
3. **Cauldron Aegis Protocol** (`cauldron_aegis_protocol`) - Security and protection module
4. **Cauldron Lore** (`cauldron_lore`) - Knowledge management module
5. **Cauldron Command Cauldron** (`cauldron_command_cauldron`) - Command and control module

## Getting Started

1. Run the `download-frappe-bench.ps1` script to download and set up the Frappe bench:
   ```
   powershell -ExecutionPolicy Bypass -File ./download-frappe-bench.ps1
   ```

2. Run the `setup-frappe-site.ps1` script to set up a new site in the Frappe bench:
   ```
   powershell -ExecutionPolicy Bypass -File ./setup-frappe-site.ps1
   ```

3. Run the `create-cauldron-apps.ps1` script to create custom Cauldron apps:
   ```
   powershell -ExecutionPolicy Bypass -File ./create-cauldron-apps.ps1
   ```

4. Follow the instructions in the `frappe-bench/README.md` file to start the development server.

## Development

For development, you'll need to set up a virtual environment and install the required dependencies. Refer to the `frappe-bench/README.md` file for detailed instructions.

## License

MIT
