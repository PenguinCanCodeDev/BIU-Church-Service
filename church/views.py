from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Service, UserSubmission
from .serializers import ServiceSerializer, UserSubmissionSerializer

def index(request):
    """ Main entry point using Django Templates. """
    current_day = datetime.today().weekday()
    # Use .iterator() to avoid broken fetchmany in some djongo/django 4.x environments
    service_qs = Service.objects.filter(day_of_week=current_day)
    service = next(service_qs.iterator(), None)
    
    # Approved announcements for the sidebar/feed
    # Using __in helps Djongo's parser avoid issues with bare boolean columns
    announcements = list(UserSubmission.objects.filter(
        submission_type__in=['announcement'], 
        is_approved__in=[True]
    ).order_by('-created_at')[:5].iterator())

    context = {
        'service': service,
        'announcements': announcements,
        'is_general': service is None,
        'today': datetime.today(),
    }
    return render(request, 'church/index.html', context)

@api_view(['GET'])
def get_current_service(request):
    """
    API Version: Determines today's service based on the day of the week.
    """
    current_day = datetime.today().weekday()
    service_qs = Service.objects.filter(day_of_week=current_day)
    service = next(service_qs.iterator(), None)
    
    if not service:
        return Response({
            "name": "BIU SERVICES", 
            "is_general": True,
            "message": "Welcome to our centralized church hub."
        })
    
    serializer = ServiceSerializer(service, context={'request': request})
    return Response(serializer.data)

class UserSubmissionCreateView(generics.CreateAPIView):
    queryset = UserSubmission.objects.all()
    serializer_class = UserSubmissionSerializer
    permission_classes = [permissions.AllowAny]

class AnnouncementListView(generics.ListAPIView):
    queryset = UserSubmission.objects.filter(submission_type='announcement', is_approved__in=[True]).order_by('-created_at')
    serializer_class = UserSubmissionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return UserSubmission.objects.filter(submission_type='announcement', is_approved__in=[True]).order_by('-created_at')

# Staff Security Logic
def is_sermon_staff(user):
    if not user.is_authenticated: return False
    if user.is_superuser: return True
    group_names = user.groups.all().values_list('name', flat=True)
    return 'SermonManagers' in group_names

def is_lyric_staff(user):
    if not user.is_authenticated: return False
    if user.is_superuser: return True
    group_names = user.groups.all().values_list('name', flat=True)
    return 'LyricManagers' in group_names

def is_announcement_staff(user):
    if not user.is_authenticated: return False
    if user.is_superuser: return True
    group_names = user.groups.all().values_list('name', flat=True)
    return 'AnnouncementManagers' in group_names

# Staff Views (Protected)

@login_required
@user_passes_test(is_sermon_staff, login_url='login')
def manage_sermons(request):
    """ View for Sermon Managers. """
    from .models import Sermon
    if request.method == "POST":
        title = request.POST.get('title')
        service_id = request.POST.get('service')
        date = request.POST.get('date')
        notes = request.POST.get('notes')
        
        service = Service.objects.get(id=service_id)
        Sermon.objects.create(service=service, title=title, date_preached=date, notes_or_link=notes)
        messages.success(request, "Sermon uploaded successfully!")
        return redirect('manage_sermons')

    services = Service.objects.all()
    sermons = Sermon.objects.all().order_by('-date_preached')
    return render(request, 'church/staff/sermons.html', {'services': services, 'sermons': sermons})

@login_required
@user_passes_test(is_lyric_staff, login_url='login')
def manage_lyrics(request):
    """ View for Lyric Managers. """
    from .models import Lyric
    if request.method == "POST":
        title = request.POST.get('title')
        service_id = request.POST.get('service')
        content = request.POST.get('content')
        
        service = Service.objects.get(id=service_id)
        Lyric.objects.create(service=service, title=title, content=content)
        messages.success(request, "Lyric uploaded successfully!")
        return redirect('manage_lyrics')

    services = Service.objects.all()
    lyrics = Lyric.objects.all().order_by('title')
    return render(request, 'church/staff/lyrics.html', {'services': services, 'lyrics': lyrics})

@login_required
@user_passes_test(is_announcement_staff, login_url='login')
def manage_announcements(request):
    """ View for Announcement Moderators. """
    if request.method == "POST":
        action = request.POST.get('action') 
        
        if action == "create":
            content = request.POST.get('content')
            image = request.FILES.get('image')
            UserSubmission.objects.create(
                submission_type='announcement',
                content=content,
                image=image,
                is_approved=True
            )
            messages.success(request, "Announcement posted successfully!")
        else:
            submission_id = request.POST.get('submission_id')
            submission = get_object_or_404(UserSubmission, id=submission_id)
            if action == "approve":
                submission.is_approved = True
                submission.save()
                messages.success(request, "Announcement approved and posted!")
            elif action == "delete":
                submission.delete()
                messages.success(request, "Submission removed.")
        
        return redirect('manage_announcements')

    pending = UserSubmission.objects.filter(is_approved__in=[False]).order_by('-created_at')
    approved = UserSubmission.objects.filter(is_approved__in=[True]).order_by('-created_at')
    return render(request, 'church/staff/announcements.html', {'pending': pending, 'approved': approved})
