from django.test import TestCase
from django.urls import reverse

from task_manager.labels.models import Label


class LabelsTests(TestCase):
    @staticmethod
    def log_decorator(func):
        def wrapper(self, *args, **kwargs):
            print(f'labels: {func.__name__}')
            result = func(self, *args, **kwargs)
            return result
        return wrapper

    def setUp(self):
        self.label = Label.objects.create(name="Urgent")

    @log_decorator
    def test_labels_list_view(self):
        response = self.client.get(reverse('labels:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.label.name)

    @log_decorator
    def test_labels_create_view(self):
        data = {'name': 'Important'}
        response = self.client.post(reverse('labels:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Label.objects.filter(name='Important').exists())

    @log_decorator
    def test_labels_update_view(self):
        data = {'name': 'Updated'}
        response = self.client.post(
            reverse(
                'labels:update',
                args=[self.label.id]
            ),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, 'Updated')

    @log_decorator
    def test_labels_delete_view(self):
        response = self.client.post(
            reverse(
                'labels:delete',
                args=[self.label.id]
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Label.objects.filter(id=self.label.id).exists())
