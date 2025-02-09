# Bitespeed Identity Service

## Overview

This is a FastAPI-based identity resolution service that manages customer identities across multiple purchases. It uses PostgreSQL as the database.

## Features

- Identifies and links contacts using email and phone number.
- Supports primary and secondary contact relationships.
- Automatically updates linked contacts based on new data.
- Uses FastAPI for a simple and efficient REST API.

## Technologies Used

- **FastAPI** (Backend framework)
- **SQLAlchemy** (ORM for database interactions)
- **PostgreSQL** (Database)
- **Render** (Cloud hosting platform)

## API Endpoints

### Identify Contact

**Endpoint:** `POST /identify`

**Request Body (JSON):**

```json
{
    "email": "test@example.com",
    "phoneNumber": "1234567890"
}
```

**Response:**

```json
{
    "contact": {
        "primaryContactId": 1,
        "emails": ["test@example.com"],
        "phoneNumbers": ["1234567890"],
        "secondaryContactIds": []
    }
}
```

## Installation

### Setup Steps

1. Clone the repository
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the database:
   ```bash
   export DATABASE_URL=postgresql://user:password@localhost/database
   ```
   You will need to install PostgreSQL locally
5. Run the FastAPI server:
   ```bash
   cd src
   python main.py
   ```
6. Access the API at:
   - **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)


## License

This project is licensed under the MIT License.

