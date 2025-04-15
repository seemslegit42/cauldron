"""
Test script for the HITL API

This script tests the HITL API endpoints for creating, retrieving, and responding to HITL requests.
"""

import os
import sys
import uuid
import requests
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Base URL for API
BASE_URL = "http://localhost:8000/api/v1"

def test_create_hitl_request():
    """Test creating a HITL request"""
    print("Testing create HITL request...")
    
    # Create a task first
    task_data = {
        "task_type": "test_task",
        "task_description": "Test task for HITL",
        "priority": 5,
        "input_data": {"test": "data"}
    }
    
    task_response = requests.post(f"{BASE_URL}/tasks", json=task_data)
    
    if task_response.status_code != 200:
        print(f"Failed to create task: {task_response.text}")
        return
    
    task_id = task_response.json().get("task_id")
    print(f"Created task with ID: {task_id}")
    
    # Create HITL request
    hitl_data = {
        "task_id": task_id,
        "request_type": "approval",
        "request_description": "Please approve this test action",
        "options": [
            {
                "option_id": "approve",
                "option_text": "Approve",
                "option_details": {"action": "test_action"}
            },
            {
                "option_id": "reject",
                "option_text": "Reject",
                "option_details": {"reason": "Test rejection"}
            }
        ],
        "timeout_seconds": 3600,
        "urgency": "normal"
    }
    
    hitl_response = requests.post(f"{BASE_URL}/hitl/requests", json=hitl_data)
    
    if hitl_response.status_code != 200:
        print(f"Failed to create HITL request: {hitl_response.text}")
        return
    
    hitl_request = hitl_response.json()
    request_id = hitl_request.get("request_id")
    print(f"Created HITL request with ID: {request_id}")
    print(json.dumps(hitl_request, indent=2))
    
    return request_id, task_id

def test_get_hitl_requests():
    """Test getting all HITL requests"""
    print("\nTesting get all HITL requests...")
    
    response = requests.get(f"{BASE_URL}/hitl/requests")
    
    if response.status_code != 200:
        print(f"Failed to get HITL requests: {response.text}")
        return
    
    hitl_requests = response.json()
    print(f"Found {len(hitl_requests)} HITL requests")
    
    if hitl_requests:
        print(f"First HITL request: {json.dumps(hitl_requests[0], indent=2)}")
    
    return hitl_requests

def test_get_hitl_request(request_id):
    """Test getting a specific HITL request"""
    print(f"\nTesting get HITL request {request_id}...")
    
    response = requests.get(f"{BASE_URL}/hitl/requests/{request_id}")
    
    if response.status_code != 200:
        print(f"Failed to get HITL request: {response.text}")
        return
    
    hitl_request = response.json()
    print(f"HITL request details: {json.dumps(hitl_request, indent=2)}")
    
    return hitl_request

def test_respond_to_hitl_request(request_id):
    """Test responding to a HITL request"""
    print(f"\nTesting respond to HITL request {request_id}...")
    
    response_data = {
        "response": "approve",
        "response_details": {"notes": "Test approval"},
        "human_id": "test_user"
    }
    
    response = requests.post(f"{BASE_URL}/hitl/requests/{request_id}/respond", json=response_data)
    
    if response.status_code != 200:
        print(f"Failed to respond to HITL request: {response.text}")
        return
    
    updated_request = response.json()
    print(f"Updated HITL request: {json.dumps(updated_request, indent=2)}")
    
    return updated_request

def test_get_task_hitl_requests(task_id):
    """Test getting HITL requests for a task"""
    print(f"\nTesting get HITL requests for task {task_id}...")
    
    response = requests.get(f"{BASE_URL}/hitl/requests/task/{task_id}")
    
    if response.status_code != 200:
        print(f"Failed to get task HITL requests: {response.text}")
        return
    
    hitl_requests = response.json()
    print(f"Found {len(hitl_requests)} HITL requests for task {task_id}")
    
    if hitl_requests:
        print(f"First HITL request: {json.dumps(hitl_requests[0], indent=2)}")
    
    return hitl_requests

def test_get_hitl_requests_by_status(status="pending"):
    """Test getting HITL requests by status"""
    print(f"\nTesting get HITL requests with status {status}...")
    
    response = requests.get(f"{BASE_URL}/hitl/requests/status/{status}")
    
    if response.status_code != 200:
        print(f"Failed to get HITL requests by status: {response.text}")
        return
    
    hitl_requests = response.json()
    print(f"Found {len(hitl_requests)} HITL requests with status {status}")
    
    if hitl_requests:
        print(f"First HITL request: {json.dumps(hitl_requests[0], indent=2)}")
    
    return hitl_requests

def test_get_hitl_requests_by_type(request_type="approval"):
    """Test getting HITL requests by type"""
    print(f"\nTesting get HITL requests with type {request_type}...")
    
    response = requests.get(f"{BASE_URL}/hitl/requests/type/{request_type}")
    
    if response.status_code != 200:
        print(f"Failed to get HITL requests by type: {response.text}")
        return
    
    hitl_requests = response.json()
    print(f"Found {len(hitl_requests)} HITL requests with type {request_type}")
    
    if hitl_requests:
        print(f"First HITL request: {json.dumps(hitl_requests[0], indent=2)}")
    
    return hitl_requests

def run_all_tests():
    """Run all HITL API tests"""
    # Create a HITL request
    request_id, task_id = test_create_hitl_request()
    
    if not request_id:
        print("Failed to create HITL request, aborting tests")
        return
    
    # Get all HITL requests
    test_get_hitl_requests()
    
    # Get specific HITL request
    test_get_hitl_request(request_id)
    
    # Get HITL requests by status
    test_get_hitl_requests_by_status("pending")
    
    # Get HITL requests by type
    test_get_hitl_requests_by_type("approval")
    
    # Get HITL requests for a task
    test_get_task_hitl_requests(task_id)
    
    # Respond to HITL request
    test_respond_to_hitl_request(request_id)
    
    # Get HITL requests by status after response
    test_get_hitl_requests_by_status("completed")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    run_all_tests()