#!/bin/bash

# Cauldron™ sEOS Development Environment Setup Script
# Purpose: Automate the docker-compose setup for local development.
# Warning: May or may not appease the resident digital spirits. Use with caution and coffee.

# --- Configuration ---
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # Assumes script is in project root
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
ENV_EXAMPLE_FILE="${PROJECT_ROOT}/secrets.env.example" # Adjust if your main example file is elsewhere
ENV_FILE="${PROJECT_ROOT}/.env"
FRONTEND_DIR="${PROJECT_ROOT}/manifold"

# --- Functions ---
check_command() {
  if ! command -v $1 &> /dev/null; then
    echo "Error: Required command '$1' not found. Please install it."
    exit 1
  fi
}

print_step() {
  echo ""
  echo "----------------------------------------"
  echo ">> $1"
  echo "----------------------------------------"
}

print_warning() {
  echo "⚠️ Warning: $1"
}

print_success() {
  echo "✅ Success: $1"
}

print_info() {
  echo "ℹ️ Info: $1"
}

# --- Prerequisites Check ---
print_step "Checking Prerequisites..."
check_command "docker"
check_command "docker-compose"
check_command "git" # Less critical for setup, but good to have
check_command "node" # For frontend setup outside Docker (if needed)
check_command "yarn" # Or npm, depending on frontend setup [cite: cauldron/manifold/README.md]
print_success "Basic prerequisites seem to be installed."

# --- Environment Setup ---
print_step "Setting up Environment Variables..."
if [ ! -f "$ENV_FILE" ]; then
  if [ -f "$ENV_EXAMPLE_FILE" ]; then
    print_warning ".env file not found. Copying from ${ENV_EXAMPLE_FILE}."
    cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
    print_info "IMPORTANT: Please review and update the placeholder values in '.env' with your actual secrets and configuration!"
    # Optional: Pause script to allow editing? Or just warn loudly.
    read -p "Press [Enter] after you have updated the .env file..."
  else
    print_warning ".env file not found, and no ${ENV_EXAMPLE_FILE} found to copy."
    print_info "Please create a '.env' file manually with the necessary environment variables."
    exit 1
  fi
else
  print_info ".env file already exists. Assuming it's configured correctly."
fi
# Exporting might be needed depending on how docker-compose consumes it, but usually it reads .env automatically
# export $(grep -v '^#' $ENV_FILE | xargs)

# --- Docker Compose Build & Run ---
print_step "Building and Starting Docker Services..."
echo "This might take a while, especially the first time. Go grab that coffee."

# Navigate to the directory containing the docker-compose file if necessary
# cd "$(dirname "$COMPOSE_FILE")" || exit 1 # Handled by using absolute path below

docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up --build -d

if [ $? -ne 0 ]; then
  echo "Error: docker-compose up failed. Check the output above for details."
  exit 1
fi

print_success "Docker containers should be starting up in the background."
print_info "Run 'docker-compose ps' to check status and 'docker-compose logs -f' to view logs."

# --- Frontend Dependency Installation ---
# This assumes you want to install frontend deps locally for development/IDE integration
# If frontend runs entirely within Docker, this might be handled in its Dockerfile build
print_step "Setting up Frontend Dependencies (Manifold)..."
if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package.json" ]; then
  cd "$FRONTEND_DIR" || exit 1
  echo "Running 'yarn install' in ${FRONTEND_DIR}..." # Or npm install
  yarn install # Or npm install
  if [ $? -ne 0 ]; then
    print_warning "Frontend dependency installation failed. You might need to run it manually in '${FRONTEND_DIR}'."
  else
    print_success "Frontend dependencies installed."
  fi
  cd "$PROJECT_ROOT" || exit 1 # Return to project root
else
  print_warning "Frontend directory or package.json not found at ${FRONTEND_DIR}. Skipping dependency installation."
fi

# --- Post-Setup Notes ---
print_step "Initial Setup Complete!"
print_info "The Docker containers should be running."
print_info "Next Steps:"
print_info "1. Verify container status: 'docker-compose ps'"
print_info "2. Check logs for errors: 'docker-compose logs -f [service_name]'"
print_info "3. Database Initialization: PostgreSQL should be initialized with extensions through the docker entrypoint scripts. Verify with: 'docker-compose exec postgres psql -U postgres -c \"\\dx\"'"
print_info "4. Frappe Setup: Run the Frappe bench setup inside the container: 'docker-compose exec frappe-bench bash -c \"cd /workspaces/cauldron && ./scripts/setup_frappe.sh\"'"
print_info "5. AetherCore Setup: Database migrations need to be run: 'docker-compose exec aethercore python -m aether_core.scripts.init_db'"
print_info "6. Frontend Dev Server: The Manifold UI should be available at http://localhost:3000"
print_info "7. API Access: Services are exposed through Traefik at http://localhost:80 with the Traefik dashboard at http://localhost:8081"
print_info "8. Required Environment Variables: Make sure your .env file includes all necessary variables for AI services (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.) if you need those features"

echo ""
echo "Good luck, brave developer. May your code compile and your spirits remain unbroken."

exit 0