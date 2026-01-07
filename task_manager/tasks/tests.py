from django.contrib.auth.models import User
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
            result = func(self, *args, **kwargs)
            return result
        return wrapper

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.status = TaskStatus.objects.create(name='New')
        self.label = Label.objects.create(name='Bug')
        self.client.login(username='testuser', password='password')

    @log_decorator
    def test_task_create(self):
        data = {
            'name': 'Test Task',
            'description': 'Description',
            'status': self.status.id,
            'labels': [self.label.id],
        }
        response = self.client.post(reverse('tasks:create'), data)
        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(name='Test Task')
        self.assertEqual(task.author, self.user)
        self.assertIn(self.label, task.labels.all())

    @log_decorator
    def test_task_update_view(self):
        task = Task.objects.create(
            name='Old Task',
            description='Old',
            status=self.status, author=self.user
        )
        TaskMembership.objects.create(
            task=task,
            user=self.user,
            role='creator'
        )
        data = {
            'name': task.name,
            'description': 'Updated',
            'status': self.status.id,
            'labels': [self.label.id],
        }
        response = self.client.post(
            reverse(
                'tasks:update',
                args=[task.id]),
            data
        )
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.description, 'Updated')
        self.assertIn(self.label, task.labels.all())

    @log_decorator
    def test_task_delete_view(self):
        task = Task.objects.create(
            name='Delete Task',
            description='To delete',
            status=self.status,
            author=self.user
        )
        TaskMembership.objects.create(
            task=task,
            user=self.user,
            role='creator'
        )
        response = self.client.post(reverse('tasks:delete', args=[task.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=task.id).exists())
