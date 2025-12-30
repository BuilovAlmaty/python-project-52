from django.test import TestCase
from django.urls import reverse
from task_manager.statuses.models import TaskState


class StatusesTests(TestCase):
    def setUp(self):
        self.status = TaskState.objects.create(name="New")
        print('test Statuses')

    def test_status_list_view(self):
        response = self.client.get(reverse('statuses:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.status.name)

    def test_status_create_view(self):
        data = {'name': 'Testing'}
        response = self.client.post(reverse('statuses:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TaskState.objects.filter(name='Testing').exists())

    def test_status_update_view(self):
        data = {'name': 'Updated'}
        response = self.client.post(reverse('statuses:update', args=[self.status.id]), data)
        self.assertEqual(response.status_code, 302)
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'Updated')

    def test_status_delete_view(self):
        response = self.client.post(reverse('statuses:delete', args=[self.status.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TaskState.objects.filter(id=self.status.id).exists())
