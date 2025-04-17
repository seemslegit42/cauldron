# Frappe REST API Authentication Guide

## Overview

This guide explains how to configure and use REST API authentication in Frappe for the Cauldron project. Frappe provides several authentication methods for its REST API, including API Keys, JWT, and Basic Authentication.

## Configuration

### Enabling API Authentication

To enable API authentication in Frappe, run the provided script:

```bash
chmod +x configure-api-auth.sh
./configure-api-auth.sh
```

This script will:

1. Enable API Key authentication in System Settings
2. Enable JWT authentication in System Settings
3. Configure CORS settings for cross-origin requests
4. Create an API Key for the specified user
5. Generate sample API authentication scripts
6. Create API documentation

### Configuration Options

You can customize the API authentication configuration with the following options:

```bash
./configure-api-auth.sh --user "ApiUser" --api-key-expiry 90 --allowed-origins "https://example.com,https://app.example.com"
```

Available options:

- `--container NAME`: Container name (default: frappe-web)
- `--site-name NAME`: Site name (default: cauldron.local)
- `--user NAME`: User to create API key for (default: Administrator)
- `--no-api-keys`: Disable API key authentication
- `--no-jwt`: Disable JWT authentication
- `--no-cors`: Disable CORS
- `--allowed-origins ORIGINS`: Comma-separated list of allowed origins (default: *)
- `--api-key-expiry DAYS`: API key expiry in days (default: 30)

## Authentication Methods

### 1. API Key Authentication

API Key authentication uses a key-secret pair to authenticate API requests. This is the recommended method for server-to-server communication.

#### How It Works

1. You generate an API Key and Secret for a user
2. For each API request:
   - Generate a signature using the API Secret
   - Include the API Key, signature, and timestamp in the Authorization header
   - Make your API request

#### Authentication Header Format

```
Authorization: token {api_key}:{signature}:{timestamp}
```

Where:
- `{api_key}` is your API Key
- `{signature}` is an HMAC-SHA256 hash of `{timestamp}|{api_key}` using your API Secret as the key
- `{timestamp}` is the current Unix timestamp (seconds since epoch)

#### Example in Python

```python
import requests
import hmac
import hashlib
import time

# API credentials
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"

# Generate authentication headers
def get_auth_headers():
    timestamp = str(int(time.time()))
    message = timestamp + "|" + API_KEY
    signature = hmac.new(
        API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return {
        "Authorization": f"token {API_KEY}:{signature}:{timestamp}"
    }

# Make API request
def api_request(endpoint, method="GET", data=None):
    url = f"http://localhost:8000/api/method/{endpoint}"
    headers = get_auth_headers()
    headers["Content-Type"] = "application/json"
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    
    return response.json()

# Example: Get list of users
users = api_request("frappe.client.get_list", "POST", {
    "doctype": "User",
    "fields": ["name", "full_name", "email"]
})
```

### 2. JWT Authentication

JWT (JSON Web Token) authentication is suitable for web applications and mobile apps where users log in with their credentials.

#### How It Works

1. User logs in with username and password to obtain a JWT token
2. The JWT token is included in subsequent API requests
3. The token expires after a configured time (default: 1 hour)

#### Obtaining a JWT Token

```
POST /api/method/frappe.auth.get_logged_user
Content-Type: application/json
Authorization: Basic {base64_encoded_credentials}

{}
```

Where `{base64_encoded_credentials}` is the Base64 encoding of `username:password`.

#### Using the JWT Token

```
GET /api/resource/User
Authorization: Bearer {jwt_token}
```

#### Example in JavaScript

```javascript
// Login and get JWT token
async function login(username, password) {
    const credentials = btoa(`${username}:${password}`);
    
    const response = await fetch('/api/method/frappe.auth.get_logged_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Basic ${credentials}`
        },
        body: JSON.stringify({})
    });
    
    // JWT token is set in cookies
    return response.json();
}

// Make API request with JWT
async function apiRequest(endpoint, method = 'GET', data = null) {
    const url = `/api/method/${endpoint}`;
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include' // Include cookies for JWT
    };
    
    if (method === 'POST' && data) {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    return response.json();
}

// Example usage
async function main() {
    await login('administrator', 'password');
    
    const users = await apiRequest('frappe.client.get_list', 'POST', {
        doctype: 'User',
        fields: ['name', 'full_name', 'email']
    });
    
    console.log(users);
}
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

## Creating Custom API Endpoints

You can create custom API endpoints in Frappe by defining whitelisted methods in your application.

### Example: Custom API Endpoint

```python
# In your_app/api.py
import frappe
from frappe import _
from frappe.utils import nowdate
from frappe.utils.response import build_response

@frappe.whitelist()
def get_invoices_summary():
    """Get a summary of invoices"""
    
    # Check if user has permission
    if not frappe.has_permission("Invoice", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    # Get invoice data
    invoices = frappe.get_all(
        "Invoice",
        filters={"posting_date": [">=", nowdate()]},
        fields=["name", "customer", "grand_total", "status"]
    )
    
    # Calculate summary
    total_amount = sum(invoice.grand_total for invoice in invoices)
    status_counts = {}
    for invoice in invoices:
        status = invoice.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Return response
    return {
        "total_invoices": len(invoices),
        "total_amount": total_amount,
        "status_counts": status_counts,
        "invoices": invoices
    }
```

### Calling the Custom API Endpoint

```python
import requests

# API credentials
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"

# Get authentication headers
headers = get_auth_headers()
headers["Content-Type"] = "application/json"

# Call the custom API endpoint
response = requests.post(
    "http://localhost:8000/api/method/your_app.api.get_invoices_summary",
    headers=headers
)

# Print the response
print(response.json())
```

## Security Best Practices

1. **Use Dedicated API Users**: Create dedicated users for API access with minimal permissions
2. **Set API Key Expiry**: Always set an expiry date for API keys
3. **Use HTTPS**: Always use HTTPS for API requests in production
4. **Implement Rate Limiting**: Use a proxy server to implement rate limiting
5. **Monitor API Usage**: Regularly review API logs for suspicious activity
6. **Rotate API Keys**: Periodically rotate API keys and secrets
7. **Validate Input**: Always validate and sanitize input data
8. **Check Permissions**: Always check permissions before performing operations
9. **Use Whitelisting**: Only expose methods that are explicitly whitelisted
10. **Limit Response Data**: Only return the data that is needed

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

## References

- [Frappe REST API Documentation](https://frappeframework.com/docs/user/en/api/rest)
- [Frappe Authentication](https://frappeframework.com/docs/user/en/api/rest#authentication)
- [Frappe Whitelisting](https://frappeframework.com/docs/user/en/api/python-api#whitelisting)
