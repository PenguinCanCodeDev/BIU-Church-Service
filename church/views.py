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
    service = Service.objects.filter(day_of_week=current_day).first()
    
    # Approved announcements for the sidebar/feed
    announcements = UserSubmission.objects.filter(
        submission_type='announcement', 
        is_approved=True
    ).order_by('-created_at')[:5]

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
    service = Service.objects.filter(day_of_week=current_day).first()
    
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
    queryset = UserSubmission.objects.filter(submission_type='announcement', is_approved=True).order_by('-created_at')
    serializer_class = UserSubmissionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return UserSubmission.objects.filter(submission_type='announcement', is_approved=True).order_by('-created_at')

# Staff Security Logic
def is_church_staff(user):
    # This keeps them OUT of the Admin but IN the custom portals
    # They just need to be in a group named 'Staff' OR be a superuser
    return user.is_authenticated and (user.groups.filter(name='Staff').exists() or user.is_superuser)

# Staff Views (Protected)

@login_required
@user_passes_test(is_church_staff, login_url='login')
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
@user_passes_test(is_church_staff, login_url='login')
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
@user_passes_test(is_church_staff, login_url='login')
def manage_announcements(request):
    """ View for Announcement Moderators. """
    if request.method == "POST":
        submission_id = request.POST.get('submission_id')
        action = request.POST.get('action') # approve or delete
        
        submission = get_object_or_404(UserSubmission, id=submission_id)
        if action == "approve":
            submission.is_approved = True
            submission.save()
            messages.success(request, "Announcement approved and posted!")
        elif action == "delete":
            submission.delete()
            messages.success(request, "Submission removed.")
        
        return redirect('manage_announcements')

    pending = UserSubmission.objects.filter(is_approved=False).order_by('-created_at')
    approved = UserSubmission.objects.filter(is_approved=True).order_by('-created_at')
    return render(request, 'church/staff/announcements.html', {'pending': pending, 'approved': approved})
