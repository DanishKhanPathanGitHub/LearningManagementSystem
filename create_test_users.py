import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ELearningApp.settings') 
django.setup()

from accounts.models import User, userProfile
from classroom.models import Assignment, Classroom

def create_test_users():
    tutor = userProfile.objects.get(user__email="dinda@gmail.com")
    cls = Classroom.objects.create(name="sample", tutor=tutor, code="danishdanishkhan", password="danishdanishkhan")
    cls.save()

    for i in range(500):
        student_user = User.objects.create(
            username=f"testuser{i}",
            email=f"testemail{i}@example.com",
            password="password123",
            firstname=f"First{i}",
            lastname=f"Last{i}"
        )
        student_profile = userProfile.objects.get(user=student_user)
        cls.students.add(student_profile)

    print("Successfully created 500 test users.")

if __name__ == "__main__":
    create_test_users()
