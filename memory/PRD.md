# AnalytiCore - Product Requirements Document

## Overview
AnalytiCore is a SaaS data analysis pipeline application that enables users to upload, clean, transform, and analyze data with intelligent rule-based recommendations.

**100% Self-Contained Application** - No external platform dependencies. All ML/analysis runs locally using scikit-learn, scipy, and pandas.

## Tech Stack
- **Backend:** Django REST Framework 5.2
- **Frontend:** React 18 with Tailwind CSS
- **Database:** SQLite (development) / MySQL (production)
- **Cache/Queue:** Redis + Celery
- **Authentication:** DRF Token Authentication
- **Charting:** Recharts
- **Analytics:** Rule-based algorithms (pandas, numpy, scipy, scikit-learn) - NO AI COSTS

## Changelog
- **Dec 2025:** Removed unused `EMERGENT_LLM_KEY` from settings.py, removed `emergentintegrations` from requirements.txt, deleted unused backup file `server_fastapi_backup.py`

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

#### 14. Enhanced Admin Dashboard (NEW - Feb 14, 2026)
- [x] **Dark-themed sidebar navigation** with 10 sections
- [x] **User Metrics:** DAU, WAU, MAU, Stickiness (DAU/MAU), Growth Rate, Churn, Returning Users
- [x] **User Growth Charts:** 30-day growth trend with Recharts
- [x] **Activity Analytics:** Top actions, resource types, hourly distribution, power users
- [x] **Project Analytics:** Project status/source breakdown, transformation stats
- [x] **Pipeline Analytics:** Active/paused pipelines, success rate, run history
- [x] **Retention & Funnels:** Day 1/7/30 retention, cohort analysis, user journey funnel
- [x] **System Health:** DB response time, error rate, status indicators (healthy/warning/critical)
- [x] **All Users List:** Complete user table with email, status, projects, plan
- [x] **All Projects List:** Complete project table with user, source, status, rows
- [x] **Activity Feed:** Real-time activity log

#### 15. Code Refactoring & System Improvements (Feb 14, 2026)
- [x] **Refactored analysis/views.py** into modular services:
  - `DataLoaderService` - Handles loading project data into DataFrames
  - `TransformationService` - Handles data transformations
  - `ColumnActionService` - Handles individual column actions
- [x] **Fixed Redis/Celery async environment:**
  - Installed and configured Redis server
  - Celery workers now properly connected to Redis broker
  - Scheduled pipelines run asynchronously (with sync fallback)
- [x] **System Health Monitoring with Email Alerts:**
  - `check_system_health` task runs every 15 minutes
  - `daily_health_summary` sends daily summary at 8 AM
  - Email alerts to all admin users when:
    - Error rate > 5%
    - DB response > 500ms
    - Errors in 24h > 10
  - In-app notifications created for admin users
  - Thresholds: error_rate=5%, db_response=500ms, errors_24h=10

#### 16. Security & Compliance Features (Feb 14, 2026)
- [x] **Two-Factor Authentication (2FA) with Email OTP:**
  - Email-based OTP with 10-minute expiry
  - 3 attempt limit per OTP
  - Enable/disable via user settings
  - Security audit logging for all 2FA events
- [x] **Government-Grade Password Policy:**
  - Minimum 12 characters
  - Requires uppercase, lowercase, digit, special character
  - 90-day password expiry
  - Cannot reuse last 5 passwords
  - Real-time password strength indicator
- [x] **Password Reset Flow:**
  - Email-based reset with 1-hour token expiry
  - Secure token invalidation after use
  - Password validation on reset
- [x] **Security Settings Page:**
  - 2FA enable/disable
  - Password change with validation
  - Security audit log display
- [x] **Admin Alert Settings (Configurable):**
  - Error rate threshold (%)
  - DB response threshold (ms)
  - Max errors in 24h
  - Health check interval
  - Alert/summary email toggles
  - Additional recipient list
- [x] **Privacy Policy & Terms of Service:**
  - Comprehensive privacy policy page
  - Terms of service page
  - Footer links on landing page
