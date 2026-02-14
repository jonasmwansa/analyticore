# AnalytiCore - Complete Implementation Guide

## ✅ Completed Features (Session 3)

### 1. Webhook Notifications System
**Models:**
- `Webhook` - User-defined webhooks with event types
- `WebhookDelivery` - Delivery tracking with retry logic

**Features:**
- Event types: project.created, project.uploaded, project.analyzed, project.transformed, project.exported, project.failed
- HMAC signature verification (SHA256)
- Automatic retry logic (up to 3 attempts)
- Delivery status tracking
- Celery task for async sending

**Usage:**
```python
from users.webhook_utils import trigger_webhook

# Trigger webhook
trigger_webhook(
    user=user,
    event_type='project.completed',
    payload={'project_id': str(project_id), 'status': 'success'}
)
```

**API Endpoints:** (To be added)
- POST /api/webhooks/ - Create webhook
- GET /api/webhooks/ - List webhooks
- DELETE /api/webhooks/{id}/ - Delete webhook
- GET /api/webhooks/{id}/deliveries - View delivery history

### 2. Billing Integration (Stripe)
**Models:**
- `StripeCustomer` - Links Django user to Stripe customer
- `BillingPlan` - Subscription plans (Free, Starter, Professional, Enterprise)
- `PaymentHistory` - Payment transaction log

**Plans Structure:**
```
Free:         $0/mo  - 5 projects, 10k rows, 10 AI analyses
Starter:      $29/mo - 20 projects, 100k rows, 50 AI analyses
Professional: $99/mo - 100 projects, 1M rows, 200 AI analyses
Enterprise:   Custom - Unlimited
```

**API Endpoints:**
- GET /api/billing/plans - List available plans
- POST /api/billing/checkout - Create Stripe checkout session
- POST /api/billing/webhook - Stripe webhook handler
- GET /api/billing/history - Payment history

**Integration Steps:**
1. Add Stripe keys to .env:
```
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```
2. Create billing plans:
```bash
python manage.py shell
from users.billing_models import BillingPlan
BillingPlan.objects.create(
    name="Starter",
    plan_type="starter",
    price_monthly=29.00,
    price_yearly=290.00,
    max_projects=20,
    max_rows_per_project=100000,
    max_ai_analyses_per_month=50,
    features=["AI Analysis", "Exports", "Email Support"]
)
```

### 3. Scheduled Pipelines (Celery)
**Models:**
- `ScheduledPipeline` - Pipeline scheduling configuration
- `PipelineRun` - Execution history with logs

**Features:**
- Schedule types: Hourly, Daily, Weekly, Monthly, Custom (cron)
- Pipeline configuration storage
- Execution logs and metrics
- Status tracking (active, paused, failed)
- Run history with duration tracking

**Celery Configuration:**
- Broker: Redis
- Beat scheduler for cron tasks
- Tasks:
  - `retry_failed_webhooks_task` - Every 15 minutes
  - `execute_scheduled_pipeline` - On demand
  - `check_and_run_scheduled_pipelines` - Scheduled checker

**Starting Celery:**
```bash
# Terminal 1: Start Celery worker
celery -A analyticore_api worker --loglevel=info

# Terminal 2: Start Celery beat (scheduler)
celery -A analyticore_api beat --loglevel=info
```

**API Endpoints:** (To be added)
- POST /api/schedules/ - Create scheduled pipeline
- GET /api/schedules/ - List schedules
- GET /api/schedules/{id}/runs - View run history
- POST /api/schedules/{id}/pause - Pause schedule
- POST /api/schedules/{id}/resume - Resume schedule

### 4. Usage Tracking
Already implemented in `UsageTracking` model with Celery task support.

**Usage:**
```python
from users.tasks import track_usage

track_usage.delay(
    user_id=str(user.user_id),
    action='project_created',
    resource_type='project',
    resource_id=str(project_id),
    metadata={'source_type': 'file_upload'}
)
```

## 🔧 Environment Variables (.env)

