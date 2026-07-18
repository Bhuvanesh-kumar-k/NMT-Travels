# NMT Travels - Deployment Runbook

This document provides step-by-step instructions for deploying and maintaining the NMT Travels Call Taxi Management System on PythonAnywhere.

## Prerequisites

- PythonAnywhere account
- SSH access to PythonAnywhere
- MySQL database credentials
- Domain name configured
- SSL certificate (PythonAnywhere provides free SSL)

## Initial Setup

### 1. Create PythonAnywhere Web App

1. Log in to PythonAnywhere
2. Go to "Web" tab
3. Click "Add a new web app"
4. Select "Manual Configuration" (recommended for Django)
5. Choose Python 3.10
6. Enter domain name (e.g., `yourusername.pythonanywhere.com`)

### 2. Set Up MySQL Database

1. Go to "Databases" tab
2. Click "MySQL" to create a new database
3. Note down:
   - Database name
   - Username
   - Password
   - Host (typically `mysql.server`)

### 3. Clone Repository

```bash
cd ~
git clone <repository-url> nmt-travels
cd nmt-travels
```

### 4. Create Virtual Environment

```bash
python3.10 -m venv venv
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create `.env` file:

```bash
nano .env
```

Add the following:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.pythonanywhere.com

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=mysql.server
DB_PORT=3306

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password

SENTRY_DSN=your-sentry-dsn-optional
```

### 7. Run Migrations

```bash
python manage.py migrate
```

### 8. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 9. Configure WSGI File

1. Go to "Web" tab
2. Click on the WSGI configuration file link
3. Replace contents with:

```python
import os
import sys

path = '/home/yourusername/nmt-travels'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'nmt_travels.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

4. Save the file

### 10. Configure Static Files

In the "Web" tab:
- Static files section:
  - URL: `/static/`
  - Directory: `/home/yourusername/nmt-travels/staticfiles`

### 11. Configure Media Files

In the "Web" tab:
- Static files section:
  - URL: `/media/`
  - Directory: `/home/yourusername/nmt-travels/media`

### 12. Create Default Admin User

```bash
python manage.py init_admin
```

Default credentials:
- Username: `Admin`
- Password: `Admin@123`

### 13. Reload Web App

In the "Web" tab, click the "Reload" button.

## Deployment Process

### Automated Deployment via GitHub Actions

The project includes GitHub Actions CI/CD for automated deployment.

#### Setup GitHub Actions Secrets

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Add the following secrets:

- `PYTHONANYWHERE_HOST`: Your PythonAnywhere SSH host
- `PYTHONANYWHERE_USERNAME`: Your PythonAnywhere username
- `SSH_PRIVATE_KEY`: Your SSH private key
- `SECRET_KEY`: Django secret key
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port

#### Manual Deployment Script

If you need to deploy manually:

```bash
cd ~/nmt-travels
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch /var/www/yourusername_pythonanywhere_com_wsgi.py
```

Or use the provided script:

```bash
bash scripts/deploy.sh
```

## Frontend Deployment

### Option 1: Serve from Django (Recommended for PythonAnywhere)

1. Build the React frontend locally:

```bash
cd frontend
npm run build
```

2. Copy build files to Django static files:

```bash
cp -r build/* ../static/
```

3. Update Django settings to serve React app:

In `nmt_travels/urls.py`, add:

```python
from django.views.generic import TemplateView

urlpatterns += [
    path('', TemplateView.as_view(template_name='index.html')),
]
```

### Option 2: Separate Frontend Deployment

Deploy frontend to a service like Netlify or Vercel, and configure CORS in Django settings.

## Database Backups

### Automated Daily Backups

Set up a cron job in PythonAnywhere:

1. Go to "Tasks" tab
2. Click "Add a new cron job"
3. Configure:
   - Command: `/home/yourusername/nmt-travels/scripts/backup_db.sh`
   - Schedule: Daily at 2 AM
   - Minute: 0, Hour: 2

### Manual Backup

```bash
mysqldump -u username -p database_name > backup.sql
```

### Restore from Backup

```bash
mysql -u username -p database_name < backup.sql
```

## Monitoring and Maintenance

### Check Application Logs

1. Go to "Web" tab
2. Click on the log file links:
   - Error log
   - Access log

### Monitor with Sentry

If Sentry is configured:
- Check Sentry dashboard for errors
- Set up alerts for critical issues

### Update Dependencies

```bash
cd ~/nmt-travels
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Security Updates

1. Regularly check for Django security updates
2. Update Django when security patches are released
3. Test updates in development first

## Troubleshooting

### Application Not Loading

1. Check error logs in "Web" tab
2. Verify WSGI configuration
3. Reload the web app
4. Check database connectivity

### Database Connection Issues

1. Verify database credentials in `.env`
2. Check MySQL service status
3. Test connection manually:

```bash
mysql -h mysql.server -u username -p database_name
```

### Static Files Not Loading

1. Verify static files configuration in "Web" tab
2. Run `collectstatic` again
3. Check file permissions

### Permission Errors

```bash
chmod 755 ~/nmt-travels
chmod -R 755 ~/nmt-travels/staticfiles
```

### Import Errors

1. Ensure all dependencies are installed
2. Check Python version compatibility
3. Reinstall requirements:

```bash
pip install -r requirements.txt --force-reinstall
```

## Performance Optimization

### Enable Caching (Optional)

If using Redis:

1. Install Redis on PythonAnywhere (paid plan)
2. Update settings to use Redis cache
3. Configure cache backends

### Database Optimization

1. Add indexes to frequently queried fields
2. Use `select_related` and `prefetch_related` in queries
3. Monitor slow queries

### Static File Optimization

1. Enable gzip compression (configured in settings)
2. Use CDN for static files (optional)

## Security Checklist

- [ ] DEBUG set to False in production
- [ ] SECRET_KEY is strong and not committed to git
- [ ] Database credentials are secure
- [ ] HTTPS is enabled
- [ ] CSRF protection is enabled
- [ ] Rate limiting is configured
- [ ] Audit logging is enabled
- [ ] Regular backups are scheduled
- [ ] Security headers are configured
- [ ] File permissions are correct

## Rollback Procedure

If deployment fails:

1. Revert to previous commit:

```bash
cd ~/nmt-travels
git log
git checkout <previous-commit-hash>
```

2. Restore database from backup:

```bash
mysql -u username -p database_name < backup.sql
```

3. Reload web app

## Contact and Support

For deployment issues:
- Check PythonAnywhere documentation
- Review error logs
- Contact development team

## Maintenance Schedule

- **Daily**: Automated backups run at 2 AM
- **Weekly**: Review logs and monitor performance
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Full system review and optimization
