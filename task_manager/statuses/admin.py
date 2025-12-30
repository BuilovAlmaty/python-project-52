from django.contrib import admin
from task_manager.statuses.models import TaskState

# Register your models here.
admin.site.register(TaskState)
