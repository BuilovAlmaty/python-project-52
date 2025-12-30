from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class UsersTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            password='password'
        )
        self.client.login(username='testuser', password='password')
        print('test Users')

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

    def test_user_update_view(self):
        data = {
            'username': 'testuser',
            'first_name': 'Updated',
            'last_name': 'User',
            'new_password1': '',
            'new_password2': '',
        }
        response = self.client.post(reverse('users:update', args=[self.user.id]), data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_user_update_password(self):
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'new_password1': 'newpass1234',
            'new_password2': 'newpass1234',
        }
        response = self.client.post(reverse('users:update', args=[self.user.id]), data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass1234'))

    def test_user_login_view(self):
        self.client.logout()
        data = {
            'username': 'testuser',
            'password': 'password',
        }
        response = self.client.post(reverse('users:login'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_user_logout_view(self):
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_user_delete_view(self):
        response = self.client.post(reverse('users:delete', args=[self.user.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())
