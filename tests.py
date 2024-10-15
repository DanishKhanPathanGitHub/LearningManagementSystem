import os
import django
from django.utils import timezone

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ELearningApp.settings')
django.setup()

print(timezone.now())