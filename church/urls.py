from django.urls import path
from .views import (
    index, get_current_service, UserSubmissionCreateView, AnnouncementListView,
    manage_sermons, manage_lyrics, manage_announcements
)

urlpatterns = [
    path('', index, name='index'),
    path('api/current-service/', get_current_service, name='get_current_service'),
    path('api/submissions/', UserSubmissionCreateView.as_view(), name='user_submission_create'),
    path('api/announcements/', AnnouncementListView.as_view(), name='announcement_list'),
    
    # Staff Paths
    path('staff/sermons/', manage_sermons, name='manage_sermons'),
    path('staff/lyrics/', manage_lyrics, name='manage_lyrics'),
    path('staff/announcements/', manage_announcements, name='manage_announcements'),
]
