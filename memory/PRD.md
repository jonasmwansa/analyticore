# AnalytiCore - Product Requirements Document

## Overview
AnalytiCore is a SaaS data analysis pipeline application that enables users to upload, clean, transform, and analyze data with intelligent rule-based recommendations.

## Tech Stack
- **Backend:** Django REST Framework 5.2
- **Frontend:** React 18 with Tailwind CSS
- **Database:** SQLite (development) / MySQL (production)
- **Cache/Queue:** Redis + Celery
- **Authentication:** DRF Token Authentication
- **Charting:** Recharts
- **Analytics:** Rule-based algorithms (pandas, numpy, scipy, scikit-learn) - NO AI COSTS

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

#### 3. Data Ingestion (Multi-Source)
- [x] **File Upload:** CSV, Excel (.xlsx, .xls), JSON
- [x] **Google Sheets Integration:** OAuth 2.0 flow, spreadsheet picker, sheet selection
- [x] **Database Connections:** MySQL and PostgreSQL with test connection and table selection
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

#### 11. Machine Learning Pipeline (FREE - scikit-learn)
- [x] **Model Training:** Regression (Linear, Ridge, Random Forest) & Classification (Logistic, Decision Tree, Random Forest)
- [x] **Auto-ML:** Automatic model selection and hyperparameter optimization
- [x] **Clustering:** K-Means with elbow method for optimal K
- [x] **Feature Importance:** Visualization of feature contributions
- [x] **PCA:** Dimensionality reduction analysis

#### 12. Data Export (FREE)
- [x] Export to CSV, Excel (.xlsx), JSON

#### 13. Notification System
- [x] Email, In-App, Push Notifications

### Backlog (Future Tasks)

#### P2 - Medium Priority
- [ ] Stripe billing integration
- [ ] Webhook notifications

## Scheduled Pipelines Feature

### Schedule Types
- **Hourly**: Run at a specific minute every hour
- **Daily**: Run at a specific time every day
- **Weekly**: Run on a specific day and time each week
- **Monthly**: Run on a specific day of month at a specific time

### Action Types
- **Refresh Data**: Reload data from source and update statistics
- **Run Analysis**: Execute statistical analysis pipeline
- **Apply Cleaning**: Apply configured data cleaning rules
- **Export Data**: Export data to configured format (CSV/Excel/JSON)
- **Full Pipeline**: Refresh + Analysis + Cleaning + Export

### Pipeline Runs
- Track all executions with status (pending, running, completed, failed)
- Store logs, duration, rows processed
- Support both scheduled and manual triggers
- Automatic failure tracking (pauses after 3 consecutive failures)

### API Endpoints
- `GET /api/pipelines/schedules/` - List all schedules
- `POST /api/pipelines/schedules/create/` - Create new schedule
- `GET /api/pipelines/schedules/{id}/` - Get schedule details with run history
- `PUT /api/pipelines/schedules/{id}/update/` - Update schedule
- `DELETE /api/pipelines/schedules/{id}/delete/` - Delete schedule
- `POST /api/pipelines/schedules/{id}/toggle/` - Pause/Activate schedule
- `POST /api/pipelines/schedules/{id}/run/` - Trigger manual run
- `GET /api/pipelines/schedules/stats/` - Get aggregated statistics
- `GET /api/pipelines/runs/` - Get run history

**Note**: When Redis/Celery is not available, scheduled runs execute synchronously.

## Data Source Integration Details

### Google Sheets (Requires Configuration)
**Environment Variables Required:**
```
GOOGLE_SHEETS_CLIENT_ID=your_client_id
GOOGLE_SHEETS_CLIENT_SECRET=your_client_secret
```
- OAuth 2.0 authentication flow
- List user's spreadsheets
- Select specific sheet within spreadsheet
- Import data directly into project

### Database Connections
**MySQL:**
- Host, Port, Database, Username, Password
- Test connection before import
- Select table or write custom SQL query

**PostgreSQL:**
- Host, Port, Database, Username, Password
- Test connection before import
- Select table or write custom SQL query

## API Endpoints

### Integration APIs
- `GET /api/integrations/google-sheets/status` - Check Google Sheets connection status
- `GET /api/integrations/google-sheets/auth` - Get OAuth authorization URL
- `GET /api/integrations/google-sheets/callback` - OAuth callback handler
- `POST /api/integrations/google-sheets/disconnect` - Disconnect Google Sheets
- `GET /api/integrations/google-sheets/list` - List user's spreadsheets
- `GET /api/integrations/google-sheets/{id}/metadata` - Get spreadsheet metadata
- `POST /api/integrations/google-sheets/{id}/preview` - Preview sheet data
- `POST /api/integrations/google-sheets/{project_id}/import` - Import sheet data to project
- `POST /api/integrations/mysql/test` - Test MySQL connection
- `POST /api/integrations/postgresql/test` - Test PostgreSQL connection
- `POST /api/integrations/database/{project_id}/import` - Import database data to project

## Credentials
- **Test User:** test@example.com / testpass123

---
*Last Updated: February 14, 2026*
*All analytics features work completely OFFLINE with NO API costs!*
