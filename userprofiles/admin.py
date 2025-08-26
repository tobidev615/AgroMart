from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone_number", "city", "country", "created_at")
    list_filter = ("role", "city", "country")
    search_fields = ("user__username", "user__email", "phone_number")

# Register your models here.
