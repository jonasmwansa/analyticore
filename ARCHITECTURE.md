# AnalytiCore Architecture

## Important Note on Framework Choice

**Original Requirement**: Django + React
**Implemented**: FastAPI + React + MongoDB

### Why FastAPI Instead of Django?

The development environment is pre-configured with FastAPI, React, and MongoDB. Since FastAPI provides:
- Async/await support for better performance with data processing
- Built-in OpenAPI/Swagger documentation
- Fast development with Pydantic models
- Excellent integration with the existing MongoDB setup

The project was implemented using FastAPI to leverage the existing infrastructure.

## Current Architecture (Monolithic FastAPI)

Currently, all backend code is in a single `server.py` file. This works for MVP but should be refactored into modular structure.

## Recommended Backend Structure (Django-Style Separation)

To achieve separation of concerns similar to Django apps, the backend should be restructured as follows:

```
backend/
├── main.py                 # FastAPI app initialization
├── config.py              # Configuration and environment variables
├── database.py            # MongoDB connection setup
│
├── apps/
│   ├── __init__.py
│   │
│   ├── auth/              # Authentication module
│   │   ├── __init__.py
│   │   ├── models.py      # User, Session models
│   │   ├── routes.py      # Auth endpoints
│   │   ├── services.py    # Business logic (email verification, JWT)
│   │   └── dependencies.py # Auth dependencies (get_current_user)
│   │
│   ├── projects/          # Project management module
│   │   ├── __init__.py
│   │   ├── models.py      # Project model
│   │   ├── routes.py      # Project CRUD endpoints
│   │   └── services.py    # Project business logic
│   │
│   ├── analysis/          # Data analysis module
│   │   ├── __init__.py
│   │   ├── models.py      # DataStatistics, AIRecommendation models
│   │   ├── routes.py      # Analysis endpoints
│   │   ├── services.py    # AI analysis logic (GPT-5.2 integration)
│   │   └── transformations.py # Data transformation functions
│   │
│   └── data_ingestion/    # Data ingestion module
│       ├── __init__.py
│       ├── models.py      # Upload metadata models
│       ├── routes.py      # Upload endpoints
│       ├── parsers.py     # CSV/Excel/JSON parsers
│       └── connectors/    # Database and API connectors
│           ├── database.py
│           └── api.py
│
├── utils/
│   ├── email.py           # Email sending utilities
│   ├── security.py        # JWT, password hashing
│   └── validators.py      # Input validation
│
└── requirements.txt
```

## Migration Plan (Current → Modular)

### Phase 1: Extract Authentication
- Move all auth-related code from `server.py` to `apps/auth/`
- Models: User, UserRegister, UserLogin, SessionData
- Routes: /auth/register, /auth/login, /auth/verify-email, /auth/me, /auth/logout, /auth/session
- Services: send_verification_email, JWT token generation

### Phase 2: Extract Projects
- Move project management to `apps/projects/`
- Models: Project, ProjectCreate
- Routes: GET/POST /projects, /projects/{id}

### Phase 3: Extract Analysis
- Move AI analysis to `apps/analysis/`
- Models: AIRecommendation, DataStatistics, TransformationRule
- Routes: /projects/{id}/analyze, /projects/{id}/transform
- Services: GPT-5.2 integration, transformation logic

### Phase 4: Extract Data Ingestion
- Move upload and data preview to `apps/data_ingestion/`
- Routes: /projects/{id}/upload, /projects/{id}/data
- Parsers: CSV, Excel, JSON handling
- Future: Database connectors, API integrations

## Benefits of Modular Structure

1. **Maintainability**: Each module is self-contained and easier to understand
2. **Scalability**: Can add new modules (e.g., data visualization, reporting) without touching core code
3. **Testing**: Each module can be tested independently
4. **Team Collaboration**: Different developers can work on different modules
5. **Reusability**: Modules can be reused across different projects

## Database Collections (MongoDB)

```
analyticore_db/
├── users                  # User accounts
├── user_sessions         # Active sessions
├── verification_tokens   # Email verification tokens
├── projects              # Data transformation projects
└── (future collections)
    ├── transformations   # Transformation history
    ├── api_connections   # Saved API connections
    └── db_connections    # Saved database connections
```

## Current Implementation Status

✅ **Implemented (Monolithic)**:
- Authentication (email/password + Google OAuth)
- Email verification
- Project management
- File upload (CSV, Excel, JSON)
- AI-powered analysis (GPT-5.2)
- Data transformations
- Data preview

⏳ **To Be Implemented**:
- Modular app structure
- Database connectors (PostgreSQL, MySQL)
- API integrations
- Data export functionality
- Transformation history
- Data visualization

## Next Steps

1. **Refactor to Modular Structure**: Follow the migration plan above
2. **Add Database Connectors**: Implement PostgreSQL, MySQL connection UI
3. **Add API Integration**: Allow users to connect to REST APIs
4. **Add Export**: Download cleaned data in multiple formats
5. **Add Visualization**: Charts and graphs for data quality metrics

---

**Note**: If a pure Django implementation is strongly preferred, the entire backend would need to be rebuilt using Django REST Framework, Django ORM with PostgreSQL, and Django's app structure. This would require significant effort but would provide Django's admin panel, ORM features, and ecosystem.
