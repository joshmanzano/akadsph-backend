from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Parent, Child, Tutor
import os

class Command(BaseCommand):

    def handle(self, *args, **options):
        if(os.environ['STAGE'] == 'dev'):
            Parent.objects.all().delete()
            Child.objects.all().delete()
            Tutor.objects.all().delete()