- [x] **Security Audit Logging:**
  - Login success/failure
  - Password changes/resets
  - 2FA enable/disable
  - Account lockout events
  - Settings changes

#### 17. Magic Analysis - One-Click Data Analysis (Feb 14, 2026) ✨ NEW
- [x] **One-Click Analysis Button:**
  - "Analyze My Data" button in Analysis tab
  - Triggers comprehensive analysis pipeline
  - Re-analyze button for refreshing results
- [x] **Executive Summary:**
  - Quality Score ring (0-100) with color-coded label
  - Plain-English summary text explaining data characteristics
  - Stats cards: Total Rows, Columns, Missing Values, Duplicates
- [x] **Data Profile:**
  - Column-by-column profiling (type, missing, unique, statistics)
  - Distribution type detection (normal, skewed, heavy-tailed)
  - Outlier detection per column with counts/percentages
  - Cardinality analysis for categorical columns
- [x] **Data Quality Assessment:**
  - Quality score calculation (missing values, duplicates, size penalties)
  - Issues list with severity levels (critical/warning/info)
  - Issue types: missing_values, duplicates, outliers, high_cardinality, constant_column
- [x] **Cleaning Suggestions with User Options:**
  - Per-column cleaning recommendations
  - Dropdown to select strategy: mean, median, mode, forward_fill, constant, drop_rows
  - Recommended strategy highlighted with sparkle icon
  - Select All / Apply Selected functionality
  - Priority levels: high/medium/low
- [x] **Plain-English Insights:**
  - Strong correlation detection with natural language description
  - Distribution patterns explained in simple terms
  - Category dominance warnings
  - ML readiness assessment
  - Small dataset warnings
- [x] **Suggested Visualizations:**
  - Automatic chart recommendations based on data types
  - Histogram for numeric distributions
  - Heatmap for correlation visualization
  - Scatter plots for correlated pairs
  - Bar/pie charts for categorical columns
- [x] **Apply Cleaning Operations:**
  - POST endpoint to apply selected cleaning strategies
  - Supports: missing value handling, duplicate removal, type conversion, text normalization
  - Returns change log with affected counts

#### 18. Dashboard Layout with Collapsible Sidebar (Feb 14, 2026) ✨ NEW
- [x] **Shared DashboardLayout Component:**
  - Collapsible sidebar (expand/collapse with toggle button)
  - Responsive design (mobile hamburger menu)
  - Sidebar state persisted in localStorage
  - Navigation items: Dashboard, Schedules, Security, Notifications
  - Admin Dashboard (visible only for staff users)
- [x] **User Profile Section:**
  - User avatar with initials
  - Name and email display
  - Settings dropdown menu
  - Quick access to logout
- [x] **Applied to Pages:**
  - Dashboard (Projects list)
  - ScheduledPipelines page

#### 19. Export Analysis Reports (Feb 14, 2026) ✨ NEW
- [x] **Export Button in Magic Analysis:**
  - Dropdown menu with format options
  - Export as Excel (.xlsx) with multiple sheets
  - Export as CSV (plain text summary)
  - Export as JSON (raw analysis data)
- [x] **Excel Report Contents:**
  - Executive Summary sheet
  - Data Quality issues sheet
  - Key Insights sheet
  - Column Profile sheet (with statistics)
  - Cleaning Suggestions sheet
  - Correlation Matrix sheet
  - Statistics Summary sheet
- [x] **CSV Report Contents:**
  - Executive summary section
  - Data quality issues table
  - Key insights list
  - Column profile summary

#### 20. Frontend Component Refactoring (Feb 14, 2026) ✨ NEW
- [x] **AdminDashboard.js Refactoring:**
  - Reduced from ~1235 lines to ~180 lines
  - Created 11 reusable section components in `/frontend/src/components/admin/`:
    - `OverviewSection.js` - Main dashboard overview with charts
    - `UserMetricsSection.js` - DAU/WAU/MAU metrics
    - `ActivitySection.js` - Activity analytics and power users
    - `ProjectsSection.js` - Project analytics and statistics
    - `PipelinesSection.js` - Pipeline run analytics
    - `RetentionSection.js` - Retention & funnel analytics
    - `SystemSection.js` - System health monitoring
    - `UsersListSection.js` - All users table
    - `ProjectsListSection.js` - All projects table
    - `ActivityFeedSection.js` - Real-time activity feed
    - `AlertSettingsSection.js` - Admin alert configuration
  - Index file for clean exports: `/frontend/src/components/admin/index.js`