```bash
# MySQL
MYSQL_DATABASE=analyticore_db
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
USE_MYSQL=True  # Set to True for production

# Django
DJANGO_SECRET_KEY=your-secret-key
DEBUG=False  # Set to False in production
CORS_ORIGINS=https://yourdomain.com

# AI
EMERGENT_LLM_KEY=sk-emergent-...

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=microphase3000@gmail.com
DEFAULT_FROM_EMAIL=microphase3000@gmail.com
EMAIL_HOST_PASSWORD=ymfzvsbynaudwbxr
EMAIL_USE_TLS=True

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Stripe
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## 📊 Database Schema (15 tables)

### Authentication & Users
- users
- email_verification_tokens
- google_auth_sessions
- subscriptions
- usage_tracking
- stripe_customers
- payment_history
- billing_plans

### Projects & Data
- projects
- data_sources
- data_uploads

### Pipeline & Analysis
- analysis_runs
- transformation_logs
- scheduled_pipelines
- pipeline_runs

### Exports & Webhooks
- exports
- webhooks
- webhook_deliveries

### Celery (django-celery-beat)
- django_celery_beat_* (7 tables)

## 🚀 Deployment Checklist

### 1. Install Redis
```bash
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### 2. Configure MySQL
```bash
sudo apt-get install mysql-server
mysql -u root -p
CREATE DATABASE analyticore_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Set Environment Variables
Update .env with production values

### 4. Run Migrations
```bash
cd /app/backend
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. Create Billing Plans
```bash
python manage.py shell
# Execute billing plan creation script
```

### 6. Start Services
```bash
# Django
sudo supervisorctl restart backend

# Celery Worker
celery -A analyticore_api worker --loglevel=info &

# Celery Beat
celery -A analyticore_api beat --loglevel=info &
```

### 7. Configure Stripe Webhook
1. Go to Stripe Dashboard > Webhooks
2. Add endpoint: https://yourdomain.com/api/billing/webhook
3. Select events: checkout.session.completed, payment_intent.succeeded
4. Copy webhook secret to .env

## 📱 Frontend Integration

### Billing UI
```javascript
import { api } from '../api';

// Get plans
const plans = await api.get('/billing/plans');

// Create checkout
const response = await api.post('/billing/checkout', {
  plan_id: selectedPlan.plan_id,
  billing_period: 'monthly'
});
window.location.href = response.data.checkout_url;
```

### Webhooks UI
```javascript
// Create webhook
await api.post('/webhooks/', {
  name: 'My Webhook',
  url: 'https://myapp.com/webhook',
  event_types: ['project.completed', 'project.failed'],
  secret: 'my-secret-key'
});
```

## 🧪 Testing New Features

### Test Webhook
```bash
curl -X POST https://yourdomain.com/api/webhooks/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Webhook",
    "url": "https://webhook.site/unique-url",
    "event_types": ["project.completed"],
    "secret": "test-secret"
  }'
```

### Test Billing
```bash
curl -X GET https://yourdomain.com/api/billing/plans \
  -H "Authorization: Token YOUR_TOKEN"
```

### Test Scheduled Pipeline
```python
from pipelines.tasks import execute_scheduled_pipeline
execute_scheduled_pipeline.delay(schedule_id)
```

## 🎯 Next Steps

1. **Build Frontend UIs:**
   - Billing/subscription page
   - Webhook management page
   - Scheduled pipeline configuration page
   
2. **Add Missing API Endpoints:**
   - Webhook CRUD
   - Scheduled pipeline CRUD
   
3. **Testing:**
   - End-to-end billing flow
   - Webhook delivery testing
   - Scheduled pipeline execution
   
4. **Monitoring:**
   - Celery monitoring (Flower)
   - Webhook delivery metrics
   - Billing analytics dashboard

## 💡 Business Metrics to Track

### Revenue Metrics
- MRR (Monthly Recurring Revenue)
- ARR (Annual Recurring Revenue)
- Churn rate
- Average revenue per user (ARPU)
- Lifetime value (LTV)

### Usage Metrics
- Projects created per user
- Data rows processed
- AI analyses performed
- Export requests
- Pipeline executions

### System Metrics
- Webhook delivery success rate
- Pipeline execution time
- API response times
- Error rates

## 📈 Growth Features (Future)

1. **Team Collaboration** - Multi-user workspaces
2. **API Access** - REST API for programmatic access
3. **Data Warehouse Connectors** - Snowflake, BigQuery
4. **Advanced Pipelines** - Custom Python steps
5. **White Labeling** - Custom branding for enterprise
6. **Audit Logs** - Complete activity tracking
7. **SSO Integration** - SAML, LDAP support
8. **Data Governance** - Column-level permissions
9. **Export Templates** - Customizable report formats
10. **Alerting** - Slack, Teams, PagerDuty integration
