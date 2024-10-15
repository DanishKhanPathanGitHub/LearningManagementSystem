import calendar
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from accounts.utils import check_role_student, check_role_tutor
from .utils import check_classroom_participant
from django.views.decorators.http import require_POST, require_GET
import os
from .models import *
from .forms import AnnouncementForm, AssignmentForm, AssignmentSubmissionForm, CommentForm, LectureForm, SectionForm
from accounts.models import userProfile, User
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
# Create your views here.
@login_required(login_url='login')
@user_passes_test(check_role_student)
def classroom(request, id):
    user = request.user  # Access the authenticated user
    if check_classroom_participant(user, id):
        Class = get_object_or_404(Classroom, id=id)
        context = {
            "Class":Class,
        }
        return render(request, 'classroom/classroom.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_student)
def classroomJoin(request):
    if request.POST:
        code = request.POST['code']
        password = request.POST['password']
        try:
            classroom_to_join = Classroom.objects.get(code=code, password=password)
            user_profile = userProfile.objects.get(user=request.user)
            if classroom_to_join.students.filter(user=request.user).exists():
                messages.warning(request, 'You are already a member of this classroom.')
                return redirect('home')
            classroom_to_join.requests.add(user_profile)
            classroom_to_join.save()
            noti = Notification.objects.create(
                title=f"Classroom Join request from {user_profile.user.username}",
                content = f"User {user_profile.user.username} Requested to join your classroom: {classroom_to_join.name}",
                user=classroom_to_join.tutor
            )
            messages.success(request, 'Wait for tutor to Approve your joining request')
            return redirect('home')
        except:
            messages.error(request, 'invalid class credentials')
            return redirect('classroomJoin')
   
    return render(request, 'classroom/classroomJoin.html')


@login_required(login_url='login')
@user_passes_test(check_role_student)
def classroomExit(request, id):
    if request.POST:
        try:
            user_profile = userProfile.objects.get(user=request.user)
            classroom = Classroom.objects.get(id=id)
            studentClassroom = StudentClassroom.objects.get(student=user_profile, classroom=classroom)
            studentClassroom.delete()
            messages.success(request, 'You Left the classroom succesfully')
            return redirect('home')
        except:
            messages.warning(request, 'Unable to exit classroom due to some error')
            return redirect(f'classroom/{id}/')
    else:
        return render(request, '404.html')


@login_required(login_url='login')
def assignments(request, id):
    user = request.user  # Access the authenticated user
    if check_classroom_participant(user, id):
        Class = Classroom.objects.get(id=id)                                        
        assignments = Assignment.objects.filter(classroom=Class).order_by('-assigned_date')
        if request.GET:
            filter = request.GET.get('filter')
        
            user_profile = userProfile.objects.get(user=user)
            if filter == '2_days':
                today = timezone.now()
                assignments = assignments.filter(due_date__date__lte=today+timedelta(days=2), due_date__date__gte=today)
            elif filter == 'this_week':
                today = timezone.now().date()
                end_of_week = today + timedelta(days=(6-today.weekday()))
                assignments = assignments.filter(due_date__date__lte=end_of_week, due_date__date__gte=today)
            elif filter == 'next_10_days':
                today = timezone.now()
                assignments = assignments.filter(due_date__date__lte=today+timedelta(days=10), due_date__date__gte=today)
            elif filter == 'this_month':
                today = timezone.now().date()
                end_of_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])
                assignments = assignments.filter(due_date__lte=end_of_month, due_date__date__gte=today)
            elif user.role == 1:
                if filter == 'pending_submissions':
                    submitted_assignments = AssignmentSubmission.objects.filter(
                        student=user_profile
                    ).values_list('assignment_id', flat=True)
                    assignments = assignments.exclude(id__in=submitted_assignments).filter(due_date__gt=timezone.now()) 

                elif filter == 'pending_approvals':
                    assignments = Assignment.objects.filter(       
                        id__in=AssignmentSubmission.objects.filter(
                            student=user_profile,
                            is_approved=False,
                            assignment__classroom=Class 
                        ).values_list('assignment', flat=True)
                    )
                
                elif filter == 'approved':
                    assignments = Assignment.objects.filter(
                        id__in=AssignmentSubmission.objects.filter(
                            student=user_profile,
                            is_approved=True,
                            assignment__classroom=Class  
                        ).values_list('assignment', flat=True)  
                    )
                
                elif filter == 'missed':
                    submitted_assignments = AssignmentSubmission.objects.filter(
                        student=user_profile
                    ).values_list('assignment_id', flat=True)
                    assignments = assignments.exclude(id__in=submitted_assignments).filter(due_date__lt=timezone.now())
                else:
                    return render(request, '404.html')
            else:            
                if filter == 'active':
                    assignments = assignments.filter(due_date__gt=timezone.now())
                
                elif filter == 'due_date_passed':
                    assignments = assignments.filter(due_date__lt=timezone.now())
                else:
                    return render(request, '404.html')
                
            
        assignment_form = AssignmentForm()
        context = {
            "assignments":assignments,
            "assignment_form":assignment_form,
            "Class":Class,
        }
        return render(request, 'classroom/assignments.html', context)
    else:
        return render(request, '403.html')
    
