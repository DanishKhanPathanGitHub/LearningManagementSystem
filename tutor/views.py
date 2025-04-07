import threading
from django.http import JsonResponse
from django.shortcuts import render, redirect
from classroom.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.db.models import Count, Prefetch
from django.core import cache

from accounts.utils import check_role_tutor
from classroom.utils import check_classroom_participant, load_class_data_from_cache
from .forms import *
from accounts.models import userProfile
from django.contrib import messages


@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def tutorClassroom(request, id):
    user = request.user 
    if check_classroom_participant(user, id):
        class_data = load_class_data_from_cache(request, user.id, id)
        Class = class_data['class']
        classroom_data = Classroom.objects.only('id').prefetch_related(
            Prefetch(
                'requests', queryset=userProfile.objects.select_related('user').only(
                'profile_pic', 'id', 'user__username', 'user__email'
            )),
            Prefetch(
                'classroom_students_data__student__user',
                queryset=User.objects.select_related('userprofile').only('id', 'username', 'userprofile__profile_pic')
            )
        ).get(id=id)

        mini_form = ClassroomMiniForm(instance=Class)
        if request.POST:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                action = request.POST.get('action')
                student_id = request.POST.get('student_id')
                if action == 'approve':
                    student_request = userProfile.objects.select_related('user').only(
                        'user__username', 'user__email', 'profile_pic'
                    ).get(id=student_id)
                    classroom_data.requests.remove(student_request)
                    classroom_data.students.add(student_request)
                    StudentClassroom.objects.create(classroom=Class, student=student_request)
                    Notification.objects.create(
                        user = student_request,
                        title="Classroom Join request accepted!",
                        content=f"""
                            Hello {student_request.user.username} \n Your requst to join classroom:
                            {Class.name} accepted by the tutor
                        """,
                        link = f'/classroom/{Class.id}'
                    )

                    return JsonResponse({
                            'status': 'success', 'message': 'Request approved',
                            'student': {
                            'username': student_request.user.username,
                            'email': student_request.user.email,
                            'profile_pic': student_request.profile_pic.url if student_request.profile_pic else '/static/images/male.png'
                            }
                        })
                elif action == 'reject':
                    student_request = userProfile.objects.select_related('user').only('user__username').get(id=student_id)
                    Class.requests.remove(student_request)
                    Notification.objects.create(
                        user = student_request,
                        title="Classroom Join request denied!",
                        content=f"""
                            Hello {student_request.user.username} \n Your requst to join classroom:
                            {Class.name} rejected by the tutor
                        """
                    )

                    return JsonResponse({'status': 'success', 'message': 'Request rejected'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)
            else:
                mini_form = ClassroomMiniForm(request.POST, request.FILES, instance=Class)
                if mini_form.is_valid():
                    mini_form.save()
                    messages.success(request, 'changes saved succesfully')
                    return redirect('tutorClassroom', id)

        context = {
            "Class":Class,
            "class_students":classroom_data.classroom_students_data.all()[:6],
            "mini_form":mini_form,
            "requests":classroom_data.requests.all(),
        }
        return render(request, 'tutor/tutorClassroom.html', context)
    
@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def tutorClassroomDelete(request, id):
    user = request.user 
    if check_classroom_participant(user, id):

        if request.POST:
            Class = Classroom.objects.select_related('tutor__user').prefetch_related(
                'assignments', 'assignments__assignment_submissions', 'announcements',
                'classroom_students_data', 'students__user'
            ).get(id=id)

            def send_notification_to_students():
                notifications = [
                    Notification(
                        title="Classroom deactivated",
                        content=f"Hello {student.user.username}! Your classroom: {Class.name} has been deactivated by the tutor.",
                        user=student
                    )
                    for student in Class.students.all()
                ]
                Notification.objects.bulk_create(notifications)


            def deleting_class():   
                Class.delete()

            def deleting_the_cache():
                student_cache_keys = [f'classroom_participant_{student.user.id}_{id}' for student in Class.students.all()]
                for key in student_cache_keys:
                    cache.cache.delete(key=key)

            notification_thread = threading.Thread(target=send_notification_to_students)
            deletion_thread = threading.Thread(target=deleting_class)
            deletion_cache_thread = threading.Thread(target=deleting_the_cache)

            notification_thread.start()
            deletion_thread.start()
            deletion_cache_thread.start()

            notification_thread.join()
            deletion_thread.join()
            deletion_cache_thread.join()

            cache_key = f"classroom_participant_{request.user.id}_{id}"
            cache.cache.delete(key=cache_key) 
       
            messages.success(request, 'Your classroom has been deleted successfully.')
            return redirect('home')
        else:
            return render(request, '403.html')

@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def classroomAdd(request):
    if request.POST:
        class_form = ClassroomForm(request.POST, request.FILES)
        if class_form.is_valid():
            Class = class_form.save(commit=False)
            Class.tutor = request.user.userprofile
            Class.save()
            messages.success(request, "class created succesfully")
            return redirect('home')

    else:
        class_form = ClassroomForm()
    context = {
        "class_form":class_form
    }
    return render(request, 'tutor/classroom_add.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def studentCorner(request, id, sid=None):
    if check_classroom_participant(request.user, id):
        student = None
        class_data = load_class_data_from_cache(request, request.user.id, id)
        Class = class_data['class']
        classroom_data = Classroom.objects.only('id').prefetch_related(
            Prefetch(
                'classroom_students_data__student__user',
                queryset=User.objects.select_related('userprofile').only('id', 'username', 'userprofile__profile_pic')
            )
        ).get(id=id)
        if request.GET and  request.headers.get('x-requested-with') == 'XMLHttpRequest':
            name = request.GET['name']
            student = classroom_data.classroom_students_data.filter(student__user__username__icontains=name)
            return JsonResponse({
                'student':student,
                'student_profile': student.student,
            })
        lectures = None
        completed_lectures_by_student = None
        completed_lectures_ratio = 0
        assignments =  None
        pending_approval_assignments = None
        pending_approval_ratio = 0
        approved_assignments = None
        approved_assignments_ratio = 0


        if sid:
            try:
                student = StudentClassroom.objects.select_related('student__user').only(
                    'student__profile_pic', 'student__user__username', 'student__user__email'
                ).get(id=sid)
                if check_classroom_participant(student.student.user, id, use_cache=False):
                    lectures = Lecture.objects.filter(section__classroom=Class).order_by('section__order', 'order')
                    
                    completed_lectures_by_student = Lecture.objects.filter(
                        section__classroom=Class,
                        id__in=StudentLectureProgress.objects.filter(
                            student=student.student
                        ).values_list('lecture', flat=True)
                    )
                    completed_lectures_ratio = (100*completed_lectures_by_student.count())//lectures.count() if lectures else 0
                    
                    assignments =  Assignment.objects.filter(classroom=Class).order_by('-assigned_date')

                    
                    pending_approval_assignments = Assignment.objects.filter(       
                        id__in=AssignmentSubmission.objects.filter(
                            student=student.student,
                            is_approved=False,
                            assignment__classroom=Class 
                        ).values_list('assignment', flat=True)
                    )

                    pending_approval_ratio = (100*pending_approval_assignments.count())//assignments.count() if assignments else 0
                
                    approved_assignments = Assignment.objects.filter(
                        id__in=AssignmentSubmission.objects.filter(
                            student=student.student,
                            is_approved=True,
                            assignment__classroom=Class  
                        ).values_list('assignment', flat=True)  
                    )

                    approved_assignments_ratio = (100*approved_assignments.count())//assignments.count() if assignments else 100

                else:
                    return render(request, '403.html')
            except Exception as e:
                return render(request, '403.html')
        
        context = {
            'Class':Class,
            'students':classroom_data.classroom_students_data.all(),
            'student':student,
            'lectures':lectures,
            'completed_lectures_by_student':completed_lectures_by_student,
            'completed_lectures_ratio':completed_lectures_ratio,
            'assignments':assignments,
            'approved_assignments':approved_assignments,
            'approved_assignments_ratio':approved_assignments_ratio,
            'pending_approval_ratio':pending_approval_ratio,
            'pending_approval_assignments':pending_approval_assignments
        }
        return render(request, 'tutor/student_corner.html', context)
    else:
        return render(request, '403.html')

@login_required(login_url='login')
@user_passes_test(check_role_tutor)
@require_POST
def remove_student_from_class(request, id, sid):
    if check_classroom_participant(request.user, id):
        try:
            student_profile = userProfile.objects.select_related('user').only('user__username').get(id=sid)
            if check_classroom_participant(student_profile.user, id, use_cache=False):
                student_classroom_profile = StudentClassroom.objects.select_related('classroom').only(
                    'classroom__name'
                ).get(student=student_profile, classroom__id=id)
                noti = Notification.objects.create(
                    title = 'You got removed from the class',
                    content = f'Hey {student_profile.user.username} You got removed from the class {student_classroom_profile.classroom.name} by the tutor',
                    user = student_profile
                )
                
                cache_key = f'classroom_participant_{student_profile}_{id}'
                cache.cache.delete(cache_key) 

                cache_key = f'{student_profile.user.id}_class_{id}_data'
                cache.cache.delete(cache_key) 

                student_classroom_profile.delete()
                messages.success(request, f'student {student_profile.user.username} removed from the class')
                return redirect(f'/tutor/studentCorner/{id}/students/')
                
            else:
                return render(request, '403.html')
        except Exception as e:
            print(e)
            return render(request, '404.html')
    else:
        return render(request, '403.html')

@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def tutorSpecificAssignment(request, id, asid):
    if check_classroom_participant(request.user, id):
        Class = Classroom.objects.get(id=id)
        assignment = Assignment.objects.select_related('classroom').get(id=asid)
        due_date_initial = assignment.due_date
        if assignment.classroom != Class:
            return render(request, '404.html')
        
        assignment_form = AssignmentUpdateForm(instance=assignment)
        class_students = Class.students.all()

        students_with_pending_submission = class_students.exclude(
            id__in=assignment.assignment_submissions.values_list('student', flat=True)
        ).select_related('user').only('id', 'user__username')
        approved_submission = assignment.assignment_submissions.filter(is_approved=True).select_related('student__user').only(
            'upload_date', 'late_submission', 'submitted_file', 'assignment',
            'student__profile_pic', 'student__user__email', 'student__user__username',
        )
        pending_approval = assignment.assignment_submissions.filter(is_approved=False).select_related('student__user').only(
            'upload_date', 'late_submission', 'submitted_file', 'assignment',
            'student__profile_pic', 'student__user__email', 'student__user__username',
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.POST:
                assignment_form = AssignmentUpdateForm(request.POST, instance=assignment)

                if assignment_form.is_valid():
                    due_date = assignment_form.cleaned_data.get('due_date')

                    if due_date is None:
                        due_date = due_date_initial
                    
                    updated_assignment = assignment_form.save(commit=False)
                    updated_assignment.classroom = Class
                    updated_assignment.due_date = due_date
                    updated_assignment.save()
                    cache.cache.set(f'cache_reload_{id}_all', (True, timezone.now()), timeout=181)
                    return JsonResponse({
                        'status': 'success',
                        'message': 'assignment updated successfully'
                    })

                else:
                    return JsonResponse({
                        'status': 'failure',
                        'errors': assignment_form.errors
                    })
            elif request.GET:
                submission_id = request.GET.get('submission_id')
                action = request.GET.get('action')
                submission = AssignmentSubmission.objects.select_related('student__user').only(
                    'is_approved', 'late_submission', 'upload_date', 'submitted_file',
                    'student__profile_pic', 'student__user__username', 'student__user__email'
                ).get(id=submission_id)
                username = submission.student.user.username
                if action == 'approve':
                    submission.is_approved = True
                    submission.save(update_fields=['is_approved'])
                    noti = Notification.objects.create(
                        user=submission.student,
                        title="Submission Approoved",
                        content=f"Hey {username}! Your assignment submission for assignment: {assignment.name} \
                        in {Class.name} got approoved by the tutor.",
                        link = f'/classroom/{Class.id}/assignments/{assignment.id}'
                    )
                    
                    cache.cache.set(f'cache_reload_{id}_student', (True, timezone.now()), timeout=181)
                    return JsonResponse({
                        'status': 'success', 'message': 'submission approved', 
                        'submission': {
                            'id':submission.id,
                            'student':{
                                'user':{
                                    'username':username,
                                    'email':submission.student.user.email,
                                },
                                'profile_pic': submission.student.profile_pic.url if submission.student.profile_pic else None,
                            },
                            'submitted_file':submission.submitted_file.url,
                            'upload_date':submission.upload_date,
                            'late_submission':submission.late_submission,
                        }
                    })
                else:
                    noti = Notification.objects.create(
                        user=submission.student,
                        title="Submission rejected",
                        content=f"Hey {username}! Your assignment submission for assignment: {assignment.name} \
                        in {Class.name} got rejected by the tutor. You have to resubmit it.",
                        link = f'/classroom/{Class.id}/assignments/{assignment.id}'
                    )
                    
                    cache.cache.set(f'cache_reload_{id}_student', (True, timezone.now()), timeout=181)

                    submission.submitted_file.delete()
                    submission.delete()
                    
                    return JsonResponse({'status': 'success', 'message': 'submission rejected', 'username': f'{username}'})
            else:
                return redirect('403.html')
                
                


        context = {
            "Class":Class,
            "assignment": assignment,
            "assignment_form": assignment_form,
            'approved_submission': approved_submission,
            "students_with_pending_submission": students_with_pending_submission,
            "pending_approval": pending_approval

        }
        return render(request, 'tutor/tutorSpecificAssignment.html', context)        
    else:
        return render(request, '403.html')

@login_required(login_url='login')
@user_passes_test(check_role_tutor)
@require_POST
def notify_all(request, id, asid):
    try:
        assignment = Assignment.objects.only('due_date', 'late_submission_allow', 'name').get(pk=asid)
        last_notification = Notification.objects.only('timestamp').filter(
            assignment=assignment
        ).order_by('-timestamp').first()
        if last_notification and timezone.now() - last_notification.timestamp < timedelta(hours=12):
            return JsonResponse({'status':'failure', 'message':'You can notify students only once every 12 hours.'})
        
        
        classroom = Classroom.objects.only('name').get(pk=id)

        if assignment.due_date <= timezone.now() and assignment.late_submission_allow is False:
            return JsonResponse({'status':'failure', 'message':'Due date of this assignment has passed and You didn\'t allowed late submission'})

        students = classroom.students.exclude(
            id__in=AssignmentSubmission.objects.filter(
                assignment=assignment, 
            ).values_list('student_id', flat=True)  
        ).select_related('user').only('user__username')
        
        notifications = [
            Notification(
                title='Complete Assignment',
                content=f'''Hey {student.user.username}! \nGreetings from {classroom.name}, \
                Complete Your assignment: \n{assignment.name}''',
                user=student,
                link=f'/classroom/{id}/assignments/{asid}',
                assignment = assignment
            )  
            for student in students 
        ]
        Notification.objects.bulk_create(notifications)
            
        return JsonResponse({'status': 'success', 'message': 'Notifications sent to all students.'})
    
    except Assignment.DoesNotExist:
        return JsonResponse({'status': 'failure', 'message': 'Assignment not found.'})
    
    except Classroom.DoesNotExist:
        return JsonResponse({'status': 'failure', 'message': 'Classroom not found.'})
    
    except Exception as e:
        return JsonResponse({'status': 'failure', 'message': f'An error occurred {str(e)}'})

@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def SpecificAssignment_delete(request, id, asid):
    if check_classroom_participant(request.user, id):
        Assignment.objects.get(id=asid).delete()
        cache.cache.set(f'cache_reload_{id}_all', (True, timezone.now()), timeout=181)
        messages.success(request, 'Assignment Delted')
        return redirect(f'/classroom/{id}/assignments/')




