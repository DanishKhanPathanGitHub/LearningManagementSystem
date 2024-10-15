from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from classroom.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST

from accounts.utils import check_role_tutor
from classroom.utils import check_classroom_participant
from .forms import *
from accounts.models import userProfile
from django.contrib import messages


@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def tutorClassroom(request, id):
    user = request.user  # Access the authenticated user
    if check_classroom_participant(user, id):
        Class = Classroom.objects.get(id=id)  
        class_students = StudentClassroom.objects.filter(
            classroom=Class
        )[:6]
        requests_students = Class.requests.all()
        mini_form = ClassroomMiniForm(instance=Class)
        if request.POST:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                action = request.POST.get('action')
                student_id = request.POST.get('student_id')
                if action == 'approve':
                    student_request = userProfile.objects.get(id=student_id)
                    Class.requests.remove(student_request)
                    Class.students.add(student_request)
                    Class.save()
                    StudentClassroom.objects.create(classroom=Class, student=student_request)
                    notification = Notification.objects.create(
                        user = student_request,
                        title="Classroom Join request accepted!",
                        content=f"""
                            Hello {student_request.user.username} \n Your requst to join classroom:
                            {Class.name} accepted by the tutor
                        """,
                        link = f'/classroom/{Class.id}'
                    )
                    notification.save()
                    return JsonResponse({
                            'status': 'success', 'message': 'Request approved',
                            'student': {
                            'username': student_request.user.username,
                            'email': student_request.user.email,
                            'profile_pic': student_request.profile_pic.url if student_request.profile_pic else '/static/images/male.png'
                            }
                        })
                elif action == 'reject':
                    student_request = userProfile.objects.get(id=student_id)
                    Class.requests.remove(student_request)
                    Class.save()
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
            "class_students":class_students,
            "mini_form":mini_form,
            "requests":requests_students,
        }
        return render(request, 'tutor/tutorClassroom.html', context)
    
@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def tutorClassroomDelete(request, id):
    user = request.user  # Access the authenticated user
    if check_classroom_participant(user, id):
        if request.POST:
            Class = Classroom.objects.get(id=id)  
            for student in Class.students.all():
                notification = Notification.objects.create(
                    title="Classroom deactivated",
                    content=f"hello {student.user.username}!! Your classroom: {Class.name} has been deactictivated by the tutor",
                    user = student
                )
                notification.save()
            Class.delete()

            messages.success(request, 'Your classroom has been deleted successfully.')
   

@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def classroomAdd(request):
    if request.POST:
        class_form = ClassroomForm(request.POST, request.FILES)
        if class_form.is_valid():
            Class = class_form.save(commit=False)
            Class.tutor = userProfile.objects.get(user=request.user)
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
        Class = Classroom.objects.get(id=id)
        students = StudentClassroom.objects.filter(classroom=Class)

        if request.GET and  request.headers.get('x-requested-with') == 'XMLHttpRequest':
            name = request.GET['name']
            student = students.filter(student__user__username__icontains=name)
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
                student = StudentClassroom.objects.get(id=sid)
                if check_classroom_participant(student.student.user, id):
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
                print(str(e))
                return render(request, '403.html')
        
        context = {
            'Class':Class,
            'students':students,
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
        print('inside requety')
        try:
            print('inside try block')
            student_profile = userProfile.objects.get(id=sid)
            if check_classroom_participant(student_profile.user, id):
                print("Yes")
                classroom = Classroom.objects.get(id=id)
                student_classroom_profile = StudentClassroom.objects.get(student=student_profile, classroom=classroom)
                username = student_profile.user.username
                noti = Notification.objects.create(
                    title = 'You got removed from the class',
                    content = f'Hey {username} You got removed from the class {student_classroom_profile.classroom.name} by the tutor',
                    user = student_profile
                )
                noti.save()
                student_classroom_profile.delete()
                messages.success(request, f'student {username} removed from the class')
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
        assignment = Assignment.objects.get(id=asid)
        due_date_initial = assignment.due_date
        print(assignment.due_date, 'due_date 1')
        if assignment.classroom != Class:
            return render(request, '404.html')
        
        assignment_form = AssignmentUpdateForm(instance=assignment)
        class_students = Class.students.all()
        assignment_submissions = AssignmentSubmission.objects.filter(assignment=assignment)

        students_with_pending_submission = class_students.exclude(
            id__in=assignment_submissions.values_list('student', flat=True)
        )
        approved_submission = assignment_submissions.filter(is_approved=True)
        pending_approval = assignment_submissions.filter(is_approved=False)

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
                submission = AssignmentSubmission.objects.get(id=submission_id)
                username = submission.student.user.username
                if action == 'approve':
                    submission.is_approved = True
                    submission.save()
                    noti = Notification.objects.create(
                        user=submission.student,
                        title="Submission Approoved",
                        content=f"Hey {username}! Your assignment submission for assignment: {assignment.name} \
                        in {Class.name} got approoved by the tutor.",
                        link = f'/classroom/{Class.id}/assignments/{assignment.id}'
                    )
                    noti.save()
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
                        in {Class.name} got rejected by the tutor. You have to re submit it.",
                        link = f'/classroom/{Class.id}/assignments/{assignment.id}'
                    )
                    noti.save()
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
        # Fetch assignment and classroom objects
        assignment = Assignment.objects.get(pk=asid)
        classroom = Classroom.objects.get(pk=id)

        if assignment.due_date <= timezone.now() and assignment.late_submission_allow is False:
            return JsonResponse({'status':'failure', 'message':'Due date of this assignment has passed and You didn\'t allowed late submission'})

        # Get all students in the class and exclude those who have submitted the assignment
        students = classroom.students.exclude(
            id__in=AssignmentSubmission.objects.filter(
                assignment=assignment, 
            ).values_list('student_id', flat=True)  # Fixed exclude query
        )
        last_notification = Notification.objects.filter(
            assignment=assignment
        ).order_by('-timestamp').first()
        if last_notification and timezone.now() - last_notification.timestamp < timedelta(hours=12):
            return JsonResponse({'status':'failure', 'message':'You can notify students only once every 12 hours.'})
           
        # Send notifications to each student who hasn't submitted
        for student in students:
            notification = Notification.objects.create(
                title='Complete Assignment',
                content=f'''Hey {student.user.username}! \nGreetings from {classroom.name}, \
                Complete Your assignment: \n{assignment.name}''',
                user=student,
                link=f'/classroom/{id}/assignments/{asid}',
                assignment = assignment
            )
            notification.save()
            
       
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
        Class = Classroom.objects.get(id=id)
        assignment = Assignment.objects.get(id=asid)
        assignment.delete()
        messages.success(request, 'Assignment Delted')
        return redirect(f'/classroom/{Class.id}/assignments/')




