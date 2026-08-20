from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from planner.models import Task
from notes.models import Note, Category

class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='dash_user1', email='dash1@example.com', password='Password123!')
        self.user2 = User.objects.create_user(username='dash_user2', email='dash2@example.com', password='Password123!')

        # Create tasks for user1
        Task.objects.create(user=self.user1, title='Task 1', status=Task.STATUS_COMPLETED, is_completed=True)
        Task.objects.create(user=self.user1, title='Task 2', status=Task.STATUS_PENDING, is_completed=False)

        # Create tasks for user2
        Task.objects.create(user=self.user2, title='User2 Task', status=Task.STATUS_PENDING, is_completed=False)

    def test_01_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_02_dashboard_statistics_and_data_isolation(self):
        self.client.login(username='dash_user1', password='Password123!')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_tasks'], 2)
        self.assertEqual(response.context['completed_tasks'], 1)
        self.assertEqual(response.context['pending_tasks'], 1)
        self.assertEqual(response.context['completion_rate'], 50.0)
