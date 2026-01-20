# User Management System

A comprehensive FastAPI-based User Management System built with modern Python technologies for managing employees, departments, jobs, and user authentication with role-based access control.

## 🎯 Project Overview

The User Management System is designed to provide a robust API for managing organizational structure, employee records, and user authentication. It features employee lifecycle management, secure password handling, JWT-based authentication, and comprehensive database migrations.

### Key Features

- **User Authentication**: Secure login and signup with JWT tokens
- **Employee Management**: Full CRUD operations for employee records
- **Organizational Structure**: Manage departments and job positions
- **Employee Status Tracking**: Track employee employment status (Full Time, Part Time, Contract, etc.)
- **Role-Based Access Control**: Admin functionality for creating and managing users
- **Password Security**: Strong password requirements with Argon2 hashing
- **Database Migrations**: Alembic-based version control for database schema
- **Comprehensive Testing**: Unit and integration tests for all endpoints

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.128.0+
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: JWT (PyJWT 2.10.1+)
- **Phone Validation**: phonenumbers 9.0.22+
- **Database Migrations**: Alembic 1.17.2+
- **Python**: 3.13+

## 📋 Project Structure

```
.
├── alembic/                 # Database migrations
│   ├── versions/            # Migration scripts
│   ├── env.py
│   └── script.py.mako
├── app/                     # Main application
│   ├── main.py             # FastAPI app initialization
│   ├── schemas.py          # Pydantic schemas for request/response
│   ├── dependencies/       # Dependency injection
│   │   ├── database.py     # Database configuration
│   │   └── setting.py      # Application settings
│   ├── models/             # SQLAlchemy models
│   │   └── user.py         # User, Employee, Department, Job models
│   └── routers/            # API route handlers
│       ├── auth.py         # Authentication endpoints
│       ├── user.py         # User management endpoints
│       └── department.py   # Department management endpoints
├── tests/                  # Test suite
│   ├── conftest.py        # pytest configuration and fixtures
│   ├── test_main.py       # Main application tests
│   ├── test_user_and_auth.py    # User and auth tests
│   └── test_department_and_job.py   # Department/job tests
├── pyproject.toml         # Project dependencies and metadata
├── alembic.ini           # Alembic configuration
└── README.md             # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.13 or higher
- MySQL database
- pip or poetry for dependency management

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "User Management System"
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   # On Windows
   .\.venv\Scripts\activate
   # On Unix/macOS
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root:
   ```
   DATABASE_URL=mysql+mysqlconnector://user:password@localhost:3306/user_management_system
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   SUPERUSER_USERNAME=superadmin@admin.com
   SUPERUSER_PASSWORD=superadmin
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the application**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## 📚 API Endpoints

### Authentication (`/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signin` | User login with username and password |
| POST | `/auth/signup` | Create new user (admin only) |
| GET | `/user/me` | Get current user information |
| PUT | `/user/password` | Update current user password |

### User Management (`/user`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/user` | List all users (admin only) |
| GET | `/user/status` | List employee statuses |
| POST | `/user/status` | Create new employee status |

### Department Management (`/department`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/department` | List all departments |
| POST | `/department` | Create new department |
| GET | `/department/{id}` | Get department details |
| PUT | `/department/{id}` | Update department |
| DELETE | `/department/{id}` | Delete department |

### Job Management (`/job`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/job` | List all jobs |
| POST | `/job` | Create new job |
| GET | `/job/{id}` | Get job details |
| PUT | `/job/{id}` | Update job |
| DELETE | `/job/{id}` | Delete job |

## 🔐 Authentication

The system uses JWT (JSON Web Tokens) for authentication:

1. **Login**: POST to `/auth/signin` with credentials
2. **Token**: Receive JWT access token valid for 30 minutes (configurable)
3. **Authorization**: Include token in requests: `Authorization: Bearer {token}`

### Password Requirements

Passwords must meet the following criteria:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character (@$!%*?&)

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_user_and_auth.py -v

# Run with coverage
pytest --cov=app tests/
```

### Test Coverage

The project includes tests for:
- User authentication (signin, signup)
- Password validation
- Employee management
- Department and job management
- Employee status tracking
- Authorization and access control

## 📊 Database Schema

### User Table
Stores user login credentials and status.

### Employee Table
Stores employee personal information including:
- Full name, gender, birthday
- Contact information (phone, email, address)
- Employment details (hire date, salary, status)
- Department and job assignment

### Department Table
Stores organizational departments.

### Job Table
Stores job positions linked to departments.

### EmployeeStatus Table
Stores employment status types (Full Time, Part Time, Contract, etc.).

## 🔄 Database Migrations

Manage database schema changes using Alembic:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Revert to previous version
alembic downgrade -1

# View migration history
alembic history
```

## 🛡️ Security Features

- **Password Hashing**: Argon2 algorithm for secure password storage
- **JWT Authentication**: Token-based API security
- **Email Validation**: EmailStr validation for valid email formats
- **Phone Validation**: International phone number validation (E.164 format)
- **Access Control**: Role-based access to endpoints
- **Status Checks**: Inactive users cannot perform administrative actions

## 📝 Environment Configuration

Key settings can be configured via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | MySQL connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |
| `SUPERUSER_USERNAME` | Initial admin username | superadmin@admin.com |
| `SUPERUSER_PASSWORD` | Initial admin password | superadmin |

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/AmazingFeature`)
2. Commit changes (`git commit -m 'Add AmazingFeature'`)
3. Push to branch (`git push origin feature/AmazingFeature`)
4. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Troubleshooting

### Database Connection Issues
- Ensure MySQL service is running
- Verify `DATABASE_URL` environment variable
- Check user credentials and database name

### Migration Errors
- Run `alembic current` to check current state
- Review migration files in `alembic/versions/`
- Rollback if necessary: `alembic downgrade -1`

### Authentication Issues
- Verify JWT_SECRET_KEY is set
- Check token expiration
- Ensure Authorization header format: `Bearer {token}`

## 📞 Support

For issues or questions, please create an issue in the repository or contact the development team.

---

**Last Updated**: January 2026
**Version**: 0.1.0
