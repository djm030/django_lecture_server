from django.contrib import admin
from .models import Instructor_Application


class InstructorApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "description", "career", "created_at", "updated_at")
    search_fields = ("user__username", "description", "career")


admin.site.register(Instructor_Application, InstructorApplicationAdmin)