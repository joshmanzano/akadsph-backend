from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists() and 'ADMIN_PASS' in os.environ:
            User.objects.create_superuser("admin", "josh@akadsph.com", os.environ['ADMIN_PASS'])