import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from classroom.models import Announcement, Assignment, AssignmentSubmission, Classroom, Comment, Lecture, Notification
@receiver(post_save, sender=Assignment)
#reciever will get the signal->post_save from sender-> user
#reciever function below will create/update the userProfile accordingly
#immediately after creation/updation of user(sender)
def assignment_post_save(sender, created, instance, **kwargs):
    if created:
        assignment = instance
        classroom = assignment.classroom
        
        link = f'/classroom/{classroom.id}/assignments/{assignment.id}/'
        tutor_link = f'/tutor/classroom/{classroom.id}/assignments/{assignment.id}/'
        Announcement.objects.create(
            title=f"New Assignment: {assignment.name}",
            content=f"An assignment titled '{assignment.name}' has been added to the classroom.",
            classroom=classroom,
            link=link,
            tutor_link=tutor_link,
        )
    else:
        pass

@receiver(post_save, sender=Lecture)
#reciever will get the signal->post_save from sender-> user
#reciever function below will create/update the userProfile accordingly
#immediately after creation/updation of user(sender)
def lecture_post_save(sender, created, instance, **kwargs):
    if created:
        lecture = instance
        classroom = lecture.section.classroom
        
        link = f'/classroom/{classroom.id}/lectures/{lecture.slug}/'
        Announcement.objects.create(
            title=f"New lecture: {lecture.title}",
            content=f"Lecture'{lecture.title}' has been added to the section: {lecture.section.title}.",
            classroom=classroom,
            link=link,
            tutor_link = link
        )
    else:
        pass

@receiver(pre_delete, sender=Classroom)
def delete_classroom_pic(sender, instance, **kwargs):
    if instance.cover_pic:
        instance.cover_pic.delete(save=False)
    link=f'/classroom/{instance.id}/'
    Notification.objects.filter(link__icontains=link).delete()

@receiver(pre_delete, sender=Assignment)
def delete_assignment_file(sender, instance, **kwargs):
    if instance.assignment:
        instance.assignment.delete(save=False)

@receiver(pre_delete, sender=AssignmentSubmission)
def delete_submission_file(sender, instance, **kwargs):
    if instance.submitted_file:
        instance.submitted_file.delete(save=False)

@receiver(pre_delete, sender=Announcement)
def delete_announcement_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)

@receiver(pre_delete, sender=Lecture)
def delete_lecture_files(sender, instance, **kwargs):
    if instance.attachment:
        instance.attachment.delete(save=False)
    if instance.video:
        instance.video.delete(save=False)

@receiver(pre_delete, sender=Comment)
def delete_comment_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)
