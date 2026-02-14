# AnalytiCore - Product Requirements Document

## Overview
AnalytiCore is a SaaS data analysis pipeline application that enables users to upload, clean, transform, and analyze data with AI-powered recommendations.

## Tech Stack
- **Backend:** Django REST Framework 5.2
- **Frontend:** React 18 with Tailwind CSS
- **Database:** MySQL (MariaDB)
- **Cache/Queue:** Redis + Celery
- **Authentication:** DRF Token Authentication

## Core Features

### ✅ Implemented Features

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

#### 3. Notification System
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

#### 4. Admin Dashboard
- [x] System statistics (users, projects, active subscriptions)
- [x] User management list
- [x] Project overview
- [x] Admin-only access control

#### 5. Infrastructure
- [x] MySQL database configured
- [x] Redis for caching and message queue
- [x] Celery worker for async tasks
- [x] Celery beat for scheduled tasks

### 🔄 In Progress

#### Data Pipeline
- [ ] File upload processing (CSV, Excel, JSON)
- [ ] Data profiling and statistics
- [ ] AI-powered cleaning recommendations
- [ ] Data transformations

### 📋 Backlog (Future Tasks)

#### P1 - High Priority
- [ ] File upload and data ingestion
- [ ] Data visualization charts
- [ ] Export functionality (PDF, CSV, Excel)

#### P2 - Medium Priority
- [ ] Stripe billing integration
- [ ] Webhook notifications
- [ ] Scheduled pipelines (Celery Beat)

#### P3 - Low Priority
- [ ] Google Sheets integration
- [ ] API data source connections
- [ ] Database connections (PostgreSQL, MySQL)

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
- `GET /api/projects/{id}/statistics/` - Get project stats

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

## Test Coverage
- 26 automated tests passing
- Coverage: Auth, Projects, Notifications, Admin Dashboard

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
```

---
*Last Updated: February 14, 2026*
