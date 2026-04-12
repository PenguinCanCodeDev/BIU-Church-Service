from django.db import models

class Service(models.Model):
    DAY_CHOICES = [
        (6, 'Sunday'),     # OASIS
        (1, 'Tuesday'),    # CFI
        (3, 'Thursday'),   # BIU
    ]
    name = models.CharField(max_length=100) # BIU, CFI, OASIS
    day_of_week = models.IntegerField(choices=DAY_CHOICES, unique=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    theme_color = models.CharField(max_length=20, default="#FFFFFF")
    
    # Social Media Links
    tiktok_url = models.URLField(max_length=500, blank=True, null=True, help_text="Full URL to TikTok profile")
    instagram_url = models.URLField(max_length=500, blank=True, null=True, help_text="Full URL to Instagram profile")
    youtube_url = models.URLField(max_length=500, blank=True, null=True, help_text="Full URL to YouTube channel")
    twitter_url = models.URLField(max_length=500, blank=True, null=True, help_text="Full URL to Twitter/X profile")

    def __str__(self):
        return f"{self.name} ({self.get_day_of_week_display()})"

class AccountDetail(models.Model):
    service = models.ForeignKey(Service, related_name='accounts', on_delete=models.CASCADE)
    account_type = models.CharField(max_length=50) # Tithe, Offering, etc.
    account_name = models.CharField(max_length=200, default="Church Account")
    account_number = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.service.name} - {self.account_type}"

class Lyric(models.Model):
    service = models.ForeignKey(Service, related_name='lyrics', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title

class Sermon(models.Model):
    service = models.ForeignKey(Service, related_name='sermons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    date_preached = models.DateField()
    notes_or_link = models.TextField(blank=True)

    def __str__(self):
        return self.title

class UserSubmission(models.Model):
    SUBMISSION_TYPES = [
        ('announcement', 'Announcement'),
        ('suggestion', 'Suggestion'),
        ('complaint', 'Complaint'),
    ]
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_TYPES)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_submission_type_display()} - {self.created_at.date()}"
