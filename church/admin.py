from django.contrib import admin
from .models import Service, AccountDetail, Lyric, Sermon, UserSubmission

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

@admin.register(UserSubmission)
class UserSubmissionAdmin(admin.ModelAdmin):
    list_display = ('submission_type', 'is_approved', 'created_at')
    list_filter = ('submission_type', 'is_approved')
    actions = ['approve_submissions']

    def approve_submissions(self, request, queryset):
        queryset.update(is_approved=True)
    approve_submissions.short_description = "Approve selected submissions"
