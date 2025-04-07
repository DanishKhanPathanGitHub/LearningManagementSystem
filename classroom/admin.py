from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Classroom)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(Announcement)
admin.site.register(Notification)
admin.site.register(StudentClassroom)
admin.site.register(Section)
admin.site.register(Lecture)
admin.site.register(Comment)
admin.site.register(StudentLectureProgress)
