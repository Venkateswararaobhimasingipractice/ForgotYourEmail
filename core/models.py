from django.db import models
from django.utils import timezone
# Create your models here.
class AppUser(models.Model):
    firebase_uid = models.CharField(max_length=128, unique=True)
    email = models.EmailField(unique=True)
    type = models.CharField(max_length=20, choices=[("manual", "Manual"), ("google", "Google"), ("link", "Link")], default="manual")
    google_id = models.CharField(max_length=128, null=True, blank=True)
    access_token = models.TextField(null=True, blank=True)
    fcm_token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    login = models.BooleanField(default=True)
    expire=models.BooleanField(default=True)
    last_notified_date = models.DateField(null=True, blank=True)


    def __str__(self):
        return self.email

class UserProfile(models.Model):
    user = models.OneToOneField(AppUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    profile_image_url = models.URLField(default='https://i.imgur.com/7suwDp5.jpeg')

    def get_profile_image_url(self):
        return self.profile_image_url or 'https://i.imgur.com/7suwDp5.jpeg'
    


from django.db import models
from django.contrib.auth.models import User

class EmailAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_id = models.CharField(max_length=128)
    subject = models.TextField()
    action = models.CharField(max_length=20, choices=[
        ('auto_reply', 'Auto Reply'),
        ('schedule', 'Schedule'),
        ('todo', 'To-Do'),
        ('ignore', 'Ignore')
    ])
    todo_done = models.BooleanField(default=False)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email_id

from django.db import models
from django.contrib.auth.models import User

class TodoTask(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("done", "Done")]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_id = models.CharField(max_length=255, null=True, blank=True)  # Optional
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.status}"

from django.db import models
from django.utils import timezone
class ScheduledTask(models.Model):
    TYPE_CHOICES = [
        ("email", "Email Schedule"),
        ("calendar", "Google Calendar Task"),
    ]

    user = models.ForeignKey("AppUser", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    schedule_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="calendar")
    scheduled_time = models.DateTimeField()
    done = models.BooleanField(default=False)

    # Email schedule-specific fields
    recipient_email = models.EmailField(null=True, blank=True)
    email_subject = models.CharField(max_length=255, null=True, blank=True)
    email_body = models.TextField(null=True, blank=True)

    # Google Calendar specific fields
    google_event_id = models.CharField(max_length=255, null=True, blank=True)
    google_event_link = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_due(self):
        return not self.done and self.scheduled_time <= timezone.now()

    def __str__(self):
        return f"{self.title} ({self.schedule_type})"


# models.py
from django.db import models
from django.utils import timezone

class Todo(models.Model):
    id = models.AutoField(primary_key=True)
    user_uid = models.CharField(max_length=200)   
    title = models.CharField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)
    done = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class IgnoredEmail(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="ignored_emails")
    ignored_email = models.EmailField()  # The sender's email that was ignored
    count = models.PositiveIntegerField(default=1)  # Number of times ignored
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ignored_email')

    def __str__(self):
        return f"{self.user.email} ignored {self.ignored_email} ({self.count} times)"
    


class EmailClassification(models.Model):
    uid = models.CharField(max_length=100)
    email_id = models.CharField(max_length=200, unique=True)
    classification = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email_id
from django.db import models

class EmailSummary(models.Model):
    email_id = models.CharField(max_length=255, unique=True)  # Gmail Message ID
    sender = models.CharField(max_length=255, blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email_id} - {self.subject[:30]}"

class OpenRouterAPIKey(models.Model):
    key = models.CharField(max_length=255, unique=True)
    requests_today = models.PositiveIntegerField(default=0)
    last_reset = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.key[-6:]} | {self.requests_today}"
    

class MVPUser(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    accepted_disclaimer = models.BooleanField(default=False)
    downloaded = models.BooleanField(default=False)  # 🔑 new
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email