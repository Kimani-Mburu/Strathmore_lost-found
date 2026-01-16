"""API Documentation for Strathmore University Digital Lost & Found Web Application"""

# API Endpoints Documentation

## Authentication Endpoints

### Register User
- **Endpoint**: POST /api/auth/register
- **Description**: Register a new user
- **Request Body**:
  ```json
  {
    "name": "John Doe",
    "email": "john.doe@strathmore.ac.ke",
    "password": "secure_password"
  }
  ```
- **Response**: 201 Created

### Login
- **Endpoint**: POST /api/auth/login
- **Description**: User login
- **Request Body**:
  ```json
  {
    "email": "john.doe@strathmore.ac.ke",
    "password": "secure_password"
  }
  ```
- **Response**: 200 OK with auth token

### Get Profile
- **Endpoint**: GET /api/auth/profile
- **Description**: Get current user profile
- **Headers**: Authorization: Bearer {token}
- **Response**: 200 OK

## Items Endpoints

### Report Item
- **Endpoint**: POST /api/items/report
- **Description**: Report lost or found item with photo
- **Headers**: Authorization: Bearer {token}
- **Form Data**:
  - title: string
  - description: string
  - category: string
  - item_type: 'lost' or 'found'
  - date: ISO datetime
  - location: string
  - photo: file (image/jpeg, image/png)
- **Response**: 201 Created

### Get Items
- **Endpoint**: GET /api/items
- **Description**: Get all verified items (paginated)
- **Query Parameters**:
  - category: string (optional)
  - item_type: 'lost' or 'found' (optional)
  - page: integer (default: 1)
- **Response**: 200 OK

### Get Item Details
- **Endpoint**: GET /api/items/{item_id}
- **Description**: Get specific item details
- **Response**: 200 OK

### Get Item Photo
- **Endpoint**: GET /api/items/{item_id}/photo
- **Description**: Get item photo
- **Response**: 200 OK (image file)

### Claim Item
- **Endpoint**: POST /api/items/{item_id}/claim
- **Description**: Claim a found item
- **Headers**: Authorization: Bearer {token}
- **Request Body**:
  ```json
  {
    "notes": "This is my lost item"
  }
  ```
- **Response**: 201 Created

## Admin Endpoints

### Get Pending Items
- **Endpoint**: GET /api/admin/items/pending
- **Description**: Get items awaiting verification
- **Headers**: Authorization: Bearer {token}, Admin role required
- **Response**: 200 OK

### Verify Item
- **Endpoint**: PUT /api/admin/items/{item_id}/verify
- **Description**: Approve or reject an item
- **Headers**: Authorization: Bearer {token}, Admin role required
- **Request Body**:
  ```json
  {
    "action": "approve" or "reject"
  }
  ```
- **Response**: 200 OK

### Update Item Status
- **Endpoint**: PUT /api/admin/items/{item_id}/status
- **Description**: Update item status
- **Headers**: Authorization: Bearer {token}, Admin role required
- **Request Body**:
  ```json
  {
    "status": "pending|verified|claimed|rejected"
  }
  ```
- **Response**: 200 OK
