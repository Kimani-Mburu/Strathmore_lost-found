"""
Testing Script for API Endpoints
"""

import requests
import json

BASE_URL = 'http://localhost:5000/api'

# Test data
test_user = {
    'name': 'Test User',
    'email': 'test@strathmore.ac.ke',
    'password': 'testpass123'
}

def test_registration():
    print("\n=== Testing User Registration ===")
    response = requests.post(
        f'{BASE_URL}/auth/register',
        json=test_user
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_login():
    print("\n=== Testing Login ===")
    response = requests.post(
        f'{BASE_URL}/auth/login',
        json={
            'email': test_user['email'],
            'password': test_user['password']
        }
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    return data.get('token')

def test_get_items(token):
    print("\n=== Testing Get Items ===")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{BASE_URL}/items',
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_report_item(token):
    print("\n=== Testing Report Item ===")
    headers = {'Authorization': f'Bearer {token}'}
    
    data = {
        'title': 'Test Lost Phone',
        'description': 'Samsung Galaxy S21 in black case',
        'category': 'electronics',
        'item_type': 'lost',
        'date': '2026-01-15T10:00:00',
        'location': 'Library Main Building'
    }
    
    files = {'photo': open('path/to/test/image.jpg', 'rb')}  # Update path
    
    try:
        response = requests.post(
            f'{BASE_URL}/items/report',
            headers=headers,
            data=data,
            files=files
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    print("Starting API Tests...")
    
    # Run tests
    test_registration()
    token = test_login()
    
    if token:
        test_get_items(token)
        # test_report_item(token)  # Uncomment to test with actual image
    
    print("\n=== Tests Complete ===")
