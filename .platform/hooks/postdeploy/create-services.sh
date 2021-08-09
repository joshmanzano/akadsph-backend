#!/usr/bin/env bash

# Create the celery systemd service file

echo "[Unit]
Name=Celery Worker
Description=Celery worker for Akads
After=network.target

[Service]
Type=simple
Restart=always
RestartSec=1
StartLimitInterval=0
User=root
WorkingDirectory=/var/app/current
ExecStart=$PYTHONPATH/celery -A backend worker --loglevel=INFO -n worker.%%h
EnvironmentFile=/opt/elasticbeanstalk/deployment/env

[Install]
WantedBy=multi-user.target
" | tee /etc/systemd/system/celery-worker.service

# Start celery service
systemctl start celery-worker.service

# Enable celery service to load on system start
systemctl enable celery-worker.service

echo "[Unit]
Name=Celery Beat
Description=Celery beat for Akads
After=network.target

[Service]
Type=simple
Restart=always
RestartSec=1
StartLimitInterval=0
User=root
WorkingDirectory=/var/app/current
ExecStart=$PYTHONPATH/celery -A backend beat -s /tmp/celerybeat-schedule -S redbeat.RedBeatScheduler
EnvironmentFile=/opt/elasticbeanstalk/deployment/env

[Install]
WantedBy=multi-user.target
" | tee /etc/systemd/system/celery-beat.service

# Start celery service
systemctl start celery-beat.service

# Enable celery service to load on system start
systemctl enable celery-beat.service

echo "[Unit]
Name=Daphne
Description=Daphne for Akads
After=network.target

[Service]
Type=simple
Restart=always
RestartSec=1
StartLimitInterval=0
User=root
WorkingDirectory=/var/app/current
ExecStart=$PYTHONPATH/daphne backend.asgi:application --bind 0.0.0.0 --port 8888 --verbosity 1
EnvironmentFile=/opt/elasticbeanstalk/deployment/env

[Install]
WantedBy=multi-user.target
" | tee /etc/systemd/system/daphne.service

# Start celery service
systemctl start dahpne.service

# Enable celery service to load on system start
systemctl enable daphne.service