import os
import django



# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ELearningApp.settings')
django.setup()

import tempfile
from django.core.files import File
from accounts.models import User, userProfile
from classroom.models import (
    Classroom, StudentClassroom, Assignment, AssignmentSubmission, 
    Announcement, Notification, Section, Lecture, StudentLectureProgress, Comment
)
from chatroom.models import ChatGroup
from django.utils.text import slugify
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image



def create_dummy_image():
    # Create a simple red square image
    image = Image.new('RGB', (100, 100), color='red')
    temp_file = BytesIO()
    image.save(temp_file, format='JPEG')
    temp_file.seek(0)
    return ContentFile(temp_file.read(), 'dummy_image.jpg')

def create_dummy_file(filename="dummy_file.txt", content="This is a dummy file for testing."):
    return ContentFile(content.encode('utf-8'), filename)

def create_dummy_video(filename="dummy_video.mp4"):
    # Creates a small binary placeholder for video
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42mp41isom\x00\x00\x00\x08free')
    temp_file.seek(0)
    return ContentFile(temp_file.read(), filename)

def create_test_data():
    # Creating a tutor and classroom
    tutor = userProfile.objects.get(user__email="dinda@gmail.com")
    classroom = Classroom.objects.create(
        name="Sample Classroom",
        tutor=tutor, 
        code="samplecode1234", 
        password="samplepassword1234",
        cover_pic=create_dummy_image()
    )

    ChatGroup.objects.create(classroom=classroom, personal_group=False)
    # Adding students to classroom
    for userprofile in userProfile.objects.filter(user__role=1):  
        classroom.students.add(userprofile)
        StudentClassroom.objects.create(classroom=classroom, student=userprofile)
    
    # Create announcements
    for i in range(15):  # 50 announcements
        Announcement.objects.create(
            title=f"Announcement {i + 1}",
            content="This is a test announcement content.",
            classroom=classroom,
            file=create_dummy_file(filename=f"announcement_{i + 1}.txt")
        )
    
    # Create sections and lectures within each section
    for sec in range(15):  # 5 sections
        section = Section.objects.create(
            title=f"Section {sec + 1}",
            order=sec + 1,
            classroom=classroom
        )
        
        for lec in range(10):  
            Lecture.objects.create(
                title=f"Lecture {lec + 1} in {section.title}",
                section=section,
                order=lec + 1,
                attachment=create_dummy_file(filename=f"lecture_{sec + 1}_{lec + 1}.pdf"),
                video=create_dummy_video(filename=f"lecture_video_{sec + 1}_{lec + 1}.mp4"),
                slug=slugify(f"Lecture {lec + 1} in {section.title}")
            )
    
    # Create assignments
    for i in range(30):  # 25 assignments
        assignment = Assignment.objects.create(
            name=f"Assignment {i + 1}",
            assignment=create_dummy_file(filename=f"assignment_{i + 1}.pdf"),
            classroom=classroom,
            due_date="2024-12-31"
        )
        
        # Create submissions for each assignment
        for student in classroom.students.all():  # 20 submissions per assignment
            AssignmentSubmission.objects.create(
                submitted_file=create_dummy_file(filename=f"submission_{i + 1}_{student.user.username}.pdf"),
                assignment=assignment,
                student=student
            )
    
    # Create notifications for students in the classroom
    for student in classroom.students.all():
        Notification.objects.create(
            title="Welcome to the Classroom",
            content="Hello, this is a test notification for your classroom activities.",
            user=student
        )
    
    # Create student progress for lectures
    for lecture in Lecture.objects.filter(section__classroom=classroom):
        for student in classroom.students.all():  # Mark 30 students as progressing through each lecture
            StudentLectureProgress.objects.create(
                lecture=lecture,
                student=student
            )
    
    # Create comments on lectures
    for lecture in Lecture.objects.filter(section__classroom=classroom):
        for student in classroom.students.all():  # 10 comments per lecture
            Comment.objects.create(
                lecture=lecture,
                text="This is a test comment on the lecture.",
                user=student,
                image=create_dummy_image()
            )
    
    print("Test data creation complete.")

if __name__ == "__main__":
    create_test_data()
