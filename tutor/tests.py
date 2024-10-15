
import datetime
from django.test import Client, TestCase
import time
from django.urls import reverse
from accounts.models import User, userProfile
from classroom.models import Classroom, Assignment, Notification
# Create your tests here.


class NotificationTestCase(TestCase):
    def setUp(self):        
        # Create a tutor
        self.tutor_user = User.objects.create(
            username="testtutor",
            email="testtutor@example.com",
            password="password123",
            firstname="Tutor",
            lastname="Test"
        )
        self.user = User.objects.create(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            firstname="Student",
            lastname="User"
        )

        self.tutor_user.role =  2
        self.tutor_user.is_active = True
        self.tutor_user.save()
        # Create the userProfile for the tutor
        self.tutor_profile = userProfile.objects.get(user=self.tutor_user)
        
        # Create a classroom with the tutor
        self.classroom = Classroom.objects.create(
            name="Test Classroom",
            tutor=self.tutor_profile,  # Set the tutor profile here
            code="TEST123",  # Ensure the code meets your validator requirements
            password="password123"  # Ensure the password meets your validator requirements
        )
        # Create test students and their profiles, and add them to the classroom

        self.client = Client()
        self.client.force_login(user=self.tutor_user)


    def test_notify_all(self):

        for i in range(10000):
            student_user = User.objects.create(
                username=f"testuser{i}",
                email=f"testemail{i}@example.com",
                password="password123",
                firstname=f"First{i}",
                lastname=f"Last{i}"
            )
            student_profile = userProfile.objects.get(user=student_user)
            self.classroom.students.add(student_profile)

        self.assignment = Assignment.objects.create(name="Test Assignment", classroom=self.classroom, due_date=datetime.datetime.now())

        start_time = time.perf_counter()
        response = self.client.post(
            reverse('notify_all', args=[self.classroom.id, self.assignment.id]), 
            {'message':'Send Notification',}, 
            content_type='application/json'
        )

        end_time = time.perf_counter()
        elapsed_time = end_time-start_time
        print(f'notification sent to 1000 students in {elapsed_time} time')

        self.assertEqual(response.json()['status'], 'success')
        

        response = self.client.post(
            reverse('notify_all', args=[self.classroom.id, self.assignment.id]), 
            {'message':'Send Notification',}, 
            content_type='application/json'
        )

        self.assertEqual(response.json().get('status'), 'failure')
        self.assertEqual(response.json()['message'], 'You can notify students only once every 12 hours.')

        
    def test_student_join_notification(self):
        student_profile = userProfile.objects.get(user=self.user)
        self.classroom.requests.add(student_profile)

        url = reverse('tutorClassroom', args=[self.classroom.id])

        response = self.client.post(
            url, {
                'action':'approve',
                'student_id':student_profile.id
            },
            HTTP_X_REQUESTED_WITH = 'XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)

        notification = Notification.objects.filter(
            content__contains=f"{self.classroom.name} accepted"
        ).first()

        self.assertIsNotNone(notification)
        self.assertEqual(notification.link, f'/classroom/{self.classroom.id}')
