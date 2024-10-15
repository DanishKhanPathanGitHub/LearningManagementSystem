from django.urls import path, include
from . import views

urlpatterns = [
    path('tutorClassroom/<int:id>/', views.tutorClassroom, name='tutorClassroom'),
    path('tutorClassroom/<int:id>/delete/', views.tutorClassroomDelete, name='tutorClassroomDelete'),
    path("studentCorner/<int:id>/students/", views.studentCorner, name="studentCorner"),
    path("studentCorner/<int:id>/students/<int:sid>/", views.studentCorner, name="studentCorner"),
    path("studentCorner/<int:id>/students/remove_student/<int:sid>/", views.remove_student_from_class, name="remove_student_from_class"),
    
    path('classroom/add/', views.classroomAdd, name='classroomAdd'),
    
    path('classroom/<int:id>/assignments/<int:asid>/', views.tutorSpecificAssignment, name='tutorSpecificAssignment'),
    path('classroom/<int:id>/assignments/<int:asid>/delete/', views.SpecificAssignment_delete, name='SpecificAssignment_delete'),
    path('notify_all/<int:id>/<int:asid>/', views.notify_all, name="notify_all"),
    
    #path('classrroom/<int:id>/lectures/<int:lid>/delete/', views.SpecificLecture_delete, name='SpecificLecture_delete'),
]
 