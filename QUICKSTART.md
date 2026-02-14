# AnalytiCore - Quick Start Guide

## 5-Minute Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ & Yarn
- MySQL/MariaDB
- Redis

### Step 1: Clone & Environment Setup

```bash
# Clone repository
git clone <your-repo-url>
cd analyticore

# Create Python virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# OR: .\venv\Scripts\activate  # Windows
```

### Step 2: Backend Configuration

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=mysql://root:password@localhost:3306/analyticore
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@analyticore.com
APP_URL=http://localhost:3000
EOF

# Create database
mysql -u root -p -e "CREATE DATABASE analyticore CHARACTER SET utf8mb4;"

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Enter: admin@analyticore.com / YourPassword123!
```

### Step 3: Frontend Configuration

```bash
cd ../frontend

# Install dependencies
yarn install

# Create .env file
echo "REACT_APP_BACKEND_URL=http://localhost:8001" > .env
```

### Step 4: Start All Services

Open 5 terminal windows:

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Backend API
cd backend && source venv/bin/activate
python manage.py runserver 0.0.0.0:8001

# Terminal 3: Celery Worker
cd backend && source venv/bin/activate
celery -A analyticore_api worker -l info

# Terminal 4: Celery Beat (scheduler)
cd backend && source venv/bin/activate
celery -A analyticore_api beat -l info

# Terminal 5: Frontend
cd frontend
yarn start
```

### Step 5: Access the Application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:8001/api/ |
| **Django Admin** | http://localhost:8001/admin/ |

### Step 6: Test the Setup

```bash
# Test API
curl http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@analyticore.com","password":"YourPassword123!"}'
```

---

## Default Credentials

| User | Email | Password | Role |
|------|-------|----------|------|
| Admin | admin@analyticore.com | (your password) | Staff/Admin |

---

## Key URLs

| Page | URL |
|------|-----|
| Landing Page | / |
| Sign In | /signin |
| Sign Up | /signup |
| Dashboard | /dashboard |
| Admin Dashboard | /admin |
| Privacy Policy | /privacy |
| Terms of Service | /terms |
| Security Settings | /settings/security |
| Password Reset | /forgot-password |

---

## Quick API Test

```bash
# 1. Login and get token
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@analyticore.com","password":"YourPassword123!"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

echo "Token: $TOKEN"

# 2. Get user info
curl -s http://localhost:8001/api/auth/me \
  -H "Authorization: Token $TOKEN" | python3 -m json.tool

# 3. Get admin analytics (if admin)
curl -s http://localhost:8001/api/saas-admin/analytics/summary \
  -H "Authorization: Token $TOKEN" | python3 -m json.tool
```

---

## Troubleshooting

### MySQL Connection Error
```bash
# Check MySQL is running
sudo systemctl status mysql

# Create database if missing
mysql -u root -p -e "CREATE DATABASE analyticore;"
```

### Redis Connection Error
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server
redis-cli ping  # Should return: PONG
```

### Port Already in Use
```bash
# Kill process on port
sudo lsof -t -i:8001 | xargs kill -9  # Backend
sudo lsof -t -i:3000 | xargs kill -9  # Frontend
```

### Email Not Working
For Gmail, enable "Less secure app access" or use App Passwords:
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Create App Password for "Mail"
4. Use that password in EMAIL_HOST_PASSWORD

---

## Next Steps

1. **Upload Data**: Create a project and upload a CSV file
2. **Analyze**: Run analysis to get cleaning recommendations
3. **Transform**: Apply transformations to clean your data
4. **Visualize**: Create charts and explore insights
5. **Schedule**: Set up automated analysis pipelines
6. **Enable 2FA**: Go to Security Settings to enable two-factor auth

---

For full documentation, see `TECHNICAL_DOCUMENTATION.md`
