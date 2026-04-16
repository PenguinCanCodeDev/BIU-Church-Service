from django.contrib import admin
from .models import Service, AccountDetail, Lyric, Sermon, UserSubmission, Announcement

class AccountDetailInline(admin.TabularInline):
    model = AccountDetail
    extra = 1

class LyricInline(admin.StackedInline):
    model = Lyric
    extra = 1

class SermonInline(admin.StackedInline):
    model = Sermon
    extra = 1

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'day_of_week')
    inlines = [AccountDetailInline, LyricInline, SermonInline]

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_approved', 'short_content')
    list_filter = ('is_approved', 'created_at')
    fields = ('content', 'image', 'is_approved') # Hide submission_type since it's hardcoded
    actions = ['approve_announcements']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(submission_type='announcement')

    def save_model(self, request, obj, form, change):
        obj.submission_type = 'announcement'
        super().save_model(request, obj, form, change)

    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    def approve_announcements(self, request, queryset):
        queryset.update(is_approved=True)

@admin.register(UserSubmission)
class UserSubmissionAdmin(admin.ModelAdmin):
    list_display = ('submission_type', 'is_approved', 'created_at')
    list_filter = ('submission_type', 'is_approved')
    actions = ['approve_submissions']

    def get_queryset(self, request):
        # Only show Suggestions and Complaints here
        return super().get_queryset(request).exclude(submission_type='announcement')

    def approve_submissions(self, request, queryset):
        queryset.update(is_approved=True)
    approve_submissions.short_description = "Approve selected submissions"