@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def assignments_add(request, id):
    user = request.user
    if check_classroom_participant(user, id):
        if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = AssignmentForm(request.POST, request.FILES)
            if form.is_valid():
                assignment = form.save(commit=False)
                assignment.classroom_id = id
                assignment.save()
                response = {
                    'status': 'success',
                    'message': 'Assignment added succesfully',
                }
                return JsonResponse(response)
            else:
                return JsonResponse({
                    'status': 'failure',
                    'errors': form.errors
                })
        else:
            return render(request, '404.html')
    else:
        return render(request, '404.html')
    
    
@login_required(login_url='login')
@user_passes_test(check_role_student)    
def SpecificAssignment(request, id, asid):
    user = request.user
    assignment = Assignment.objects.get(id=asid)
    if check_classroom_participant(user, id):
        if assignment.classroom.id != id:
            return render(request, '404.html') 
        Class = Classroom.objects.get(id=id)                                   
        user_profile = userProfile.objects.get(user=user)
        try:
            check = AssignmentSubmission.objects.get(assignment=assignment, student=user_profile)
            submission_status = True
            approved_status = check.is_approved
        except:
            check = None
            submission_status = False
            approved_status = False

        if request.POST:
            if approved_status == True:
                messages.warning(request, 'you already submitted assignment and got approved')
                return redirect(f'/classroom/{Class.id}/assignments/{asid}')
            submission_form = AssignmentSubmissionForm(request.POST, request.FILES)


            if submission_form.is_valid():
                submission = submission_form.save(commit=False)
                upload_date = timezone.now()
                print(upload_date)
                print(assignment.due_date)
                if upload_date > assignment.due_date:
                    if assignment.late_submission_allow == True:
                        submission.assignment = assignment
                        submission.late_submission = True
                        submission.student = user_profile
                        submission.save()
                        messages.warning(request, 'Late submission done!')
                        return redirect(f'/classroom/{Class.id}/assignments/{asid}')
                    else:
                        messages.warning(request, 'You are unable to submit assignment after due date passed')
                        return redirect(f'/classroom/{Class.id}/assignments/{asid}')
                else:
                    submission.assignment = assignment
                    submission.student = user_profile
                    submission.save()
                    if check:
                        check.submitted_file.delete()
                        check.delete()
                        messages.success(request, 'Assignment re submitted succesflly')
                    else:
                        messages.success(request, 'Assignment submitted succesflly before due date')
                        
                    return redirect(f'/classroom/{Class.id}/assignments/{asid}')
           
        else:    
            submission_form = AssignmentSubmissionForm()

        context = {
            "assignment":assignment,
            "asid":asid,
            "Class":Class,
            "submission_form":submission_form,
            "submission_status":submission_status,
            "approved_status":approved_status,
            "check":check,
        }
        return render(request, 'classroom/SpecificAssignment.html', context)
    else:
        return render(request, '403.html')

@login_required(login_url='login')
@user_passes_test(check_role_student) 
def SubmissionDelete(request, id, asid):
    user = request.user
    Class = Classroom.objects.get(id=id)
    if check_classroom_participant(user, id):                                
        assignment = Assignment.objects.get(id=asid)
        user_profile = userProfile.objects.get(user=user)
        try:
            check = AssignmentSubmission.objects.get(assignment=assignment, student=user_profile)
        except:
            check = None
        if check:
            check.submitted_file.delete()
            check.delete()
            messages.success(request, 'submission removed!')
            return redirect(f'/classroom/{Class.id}/assignments/{asid}')
        else:
            messages.error(request, 'No submission found')
            return redirect(f'/classroom/{Class.id}/assignments/{asid}')

