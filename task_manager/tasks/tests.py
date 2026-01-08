from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from task_manager.labels.models import Label
from task_manager.statuses.models import TaskStatus
from task_manager.tasks.models import Task, TaskMembership


class TaskTests(TestCase):
    @staticmethod
    def log_decorator(func):
        def wrapper(self, *args, **kwargs):
            print(f'tasks: {func.__name__}')
            return func(self, *args, **kwargs)
        return wrapper

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password', # NOSONAR
            first_name='Test',
            last_name='User'
        )
        self.other_user = User.objects.create_user(
            username='other',
            password='password'
        )
        self.status = TaskStatus.objects.create(name='New')
        self.label = Label.objects.create(name='Bug')
        self.client.login(username='testuser', password='password')

    @log_decorator
    def test_task_create_with_executor(self):
        data = {
            'name': 'Task',
            'description': 'Desc',
            'status': self.status.id,
            'executor': self.other_user.id,
            'labels': [self.label.id],
        }

        response = self.client.post(reverse('tasks:create'), data)
        self.assertEqual(response.status_code, 302)

        task = Task.objects.get(name='Task')
        self.assertEqual(task.author, self.user)

        self.assertTrue(
            TaskMembership.objects.filter(
                task=task,
                user=self.other_user,
                role='executor'
            ).exists()
        )

    @log_decorator
    def test_task_create_integrity_error(self):
        data = {
            'name': 'Task',
            'status': self.status.id,
        }

        with patch('task_manager.tasks.views.transaction.atomic',
                   side_effect=IntegrityError):
            response = self.client.post(reverse('tasks:create'), data)

        self.assertEqual(response.status_code, 200)

    @log_decorator
    def test_task_update_no_permission(self):
        task = Task.objects.create(
            name='Task',
            status=self.status,
            author=self.other_user
        )

        with patch(
            'task_manager.tasks.views.has_permission',
            return_value=False
        ):
            response = self.client.post(
                reverse('tasks:update', args=[task.id]),
                {}
            )

        self.assertEqual(response.status_code, 302)

    @log_decorator
    def test_task_delete_no_permission(self):
        task = Task.objects.create(
            name='Task',
            status=self.status,
            author=self.other_user
        )

        response = self.client.post(
            reverse('tasks:delete', args=[task.id])
        )

        self.assertEqual(response.status_code, 302)

    @log_decorator
    def test_task_delete_protected_error(self):
        task = Task.objects.create(
            name='Task',
            status=self.status,
            author=self.user
        )

        with patch.object(Task, 'delete',
                          side_effect=Exception()):
            response = self.client.post(
                reverse('tasks:delete', args=[task.id])
            )

        self.assertEqual(response.status_code, 302)
