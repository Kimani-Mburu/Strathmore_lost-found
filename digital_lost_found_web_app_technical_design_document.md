# Digital Lost & Found Web Application

## 1. Introduction
This document describes the technical design and implementation plan for the **Digital Lost & Found Web Application** developed for a university environment. It is written from the perspective of the **Development Team** and focuses on system architecture, technology choices, core modules, and implementation details.

The system enables students and staff to report, search, verify, and claim lost and found items on campus.

---

## 2. System Overview
The application is a **web-based system** accessible via desktop and mobile browsers. It follows a **client–server architecture** where the frontend communicates with a backend API, which handles business logic and data persistence.

### Key User Roles
- **User (Student/Staff)**: Reports lost items, searches found items, and claims items
- **Admin**: Verifies listed items and manages item status

---

## 3. Technology Stack (Demonstration-Oriented)

The system uses a **simple REST-based framework** suitable for demonstration and rapid development, while maintaining a clean and modern user interface.

### Backend (REST API)
- **Python Flask** (lightweight REST framework)
- Flask-RESTful or standard Flask routes
- JSON-based REST endpoints
- Minimal setup suitable for sprint demonstrations

### Frontend (UI-Focused)
- HTML5, CSS3, JavaScript
- Lightweight framework (React.js or Vanilla JS with components)
- Mobile-first, responsive design
- Emphasis on usability and clarity

### Database
- SQLite or MySQL (simple relational database)
- Easy setup for demos and testing

### Authentication
- Simple email-based login (university email)
- Token-based session handling

---

## 4. System Architecture

### REST-Based Architecture Description
The application uses a **Flask-based REST architecture** designed for simplicity and demonstration:

1. **Web Client (UI)**: Handles user interaction and presentation
2. **Flask REST API Server**: Handles HTTP requests, business logic, and validation
3. **Database and File Storage**: Stores users, item records, and uploaded item photos

The frontend communicates with the Flask backend via RESTful HTTP endpoints using JSON and multipart/form-data.

---

## 5. Core Functional Modules

> **Note:** This system stores **actual item photos** (not placeholders) in the database or file storage and links them directly to item records.

### 5.1 User Authentication Module
- User registration and login using university email
- Token-based authentication
- Role-based access control (User vs Admin)

### 5.2 Lost Item Reporting Module
- Form to submit lost item details
- **Upload and store actual item photos** (JPEG/PNG)
- Server validates image type and size
- Photos stored in database as BLOBs or in file storage with DB references
- Store item category, description, date, and location

### 5.3 Found Item Search Module
- Browse and search items by category
- View item details and status
- Filter results (date and location – optional)

### 5.4 Claim Management Module
- Allow users to mark items as claimed
- Track claim status
- Prevent duplicate claims

### 5.5 Admin Verification Module
- Admin dashboard
- Approve or reject listed items
- Update item visibility and status

### 5.6 Notification Module
- Notify users when a matching item is found
- Email alerts for claim updates

---

## 6. Database Design

### Image Storage Strategy
To support **real item photos**, the system uses one of the following approaches (suitable for demos):

- **Option 1: Database Storage (BLOBs)**
  - Item photos stored directly in the database as binary data
  - Simple setup for demonstrations

- **Option 2: File Storage with References (Recommended)**
  - Photos stored on the server file system
  - Database stores the photo file path or URL
  - Better performance and easier scaling

### Key Tables
- **Users** (user_id, name, email, role)
- **Items** (item_id, title, description, category, photo_path/BLOB, status, date, location)
- **Claims** (claim_id, item_id, user_id, claim_date, status)

Relationships:
- One user can report many items
- One item can have one active claim

---

## 7. API Endpoints (Sample)

- POST /api/login
- POST /api/items/report (multipart/form-data for image upload)
- GET /api/items
- GET /api/items/<id>/photo
- PUT /api/items/<id>/claim
- PUT /api/admin/items/<id>/verify

All endpoints are implemented using Flask routes and secured with basic authentication tokens.

---

## 8. Security Considerations (Basic for Demonstration)

- Image file type and size validation
- Protection against malicious file uploads
- Authentication and role-based authorization
- HTTPS assumed in deployment

---

## 9. Testing Strategy

- **Smoke Testing**: Verify core system functionality after deployment
- **Sanity Testing**: Validate recent changes or bug fixes
- **Regression Testing**: Ensure new features do not break existing ones

---

## 10. Deployment Overview (Demo Setup)

- Flask backend running on a lightweight server
- Frontend served as static files
- Images stored locally on the server
- Suitable for local or classroom demonstration

---

## 11. Conclusion
This document presents a **simple REST-based technical design** for a Digital Lost & Found Web Application, intended for demonstration and learning purposes. While the backend is intentionally lightweight, strong emphasis is placed on a **clean, intuitive, and responsive user interface** to effectively demonstrate usability, Scrum collaboration, and core system functionality.

