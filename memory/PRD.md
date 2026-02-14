# AnalytiCore - Product Requirements Document

## Overview
AnalytiCore is a SaaS data analysis pipeline application that enables users to upload, clean, transform, and analyze data with AI-powered recommendations.

## Tech Stack
- **Backend:** Django REST Framework 5.2
- **Frontend:** React 18 with Tailwind CSS
- **Database:** MySQL (MariaDB)
- **Cache/Queue:** Redis + Celery
- **Authentication:** DRF Token Authentication
- **Charting:** Recharts

## Core Features

### Implemented Features

#### 1. Authentication System
- [x] Email/Password login
- [x] User registration with email verification
- [x] JWT Token authentication
- [x] Google OAuth (frontend ready)
- [x] Protected routes

#### 2. Project Management
- [x] Create projects with name and source type
- [x] List user's projects with pagination
- [x] Project detail view
- [x] Delete projects
- [x] Project statistics and recommendations endpoints

#### 3. File Upload & Data Ingestion
- [x] CSV file upload
- [x] Excel (.xlsx, .xls) file upload
- [x] JSON file upload
- [x] Automatic column type detection
- [x] Data preview (first 100 rows)
- [x] File size up to 100MB

#### 4. Statistical Analysis
- [x] **Descriptive Statistics:**
  - Count, Mean, Standard Deviation
  - Min, 25% (Q1), Median (50%), 75% (Q3), Max
  - Skewness, Kurtosis, Variance
  - Range, IQR (Interquartile Range)
  - Missing values count and percentage
- [x] **Categorical Analysis:**
  - Unique count, Top value, Frequency
  - Value counts distribution

#### 5. Correlation Analysis
- [x] Pearson correlation matrix
- [x] Spearman correlation (optional)
- [x] Kendall correlation (optional)
- [x] Interactive heatmap visualization
- [x] Top correlations ranking with strength classification
  - very_strong (>= 0.8)
  - strong (>= 0.6)
  - moderate (>= 0.4)
  - weak (>= 0.2)
  - very_weak (< 0.2)

#### 6. Distribution Analysis
- [x] Histogram with configurable bins
- [x] Box plot statistics
- [x] Normality tests (Shapiro-Wilk, D'Agostino)
- [x] Distribution type inference
- [x] Outlier detection

#### 7. Data Visualization
- [x] Bar Chart
- [x] Line Chart
- [x] Scatter Plot
- [x] Pie Chart
- [x] Histogram
- [x] Box Plot
- [x] Correlation Heatmap
- [x] Column selector for X/Y axes
- [x] Chart type switcher

#### 8. AI-Powered Cleaning Recommendations
- [x] GPT-5.2 powered analysis
- [x] Missing value strategies
- [x] Outlier detection
- [x] Data type suggestions
- [x] Duplicate detection
- [x] Column renaming suggestions

#### 9. Data Transformations
- [x] Fill missing values (mean, median, mode, forward-fill, constant)
- [x] Remove duplicates
- [x] Convert data types
- [x] Remove outliers (IQR method)
- [x] Rename columns
- [x] Transformation logging

#### 10. Data Export
- [x] Export to CSV
- [x] Export to Excel (.xlsx)
- [x] Export to JSON

#### 11. Notification System
- [x] **Email Notifications**
  - Analysis complete, data issues, export ready, upload complete
  - Configurable frequency (instant, daily, weekly, never)
  - Beautiful HTML email templates
- [x] **In-App Notifications**
  - Bell icon with unread count badge
  - Dropdown with latest notifications
  - Mark as read/mark all read
  - Real-time polling (30s intervals)
- [x] **Push Notifications**
  - Service worker configured
  - VAPID keys for secure push
  - Browser permission handling

#### 12. Admin Dashboard
- [x] System statistics (users, projects, active subscriptions)
- [x] User management list
- [x] Project overview
- [x] Admin-only access control

#### 13. Infrastructure
- [x] MySQL database configured
- [x] Redis for caching and message queue
- [x] Celery worker for async tasks
- [x] Celery beat for scheduled tasks

### Backlog (Future Tasks)

#### P1 - High Priority
- [ ] Google Sheets integration
- [ ] Database source connections (PostgreSQL, MySQL)

#### P2 - Medium Priority
- [ ] Stripe billing integration
- [ ] Webhook notifications
- [ ] Scheduled pipelines (Celery Beat)

#### P3 - Low Priority
- [ ] API data source connections
- [ ] PDF report generation
- [ ] Team collaboration features

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### Projects
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}/` - Get project detail
- `DELETE /api/projects/{id}/` - Delete project

### Data Ingestion
- `POST /api/projects/{id}/upload` - Upload file
- `GET /api/projects/{id}/data` - Get data preview

### Analysis
- `POST /api/analysis/{id}/analyze` - Run AI analysis
- `POST /api/analysis/{id}/transform` - Apply transformations
- `GET /api/analysis/{id}/statistics` - Get descriptive statistics
- `GET /api/analysis/{id}/correlation` - Get correlation matrix
- `GET /api/analysis/{id}/distribution` - Get distribution analysis
- `GET /api/analysis/{id}/chart` - Get chart data
- `GET /api/analysis/{id}/columns` - Get column info
- `GET /api/analysis/{id}/column?column={name}` - Get single column analysis

### Exports
- `GET /api/exports/{id}/export?format={csv|xlsx|json}` - Export data

### Notifications
- `GET /api/notifications/` - List notifications
- `GET /api/notifications/summary` - Get unread count
- `POST /api/notifications/{id}/read` - Mark as read
- `POST /api/notifications/read-all` - Mark all read
- `GET /api/notifications/preferences` - Get preferences
- `PUT /api/notifications/preferences` - Update preferences
- `POST /api/notifications/push/subscribe` - Subscribe to push

### Admin
- `GET /api/saas-admin/dashboard` - Admin stats
- `GET /api/saas-admin/users` - List all users
- `GET /api/saas-admin/projects` - List all projects

## Database Schema

### Core Models
- **User** - Custom user with email, name, verification status
- **Project** - User's data projects with status tracking
- **Notification** - In-app notifications with read status
- **NotificationPreference** - User notification settings
- **PushSubscription** - Browser push subscriptions
- **AnalysisRun** - Stores AI analysis results
- **TransformationLog** - Logs all data transformations

## Test Coverage
- 24+ automated tests passing
- Coverage: Auth, Projects, Analysis APIs, Notifications

## Credentials
- **Admin:** admin@analyticore.com / admin123

## Environment Variables
```
MYSQL_DATABASE=analyticore_db
MYSQL_USER=analyticore
MYSQL_PASSWORD=analyticore_secure_pass_2026
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=microphase3000@gmail.com
CELERY_BROKER_URL=redis://localhost:6379/0
EMERGENT_LLM_KEY=sk-emergent-xxxxx
```

---
*Last Updated: February 14, 2026*
