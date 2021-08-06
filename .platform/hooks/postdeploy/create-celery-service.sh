#!/usr/bin/env bash

# ## For Celery Worker

# # Create the celery systemd service file
# echo "[Unit]
# Name=Celery-Worker
# Description=Celery service for AkadsPH
# After=network.target
# StartLimitInterval=0

# [Service]
# Type=simple
# Restart=always
# RestartSec=1
# User=root
# WorkingDirectory=/var/app/current
# ExecStart=$PYTHONPATH/celery worker -A backend --loglevel=INFO -n worker.%%h
# EnvironmentFile=/opt/elasticbeanstalk/deployment/env

# [Install]
# WantedBy=multi-user.target
# " | tee /etc/systemd/system/celery-worker.service

# # Start celery service
# systemctl start celery-worker.service

# # Enable celery service to load on system start
# systemctl enable celery-worker.service

# ## For Celery Beat

# # Create the celery systemd service file
# echo "[Unit]
# Name=Celery-Beat
# Description=Celery service for AkadsPH
# After=network.target
# StartLimitInterval=0

# [Service]
# Type=simple
# Restart=always
# RestartSec=1
# User=root
# WorkingDirectory=/var/app/current
# ExecStart=$PYTHONPATH/celery beat -A backend --loglevel=INFO -n worker.%%h
# EnvironmentFile=/opt/elasticbeanstalk/deployment/env

# [Install]
# WantedBy=multi-user.target
# " | tee /etc/systemd/system/celery-beat.service

# # Start celery service
# systemctl start celery-beat.service

# # Enable celery service to load on system start
# systemctl enable celery-beat.service