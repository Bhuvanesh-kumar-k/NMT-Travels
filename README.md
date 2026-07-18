# NMT Travels Call Taxi Management System

A production-grade, secure, high-performance web application for managing call taxi operations, replacing Excel-based operations for NMT Travels.

## Features

- **Role-Based Access Control**: Admin and Driver roles with specific permissions
- **Trip Management**: Create, update, and track both Taxi and Local trips
- **Automatic Calculations**: Server-side calculations for all derived fields (KM, time, salary, expenses, etc.)
- **Bill Generation**: Professional A4 PDF bills for both Taxi and Local trips
- **Audit Logging**: Complete audit trail for all CRUD operations
- **Dashboard**: Visual charts for profits and expenses (weekly, monthly, yearly)
- **Mobile-Friendly UI**: Responsive design optimized for drivers using phones
- **Progressive Trip Entry**: Drivers can save partial trip data and complete later
- **Salary Management**: Track salary records and advances
- **Secure Authentication**: JWT-based auth with forced password change for Admin

## Tech Stack

### Backend
- **Framework**: Django 4.2.7
- **API**: Django REST Framework
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: MySQL (production), SQLite (development)
- **PDF Generation**: ReportLab
- **Task Queue**: Celery (optional)
- **Monitoring**: Sentry (optional)

### Frontend
- **Framework**: React
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Charts**: Recharts
- **Routing**: React Router
- **HTTP Client**: Axios

### Deployment
- **Platform**: PythonAnywhere
- **CI/CD**: GitHub Actions
- **Web Server**: Gunicorn
- **Static Files**: WhiteNoise

## Project Structure

```
nmt-travels/
├── accounts/              # User authentication and driver management
│   ├── models.py          # User and Driver models
│   ├── views.py           # Auth and driver API views
│   ├── serializers.py     # Data serializers
│   └── management/       # Django management commands
├── trips/                # Trip management
│   ├── models.py          # Trip, SalaryRecord, AuditLog models
│   ├── views.py           # Trip API views with audit logging
│   ├── serializers.py     # Trip serializers
│   └── tests.py           # Unit tests for calculations
├── billing/               # Bill generation
│   ├── models.py          # Bill model
│   ├── views.py           # PDF generation views
│   └── serializers.py     # Bill serializers
├── frontend/              # React frontend
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── context/       # Auth context
│   │   └── services/      # API service
│   └── package.json
├── nmt_travels/           # Django project settings
├── scripts/               # Deployment and backup scripts
├── requirements.txt       # Python dependencies
└── .env                  # Environment variables
```

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL 8.0+ (for production)

### Backend Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd nmt-travels
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create default admin user**
```bash
python manage.py init_admin
# Default credentials: username: Admin, password: Admin@123
```

7. **Run development server**
```bash
python manage.py runserver
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development server**
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/change-password/` - Change password
- `POST /api/auth/forgot-password/` - Forgot password
- `GET /api/auth/me/` - Get current user

### Drivers
- `GET /api/drivers/` - List all drivers
- `POST /api/drivers/` - Create driver (Admin only)
- `GET /api/drivers/<id>/` - Get driver details
- `PUT /api/drivers/<id>/` - Update driver (Admin only)
- `DELETE /api/drivers/<id>/` - Delete driver (Admin only)

### Trips
- `GET /api/trips/` - List trips (with filters)
- `POST /api/trips/` - Create trip
- `GET /api/trips/<id>/` - Get trip details
- `PUT /api/trips/<id>/` - Update trip
- `DELETE /api/trips/<id>/` - Delete trip

### Salary Records
- `GET /api/salary/` - List salary records
- `POST /api/salary/` - Create salary record (Admin only)
- `GET /api/salary/<id>/` - Get salary record
- `PUT /api/salary/<id>/` - Update salary record
- `DELETE /api/salary/<id>/` - Delete salary record

### Bills
- `GET /api/bills/` - List bills
- `POST /api/bills/` - Create bill
- `GET /api/bills/<id>/` - Get bill details
- `GET /api/bills/generate/<trip_id>/` - Generate PDF bill

