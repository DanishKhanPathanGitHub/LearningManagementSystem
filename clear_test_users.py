import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ELearningApp.settings') 
django.setup()

from accounts.models import User, userProfile
from classroom.models import Classroom

def clear_test_users():
    
    users = User.objects.filter(username__contains="testuser")
    users.delete()
    print("Successfully deleted 500 test users.")

    


if __name__ == "__main__":
    clear_test_users()
