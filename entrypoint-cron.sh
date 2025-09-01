#!/bin/bash

set -e

echo "Adding cron..."
python manage.py crontab add
mkdir -p /code/log/django

echo "Starting cron..."
exec cron -f