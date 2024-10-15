from django.urls import path, include
from . import views

urlpatterns = [
    path('classroom/<int:id>', views.classroom, name='classroom'),
    path('classroom/join/', views.classroomJoin, name='classroomJoin'),
    path('classroom/<int:id>/exit/', views.classroomExit, name="classroomExit"),
    
    path('classroom/<int:id>/assignments/', views.assignments, name='assignments'),
     path('classroom/<int:id>/assignments/add/', views.assignments_add, name='assignments_add'),
    path('classroom/<int:id>/assignments/<int:asid>/', views.SpecificAssignment, name='SpecificAssignment'),
    path('classroom/<int:id>/assignments/<int:asid>/delete/', views.SubmissionDelete, name='SubmissionDelete'),
    
    path('classroom/<int:id>/lectures/', views.lectures, name='lectures'),

    path('classroom/<int:id>/lectures/add_section', views.add_section, name='add_section'),
    path('classroom/<int:id>/lectures/update_section/<int:sid>/', views.update_section, name='update_section'),
    path('classroom/<int:id>/lectures/delete_section/<int:sid>/', views.delete_section, name='delete_section'),

    path('classroom/<int:id>/lectures/<slug:slug>/', views.lectures, name='lectures'),
    path('ajax/get_order_choices/<int:curr_section_id>/<int:section_id>/', views.get_order_choices, name='get_order_choices'),
    path('classroom/<int:id>/update_lecture/<slug:slug>/', views.update_lecture, name='update_lecture'),
    path('toggle-lecture-completion/', views.toggle_lecture_completion, name='toggle_lecture_completion'),
    
    path('classroom/<int:id>/lectures/<int:sid>/add_lecture/', views.add_lecture, name='add_lecture'),
    path('classroom/<int:id>/lectures/delete/<slug:slug>/', views.delete_lecture, name='delete_lecture'),
    
    path('classroom/<int:id>/lecture/<slug:slug>/post_comment/', views.post_comment, name='post_comment'),
    path('upvote_comment/<slug:slug>/<int:cid>/', views.upvote_comment, name="upvote_comment"),
    path('classroom/<int:id>/lectures/<slug:slug>/comments/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    

    path('classroom/<int:id>/announcements/', views.announcements, name='announcements'),
    path('classroom/<int:id>/announcements/<int:anid>/delete/', views.announcement_delete, name='announcement_delete'),
    path('classroom/<int:id>/announcements_delete_bulk/', views.announcement_delete_bulk, name='announcement_delete_bulk'),
    path('classroom/<int:id>/announcements/add/', views.announcements_add, name='announcements_add'),
    path('tutor/', include('tutor.urls')),
 ]
 