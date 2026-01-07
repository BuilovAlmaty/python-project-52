from django.contrib import admin

from task_manager.statuses.models import TaskStatus

# Register your models here.
admin.site.register(TaskStatus)