@login_required(login_url='login')
def announcements(request, id):
    user = request.user
    if check_classroom_participant(user, id): 
        Class = Classroom.objects.get(id=id)
        announcements = Announcement.objects.filter(classroom=Class).order_by('-upload_date')
        announcement_form = AnnouncementForm()
        if request.GET:
            filter = request.GET.get('filter')
            if filter == 'today':
                announcements = announcements.filter(upload_date__date=timezone.now().date())
            elif filter == "this_week":
                today = timezone.now().date()
                start_of_week = today - timedelta(days=today.weekday()) 
                announcements = announcements.filter(upload_date__date__gte=start_of_week)
            elif filter == "this_month":
                today = timezone.now().date()
                start_of_month = today.replace(day=1)
                announcements = announcements.filter(upload_date__date__gte=start_of_month)
        context = {
            "announcements":announcements,
            "announcement_form":announcement_form,
            "Class":Class,
        }
        return render(request, 'classroom/announcements.html', context)
    else:
        return render(request, '403.html')

@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def announcements_add(request, id):
    user = request.user
    if check_classroom_participant(user, id):
        if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = AnnouncementForm(request.POST, request.FILES)
            if form.is_valid():
                announcement = form.save(commit=False)
                announcement.classroom_id = id
                announcement.save()
                response = {
                    'status': 'success',
                    'announcement': {
                        'id': announcement.id,
                        'title': announcement.title,
                        'upload_date': announcement.upload_date,
                        'content': announcement.content,
                    }
                }
                return JsonResponse(response)
            else:
                return JsonResponse({
                    'status': 'failure',
                    'errors': form.errors
                })
        else:
            return render(request, '404.html')
    else:
        return render(request, '404.html')


@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def announcement_delete(request, id, anid):
    if check_classroom_participant(request.user, id):
        if request.POST:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                try:
                    announcement = Announcement.objects.get(id=anid)
                    announcement.delete()
                    return JsonResponse({
                        'status':'success',
                        'message':'announcement deleted'
                    })
                except:
                    return JsonResponse({
                        'status':'failure',
                        'message': 'announcement deletion unsuccesfull'
                    })
            else:
                return JsonResponse({
                    'status':'failure',
                    'message':'invalid request',
                })
        else:
            return render(request, '404.html')
    else:
        return render(request, '404.html')

@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def announcement_delete_bulk(request, id):
    if check_classroom_participant(request.user, id):
        if request.method == 'POST':
            announcement_ids = request.POST.getlist('announcement_ids[]')
            # Logic to delete announcements goes here
            try:
                Announcement.objects.filter(id__in=announcement_ids).delete()
            except:
                return JsonResponse({'status': 'error', 'message': 'Announcement deletion unsuccesfull'})
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Invalid request.'})
    else:
        return render(request, '404.html')

from django.db import transaction

@login_required(login_url='login')
@user_passes_test(check_role_tutor)
@require_POST
def add_section(request, id):
    if check_classroom_participant(request.user, id):
        Class = Classroom.objects.get(id=id)
        
        section_form = SectionForm(request.POST, classroom=Class)
        
        try:
            with transaction.atomic():  # Ensures atomicity
                section = section_form.save(commit=False)
                section.classroom = Class
                curr_ord = section.order
                sections_below = Section.objects.filter(classroom=Class, order__gte=curr_ord)

                # Update the order of the other sections
                for sec in sections_below[::-1]:
                    sec.order += 1
                    sec.save()

                section.save()
                messages.success(request, f'Section added to position: {curr_ord} and other sections arranged accordingly')
                return JsonResponse({
                    'status': 'success'
                })
        except Exception as e:
            messages.error(request, str(e))
            return JsonResponse({'status': 'failure', 'message': str(e)})
    
    else:
        return render(request, '403.html')
    

