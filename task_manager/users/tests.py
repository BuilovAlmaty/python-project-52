from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


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
            password='password'
        )
        self.client.login(username='testuser', password='password')

    @log_decorator
    def test_user_create_view(self):
        data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
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
            'password1': '',
            'password2': '',
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
            'password1': 'newpass1234',
            'password2': 'newpass1234',
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
            'password': 'password',
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