- [x] **ProjectView.js Refactoring:**
  - Integrated with shared `DashboardLayout` component
  - Created 3 reusable components in `/frontend/src/components/project/`:
    - `DataPreviewSection.js` - Statistics cards and data table
    - `RecommendationsSection.js` - AI cleaning recommendations
    - `ProjectHeader.js` - Navigation and export controls
  - Consistent sidebar navigation across all pages

#### 21. Enhanced Export Feature (Feb 14, 2026) ✨ NEW
- [x] **Summary Statistics Export:**
  - Export descriptive statistics for all columns (CSV/Excel)
  - Includes: count, mean, std, min, 25%, median, 75%, max, skewness, kurtosis
  - Separate sheets for numeric and categorical columns in Excel
- [x] **Correlation Matrix Export:**
  - Export correlation coefficients (CSV/Excel)
  - Supports Pearson, Spearman, and Kendall methods
  - Includes top correlations list with strength classification
- [x] **Distribution Analysis Export:**
  - Export histogram data, box plot statistics (CSV/Excel)
  - Includes normality tests (Shapiro-Wilk, D'Agostino) results
  - Per-column distribution type and outlier counts
- [x] **Visualization Export (PNG/SVG):**
  - Correlation Heatmap - interactive color-coded matrix
  - Distribution Charts - histogram + box plot for numeric columns
  - Summary Dashboard - overview with multiple charts (missing values, data types, stats)

#### 22. Compare Projects Feature (Feb 14, 2026) ✨ NEW
- [x] **Compare Projects API:**
  - GET `/api/projects/comparable/` - List projects with data available for comparison
  - POST `/api/projects/compare/` - Compare 2-4 projects with quality scores and metrics
- [x] **Dedicated Compare Page (`/compare`):**
  - Project selection cards with checkboxes (2-4 projects)
  - Side-by-side comparison table (quality score, rows, columns, missing %, duplicates, issues)
  - Charts tab with radar chart and bar charts
  - Details tab with per-project breakdown cards
  - Comparison metrics: Best Quality, Most Complete, Most Rows, Fewest Issues
- [x] **Compare Projects Modal (Dashboard):**
  - Accessible via "Compare" button on Dashboard
  - Quick project selection without leaving dashboard
  - "Open Full Page" link to dedicated compare page
- [x] **Enhanced Export Modal:**
  - Integrated into Magic Analysis "Export Report" dropdown
  - "Advanced Export Options..." opens modal with 6 export types
  - Format selectors (CSV/Excel/PNG/SVG)
  - Method selector for correlation (Pearson/Spearman/Kendall)

### Enhanced Export API Endpoints (NEW)
- `GET /api/exports/{project_id}/export-statistics?export_format=csv|excel` - Export summary statistics
- `GET /api/exports/{project_id}/export-correlation?export_format=csv|excel&method=pearson|spearman|kendall` - Export correlation matrix
- `GET /api/exports/{project_id}/export-distribution?export_format=csv|excel` - Export distribution analysis
- `GET /api/exports/{project_id}/export-visualization?export_format=png|svg&chart_type=correlation|distribution|summary` - Export visualizations

### Compare Projects API Endpoints (NEW)
- `GET /api/projects/comparable/` - Get list of projects with data for comparison
- `POST /api/projects/compare/` - Compare 2-4 projects { project_ids: [...] }

### Export Analysis API Endpoints (Updated)
- `GET /api/analysis/{project_id}/magic-export?export_format=json|csv|excel` - Export comprehensive analysis report

### Security API Endpoints
- `POST /api/auth/2fa/enable` - Send OTP to enable 2FA
- `POST /api/auth/2fa/verify-enable` - Verify OTP and enable 2FA
- `POST /api/auth/2fa/disable` - Disable 2FA (requires password)
- `POST /api/auth/2fa/send-otp` - Send login OTP
- `POST /api/auth/2fa/verify-otp` - Verify login OTP and get token
- `POST /api/auth/password/reset-request` - Request password reset
- `POST /api/auth/password/verify-token` - Verify reset token
- `POST /api/auth/password/reset` - Reset password with token
- `POST /api/auth/password/update` - Update password (authenticated)
- `POST /api/auth/password/validate` - Validate password strength
- `GET /api/auth/security/settings` - Get user security settings
- `GET /api/auth/security/audit-log` - Get security audit log
- `GET /api/saas-admin/settings/alerts` - Get alert settings (admin)
- `PUT /api/saas-admin/settings/alerts/update` - Update alert settings (admin)
- `POST /api/saas-admin/settings/alerts/test-email` - Send test alert email

### Admin Dashboard API Endpoints
- `GET /api/saas-admin/analytics/summary` - Dashboard overview
- `GET /api/saas-admin/analytics/users` - User metrics (DAU/WAU/MAU/stickiness)
- `GET /api/saas-admin/analytics/user-growth?days=30` - User growth chart
- `GET /api/saas-admin/analytics/activity?days=30` - Activity analytics
- `GET /api/saas-admin/analytics/projects?days=30` - Project analytics
- `GET /api/saas-admin/analytics/pipelines?days=30` - Pipeline analytics
- `GET /api/saas-admin/analytics/subscriptions` - Subscription breakdown
- `GET /api/saas-admin/analytics/retention` - Cohort retention analysis
- `GET /api/saas-admin/analytics/funnel` - User journey funnel
- `GET /api/saas-admin/analytics/feed?limit=50` - Activity feed
- `GET /api/saas-admin/analytics/health` - System health metrics

### Backlog (Future Tasks)

#### P2 - Medium Priority
- [ ] Stripe billing integration
- [ ] Webhook notifications
- [ ] Real-time WebSocket notifications
- [ ] User impersonation (admin)

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

### Pipeline Notifications
- **Pipeline Complete**: Email/push notification when pipeline succeeds
- **Pipeline Failed**: Email/push notification when pipeline fails
- Configurable in Notification Settings page
- In-app notifications with bell icon

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
- **Admin User:** admin@analyticore.com / adminpassword (is_staff=true)

---
### Code Architecture

```
/app/
├── backend/
│   ├── analytics/
│   │   ├── services/
│   │   ├── magic_analysis_service.py
│   │   ├── magic_views.py
│   │   └── urls.py
│   └── ...
└── frontend/
    └── src/
        ├── components/
        │   ├── admin/              # Refactored admin components (11 sections)
        │   │   ├── index.js
        │   │   ├── OverviewSection.js
        │   │   ├── UserMetricsSection.js
        │   │   ├── ActivitySection.js
        │   │   ├── ProjectsSection.js
        │   │   ├── PipelinesSection.js
        │   │   ├── RetentionSection.js
        │   │   ├── SystemSection.js
        │   │   ├── UsersListSection.js
        │   │   ├── ProjectsListSection.js
        │   │   ├── ActivityFeedSection.js
        │   │   ├── AlertSettingsSection.js
        │   │   └── MetricCard.js
        │   ├── project/            # Refactored project components
        │   │   ├── index.js
        │   │   ├── DataPreviewSection.js
        │   │   ├── RecommendationsSection.js
        │   │   └── ProjectHeader.js
        │   ├── DashboardLayout.js  # Shared layout with collapsible sidebar
        │   └── ui/                 # Shadcn UI components
        └── pages/
            ├── AdminDashboard.js   # Refactored (~180 lines)
            └── ProjectView.js      # Refactored with DashboardLayout
```

---
*Last Updated: February 14, 2026*
*All analytics features work completely OFFLINE with NO API costs!*
*Magic Analysis provides one-click insights using local ML methods only - no external AI services required!*
