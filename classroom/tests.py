from django.utils import timezone

from accounts.models import userProfile
from .models import Classroom, Notification,  Assignment
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
class AssignmentTest(TestCase):

    def setUp(self):
        self.tutor_user = get_user_model().objects.create(
            username="testtutor",
            email="testtutor@example.com",
            password="password123",
            firstname="Tutor",
            lastname="Test"
        )
        self.tutor_user.role =  2
        self.tutor_user.is_active = True
        self.tutor_profile = userProfile.objects.get(user=self.tutor_user)
        
        self.classroom = Classroom.objects.create(
            name="Test Classroom",
            tutor=self.tutor_profile,  
            code="TEST123",  
            password="password123"  
        )

        self.assignment = Assignment.objects.create(
            title="titleAssignment"
        )

        self.client = Client()
        self.client.force_login(user=self.tutor_user)