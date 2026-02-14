# AnalytiCore - Technical Documentation

## Complete Local Implementation Guide

**Version:** 1.0.0  
**Last Updated:** February 14, 2026  
**Author:** AnalytiCore Development Team

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Prerequisites](#3-prerequisites)
4. [Project Structure](#4-project-structure)
5. [Backend Setup](#5-backend-setup)
6. [Frontend Setup](#6-frontend-setup)
7. [Database Configuration](#7-database-configuration)
8. [Redis & Celery Setup](#8-redis--celery-setup)
9. [Environment Variables](#9-environment-variables)
10. [Running the Application](#10-running-the-application)
11. [API Reference](#11-api-reference)
12. [Security Features](#12-security-features)
13. [Admin Dashboard](#13-admin-dashboard)
14. [Data Analysis Pipeline](#14-data-analysis-pipeline)
15. [Scheduled Pipelines](#15-scheduled-pipelines)
16. [Testing](#16-testing)
17. [Troubleshooting](#17-troubleshooting)

---

## 1. Project Overview

AnalytiCore is a comprehensive SaaS data analytics platform that provides:

- **Data Ingestion**: Upload CSV, Excel, connect to Google Sheets, MySQL, PostgreSQL
- **Data Profiling**: Automatic data quality analysis and statistics
- **Data Cleaning**: Rule-based and AI-powered data transformation
- **Data Analysis**: Statistical analysis, correlation, distribution analysis
- **Machine Learning**: Automated ML model training, clustering, predictions
- **Visualization**: Interactive charts and dashboards
- **Scheduled Pipelines**: Automated recurring analysis jobs
- **Admin Analytics**: Comprehensive user metrics, system health monitoring
- **Security**: Government-grade security with 2FA, password policies, audit logging

---

## 2. Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Core language |
| Django | 5.x | Web framework |
| Django REST Framework | 3.15+ | REST API |
| Celery | 5.x | Task queue |
| Redis | 7.x | Message broker & cache |
| MySQL/MariaDB | 8.x/10.x | Primary database |
| Pandas | 2.x | Data processing |
| Scikit-learn | 1.x | Machine learning |
| NumPy/SciPy | Latest | Scientific computing |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.x | UI framework |
| React Router | 6.x | Routing |
| Tailwind CSS | 3.x | Styling |
| Shadcn/UI | Latest | Component library |
| Recharts | 2.x | Data visualization |
| Axios | 1.x | HTTP client |
| Lucide React | Latest | Icons |

---

## 3. Prerequisites

### Required Software

```bash
# Python 3.11+
python3 --version

# Node.js 18+ & Yarn
node --version
yarn --version

# MySQL/MariaDB
mysql --version

# Redis
redis-server --version

# Git
git --version
```

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 10GB+ free space
- **CPU**: 2+ cores recommended

---

## 4. Project Structure

```
/app/
├── backend/                    # Django Backend
│   ├── analyticore_api/       # Django project settings
│   │   ├── settings.py        # Main settings
│   │   ├── urls.py            # Root URL config
│   │   ├── celery.py          # Celery configuration
│   │   └── wsgi.py
│   ├── users/                 # User management app
│   │   ├── models.py          # User model
│   │   ├── views.py           # Auth views
│   │   ├── security_models.py # 2FA, Password history
│   │   ├── security_views.py  # Security endpoints
│   │   ├── analytics_views.py # Admin analytics
│   │   ├── admin_settings_views.py
│   │   ├── notification_service.py
│   │   ├── health_monitoring.py
│   │   └── password_validators.py
│   ├── projects/              # Project management
│   │   ├── models.py
│   │   └── views.py
│   ├── analysis/              # Data analysis
│   │   ├── models.py
│   │   ├── views.py           # Refactored views
│   │   ├── statistics.py      # Statistical analyzer
│   │   ├── insights.py        # Rule-based insights
│   │   └── services/          # Service classes
│   │       ├── data_loader.py
│   │       ├── transformation_service.py
│   │       └── column_action_service.py
│   ├── pipelines/             # Scheduled pipelines
│   │   ├── models.py
│   │   ├── views.py
│   │   └── tasks.py
│   ├── notifications/         # Notification system
│   ├── exports/               # Data export
│   ├── api_integrations/      # Google Sheets, etc.
│   ├── ml/                    # Machine learning
│   │   └── offline_ml.py
│   ├── requirements.txt
│   └── manage.py
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/            # Shadcn components
│   │   │   ├── ProtectedRoute.js
│   │   │   └── data_sources/
│   │   ├── pages/
│   │   │   ├── LandingPage.js
│   │   │   ├── SignIn.js
│   │   │   ├── SignUp.js
│   │   │   ├── Dashboard.js
│   │   │   ├── ProjectView.js
│   │   │   ├── AdminDashboard.js
│   │   │   ├── ScheduledPipelines.js
│   │   │   ├── SecuritySettings.js
│   │   │   ├── ResetPassword.js
│   │   │   ├── PrivacyPolicy.js
│   │   │   └── TermsOfService.js
│   │   ├── api.js             # API client
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
│
└── memory/
    └── PRD.md                 # Product requirements
```

---

## 5. Backend Setup

### 5.1 Clone and Setup Virtual Environment

```bash
# Clone the repository
git clone <repository-url>
cd analyticore

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
.\venv\Scripts\activate   # Windows

# Navigate to backend
cd backend
```

### 5.2 Install Dependencies

```bash
# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 5.3 Key Python Packages

```txt
# requirements.txt (key packages)
Django>=5.0
djangorestframework>=3.15
django-cors-headers>=4.0
mysqlclient>=2.2
PyMySQL>=1.1
redis>=5.0
celery>=5.3
django-celery-beat>=2.5
pandas>=2.0
numpy>=1.24
scipy>=1.11
scikit-learn>=1.3
openpyxl>=3.1
python-dotenv>=1.0
google-api-python-client>=2.100
pywebpush>=1.14
croniter>=1.4
```

### 5.4 Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser
# Email: admin@analyticore.com
# Password: (use a strong password)
```

---

## 6. Frontend Setup

### 6.1 Install Dependencies

```bash
cd frontend

# Install with Yarn (recommended)
yarn install

# OR with npm (not recommended, may cause issues)
npm install
```

### 6.2 Key Frontend Packages

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0",
    "recharts": "^2.10.0",
    "lucide-react": "^0.294.0",
    "sonner": "^1.2.0",
    "tailwindcss": "^3.3.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0"
  }
}
```

---

## 7. Database Configuration

### 7.1 MySQL/MariaDB Setup

```bash
# Install MySQL (Ubuntu)
sudo apt-get install mysql-server mysql-client libmysqlclient-dev

# OR MariaDB
sudo apt-get install mariadb-server mariadb-client libmariadb-dev

# Start service
sudo systemctl start mysql
sudo systemctl enable mysql

# Secure installation
sudo mysql_secure_installation
```

### 7.2 Create Database

```sql
-- Connect to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE analyticore CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'analyticore_user'@'localhost' IDENTIFIED BY 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON analyticore.* TO 'analyticore_user'@'localhost';
FLUSH PRIVILEGES;

-- Exit
EXIT;
```

### 7.3 Database Models Overview

```python
# Key Models

# users/models.py
class User(AbstractBaseUser):
    user_id = UUIDField(primary_key=True)
    email = EmailField(unique=True)
    name = CharField(max_length=255)
    is_verified = BooleanField(default=False)
    is_staff = BooleanField(default=False)

# users/security_models.py
class TwoFactorOTP:
    user = ForeignKey(User)
    code = CharField(max_length=6)
    expires_at = DateTimeField()
    is_used = BooleanField()

class UserSecuritySettings:
    user = OneToOneField(User)
    two_factor_enabled = BooleanField()
    password_expires_at = DateTimeField()

class PasswordHistory:
    user = ForeignKey(User)
    password_hash = CharField()

class AdminAlertSettings:
    error_rate_threshold = FloatField(default=5.0)
    db_response_threshold_ms = IntegerField(default=500)
    max_errors_24h = IntegerField(default=10)

# projects/models.py
class Project:
    project_id = UUIDField(primary_key=True)
    user = ForeignKey(User)
    name = CharField()
    file_path = CharField()
    status = CharField()  # uploaded, analyzed, transformed

# pipelines/models.py
class ScheduledPipeline:
    pipeline_id = UUIDField(primary_key=True)
    project = ForeignKey(Project)
    schedule_type = CharField()  # hourly, daily, weekly
    is_active = BooleanField()

class PipelineRun:
    pipeline = ForeignKey(ScheduledPipeline)
    status = CharField()  # pending, running, completed, failed
    started_at = DateTimeField()
```

---

## 8. Redis & Celery Setup

### 8.1 Install Redis

```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify
redis-cli ping
# Should return: PONG
```

### 8.2 Celery Configuration

```python
# analyticore_api/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analyticore_api.settings')

app = Celery('analyticore')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Scheduled tasks
app.conf.beat_schedule = {
    'check-system-health': {
        'task': 'users.health_monitoring.check_system_health',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'daily-health-summary': {
        'task': 'users.health_monitoring.daily_health_summary',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
    },
}
```

### 8.3 Running Celery Workers

```bash
# Terminal 1: Celery Worker
cd backend
celery -A analyticore_api worker --loglevel=info

# Terminal 2: Celery Beat (scheduler)
celery -A analyticore_api beat --loglevel=info
```

---

## 9. Environment Variables

### 9.1 Backend Environment (.env)

```bash
# backend/.env

# Database
DATABASE_URL=mysql://analyticore_user:your_password@localhost:3306/analyticore
MONGO_URL=  # If using MongoDB for specific features

# Django
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Celery/Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email (for password reset, 2FA, notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@analyticore.com

# App URL (for email links)
APP_URL=http://localhost:3000

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Pipeline Storage
PIPELINE_STORAGE_PATH=/path/to/storage/pipelines
```

### 9.2 Frontend Environment (.env)

```bash
# frontend/.env

REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## 10. Running the Application

### 10.1 Development Mode

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8001

# Terminal 2: Frontend
cd frontend
yarn start

# Terminal 3: Celery Worker
cd backend
celery -A analyticore_api worker --loglevel=info

# Terminal 4: Celery Beat
cd backend
celery -A analyticore_api beat --loglevel=info

# Terminal 5: Redis (if not running as service)
redis-server
```

### 10.2 Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8001/api/ |
| Django Admin | http://localhost:8001/admin/ |

### 10.3 Production Deployment

```bash
# Using Gunicorn for backend
gunicorn analyticore_api.wsgi:application --bind 0.0.0.0:8001 --workers 4

# Build frontend
cd frontend
yarn build

# Serve with nginx or similar
```

---

## 11. API Reference

### 11.1 Authentication Endpoints

```
POST /api/auth/register
Body: { "email": "...", "password": "...", "name": "..." }
Response: { "message": "Verification email sent" }

POST /api/auth/login
Body: { "email": "...", "password": "..." }
Response: { "token": "...", "user": {...}, "requires_2fa": bool }

GET /api/auth/me
Headers: Authorization: Token <token>
Response: { "user_id": "...", "email": "...", "is_staff": bool }

POST /api/auth/logout
Headers: Authorization: Token <token>
Response: { "message": "Logged out" }
```

### 11.2 Security Endpoints

```
# Two-Factor Authentication
POST /api/auth/2fa/enable
Response: { "otp_id": "...", "message": "Code sent" }

POST /api/auth/2fa/verify-enable
Body: { "otp_id": "...", "code": "123456" }
Response: { "message": "2FA enabled" }

POST /api/auth/2fa/disable
Body: { "password": "..." }
Response: { "message": "2FA disabled" }

# Password Management
POST /api/auth/password/reset-request
Body: { "email": "..." }
Response: { "message": "Reset link sent" }

POST /api/auth/password/reset
Body: { "token": "...", "new_password": "..." }
Response: { "message": "Password reset" }

POST /api/auth/password/update
Body: { "current_password": "...", "new_password": "..." }
Response: { "message": "Password updated" }

POST /api/auth/password/validate
Body: { "password": "..." }
Response: { "valid": bool, "strength": 0-100, "requirements": {...} }

# Security Settings
GET /api/auth/security/settings
Response: { "two_factor_enabled": bool, "password_expires_at": "..." }

GET /api/auth/security/audit-log
Response: { "logs": [...] }
```

### 11.3 Project Endpoints

```
GET /api/projects/
Response: { "projects": [...] }

POST /api/projects/
Body: { "name": "...", "description": "..." }
Response: { "project_id": "...", "name": "..." }

GET /api/projects/{id}/
Response: { "project_id": "...", "statistics": {...} }

POST /api/projects/{id}/upload/
Body: FormData with file
Response: { "message": "Uploaded", "row_count": 1000 }

DELETE /api/projects/{id}/
Response: { "message": "Deleted" }
```

### 11.4 Analysis Endpoints

```
POST /api/analysis/{project_id}/analyze/
Response: { "recommendations": [...] }

GET /api/analysis/{project_id}/statistics/
Response: { "numeric": {...}, "categorical": {...} }

GET /api/analysis/{project_id}/correlation/
Response: { "matrix": [[...]], "columns": [...] }

GET /api/analysis/{project_id}/distribution/?column=age
Response: { "histogram": [...], "stats": {...} }

POST /api/analysis/{project_id}/transform/
Body: { "rules": [...] }
Response: { "message": "Applied", "new_shape": [100, 10] }

GET /api/analysis/{project_id}/columns/
Response: { "columns": [...], "numeric": [...], "categorical": [...] }

POST /api/analysis/{project_id}/column-action/
Body: { "column": "age", "action": "fill_missing", "strategy": "mean" }
Response: { "changes": [...] }
```

### 11.5 ML Endpoints

```
POST /api/ml/{project_id}/train/
Body: { "target": "price", "model_type": "regression" }
Response: { "model_id": "...", "metrics": {...} }

POST /api/ml/{project_id}/predict/
Body: { "model_id": "...", "data": {...} }
Response: { "predictions": [...] }

POST /api/ml/{project_id}/cluster/
Body: { "n_clusters": 5, "columns": [...] }
Response: { "labels": [...], "centers": [...] }

POST /api/ml/{project_id}/auto-ml/
Body: { "target": "price", "task": "regression" }
Response: { "best_model": "...", "results": [...] }
```

### 11.6 Magic Analysis Endpoints (One-Click Analysis)

```
# Run comprehensive magic analysis
GET /api/analysis/{project_id}/magic-analyze
Response: {
  "executive_summary": {
    "text": "Plain-English summary...",
    "quality_score": 90,
    "quality_label": "excellent",
    "stats": { "total_rows": 1000, "total_columns": 10, ... }
  },
  "data_profile": {
    "columns": [{ "name": "age", "type": "numeric", "statistics": {...} }]
  },
  "data_quality": {
    "quality_score": 90,
    "issues": [{ "type": "missing_values", "severity": "warning", "message": "..." }]
  },
  "cleaning_suggestions": [{
    "column": "age",
    "issue": "missing_values",
    "priority": "high",
    "options": [
      { "strategy": "mean", "description": "Fill with mean", "recommended": true }
    ]
  }],
  "key_insights": [{
    "type": "correlation",
    "priority": "high",
    "title": "Strong Relationship Found",
    "message": "'age' and 'salary' have strong positive correlation (0.85)"
  }],
  "suggested_visualizations": [{
    "type": "histogram",
    "title": "Age Distribution",
    "columns": ["age"]
  }]
}

# Apply selected cleaning operations
POST /api/analysis/{project_id}/magic-apply-cleaning
Body: {
  "actions": [{
    "column": "age",
    "issue": "missing_values",
    "strategy": "mean"
  }]
}
Response: {
  "message": "Cleaning applied",
  "original_shape": [1000, 10],
  "new_shape": [1000, 10],
  "changes": [{ "column": "age", "status": "success", "values_filled": 50 }]
}

# Export analysis report
GET /api/analysis/{project_id}/magic-export?export_format=excel
Query params: export_format = json | csv | excel
Response (JSON/CSV): { "filename": "...", "content_type": "...", "content": "..." }
Response (Excel): { "filename": "...", "content_type": "...", "content": "<base64>", "encoding": "base64" }
```

### 11.7 Pipeline Endpoints

```
GET /api/pipelines/
Response: { "pipelines": [...] }

POST /api/pipelines/
Body: { 
  "project_id": "...", 
  "name": "Daily Analysis",
  "schedule_type": "daily",
  "schedule_time": "08:00",
  "action": "full_analysis"
}
Response: { "pipeline_id": "..." }

POST /api/pipelines/{id}/run/
Response: { "run_id": "...", "status": "running" }

GET /api/pipelines/stats/
Response: { "total": 10, "active": 8, "success_rate": 95.5 }
```

### 11.7 Admin Analytics Endpoints

```
# All require is_staff=True

GET /api/saas-admin/analytics/summary
Response: { "users": {...}, "projects": {...}, "pipelines": {...} }

GET /api/saas-admin/analytics/users
Response: { "total_users": 100, "dau": 50, "wau": 80, "mau": 95, "stickiness": 52.6 }

GET /api/saas-admin/analytics/user-growth?days=30
Response: { "data": [{ "date": "...", "new_users": 5, "total_users": 100 }] }

GET /api/saas-admin/analytics/activity?days=30
Response: { "top_actions": [...], "power_users": [...] }

GET /api/saas-admin/analytics/health
Response: { "db_response_ms": 5, "error_rate": 0.5, "status": "healthy" }

GET /api/saas-admin/analytics/funnel
Response: { "funnel": [{ "stage": "Signed Up", "count": 100, "rate": 100 }] }

GET /api/saas-admin/analytics/retention
Response: { "day1_retention": 45, "cohort_retention": [...] }

# Alert Settings
GET /api/saas-admin/settings/alerts
Response: { "error_rate_threshold": 5.0, "db_response_threshold_ms": 500, ... }

PUT /api/saas-admin/settings/alerts/update
Body: { "error_rate_threshold": 10.0 }
Response: { "message": "Updated" }
```

---

## 12. Security Features

### 12.1 Password Policy

```python
# Government-grade requirements:
{
    "min_length": 12,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_digit": True,
    "require_special": True,  # !@#$%^&*()
    "password_expiry_days": 90,
    "prevent_reuse_count": 5,
    "lockout_attempts": 5,
    "lockout_duration_minutes": 30
}
```

### 12.2 Two-Factor Authentication Flow

```
1. User enables 2FA:
   POST /api/auth/2fa/enable → Sends OTP to email
   
2. User verifies OTP:
   POST /api/auth/2fa/verify-enable → 2FA activated

3. On subsequent logins:
   POST /api/auth/login → Returns { "requires_2fa": true, "otp_id": "..." }
   
4. User enters OTP:
   POST /api/auth/2fa/verify-otp → Returns auth token
```

### 12.3 Security Audit Log Events

```python
EVENT_TYPES = [
    'login_success',
    'login_failed',
    'logout',
    'password_change',
    'password_reset_request',
    'password_reset_complete',
    '2fa_enabled',
    '2fa_disabled',
    '2fa_success',
    '2fa_failed',
    'account_locked',
    'settings_changed',
]
```

---

## 13. Admin Dashboard

### 13.1 Dashboard Sections

| Section | Description |
|---------|-------------|
| Overview | Key metrics, user growth chart, system health |
| User Metrics | DAU, WAU, MAU, stickiness, growth rate, churn |
| Activity Analytics | Top actions, hourly distribution, power users |
| Project Analytics | Projects by status/source, transformations |
| Pipeline Analytics | Active/paused, success rate, run history |
| Retention & Funnels | Cohort analysis, user journey funnel |
| System Health | DB response, error rate, status indicator |
| All Users | User list with email, status, plan |
| All Projects | Project list with owner, source, rows |
| Activity Feed | Real-time activity log |
| Alert Settings | Configure thresholds, email recipients |

### 13.2 Alert Thresholds

```javascript
// Default thresholds
{
  error_rate_threshold: 5.0,      // Alert when > 5%
  db_response_threshold_ms: 500,  // Alert when > 500ms
  max_errors_24h: 10,             // Alert when > 10 errors
  health_check_interval_minutes: 15
}
```

---

## 14. Data Analysis Pipeline

### 14.1 Analysis Flow

```
1. Upload Data
   POST /api/projects/{id}/upload/
   → Parses CSV/Excel, calculates basic stats
   
2. Profile Data
   GET /api/analysis/{id}/statistics/
   → Returns descriptive statistics, data types
   
3. Generate Recommendations
   POST /api/analysis/{id}/analyze/
   → Rule-based cleaning recommendations
   
4. Apply Transformations
   POST /api/analysis/{id}/transform/
   → Applies rules, saves processed data
   
5. Visualize
   GET /api/analysis/{id}/chart-data/?type=scatter&x=age&y=income
   → Returns chart-ready data
```

### 14.2 Supported Transformations

```python
TRANSFORMATIONS = [
    'fill_missing',       # mean, median, mode, constant
    'remove_duplicates',
    'convert_type',       # numeric, datetime, string
    'remove_outliers',    # IQR method
    'cap_outliers',
    'text_transform',     # trim, lowercase, uppercase
    'rename_column',
]
```

### 14.3 ML Capabilities

```python
# Supervised Learning
- Linear Regression
- Logistic Regression
- Random Forest
- Gradient Boosting
- Support Vector Machines

# Unsupervised Learning
- K-Means Clustering
- Hierarchical Clustering
- PCA (dimensionality reduction)

# Auto-ML
- Automatic model selection
- Hyperparameter tuning
- Cross-validation
```

---

## 15. Scheduled Pipelines

### 15.1 Schedule Types

```python
SCHEDULE_TYPES = {
    'hourly': {
        'minute': 0-59  # Run at minute X every hour
    },
    'daily': {
        'time': 'HH:MM'  # Run at specific time daily
    },
    'weekly': {
        'day': 0-6,      # 0=Monday, 6=Sunday
        'time': 'HH:MM'
    },
    'monthly': {
        'day': 1-28,
        'time': 'HH:MM'
    }
}
```

### 15.2 Pipeline Actions

```python
PIPELINE_ACTIONS = [
    'full_analysis',      # Profile + recommend + visualize
    'data_refresh',       # Re-import from source
    'run_transformations', # Apply saved rules
    'generate_report',    # Export analysis report
]
```

### 15.3 Notifications

Pipelines can send notifications on:
- Completion (success)
- Failure (with error details)
- Daily summary (aggregated)

---

## 16. Testing

### 16.1 Backend Tests

```bash
cd backend

# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test analysis
python manage.py test pipelines

# With coverage
pip install coverage
coverage run manage.py test
coverage report
```

### 16.2 API Testing with curl

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@analyticore.com","password":"yourpassword"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

# Get user info
curl http://localhost:8001/api/auth/me \
  -H "Authorization: Token $TOKEN"

# Get projects
curl http://localhost:8001/api/projects/ \
  -H "Authorization: Token $TOKEN"

# Upload file
curl -X POST http://localhost:8001/api/projects/PROJECT_ID/upload/ \
  -H "Authorization: Token $TOKEN" \
  -F "file=@data.csv"
```

### 16.3 Frontend Tests

```bash
cd frontend

# Run tests
yarn test

# With coverage
yarn test --coverage
```

---

## 17. Troubleshooting

### 17.1 Common Issues

**Database Connection Error**
```bash
# Check MySQL is running
sudo systemctl status mysql

# Test connection
mysql -u analyticore_user -p -e "SELECT 1"

# Check Django settings
python manage.py dbshell
```

**Redis Connection Error**
```bash
# Check Redis is running
redis-cli ping

# Check Celery broker URL in settings
echo $CELERY_BROKER_URL
```

**Celery Tasks Not Running**
```bash
# Check worker is running
celery -A analyticore_api inspect active

# Check scheduled tasks
celery -A analyticore_api inspect scheduled

# View task queue
redis-cli LLEN celery
```

**CORS Errors**
```python
# Ensure in settings.py:
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True
```

**Email Not Sending**
```bash
# Test email config
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])
```

### 17.2 Log Locations

```bash
# Django logs (if configured)
tail -f /var/log/django/app.log

# Celery worker logs
celery -A analyticore_api worker --loglevel=debug

# Redis logs
tail -f /var/log/redis/redis-server.log
```

### 17.3 Performance Optimization

```python
# Database query optimization
- Use select_related() and prefetch_related()
- Add database indexes
- Use pagination for large datasets

# Celery optimization
- Increase worker concurrency
- Use task routing for heavy tasks
- Implement task result expiry

# Frontend optimization
- Lazy load components
- Implement virtualization for large lists
- Use React.memo for expensive renders
```

---

## Quick Start Summary

```bash
# 1. Clone and setup
git clone <repo>
cd analyticore

# 2. Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your settings
python manage.py migrate
python manage.py createsuperuser

# 3. Frontend setup
cd ../frontend
yarn install
cp .env.example .env  # Edit REACT_APP_BACKEND_URL

# 4. Start services
# Terminal 1: Redis
redis-server

# Terminal 2: Backend
cd backend && python manage.py runserver 0.0.0.0:8001

# Terminal 3: Celery Worker
cd backend && celery -A analyticore_api worker -l info

# Terminal 4: Celery Beat
cd backend && celery -A analyticore_api beat -l info

# Terminal 5: Frontend
cd frontend && yarn start

# 5. Access
# Frontend: http://localhost:3000
# Admin: http://localhost:8001/admin
```

---

## Support & Contact

For technical support or questions:
- Email: support@analyticore.com
- Documentation: https://docs.analyticore.com
- GitHub Issues: https://github.com/analyticore/issues

---

**© 2026 AnalytiCore. All rights reserved.**
