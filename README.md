# AnalytiCore - Data Analysis Platform

A powerful, self-contained SaaS application for data analysis pipelines. Upload your data, clean it automatically, run ML models, and generate insights - all without external AI costs.

## Features

- **Data Ingestion**: CSV, Excel, JSON, Google Sheets, MySQL/PostgreSQL databases
- **Auto Data Cleaning**: Smart recommendations for handling missing values, outliers, duplicates
- **Statistical Analysis**: Descriptive stats, correlation matrices, distribution analysis
- **Machine Learning**: Regression, Classification, Clustering (K-Means), PCA, Auto-ML
- **Magic Analysis**: One-click insights with executive summaries and recommendations
- **Compare Projects**: Side-by-side analysis comparison
- **Export Options**: CSV, Excel, PNG, SVG exports for reports and visualizations
- **Admin Dashboard**: User metrics, system health, activity analytics

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 5.2 + Django REST Framework |
| Frontend | React 18 + Tailwind CSS |
| Database | SQLite (dev) / MySQL (prod) |
| Task Queue | Celery + Redis |
| ML/Stats | scikit-learn, scipy, pandas, numpy |
| Charts | Recharts |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Redis (for Celery task queue)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd analyticore
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env  # Or create manually (see Environment Variables below)

# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser

# Start the backend server
python manage.py runserver 8001
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
yarn install  # or: npm install

# Create environment file
echo "REACT_APP_BACKEND_URL=http://localhost:8001" > .env

# Start the frontend
yarn start  # or: npm start
```

### 4. Start Redis & Celery (for async tasks)

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery Worker
cd backend
source venv/bin/activate
celery -A analyticore_api worker -l info

# Terminal 3: Start Celery Beat (for scheduled tasks)
celery -A analyticore_api beat -l info
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001/api/
- **API Docs**: http://localhost:8001/api/docs/
- **Admin Panel**: http://localhost:8001/admin/

## Environment Variables

### Backend (`backend/.env`)

```env
# Database (SQLite by default, MySQL optional)
USE_MYSQL=False
MYSQL_DATABASE=analyticore_db
MYSQL_USER=analyticore
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306

# Django
DJANGO_SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
CORS_ORIGINS=*

# Email (optional - for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Push Notifications (optional - generate your own VAPID keys)
VAPID_PUBLIC_KEY=your-public-key
VAPID_PRIVATE_KEY=your-private-key
```

### Frontend (`frontend/.env`)

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

## Project Structure

```
analyticore/
├── backend/
│   ├── analyticore_api/     # Django settings & main URLs
│   ├── users/               # Authentication & user management
│   ├── projects/            # Project CRUD operations
│   ├── data_ingestion/      # File upload & data source connectors
│   ├── analysis/            # Statistical analysis & ML models
│   ├── pipelines/           # Scheduled analysis pipelines
│   ├── exports/             # Data export functionality
│   ├── api_integrations/    # Google Sheets OAuth
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service layer
│   │   └── App.js
│   └── package.json
│
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/profile` - Get user profile

### Projects
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}/` - Get project details
- `DELETE /api/projects/{id}/` - Delete project
- `POST /api/projects/compare/` - Compare multiple projects

### Analysis
- `POST /api/analysis/statistics/` - Run statistical analysis
- `POST /api/analysis/correlation/` - Correlation analysis
- `POST /api/analysis/distribution/` - Distribution analysis
- `POST /api/analysis/magic/` - Magic analysis (auto-insights)
- `GET /api/analysis/{id}/export-summary/` - Export summary stats
- `GET /api/analysis/{id}/export-correlation/` - Export correlation matrix

### Data Operations
- `POST /api/ingestion/upload/` - Upload file
- `POST /api/ingestion/clean/` - Apply cleaning operations
- `GET /api/ingestion/{id}/preview/` - Preview data

## Default Test Credentials

After running migrations, create a superuser or use:
- **Admin Panel**: Create via `python manage.py createsuperuser`

## Deployment

### Production Checklist

1. Set `DEBUG=False` in backend `.env`
2. Generate a strong `DJANGO_SECRET_KEY`
3. Configure proper `CORS_ORIGINS`
4. Use MySQL/PostgreSQL instead of SQLite
5. Set up proper Redis for Celery
6. Use a production WSGI server (gunicorn)
7. Serve frontend via nginx or CDN

### Docker (Optional)

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## License

MIT License - Feel free to use for personal or commercial projects.

## Support

For issues or feature requests, please open a GitHub issue.
