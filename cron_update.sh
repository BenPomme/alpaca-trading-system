#!/bin/bash
# Automated Dashboard Update Script for Cron
# Add to crontab for automatic updates:
# */10 9-16 * * 1-5 cd /path/to/alpaca && ./cron_update.sh
# */30 * * * * cd /path/to/alpaca && ./cron_update.sh

cd "$(dirname "$0")"

echo "$(date): Starting automated dashboard update..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the manual update script
python manual_update.py

echo "$(date): Automated dashboard update completed"