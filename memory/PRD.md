# AnalytiCore - Product Requirements Document

## Overview
AnalytiCore is a SaaS data analysis pipeline application that enables users to upload, clean, transform, and analyze data with intelligent rule-based recommendations.

## Tech Stack
- **Backend:** Django REST Framework 5.2
- **Frontend:** React 18 with Tailwind CSS
- **Database:** MySQL (MariaDB)
- **Cache/Queue:** Redis + Celery
- **Authentication:** DRF Token Authentication
- **Charting:** Recharts
- **Analytics:** Rule-based algorithms (pandas, numpy, scipy) - NO AI COSTS

## Core Features - ALL WORK OFFLINE & FREE

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

#### 4. Statistical Analysis (FREE)
- [x] **Descriptive Statistics:** Count, Mean, Std, Min, 25%, Median, 75%, Max, Skewness, Kurtosis
- [x] **Categorical Analysis:** Unique count, Top value, Frequency

#### 5. Correlation Analysis (FREE)
- [x] Pearson/Spearman/Kendall correlation matrices
- [x] Interactive heatmap visualization
- [x] Top correlations ranking with strength classification

#### 6. Distribution Analysis (FREE)
- [x] Histogram with configurable bins
- [x] Box plot statistics
- [x] Normality tests (Shapiro-Wilk, D'Agostino)
- [x] Outlier detection

#### 7. Data Visualization (FREE)
- [x] Bar, Line, Scatter, Pie, Histogram, Box Plot, Heatmap charts
- [x] Column selector for X/Y axes

#### 8. Quick Insights - RULE-BASED (FREE, NO AI)
- [x] Automatic executive summary of data
- [x] Key findings with importance ranking (high/medium/low)
- [x] Data quality issues detection with severity
- [x] Pattern discovery between columns
- [x] Recommendations with priority
- [x] Regenerate button

#### 9. Column Actions (FREE)
- [x] Per-column issue detection (missing values, outliers, skewness)
- [x] **Null Handling:** Fill with Mean/Median/Mode, Forward/Backward Fill, Constant, Drop Rows
- [x] **Data Conversion:** Numeric, DateTime, String, Category
- [x] **Outlier Handling:** Remove (IQR) or Cap outliers
- [x] **Text Transforms:** Trim, Lowercase, Uppercase, Remove Special Chars
- [x] **Duplicates:** Remove duplicate rows

#### 10. Cleaning Recommendations - RULE-BASED (FREE, NO AI)
- [x] Intelligent missing value strategies based on skewness
- [x] Outlier detection using IQR method
- [x] Data type conversion suggestions
- [x] Column naming improvements

#### 11. Data Export (FREE)
- [x] Export to CSV, Excel (.xlsx), JSON

#### 12. Notification System
- [x] Email, In-App, Push Notifications

### Backlog (Future Tasks)

#### P1 - High Priority
- [ ] Google Sheets integration
- [ ] Database source connections

#### P2 - Medium Priority
- [ ] Stripe billing integration
- [ ] Scheduled pipelines

## Credentials
- **Admin:** admin@analyticore.com / admin123

---
*Last Updated: February 14, 2026*
*All analytics features work completely OFFLINE with NO API costs!*
