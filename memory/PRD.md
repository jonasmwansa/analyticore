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
- **AI:** OpenAI GPT-5.2 via Emergent LLM Key

## Core Features

### Implemented Features

#### 1. Authentication System
- [x] Email/Password login
- [x] User registration with email verification
- [x] Token authentication
- [x] Protected routes

#### 2. Project Management
- [x] Create projects with name and source type
- [x] List user's projects with pagination
- [x] Project detail view
- [x] Delete projects

#### 3. File Upload & Data Ingestion
- [x] CSV file upload
- [x] Excel (.xlsx, .xls) file upload
- [x] JSON file upload
- [x] Automatic column type detection
- [x] Data preview (first 100 rows)

#### 4. Statistical Analysis
- [x] **Descriptive Statistics:** Count, Mean, Std, Min, 25%, Median, 75%, Max, Skewness, Kurtosis
- [x] **Categorical Analysis:** Unique count, Top value, Frequency

#### 5. Correlation Analysis
- [x] Pearson/Spearman/Kendall correlation matrices
- [x] Interactive heatmap visualization
- [x] Top correlations ranking with strength classification

#### 6. Distribution Analysis
- [x] Histogram with configurable bins
- [x] Box plot statistics
- [x] Normality tests (Shapiro-Wilk, D'Agostino)
- [x] Outlier detection

#### 7. Data Visualization
- [x] Bar, Line, Scatter, Pie, Histogram, Box Plot, Heatmap charts
- [x] Column selector for X/Y axes

#### 8. AI Quick Insights (NEW)
- [x] AI-powered executive summary of data
- [x] Key findings with importance ranking (high/medium/low)
- [x] Data quality issues detection with severity
- [x] Pattern discovery between columns
- [x] Recommendations with priority
- [x] Regenerate button

#### 9. Column Actions (NEW)
- [x] Per-column issue detection (missing values, outliers, skewness)
- [x] **Null Handling:**
  - Fill with Mean/Median/Mode
  - Forward Fill / Backward Fill
  - Fill with Constant Value
  - Drop Rows with Missing
- [x] **Data Conversion:**
  - Convert to Numeric/DateTime/String/Category
- [x] **Outlier Handling:**
  - Remove Outliers (IQR method)
  - Cap Outliers
- [x] **Text Transformation:**
  - Trim Whitespace
  - Convert to Lowercase/Uppercase
  - Remove Special Characters
- [x] **Duplicate Handling:**
  - Remove Duplicates
- [x] Visual severity indicators (critical/warning/info)
- [x] One-click Apply buttons

#### 10. AI-Powered Cleaning Recommendations
- [x] GPT-5.2 powered analysis
- [x] Missing value strategies
- [x] Outlier detection
- [x] Data type suggestions

#### 11. Data Transformations
- [x] Fill missing values
- [x] Remove duplicates
- [x] Convert data types
- [x] Remove outliers
- [x] Transformation logging

#### 12. Data Export
- [x] Export to CSV, Excel (.xlsx), JSON

#### 13. Notification System
- [x] Email Notifications
- [x] In-App Notifications
- [x] Push Notifications

#### 14. Admin Dashboard
- [x] System statistics
- [x] User management

#### 15. Infrastructure
- [x] MySQL database
- [x] Redis for caching
- [x] Celery for async tasks

### Backlog (Future Tasks)

#### P1 - High Priority
- [ ] Google Sheets integration
- [ ] Database source connections (PostgreSQL, MySQL external)

#### P2 - Medium Priority
- [ ] Stripe billing integration
- [ ] Webhook notifications
- [ ] Scheduled pipelines

## New API Endpoints (This Session)

```
GET  /api/analysis/{id}/insights        - AI quick insights summary
GET  /api/analysis/{id}/column-actions  - Get recommended actions for columns
POST /api/analysis/{id}/apply-action    - Apply a column action
```

## Credentials
- **Admin:** admin@analyticore.com / admin123

---
*Last Updated: February 14, 2026*
