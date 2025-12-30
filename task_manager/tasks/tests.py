from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from task_manager.tasks.models import Task, TaskMembership
from task_manager.statuses.models import TaskState
from task_manager.labels.models import Label


class TaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.state = TaskState.objects.create(name='New')
        self.label = Label.objects.create(name='Bug')
        self.client.login(username='testuser', password='password')
        print('test Tasks')

    def test_task_create(self):
        data = {
            'title': 'Test Task',
            'description': 'Description',
            'current_state': self.state.id,
            'labels': [self.label.id],
        }
        response = self.client.post(reverse('tasks:create'), data)
        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(title='Test Task')
        self.assertEqual(task.author, self.user)
        self.assertIn(self.label, task.labels.all())

    def test_task_update_view(self):
        task = Task.objects.create(title='Old Task', description='Old', current_state=self.state, author=self.user)
        TaskMembership.objects.create(task=task, user=self.user, role='creator')
        data = {
            'title': task.title,
            'description': 'Updated',
            'current_state': self.state.id,
            'labels': [self.label.id],
        }
        response = self.client.post(reverse('tasks:update', args=[task.id]), data)
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.description, 'Updated')
        self.assertIn(self.label, task.labels.all())

    def test_task_delete_view(self):
        task = Task.objects.create(title='Delete Task', description='To delete', current_state=self.state, author=self.user)
        TaskMembership.objects.create(task=task, user=self.user, role='creator')
        response = self.client.post(reverse('tasks:delete', args=[task.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=task.id).exists())
