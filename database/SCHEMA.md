# Database Schema Documentation
# Strathmore University Digital Lost & Found Web Application

## Tables

### Users Table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',  -- 'user' or 'admin'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Items Table
```sql
CREATE TABLE items (
    item_id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    item_type VARCHAR(50) NOT NULL,  -- 'lost' or 'found'
    photo_path VARCHAR(500),
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'verified', 'claimed', 'rejected'
    date DATETIME NOT NULL,
    location VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### Claims Table
```sql
CREATE TABLE claims (
    claim_id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    claim_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(item_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## Relationships
- One User can report many Items
- One Item can have many Claims (but only one active claim)
- One User can make many Claims

## Indexes
- users.email (unique)
- items.user_id
- items.status
- items.is_verified
- claims.item_id
- claims.user_id
