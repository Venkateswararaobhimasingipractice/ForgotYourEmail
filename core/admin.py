from django.contrib import admin
from .models import AppUser, UserProfile,EmailAction,ScheduledTask,EmailClassification,EmailSummary,Todo,IgnoredEmail,OpenRouterAPIKey,MVPUser
# Register your models here.
admin.site.register(AppUser)
admin.site.register(UserProfile)
admin.site.register(EmailAction)
admin.site.register(ScheduledTask)
admin.site.register(EmailClassification)
admin.site.register(EmailSummary)
admin.site.register(IgnoredEmail)
admin.site.register(Todo)
admin.site.register(OpenRouterAPIKey)
admin.site.register(MVPUser)

