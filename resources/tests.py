from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from resources.models import Resource
from notes.models import Category

class ResourcesCRUDAndSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='res_user_a', email='ra@example.com', password='Password123!')
        self.user2 = User.objects.create_user(username='res_user_b', email='rb@example.com', password='Password123!')

        self.cat1 = Category.objects.create(user=self.user1, name='AI Tools')
        self.cat2 = Category.objects.create(user=self.user2, name='Physics Tools')

        self.resource1 = Resource.objects.create(
            user=self.user1,
            category=self.cat1,
            title='Django Docs',
            description='Official Django documentation reference.',
            link='https://docs.djangoproject.com/en/',
            resource_type=Resource.TYPE_DOCS
        )

        self.resource2_user2 = Resource.objects.create(
            user=self.user2,
            category=self.cat2,
            title='Physics Video Guide',
            description='Kinematic equations video tutorial.',
            link='https://youtube.com/physics-guide',
            resource_type=Resource.TYPE_VIDEO
        )

    def test_01_resources_page_requires_login(self):
        response = self.client.get(reverse('resources:resource_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_02_create_resource(self):
        self.client.login(username='res_user_a', password='Password123!')
        response = self.client.post(reverse('resources:resource_create'), {
            'title': 'Vite Web Dev Course',
            'description': 'Crash course on building frontend with Vite.',
            'link': 'https://vitejs.dev/',
            'resource_type': Resource.TYPE_COURSE,
            'category': self.cat1.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Resource.objects.filter(user=self.user1, title='Vite Web Dev Course').exists())

    def test_03_read_resource(self):
        self.client.login(username='res_user_a', password='Password123!')
        response = self.client.get(reverse('resources:resource_detail', kwargs={'pk': self.resource1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Docs')

    def test_04_update_resource(self):
        self.client.login(username='res_user_a', password='Password123!')
        response = self.client.post(reverse('resources:resource_edit', kwargs={'pk': self.resource1.id}), {
            'title': 'Django Docs Updated',
            'description': 'Updated documentation reference.',
            'link': 'https://docs.djangoproject.com/en/5.0/',
            'resource_type': Resource.TYPE_DOCS,
            'category': self.cat1.id
        })
        self.assertEqual(response.status_code, 302)
        self.resource1.refresh_from_db()
        self.assertEqual(self.resource1.title, 'Django Docs Updated')

    def test_05_delete_resource(self):
        self.client.login(username='res_user_a', password='Password123!')
        response = self.client.post(reverse('resources:resource_delete', kwargs={'pk': self.resource1.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Resource.objects.filter(id=self.resource1.id).exists())

    def test_06_search_resources(self):
        self.client.login(username='res_user_a', password='Password123!')
        response = self.client.get(reverse('resources:resource_list') + '?q=Docs')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Docs')

    def test_07_filter_by_type(self):
        self.client.login(username='res_user_a', password='Password123!')
        response = self.client.get(reverse('resources:resource_list') + f'?type={Resource.TYPE_DOCS}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Docs')

    def test_08_filter_by_category(self):
        self.client.login(username='res_user_a', password='Password123!')
        response = self.client.get(reverse('resources:resource_list') + f'?category={self.cat1.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Docs')

    def test_09_sorting(self):
        self.client.login(username='res_user_a', password='Password123!')
        response = self.client.get(reverse('resources:resource_list') + '?sort=title_asc')
        self.assertEqual(response.status_code, 200)

    def test_10_pagination(self):
        self.client.login(username='res_user_a', password='Password123!')
        for i in range(12):
            Resource.objects.create(
                user=self.user1,
                title=f"Resource {i}",
                link="https://example.com/test",
                resource_type=Resource.TYPE_OTHER
            )
        response = self.client.get(reverse('resources:resource_list') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['page_obj'].has_previous())

    def test_11_url_validation_invalid(self):
        self.client.login(username='res_user_a', password='Password123!')
        response = self.client.post(reverse('resources:resource_create'), {
            'title': 'Invalid Link Resource',
            'link': 'not-a-valid-url',
            'resource_type': Resource.TYPE_BOOK
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'link', 'Enter a valid URL.')

    def test_12_resource_ownership_view_isolation(self):
        self.client.login(username='res_user_a', password='Password123!')
        response = self.client.get(reverse('resources:resource_detail', kwargs={'pk': self.resource2_user2.id}))
        self.assertEqual(response.status_code, 404)

    def test_13_resource_ownership_edit_isolation(self):
        self.client.login(username='res_user_a', password='Password123!')
        response = self.client.post(reverse('resources:resource_edit', kwargs={'pk': self.resource2_user2.id}), {
            'title': 'Hacked Title',
            'link': 'https://hacked.com/'
        })
        self.assertEqual(response.status_code, 404)

    def test_14_resource_ownership_delete_isolation(self):
        self.client.login(username='res_user_a', password='Password123!')
        response = self.client.post(reverse('resources:resource_delete', kwargs={'pk': self.resource2_user2.id}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Resource.objects.filter(id=self.resource2_user2.id).exists())

    def test_15_cannot_assign_another_users_category(self):
        self.client.login(username='res_user_a', password='Password123!')
        response = self.client.post(reverse('resources:resource_create'), {
            'title': 'Illegal Category Resource',
            'link': 'https://example.com/test',
            'resource_type': Resource.TYPE_DOCS,
            'category': self.cat2.id # User B's category
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'category', 'Select a valid choice. That choice is not one of the available choices.')
