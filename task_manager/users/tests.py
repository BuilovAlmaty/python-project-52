from django.contrib.auth.models import User
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from task_manager.statuses.models import TaskStatus
from task_manager.tasks.models import Task

from .forms import UserUpdateForm


class UsersTests(TestCase):
    @staticmethod
    def log_decorator(func):
        def wrapper(self, *args, **kwargs):
            print(f'users: {func.__name__}')
            result = func(self, *args, **kwargs)
            return result
        return wrapper

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            password='password'  # NOSONAR
        )
        self.client.login(
            username='testuser',
            password='password',  # NOSONAR
        )

    @log_decorator
    def test_user_create_view(self):
        data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'newpassword123',  # NOSONAR
            'password2': 'newpassword123',  # NOSONAR
        }
        response = self.client.post(reverse('users:create'), data)
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.first_name, 'New')

    @log_decorator
    def test_user_update_view(self):
        data = {
            'username': 'testuser',
            'first_name': 'Updated',
            'last_name': 'User',
            'password1': '',  # NOSONAR
            'password2': '',  # NOSONAR
        }
        response = self.client.post(
            reverse(
                'users:update',
                args=[self.user.id]
            ),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    @log_decorator
    def test_user_update_password(self):
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'newpass1234',  # NOSONAR
            'password2': 'newpass1234',  # NOSONAR
        }
        response = self.client.post(
            reverse(
                'users:update',
                args=[self.user.id]
            ),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass1234'))

    @log_decorator
    def test_user_login_view(self):
        self.client.logout()
        data = {
            'username': 'testuser',
            'password': 'password',  # NOSONAR
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    @log_decorator
    def test_user_logout_view(self):
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)

    @log_decorator
    def test_user_delete_view(self):
        response = self.client.post(
            reverse(
                'users:delete',
                args=[self.user.id]
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    @log_decorator
    def test_user_update_view_without_password(self):
        response = self.client.post(
            reverse('users:update', args=[self.user.id]),
            {
                'username': 'testuser',
                'first_name': 'Updated',
                'last_name': 'User',
                'password1': '',  # NOSONAR
                'password2': '',  # NOSONAR
            }
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    @log_decorator
    def test_user_update_view_with_password(self):
        response = self.client.post(
            reverse('users:update', args=[self.user.id]),
            {
                'username': 'testuser',
                'first_name': 'Test',
                'last_name': 'User',
                'password1': 'newpass1234',  # NOSONAR
                'password2': 'newpass1234',  # NOSONAR
            }
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass1234'))

    @log_decorator
    def test_update_dispatch_denies_other_user(self):
        other = User.objects.create_user(
            username='other',
            password='pass'  # NOSONAR
        )
        self.client.login(
            username='other',
            password='pass',  # NOSONAR
        )

        response = self.client.post(
            reverse('users:update', args=[self.user.id]),
            {
                'username': self.user.username,
                'first_name': 'Hack',
                'last_name': 'Hack',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.first_name, 'Hack')
        self.assertEqual(other.username, 'other')

    @log_decorator
    def test_delete_dispatch_denies_other_user(self):
        other = User.objects.create_user(
            username='other',
            password='pass'  # NOSONAR
        )
        self.client.login(
            username='other',
            password='pass',  # NOSONAR
        )

        response = self.client.post(
            reverse('users:delete', args=[self.user.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(id=self.user.id).exists())
        self.assertEqual(other.username, 'other')

    @log_decorator
    def test_form_clean_matching_passwords(self):
        form = UserUpdateForm(
            instance=self.user,
            data={
                'username': self.user.username,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'new_password1': 'abc12345',  # NOSONAR
                'new_password2': 'abc12345',  # NOSONAR
            }
        )
        self.assertTrue(form.is_valid())

    @log_decorator
    def test_form_save_skips_password(self):
        old_password = self.user.password

        form = UserUpdateForm(
            instance=self.user,
            data={
                'username': self.user.username,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'new_password1': '',  # NOSONAR
                'new_password2': '',  # NOSONAR
            }
        )
        self.assertTrue(form.is_valid())
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.password, old_password)

    @log_decorator
    def test_user_delete_view_protected_error(self):
        status = TaskStatus.objects.create(name='Test status')

        Task.objects.create(
            name='Task',
            status=status,
            author=self.user,
        )

        with self.assertRaises(ProtectedError):
            self.user.delete()
