from django.db import models, transaction
from accounts.models import User, userProfile
from django.core.validators import MinLengthValidator
from tinymce.models import HTMLField
from django.core.files.storage import default_storage
from django.db.models import F

# Create your models here.

class Classroom(models.Model):
    name = models.CharField(max_length=50)
    description = HTMLField(blank=True, null=True)
    tutor = models.ForeignKey(userProfile, on_delete=models.CASCADE, related_name='classroom_tutor')
    students = models.ManyToManyField(userProfile, related_name='classroom_students', blank=True)
    requests = models.ManyToManyField(userProfile, related_name='classroom_requests', blank=True)
    cover_pic = models.ImageField(upload_to='class_coverpics', blank=False, null=True)
    code = models.CharField(MinLengthValidator(6), max_length=16, unique=True)
    password = models.CharField(MinLengthValidator(8), max_length=16, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = ("classroom")
        verbose_name_plural = ("classrooms")

    def __str__(self):
        return self.name
    
    
class StudentClassroom(models.Model):
    student = models.ForeignKey(userProfile, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, related_name='classroom_students_data', on_delete=models.CASCADE)
    joined_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'classroom')

    def delete(self, *args, **kwargs):
        """deletes the submissions and files by student"""
        print('student class delete method called')
        self.student.students_submissions.all().delete()
        
        self.classroom.students.remove(self.student)

        super().delete(*args, **kwargs)

    

class Assignment(models.Model):
    name = models.CharField(max_length=50)
    assignment = models.FileField(upload_to='class/assignments', null=True, blank=False)
    classroom = models.ForeignKey(Classroom, related_name='assignments', on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(auto_now_add=False)
    description = models.TextField(null=True, blank=True)
    late_submission_allow = models.BooleanField(default=False)


    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        """
        deletes the announcements and notifications associated with the assignment
        """
        print('assignment delete method called')
        
        # Delete associated announcements and notifications directly with bulk deletion
        link = f'/classroom/{self.classroom.id}/assignments/{self.id}/'
        Announcement.objects.filter(link=link).delete()
        Notification.objects.filter(link=link).delete()

        super().delete(*args, **kwargs)

class AssignmentSubmission(models.Model):
    submitted_file = models.FileField(upload_to='class/assignments_submissions', null=True, blank=False)
    assignment = models.ForeignKey(Assignment,  related_name='assignment_submissions', on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now=True)
    student = models.ForeignKey(userProfile, related_name='students_submissions', on_delete=models.CASCADE)
    late_submission = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'assignment')


class Announcement(models.Model):
    title = models.CharField(max_length=50)
    file = models.FileField(upload_to='class/announcements',null=True, blank=True)
    content = models.TextField()
    classroom = models.ForeignKey(Classroom, related_name='announcements', on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    link = models.URLField(max_length=1000, null=True, blank=True)
    tutor_link = models.URLField(max_length=1000, null=True, blank=True)


    def __str__(self):
        return self.title
    

class Notification(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    user = models.ForeignKey(userProfile, related_name="notifications", on_delete=models.CASCADE)
    link = models.URLField(max_length=500, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True, blank=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class Section(models.Model):
    title = models.CharField(max_length=50)
    order = models.PositiveIntegerField(null=False)
    uploaded_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    classroom = models.ForeignKey(Classroom, related_name="sections", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('classroom', 'order')
 
    def __str__(self) -> str:
        return self.title
 
    def delete(self, *args, skip_order_adjustment=False, **kwargs):
        """
        deletes the section while maintaining the order of the sections
        deleting section x will decrease the order of sections > x by 1. 
        ex. deleting section 3 make 4th 5th 6th section 3rd 4th and 5th and so on
        operation will be all in one or fail to maintain the order of all sections
        when operation fail for some lectures, ensuring atomicity
        """
        print("section delete method called")
        
        if not skip_order_adjustment:
            self.section_order_adjustments()

        super().delete(*args, **kwargs)
    
    @transaction.atomic
    def section_order_adjustments(self):
        curr_order = self.order
        self.order = 999
        self.save(update_fields=['order'])

        Section.objects.filter(
            classroom=self.classroom, order__gt=curr_order
        ).order_by('order').update(order=F('order')-1)
        

class Lecture(models.Model):
    title = models.CharField(max_length=150)
    section = models.ForeignKey(Section, related_name="lectures", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(null=False)
    attachment = models.FileField(upload_to='class/lectures/notes', null=True, blank=True)
    video = models.FileField(upload_to='class/lectures/video', null=True, blank=True)
    content = HTMLField(blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, null=False, max_length=200)


    class Meta:
        unique_together = ('section', 'order')

    def __str__(self):
        return f'section:{self.section.title} Lecture no:{self.order}'

    @transaction.atomic
    def order_adjustments(self):
        curr_order = self.order
        self.order = 999
        self.save(update_fields=['order'])

        Lecture.objects.filter(
            order__gt=curr_order, section=self.section
        ).order_by('order').update(order=F('order')-1)
    
    def delete(self, *args, skip_order_adjustment=False, **kwargs):
        """
        deletes the lecture while maintaining the order of the lectures
        deleting lecture x will decrease the order of lectures > x by 1. 
        ex. deleting lecture 3 make 4th 5th 6th lecture 3rd 4th and 5th and so on
        operation will be all in one or fail to maintain the order of all lectures 
        when operation fail for some lectures, ensuring atomicity

        also deletes the announcement associated with that lecture
        """
        print("lecture delete method called")
        try:
            link = f'/classroom/{self.section.classroom.id}/lectures/{self.slug}/'
            announcement = Announcement.objects.get(link=link)
            announcement.delete()
        except:
            pass

        if not skip_order_adjustment:
            self.order_adjustments()

        super().delete(*args, **kwargs)

class StudentLectureProgress(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    student = models.ForeignKey(userProfile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('lecture', 'student')
    
    def __str__(self):
        return f'{self.student.user.username} completed {self.lecture}'

class Comment(models.Model):
    lecture = models.ForeignKey(Lecture, related_name="comments", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    text = HTMLField()
    upvote = models.PositiveIntegerField(default=0)
    upvoted_student = models.ManyToManyField(userProfile, related_name="upvoted_comments")
    parent = models.ForeignKey('self', related_name="replies", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(userProfile, related_name="comments", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='class/lectures/comments', null=True, blank=True)