@login_required(login_url='login')
@user_passes_test(check_role_tutor)
@require_POST
def update_section(request, id, sid):
    if check_classroom_participant(request.user, id):
        Class = Classroom.objects.get(id=id)
        old_section = Section.objects.get(id=sid)
        
        section_form = SectionForm(request.POST, classroom=Class, is_update=True, instance=old_section)
        
        try:
            with transaction.atomic():  
                old_order = old_section.order
                old_section.order = 10000
                old_section.save()

                section = section_form.save(commit=False)
                section.classroom = Class
                curr_ord = section.order
                
                if curr_ord < old_order:
                    sections_below = Section.objects.filter(classroom=Class, order__gte=curr_ord, order__lt=old_order)
                    for sec in sections_below[::-1]:
                        sec.order += 1
                        sec.save()
                else:
                    sections_below = Section.objects.filter(classroom=Class, order__lte=curr_ord, order__gt=old_order)
                    for sec in sections_below:
                        sec.order -= 1
                        sec.save()

                section.save()
                messages.success(request, f'Section added to position: {curr_ord} and other sections arranged accordingly')
                return JsonResponse({
                    'status': 'success'
                })
        except Exception as e:
            messages.error(request, str(e))
            return JsonResponse({'status': 'failure', 'message': str(e)})
    
    else:
        return render(request, '403.html')


@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def delete_section(request, id, sid):
    if check_classroom_participant(request.user, id):
        print("request reached view")
        if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                section = Section.objects.get(id=sid)
                print(section.title)
                section.delete()
                return JsonResponse({
                    'status':'success',
                    'message':'section deleted'
                })
            except:
                print("in except case")
                return JsonResponse({
                    'status':'failure',
                    'message': 'section deletion unsuccesfull'
                })
        else:
            print("in elsse case")
            return JsonResponse({
                'status':'failure',
                'message':'invalid request',
            })
    else:
        return render(request, '404.html')
    
@login_required(login_url='login')
@user_passes_test(check_role_student)
def toggle_lecture_completion(request):
    if request.method == "POST":
        lecture_id = request.POST.get('lecture_id')
        student = userProfile.objects.get(user=request.user) 
        try:
            lecture = Lecture.objects.get(id=lecture_id)
        except Lecture.DoesNotExist:
            return JsonResponse({"error": "Lecture not found"}, status=404)

        progress, created = StudentLectureProgress.objects.get_or_create(
            lecture=lecture, student=student
        )

        if not created:
            # If the record already exists, delete it (unmark the lecture)
            progress.delete()
            return JsonResponse({"status": "unmarked"})
        else:
            # If a new record was created, mark the lecture as completed
            return JsonResponse({"status": "marked"})

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required(login_url='login')
@user_passes_test(check_role_tutor)
@transaction.atomic
def add_lecture(request, id, sid):
    if check_classroom_participant(request.user, id):
        Class = Classroom.objects.get(id=id)
        section = Section.objects.get(id=sid)
        sections = Section.objects.filter(classroom=Class).order_by('order')
        section_form = SectionForm(classroom=Class)
        lecture = Lecture.objects.filter(section=section, order=1).first()
        if request.POST:
            lecture_form = LectureForm(request.POST, request.FILES, section=section)
            if lecture_form.is_valid():
                try:
                    with transaction.atomic():
                        lecture_to_add = lecture_form.save(commit=False)
                        lecture_to_add.classroom = Class
                        lecture_to_add.section = section
                        curr_ord = lecture_to_add.order
                        NextLectures = Lecture.objects.filter(section=section, order__gte=curr_ord)
                        for lecture in NextLectures[::-1]:
                            lecture.order+=1
                            lecture.save()
                        
                        lecture_to_add.save()
                        messages.success(request, f'lecture: {lecture_to_add.title} added to section: {lecture_to_add.section} at order: {lecture_to_add.order}')
                        return redirect(f'/classroom/{id}/lectures/{lecture_to_add.slug}')
                except Exception as e:
                    messages.error(request, f'Error while adding the lecture:{str(e)}')
                
        else:
            lecture_form = LectureForm(section=section)
        context = {
            'lecture_form':lecture_form,
            'section':section,
            'Class':Class,
            'sections':sections,
            'curr_section':section,
            'lecture':lecture,
            'lecture_form':lecture_form,
            'section_form':section_form
        }
        return render(request, 'classroom/add_lecture.html', context)
    else:
        return render(request, '404.html')   

