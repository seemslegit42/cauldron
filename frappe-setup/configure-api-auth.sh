#!/bin/bash
# Script to configure Frappe REST API authentication using API Keys and Secrets

set -e

# Default values
CONTAINER_NAME="frappe-web"
SITE_NAME="cauldron.local"
USER_NAME="Administrator"
ENABLE_API_KEYS=true
ENABLE_JWT=true
ENABLE_CORS=true
ALLOWED_ORIGINS="*"
API_KEY_EXPIRY_DAYS=30

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
    --user)
      USER_NAME="$2"
      shift
      shift
      ;;
    --no-api-keys)
      ENABLE_API_KEYS=false
      shift
      ;;
    --no-jwt)
      ENABLE_JWT=false
      shift
      ;;
    --no-cors)
      ENABLE_CORS=false
      shift
      ;;
    --allowed-origins)
      ALLOWED_ORIGINS="$2"
      shift
      shift
      ;;
    --api-key-expiry)
      API_KEY_EXPIRY_DAYS="$2"
      shift
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --container NAME        Container name (default: frappe-web)"
      echo "  --site-name NAME        Site name (default: cauldron.local)"
      echo "  --user NAME             User to create API key for (default: Administrator)"
      echo "  --no-api-keys           Disable API key authentication"
      echo "  --no-jwt                Disable JWT authentication"
      echo "  --no-cors               Disable CORS"
      echo "  --allowed-origins ORIGINS  Comma-separated list of allowed origins (default: *)"
      echo "  --api-key-expiry DAYS   API key expiry in days (default: 30)"
      echo "  --help                  Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Configuring Frappe REST API authentication with the following settings:"
echo "  Container: $CONTAINER_NAME"
echo "  Site: $SITE_NAME"
echo "  User: $USER_NAME"
echo "  Enable API Keys: $ENABLE_API_KEYS"
echo "  Enable JWT: $ENABLE_JWT"
echo "  Enable CORS: $ENABLE_CORS"
echo "  Allowed Origins: $ALLOWED_ORIGINS"
echo "  API Key Expiry: $API_KEY_EXPIRY_DAYS days"
echo ""

# Create a Python script to configure API authentication
TEMP_DIR=$(mktemp -d)
cat > "$TEMP_DIR/configure_api_auth.py" << EOF
#!/usr/bin/env python3
import os
import sys
import frappe
import json
import random
import string
from datetime import datetime, timedelta

