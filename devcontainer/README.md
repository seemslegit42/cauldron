# Development Container Configuration

This directory contains configuration files for setting up a consistent development environment using Visual Studio Code's Remote - Containers extension or GitHub Codespaces.

## Overview

The development container provides a pre-configured environment with all the necessary tools and dependencies for developing the Cauldron™ project. This ensures that all developers work in the same environment, regardless of their local setup.

## Features

- Pre-installed development tools and dependencies
- Consistent environment across all development machines
- Integration with VS Code extensions
- Automated setup of development databases
- Support for debugging and testing

## Configuration Files

- `.devcontainer.json`: Main configuration file for the development container
- `Dockerfile`: Custom Docker image definition (if applicable)
- `docker-compose.yml`: Multi-container setup (if applicable)
- `post-create.sh`: Script to run after container creation

## Usage

### VS Code Remote - Containers

1. Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension in VS Code
2. Open the Cauldron project folder in VS Code
3. Click on the green button in the bottom-left corner of VS Code
4. Select "Reopen in Container"

### GitHub Codespaces

1. Go to the GitHub repository
2. Click on the "Code" button
3. Select the "Codespaces" tab
4. Click on "New codespace"

## Customization

To customize the development container:

1. Edit the `.devcontainer.json` file to add or modify settings
2. Update the `Dockerfile` if you need to install additional tools
3. Modify the `post-create.sh` script for custom setup steps

## Troubleshooting

If you encounter issues with the development container:

1. Check the logs in the "Remote - Containers" output panel in VS Code
2. Verify that Docker is running correctly on your machine
3. Try rebuilding the container using the "Rebuild Container" command
4. Check for any error messages during container creation