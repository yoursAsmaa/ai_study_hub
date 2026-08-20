from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import datetime

from planner.models import Task
from notes.models import Category

class TaskCRUDAndSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='student_a', email='a@example.com', password='Password123!')
        self.user2 = User.objects.create_user(username='student_b', email='b@example.com', password='Password123!')

        self.category1 = Category.objects.create(user=self.user1, name='Math')
        self.category2 = Category.objects.create(user=self.user2, name='Physics')

        self.task1 = Task.objects.create(
            user=self.user1,
            category=self.category1,
            title='Study Calculus',
            description='Chapter 1 integration',
            priority=Task.PRIORITY_HIGH,
            status=Task.STATUS_PENDING,
            due_date=timezone.now() + datetime.timedelta(days=2)
        )

        self.task2_user2 = Task.objects.create(
            user=self.user2,
            category=self.category2,
            title='Physics Homework',
            description='Mechanics problems',
            priority=Task.PRIORITY_MEDIUM,
            status=Task.STATUS_PENDING
        )

    def test_01_task_creation(self):
        self.client.login(username='student_a', password='Password123!')
        response = self.client.post(reverse('planner:task_create'), {
            'title': 'New Algorithm Task',
            'description': 'Sorting algorithms review',
            'priority': Task.PRIORITY_MEDIUM,
            'status': Task.STATUS_PENDING,
            'category': self.category1.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(user=self.user1, title='New Algorithm Task').exists())

    def test_02_task_list(self):
        self.client.login(username='student_a', password='Password123!')
        response = self.client.get(reverse('planner:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Study Calculus')
        self.assertNotContains(response, 'Physics Homework')

    def test_03_task_detail(self):
        self.client.login(username='student_a', password='Password123!')
        response = self.client.get(reverse('planner:task_detail', kwargs={'pk': self.task1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Study Calculus')

    def test_04_task_update(self):
        self.client.login(username='student_a', password='Password123!')
        response = self.client.post(reverse('planner:task_edit', kwargs={'pk': self.task1.id}), {
            'title': 'Study Calculus Updated',
            'description': 'Chapter 1 & 2 integration',
            'priority': Task.PRIORITY_HIGH,
            'status': Task.STATUS_IN_PROGRESS,
            'category': self.category1.id
        })
        self.assertEqual(response.status_code, 302)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Study Calculus Updated')

    def test_05_task_deletion_post(self):
        self.client.login(username='student_a', password='Password123!')
        response = self.client.post(reverse('planner:task_delete', kwargs={'pk': self.task1.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())

    def test_06_mark_completed_and_pending(self):
        self.client.login(username='student_a', password='Password123!')
        # Mark completed
        response1 = self.client.post(reverse('planner:task_toggle_status', kwargs={'pk': self.task1.id}))
        self.assertEqual(response1.status_code, 302)
        self.task1.refresh_from_db()
        self.assertTrue(self.task1.is_completed)

        # Mark pending
        response2 = self.client.post(reverse('planner:task_toggle_status', kwargs={'pk': self.task1.id}))
        self.assertEqual(response2.status_code, 302)
        self.task1.refresh_from_db()
        self.assertFalse(self.task1.is_completed)

    def test_07_task_search(self):
        self.client.login(username='student_a', password='Password123!')
        response = self.client.get(reverse('planner:task_list') + '?q=Calculus')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Study Calculus')

    def test_08_task_filtering(self):
        self.client.login(username='student_a', password='Password123!')
        response = self.client.get(reverse('planner:task_list') + '?priority=HIGH')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Study Calculus')

    def test_09_pagination(self):
        self.client.login(username='student_a', password='Password123!')
        for i in range(15):
            Task.objects.create(user=self.user1, title=f"Task {i}")

        response = self.client.get(reverse('planner:task_list') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['page_obj'].has_previous())

    def test_10_user_cannot_access_another_users_task(self):
        self.client.login(username='student_a', password='Password123!')
        # Student A trying to view Student B's task detail
        response = self.client.get(reverse('planner:task_detail', kwargs={'pk': self.task2_user2.id}))
        self.assertEqual(response.status_code, 404)

    def test_11_user_cannot_edit_another_users_task(self):
        self.client.login(username='student_a', password='Password123!')
        response = self.client.post(reverse('planner:task_edit', kwargs={'pk': self.task2_user2.id}), {
            'title': 'Hacked Title'
        })
        self.assertEqual(response.status_code, 404)
        self.task2_user2.refresh_from_db()
        self.assertNotEqual(self.task2_user2.title, 'Hacked Title')

    def test_12_user_cannot_delete_another_users_task(self):
        self.client.login(username='student_a', password='Password123!')
        response = self.client.post(reverse('planner:task_delete', kwargs={'pk': self.task2_user2.id}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(id=self.task2_user2.id).exists())

    def test_13_user_cannot_toggle_another_users_task(self):
        self.client.login(username='student_a', password='Password123!')
        response = self.client.post(reverse('planner:task_toggle_status', kwargs={'pk': self.task2_user2.id}))
        self.assertEqual(response.status_code, 404)
