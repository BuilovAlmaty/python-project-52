from django.contrib.auth.models import User
from django.db import models

from task_manager.labels.models import Label
from task_manager.statuses.models import TaskStatus


class Task(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_tasks',
    )
    status = models.ForeignKey(
        TaskStatus,
        on_delete=models.PROTECT,
        related_name='tasks'
    )
    labels = models.ManyToManyField(
        Label,
        related_name='tasks',
        blank=True,
    )

    def __str__(self):
        return self.name


class TaskMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('executor', 'Executor'),
        ('viewer', 'Viewer'),
        ('creator', 'Creator')
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='executor'
    )

    class Meta:
        unique_together = ('user', 'task', 'role')


class TaskStatusHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.ForeignKey(TaskStatus, on_delete=models.PROTECT)
    edited_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
