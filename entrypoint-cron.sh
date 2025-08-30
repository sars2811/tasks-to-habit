#!/bin/bash

set -e

echo "Adding cron..."
python manage.py crontab add

echo "Starting cron..."
exec cron -f