@login_required(login_url='login')
def lectures(request, id, slug=None):
    """
    if there is no slug provided, then for tutor it will load the first video
    But for the student, we have student progress
    student have completed lectures. Now his 
    """
    if check_classroom_participant(request.user, id):
        Class =Classroom.objects.get(id=id)
        sections = Section.objects.filter(classroom=Class).order_by('order')
        student = userProfile.objects.get(user=request.user)
        if request.user.role == 1:
            completed_lectures = Lecture.objects.filter(
                section__classroom=Class,
                id__in=StudentLectureProgress.objects.filter(
                    student=student
                ).values_list('lecture', flat=True)
            ).order_by('-studentlectureprogress__timestamp')

        else:
            completed_lectures = None
        current_section = sections.first()
        lecture = None

        comment_form = CommentForm()
    
        section_form = SectionForm(classroom=Class) if request.user.role == 2 else None
        section_update_form = SectionForm(classroom=Class, is_update=True) if request.user.role == 2 else None 
        if not slug:
            if student.user.role == 2:
                lecture = Lecture.objects.filter(
                    section=current_section
                ).order_by('order').first()
            else:
                lecture = completed_lectures.first()
                if not lecture:
                    lecture = Lecture.objects.filter(
                    section=current_section
                ).order_by('order').first()
                current_section = lecture.section
        else:
            try:
                lecture = Lecture.objects.get(slug=slug)
                current_section = lecture.section
            except Lecture.DoesNotExist:
                return render(request, '403.html')
        
        comment_list = Comment.objects.filter(lecture=lecture).order_by('timestamp')
        paginator = Paginator(comment_list, 5) 
        page_number = request.GET.get('page')  
        comments = paginator.get_page(page_number)  


        context = {
            'Class':Class,
            'sections':sections,
            'section_form':section_form,
            'section_update_form':section_update_form,
            'comment_form':comment_form,
            'lecture':lecture,
            'comments':comments,
            'current_section': current_section,  
            'completed_lectures':completed_lectures,
        }
        return render(request, 'classroom/lectures.html', context)
    else:
        return render(request, '403.html')