### Reports
- `GET /api/reports/summary/?range=weekly|monthly|yearly` - Get financial summary

### Audit Logs
- `GET /api/audit-logs/` - List audit logs

## Calculation Formulas

All calculations are performed server-side:

- **TOTAL KM** = ENDING KM - STARTING KM
- **TOTAL TIME** = MOD(TIME OUT - TIME IN, 1) (duration in hours)
- **NET RED INCOME** = RED TAXI INCOME - COMMISSION
- **SALARY** = TOTAL TIME × SALARY_PER_HOUR × 24
- **MAIN SALARY** = SALARY + PREVIOUS SALARY - DR_ADV
- **TOTAL EXPENSE** = CNG + PETROL + SALARY
- **BALANCE AMOUNT** = RED TAXI INCOME - TOTAL EXPENSE
- **BONUS** = TOTAL TIME × 24 × 3
- **TOTAL ADVANCE** = ADVANCE - ADVANCE_RECEIVED_TODAY

### Local Trip Total
**TOTAL** = WAITING CHARGE + INTER STATE PERMIT + LUGGAGE CHARGES + PET CHARGES + HILL CHARGES + TOLL CHARGES + DRIVER ALLOWANCE

## Trip Code Generation

Trip codes are auto-generated in the format: `YYYY + 8-digit sequence`

Example: `202610000001`

The sequence starts at `10000000` and increments for each new trip in the year.

## Testing

Run the test suite:

```bash
python manage.py test
```

Tests cover:
- All calculation formulas
- Trip status transitions
- Local trip specific fields
- Driver operations

## Deployment

### PythonAnywhere Deployment

1. **Set up PythonAnywhere account**
   - Create a new web app
   - Select Python 3.10
   - Set up MySQL database

2. **Configure environment variables**
   - Add all required variables to PythonAnywhere's environment

3. **Deploy using the script**
```bash
bash scripts/deploy.sh
```

4. **Set up automated backups**
   - Add cron job for daily backups:
```bash
0 2 * * * /home/username/nmt-travels/scripts/backup_db.sh
```

### GitHub Actions CI/CD

The project includes a GitHub Actions workflow that:
- Runs tests on every push
- Builds the frontend
- Deploys to PythonAnywhere on main branch pushes

Configure the following secrets in GitHub:
- `PYTHONANYWHERE_HOST`
- `PYTHONANYWHERE_USERNAME`
- `SSH_PRIVATE_KEY`
- `SECRET_KEY`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

## Security Features

- **Password Hashing**: bcrypt/Argon2
- **JWT Authentication**: Secure token-based auth
- **Role-Based Access Control**: Admin vs Driver permissions
- **CSRF Protection**: Enabled for all forms
- **Rate Limiting**: On authentication endpoints
- **HTTPS**: Enforced in production
- **Audit Logging**: Immutable audit trail
- **Input Validation**: Server-side validation and sanitization

## Default Credentials

- **Username**: Admin
- **Password**: Admin@123
- **Note**: Admin will be required to change password on first login

## Maintenance

### Database Backups
Automated daily backups are configured via cron job. Backups are retained for 30 days.

### Log Monitoring
Check Django logs and Sentry (if configured) for errors and performance issues.

### Updates
- Regularly update dependencies: `pip install --upgrade -r requirements.txt`
- Review and apply security patches
- Test thoroughly before deploying updates

## Support

For issues or questions:
- Check the audit logs for troubleshooting
- Review the API documentation
- Contact the development team

## License

Proprietary - NMT Travels

## Timeline and Estimates

- **MVP (core flows)**: 2-3 weeks
- **Hardened production features**: 1-2 weeks
- **Polish, testing, and deployment**: 1 week

## Cost Estimate

- **Development**: $X (based on team size and rates)
- **PythonAnywhere Hosting**: $X/month
- **Domain and SSL**: $X/year
- **Monitoring (Sentry)**: Free tier available
