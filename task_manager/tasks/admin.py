from django.contrib import admin
from .models import Task, TaskMembership

# Register your models here.
admin.site.register(Task)
admin.site.register(TaskMembership)