@login_required(login_url='login')
def get_order_choices(request, curr_section_id, section_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            print('in try block')
            # Fetch max order for the given section
            section = Section.objects.get(id=section_id)
            print('section got determined', section)
            max_order = Lecture.objects.filter(section=section).aggregate(Max('order'))['order__max'] or 0
            print('max order get determined', max_order)
            if curr_section_id == section_id:
                max_order-=1
            # Create order choices based on the number of lectures
            choices = [(i, str(i)) for i in range(max_order + 1, 0, -1)]
            print('choices get determined')
            return JsonResponse({'choices': choices})
        except Section.DoesNotExist:
            return JsonResponse({'error': 'Invalid section'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def update_lecture(request, id, slug=None):
    if check_classroom_participant(request.user, id):
        Class = Classroom.objects.get(id=id)
        sections = Section.objects.filter(classroom=Class).order_by('order')
        lecture = None
        curr_section = None
        lecture_form = None
        section_form = SectionForm(classroom=Class)
        try:
            lecture = Lecture.objects.get(slug=slug)
        except:
            return render(request, '403.html')
        
        curr_section = lecture.section 
        curr_lectures = curr_section.lectures.all()
        if request.POST:
            try:
                with transaction.atomic():
                    lecture_form = LectureForm(request.POST, request.FILES, section=curr_section, instance=lecture)
                    
                    #First of all we have to first remove the reference of lecture in old section
                    #And reorder the lectures in that old section
                    old_lecture_order = lecture.order
                    old_lecture_announcement_link = f'/classroom/{id}/lectures/{lecture.slug}/'
                    old_announcement = None
                    try:
                        old_announcement = Announcement.objects.get(
                            link = old_lecture_announcement_link
                        )
                    except:
                        pass
                    lecture.order = 1000
                    lecture.save()

                    next_lectures_in_old_section = Lecture.objects.filter(
                        section=curr_section,
                        order__gt=old_lecture_order
                    )
                    for curr_lecture in next_lectures_in_old_section:
                        curr_lecture.order-=1
                        curr_lecture.save()
                    
                    #Now as lecture is now far referenced in the old section
                    #In thee updated section, we have to move the lectures
                    updated_lecture_order = request.POST['order']
                    updated_section = request.POST['section']

                    next_lectures_in_updated_section = Lecture.objects.filter(
                        section = updated_section,
                        order__gte=updated_lecture_order
                    )
                    for curr_lecture in next_lectures_in_updated_section[::-1]:
                        curr_lecture.order+=1
                        curr_lecture.save()
                    
                    #now as reordering happend, we can adjust the lecture in new section at updated position
                    updated_lecture = lecture_form.save() 

                    #updating the announcement also
                    if old_announcement:
                        link=f'/classroom/{id}/lectures/{updated_lecture.slug}/'
                        old_announcement.link = link
                        old_announcement.save()

                    messages.success(request, f'lecture - {updated_lecture.title} saved to {updated_lecture.section.title} at ordder: {updated_lecture.order}')
                    return redirect(f'/classroom/{id}/lectures/{updated_lecture.slug}/')
                
            except Exception as e:
                if lecture_form.errors:
                    messages.error(request, 'lecture should have atleast Notes or video')
                else:
                    messages.error(request, 'error occured while updating lecture: ', str(e))    
                return redirect(f'/classroom/{id}/update_lecture/{slug}/')
                
        else:
            print('in else case')
            lecture_form = LectureForm(instance=lecture, section=curr_section)

        context = {
            'Class':Class,
            'lecture':lecture,
            'sections':sections,
            'curr_lectures':curr_lectures,
            'curr_section':curr_section,
            'lecture_form':lecture_form,
            'section_form':section_form
        }
        return render(request, 'classroom/update_lecture.html', context)
    else:
        return render(request, '403.html')

    
@login_required(login_url='login')
@user_passes_test(check_role_tutor)
def delete_lecture(request, id, slug):
    if check_classroom_participant(request.user, id):
        if request.POST:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                try:
                    lecture = Lecture.objects.get(slug=slug)
                    lecture_title = lecture.title
                    lecture.delete()
                    return JsonResponse({
                        'status':'success',
                        'message':f'lecture {lecture_title} deleted'
                    })
                except:
                    return JsonResponse({
                        'status':'failure',
                        'message': f'lecture deletion unsuccesfull'
                    })
            else:
                return JsonResponse({
                    'status':'failure',
                    'message':'invalid request',
                })
        else:
            return render(request, '404.html')
    else:
        return render(request, '404.html')



@login_required(login_url='login')
@require_POST
def post_comment(request, id, slug):
    if check_classroom_participant(request.user, id):
        Class = Classroom.objects.get(id=id)
        if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            comment_form = CommentForm(request.POST, request.FILES)

            print(f"POST Data: {request.POST}")
            print(f"Files Data: {request.FILES}")

            if comment_form.is_valid():
                lecture = Lecture.objects.get(slug=slug)
                comment = comment_form.save(commit=False)
                comment.lecture = lecture

                parent_comment_id = request.POST.get('parent_comment_id')
                try:
                    parent_comment = Comment.objects.get(id=parent_comment_id)
                    comment.parent = parent_comment
                except:
                    parent_comment = None
                    comment.parent = None
                comment.user = userProfile.objects.get(user=request.user)
                comment.save()
                return JsonResponse({'status': 'success'})
            else:
                print(comment_form.errors)
                return JsonResponse({'status':'failure', 'message':f'{comment_form.errors.as_text()}'})
        else:
            return JsonResponse({'status':'failure', 'message':'request not supported'})
                
    else:
        return render(request, '403.html')
    
@login_required(login_url='login')
@require_POST
def upvote_comment(request, slug, cid):
    try:
        lecture = Lecture.objects.get(slug=slug)
        comment = Comment.objects.get(id=cid, lecture=lecture)
    except:
        return JsonResponse({'status':'failure', 'message':'error while upvoting comment'})
    user_profile = userProfile.objects.get(user=request.user)
   
    if user_profile in comment.upvoted_student.all():
        comment.upvote = max(0, comment.upvote-1)
        print("comment downvoted")
        comment.upvoted_student.remove(user_profile)   
        comment.save()
        return JsonResponse({'status':'success', "action":'downvoted'})
    else:
        comment.upvote+=1
        print("comment  upvoted")
        comment.upvoted_student.add(user_profile)
        comment.save()
        return JsonResponse({'status':'success', "action":'upvoted'})
    
@login_required(login_url='login')
def delete_comment(request, id, slug, comment_id):
    if check_classroom_participant(request.user, id):
        if request.POST:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                try:
                    lecture = Lecture.objects.get(slug=slug)
                    comment = Comment.objects.get(id=comment_id)
                    if comment.lecture == lecture:
                        if comment.image:
                            comment.image.delete()
                        comment.delete()
                        return JsonResponse({
                            'status':'success',
                            'message':'comment deleted'
                        })
                    else:
                        return JsonResponse({
                        'status':'failure',
                        'message': 'comment deletion unsuccesfull'
                    })    
                except:
                    return JsonResponse({
                        'status':'failure',
                        'message': 'comment deletion unsuccesfull'
                    })
            else:
                return JsonResponse({
                    'status':'failure',
                    'message':'invalid request',
                })
        else:
            return render(request, '404.html')
    else:
        return render(request, '404.html')