def configure_api_auth():
    """Configure API authentication in Frappe"""
    
    # Parameters
    user_name = "$USER_NAME"
    enable_api_keys = $ENABLE_API_KEYS
    enable_jwt = $ENABLE_JWT
    enable_cors = $ENABLE_CORS
    allowed_origins = "$ALLOWED_ORIGINS"
    api_key_expiry_days = $API_KEY_EXPIRY_DAYS
    
    # Step 1: Update system settings
    print("Updating system settings...")
    
    try:
        doc = frappe.get_doc("System Settings")
        
        # Enable/disable API access
        doc.enable_api_keys = 1 if enable_api_keys else 0
        
        # Enable/disable JWT
        doc.enable_jwt_auth = 1 if enable_jwt else 0
        
        # Set JWT expiry
        doc.jwt_expiry = 3600  # 1 hour in seconds
        
        # Enable/disable CORS
        doc.enable_cors = 1 if enable_cors else 0
        
        # Set allowed origins
        if enable_cors:
            doc.allow_cors = allowed_origins
        
        # Save the settings
        doc.save()
        frappe.db.commit()
        
        print("System settings updated successfully")
    except Exception as e:
        print(f"Error updating system settings: {str(e)}")
        return False
    
    # Step 2: Create API key for the user
    if enable_api_keys:
        print(f"Creating API key for user: {user_name}")
        
        try:
            # Check if user exists
            if not frappe.db.exists("User", user_name):
                print(f"Error: User '{user_name}' does not exist")
                return False
            
            # Check if user already has an API key
            existing_keys = frappe.get_all(
                "API Key",
                filters={"user": user_name, "enabled": 1},
                fields=["name", "api_key", "api_secret"]
            )
            
            if existing_keys:
                print(f"User '{user_name}' already has {len(existing_keys)} API key(s)")
                for key in existing_keys:
                    print(f"  - Name: {key.name}")
                    print(f"    API Key: {key.api_key}")
                    if key.api_secret:
                        print(f"    API Secret: {key.api_secret}")
                    print("")
            else:
                # Generate API key and secret
                api_key = generate_api_key()
                api_secret = generate_api_secret()
                
                # Create API key document
                api_key_doc = frappe.new_doc("API Key")
                api_key_doc.user = user_name
                api_key_doc.api_key = api_key
                api_key_doc.api_secret = api_secret
                api_key_doc.enabled = 1
                
                # Set expiry date
                if api_key_expiry_days > 0:
                    api_key_doc.expires_on = datetime.now() + timedelta(days=api_key_expiry_days)
                
                # Save the API key
                api_key_doc.insert()
                frappe.db.commit()
                
                print(f"API key created successfully for user '{user_name}'")
                print(f"  - Name: {api_key_doc.name}")
                print(f"  - API Key: {api_key}")
                print(f"  - API Secret: {api_secret}")
                if api_key_expiry_days > 0:
                    print(f"  - Expires on: {api_key_doc.expires_on}")
                print("")
                print("IMPORTANT: Save these credentials securely. The API secret will not be shown again.")
        except Exception as e:
            print(f"Error creating API key: {str(e)}")
            return False
    
    # Step 3: Create a sample client script for API authentication
    print("Creating sample API authentication scripts...")
    
    sample_dir = os.path.join(os.path.dirname(frappe.get_site_path()), "api_samples")
    os.makedirs(sample_dir, exist_ok=True)
    
    # Create sample Python script
    with open(os.path.join(sample_dir, "api_auth_sample.py"), "w") as f:
        f.write("""#!/usr/bin/env python3
import requests
import json
import base64
import hmac
import hashlib
import time

# API credentials
API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"

# Frappe site URL
SITE_URL = "http://localhost:8000"

def get_auth_headers():
    """Generate authentication headers for API requests"""
    
    # Current timestamp
    timestamp = str(int(time.time()))
    
    # Create signature
    message = timestamp + "|" + API_KEY
    signature = hmac.new(
        API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    # Return headers
    return {
        "Authorization": f"token {API_KEY}:{signature}:{timestamp}"
    }

def api_request(endpoint, method="GET", data=None):
    """Make an API request to Frappe"""
    
    # Build URL
    url = f"{SITE_URL}/api/method/{endpoint}"
    
    # Get authentication headers
    headers = get_auth_headers()
    headers["Content-Type"] = "application/json"
    
    # Make request
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    else:
        raise ValueError(f"Unsupported method: {method}")
    
    # Return response
    return response.json()

# Example: Get list of users
def get_users():
    return api_request("frappe.client.get_list", "POST", {
        "doctype": "User",
        "fields": ["name", "full_name", "email", "enabled"]
    })

# Example: Create a new customer
def create_customer(customer_name, email):
    return api_request("frappe.client.insert", "POST", {
        "doc": {
            "doctype": "Customer",
            "customer_name": customer_name,
            "email": email
        }
    })

if __name__ == "__main__":
    # Example usage
    print("Getting list of users...")
    users = get_users()
    print(json.dumps(users, indent=2))
    
    # Uncomment to create a customer
    # print("Creating a new customer...")
    # customer = create_customer("Test Customer", "test@example.com")
    # print(json.dumps(customer, indent=2))
""")
    
    # Create sample JavaScript script
    with open(os.path.join(sample_dir, "api_auth_sample.js"), "w") as f:
        f.write("""// API credentials
const API_KEY = "YOUR_API_KEY";
const API_SECRET = "YOUR_API_SECRET";

// Frappe site URL
const SITE_URL = "http://localhost:8000";

/**
 * Generate authentication headers for API requests
 * @returns {Object} Headers object
 */
function getAuthHeaders() {
  // Current timestamp
  const timestamp = Math.floor(Date.now() / 1000).toString();
  
  // Create signature
  const message = timestamp + "|" + API_KEY;
  const signature = CryptoJS.HmacSHA256(message, API_SECRET).toString();
  
  // Return headers
  return {
    "Authorization": `token ${API_KEY}:${signature}:${timestamp}`
  };
}

/**
 * Make an API request to Frappe
 * @param {string} endpoint - API endpoint
 * @param {string} method - HTTP method (GET, POST)
 * @param {Object} data - Request data (for POST)
 * @returns {Promise} Promise resolving to response data
 */
async function apiRequest(endpoint, method = "GET", data = null) {
  // Build URL
  const url = `${SITE_URL}/api/method/${endpoint}`;
  
  // Get authentication headers
  const headers = {
    ...getAuthHeaders(),
    "Content-Type": "application/json"
  };
  
  // Request options
  const options = {
    method,
    headers
  };
  
  // Add body for POST requests
  if (method === "POST" && data) {
    options.body = JSON.stringify(data);
  }
  
  // Make request
  const response = await fetch(url, options);
  return response.json();
}

// Example: Get list of users
async function getUsers() {
  return apiRequest("frappe.client.get_list", "POST", {
    doctype: "User",
    fields: ["name", "full_name", "email", "enabled"]
  });
}

// Example: Create a new customer
async function createCustomer(customerName, email) {
  return apiRequest("frappe.client.insert", "POST", {
    doc: {
      doctype: "Customer",
      customer_name: customerName,
      email: email
    }
  });
}

// Example usage
async function main() {
  try {
    console.log("Getting list of users...");
    const users = await getUsers();
    console.log(users);
    
    // Uncomment to create a customer
    // console.log("Creating a new customer...");
    // const customer = await createCustomer("Test Customer", "test@example.com");
    // console.log(customer);
  } catch (error) {
    console.error("API request failed:", error);
  }
}

// Call main function
main();
""")
    
    # Create sample cURL script
    with open(os.path.join(sample_dir, "api_auth_sample.sh"), "w") as f:
        f.write("""#!/bin/bash
# API credentials
API_KEY="YOUR_API_KEY"
API_SECRET="YOUR_API_SECRET"

# Frappe site URL
SITE_URL="http://localhost:8000"

# Generate authentication headers
generate_auth_headers() {
  # Current timestamp
  TIMESTAMP=$(date +%s)
  
  # Create signature
  MESSAGE="${TIMESTAMP}|${API_KEY}"
  SIGNATURE=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$API_SECRET" | awk '{print $2}')
  
  # Return authorization header
  echo "Authorization: token ${API_KEY}:${SIGNATURE}:${TIMESTAMP}"
}

# Example: Get list of users
get_users() {
  AUTH_HEADER=$(generate_auth_headers)
  
  curl -s -X POST \\
    -H "$AUTH_HEADER" \\
    -H "Content-Type: application/json" \\
    -d '{"doctype": "User", "fields": ["name", "full_name", "email", "enabled"]}' \\
    "$SITE_URL/api/method/frappe.client.get_list" | jq
}

# Example: Create a new customer
create_customer() {
  AUTH_HEADER=$(generate_auth_headers)
  
  curl -s -X POST \\
    -H "$AUTH_HEADER" \\
    -H "Content-Type: application/json" \\
    -d '{"doc": {"doctype": "Customer", "customer_name": "Test Customer", "email": "test@example.com"}}' \\
    "$SITE_URL/api/method/frappe.client.insert" | jq
}

# Example usage
echo "Getting list of users..."
get_users

# Uncomment to create a customer
# echo "Creating a new customer..."
# create_customer
""")
    
    print(f"Sample API authentication scripts created in {sample_dir}")
    print("  - api_auth_sample.py (Python)")
    print("  - api_auth_sample.js (JavaScript)")
    print("  - api_auth_sample.sh (cURL/Bash)")
    
    # Step 4: Create API documentation
    print("Creating API documentation...")
    
    with open(os.path.join(sample_dir, "API_DOCUMENTATION.md"), "w") as f:
        f.write("""# Frappe REST API Authentication

## Overview

This document provides information on how to authenticate with the Frappe REST API using API Keys and Secrets.

## Authentication Methods

Frappe supports the following authentication methods:

1. **API Key Authentication**: Using API Key and Secret
2. **JWT Authentication**: Using JSON Web Tokens
3. **Basic Authentication**: Using username and password (not recommended for production)

## API Key Authentication

### Prerequisites

- API Key and Secret for your user
- API Key authentication enabled in System Settings

### Authentication Process

1. Generate a signature using your API Secret
2. Include the API Key, signature, and timestamp in the Authorization header
3. Make your API request

### Authentication Header Format

```
Authorization: token {api_key}:{signature}:{timestamp}
```

Where:
- `{api_key}` is your API Key
- `{signature}` is an HMAC-SHA256 hash of `{timestamp}|{api_key}` using your API Secret as the key
- `{timestamp}` is the current Unix timestamp (seconds since epoch)

### Example Code

See the sample scripts in this directory for examples of how to authenticate with the Frappe REST API:

- `api_auth_sample.py` (Python)
- `api_auth_sample.js` (JavaScript)
- `api_auth_sample.sh` (cURL/Bash)

## JWT Authentication

### Prerequisites

- Valid username and password
- JWT authentication enabled in System Settings

### Authentication Process

1. Obtain a JWT token by authenticating with your username and password
2. Include the JWT token in the Authorization header for subsequent requests

### Obtaining a JWT Token

```
POST /api/method/frappe.auth.get_logged_user
Content-Type: application/json
Authorization: Basic {base64_encoded_credentials}

{}
```

Where `{base64_encoded_credentials}` is the Base64 encoding of `username:password`.

### Using the JWT Token

```
GET /api/resource/User
Authorization: Bearer {jwt_token}
```

## API Endpoints

Frappe provides several types of API endpoints:

### Resource API

Access DocTypes directly:

- `GET /api/resource/{doctype}` - Get a list of documents
- `GET /api/resource/{doctype}/{name}` - Get a specific document
- `POST /api/resource/{doctype}` - Create a new document
- `PUT /api/resource/{doctype}/{name}` - Update a document
- `DELETE /api/resource/{doctype}/{name}` - Delete a document

### Method API

Call Frappe methods directly:

- `POST /api/method/{method_name}` - Call a whitelisted method

### Common Client Methods

Frappe provides several common client methods:

- `frappe.client.get_list` - Get a list of documents
- `frappe.client.get` - Get a specific document
- `frappe.client.insert` - Create a new document
- `frappe.client.set_value` - Update a document field
- `frappe.client.delete` - Delete a document

## Security Best Practices

1. **Keep API Keys Secure**: Never expose your API Secret in client-side code
2. **Use HTTPS**: Always use HTTPS for API requests in production
3. **Set Expiry Dates**: Set expiry dates for API Keys
4. **Limit Permissions**: Create dedicated API users with limited permissions
5. **Implement Rate Limiting**: Use a proxy server to implement rate limiting
6. **Monitor API Usage**: Regularly review API logs for suspicious activity
7. **Rotate API Keys**: Periodically rotate API Keys and Secrets

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Check that your API Key and Secret are correct
2. **Signature Mismatch**: Ensure your timestamp is in seconds since epoch
3. **API Key Expired**: Check the expiry date of your API Key
4. **Permission Denied**: Ensure your user has the necessary permissions
5. **CORS Issues**: Check that CORS is enabled and your origin is allowed

### Debugging Tips

1. Check the Frappe error logs for detailed error messages
2. Verify that your signature generation is correct
3. Ensure your timestamp is current (within a few minutes)
4. Check that your API Key is enabled
5. Verify that API authentication is enabled in System Settings
""")
    
    print(f"API documentation created in {sample_dir}/API_DOCUMENTATION.md")
    
    print("API authentication configuration completed successfully!")
    return True

def generate_api_key():
    """Generate a random API key"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def generate_api_secret():
    """Generate a random API secret"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=64))

if __name__ == "__main__":
    frappe.init(site="$SITE_NAME")
    frappe.connect()
    
    try:
        result = configure_api_auth()
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

# Copy the script to the container
docker cp "$TEMP_DIR/configure_api_auth.py" "$CONTAINER_NAME:/tmp/configure_api_auth.py"

# Make the script executable
docker exec "$CONTAINER_NAME" bash -c "chmod +x /tmp/configure_api_auth.py"

# Run the script in the container
echo "Configuring API authentication in the container..."
docker exec -u frappe "$CONTAINER_NAME" bash -c "cd /home/frappe/frappe-bench && python /tmp/configure_api_auth.py"

# Clean up
rm -rf "$TEMP_DIR"

echo "API authentication configuration completed successfully!"
echo ""
echo "You can now use the API Key and Secret to authenticate with the Frappe REST API."
echo "Sample API authentication scripts and documentation have been created in the api_samples directory."
