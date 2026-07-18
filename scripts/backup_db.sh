#!/bin/bash

# Database Backup Script for NMT Travels
# This script creates automated daily backups of the MySQL database

set -e

# Configuration
DB_NAME="${DB_NAME:-nmt_travels}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-}"
BACKUP_DIR="/home/${PYTHONANYWHERE_USERNAME}/backups"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/nmt_travels_backup_${TIMESTAMP}.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Create database backup
echo "Creating database backup..."
mysqldump -u "${DB_USER}" -p"${DB_PASSWORD}" "${DB_NAME}" | gzip > "${BACKUP_FILE}"

# Delete backups older than retention period
echo "Cleaning up old backups..."
find "${BACKUP_DIR}" -name "nmt_travels_backup_*.sql.gz" -mtime +${RETENTION_DAYS} -delete

echo "Backup completed: ${BACKUP_FILE}"
echo "Old backups (older than ${RETENTION_DAYS} days) have been deleted."
