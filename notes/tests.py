from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from notes.models import Note, Category, Tag

class NotesCRUDAndSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='notes_user_a', email='na@example.com', password='Password123!')
        self.user2 = User.objects.create_user(username='notes_user_b', email='nb@example.com', password='Password123!')

        self.cat1 = Category.objects.create(user=self.user1, name='Python')
        self.cat2 = Category.objects.create(user=self.user2, name='Java')

        self.tag1 = Tag.objects.create(user=self.user1, name='Exam')
        self.tag2 = Tag.objects.create(user=self.user2, name='Project')

        self.note1 = Note.objects.create(
            user=self.user1,
            category=self.cat1,
            title='Django MVT Architecture',
            content='Model View Template design pattern in Django web framework.'
        )
        self.note1.tags.add(self.tag1)

        self.note2_user2 = Note.objects.create(
            user=self.user2,
            category=self.cat2,
            title='Spring Boot Basics',
            content='Java Enterprise microservices'
        )
        self.note2_user2.tags.add(self.tag2)

    def test_01_notes_page_requires_login(self):
        response = self.client.get(reverse('notes:note_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_02_create_note(self):
        self.client.login(username='notes_user_a', password='Password123!')
        response = self.client.post(reverse('notes:note_create'), {
            'title': 'PostgreSQL Indexing',
            'content': 'B-Tree and Hash indexes explained.',
            'category': self.cat1.id,
            'tags': [self.tag1.id]
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Note.objects.filter(user=self.user1, title='PostgreSQL Indexing').exists())

    def test_03_read_note_detail(self):
        self.client.login(username='notes_user_a', password='Password123!')
        response = self.client.get(reverse('notes:note_detail', kwargs={'pk': self.note1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django MVT Architecture')

    def test_04_update_note(self):
        self.client.login(username='notes_user_a', password='Password123!')
        response = self.client.post(reverse('notes:note_edit', kwargs={'pk': self.note1.id}), {
            'title': 'Django MVT Architecture Updated',
            'content': 'Updated content for MVT architecture.',
            'category': self.cat1.id,
            'tags': [self.tag1.id]
        })
        self.assertEqual(response.status_code, 302)
        self.note1.refresh_from_db()
        self.assertEqual(self.note1.title, 'Django MVT Architecture Updated')

    def test_05_delete_note_post(self):
        self.client.login(username='notes_user_a', password='Password123!')
        response = self.client.post(reverse('notes:note_delete', kwargs={'pk': self.note1.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(id=self.note1.id).exists())

    def test_06_search_notes(self):
        self.client.login(username='notes_user_a', password='Password123!')
        response = self.client.get(reverse('notes:note_list') + '?q=Template')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django MVT Architecture')

    def test_07_filter_by_category(self):
        self.client.login(username='notes_user_a', password='Password123!')
        response = self.client.get(reverse('notes:note_list') + f'?category={self.cat1.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django MVT Architecture')

    def test_08_filter_by_tag(self):
        self.client.login(username='notes_user_a', password='Password123!')
        response = self.client.get(reverse('notes:note_list') + f'?tag={self.tag1.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django MVT Architecture')

    def test_09_sorting_notes(self):
        self.client.login(username='notes_user_a', password='Password123!')
        response = self.client.get(reverse('notes:note_list') + '?sort=title_asc')
        self.assertEqual(response.status_code, 200)

    def test_10_pagination(self):
        self.client.login(username='notes_user_a', password='Password123!')
        for i in range(15):
            Note.objects.create(user=self.user1, title=f"Note {i}", content="Content")

        response = self.client.get(reverse('notes:note_list') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['page_obj'].has_previous())

    def test_11_ownership_isolation_view(self):
        self.client.login(username='notes_user_a', password='Password123!')
        # User A trying to view User B's note detail
        response = self.client.get(reverse('notes:note_detail', kwargs={'pk': self.note2_user2.id}))
        self.assertEqual(response.status_code, 404)

    def test_12_ownership_isolation_edit(self):
        self.client.login(username='notes_user_a', password='Password123!')
        response = self.client.post(reverse('notes:note_edit', kwargs={'pk': self.note2_user2.id}), {
            'title': 'Hacked Title',
            'content': 'Hacked Content'
        })
        self.assertEqual(response.status_code, 404)

    def test_13_ownership_isolation_delete(self):
        self.client.login(username='notes_user_a', password='Password123!')
        response = self.client.post(reverse('notes:note_delete', kwargs={'pk': self.note2_user2.id}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Note.objects.filter(id=self.note2_user2.id).exists())

    def test_14_cannot_attach_another_users_category(self):
        self.client.login(username='notes_user_a', password='Password123!')
        response = self.client.post(reverse('notes:note_create'), {
            'title': 'Illegal Category Note',
            'content': 'Testing category isolation',
            'category': self.cat2.id # User B's category
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'category', 'Select a valid choice. That choice is not one of the available choices.')

    def test_15_cannot_attach_another_users_tag(self):
        self.client.login(username='notes_user_a', password='Password123!')
        response = self.client.post(reverse('notes:note_create'), {
            'title': 'Illegal Tag Note',
            'content': 'Testing tag isolation',
            'tags': [self.tag2.id] # User B's tag
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('tags', form.errors)
        self.assertIn('is not one of the available choices', form.errors['tags'][0])


    def test_16_category_crud(self):
        self.client.login(username='notes_user_a', password='Password123!')
        # Create Category
        res = self.client.post(reverse('notes:category_list'), {'name': 'Algorithms', 'color': '#00ff00'})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Category.objects.filter(user=self.user1, name='Algorithms').exists())

        # Edit Category
        new_cat = Category.objects.get(user=self.user1, name='Algorithms')
        res_edit = self.client.post(reverse('notes:category_edit', kwargs={'pk': new_cat.id}), {'name': 'Data Structures', 'color': '#ff0000'})
        self.assertEqual(res_edit.status_code, 302)
        new_cat.refresh_from_db()
        self.assertEqual(new_cat.name, 'Data Structures')

        # Delete Category
        res_del = self.client.post(reverse('notes:category_delete', kwargs={'pk': new_cat.id}))
        self.assertEqual(res_del.status_code, 302)
        self.assertFalse(Category.objects.filter(id=new_cat.id).exists())

    def test_17_tag_crud(self):
        self.client.login(username='notes_user_a', password='Password123!')
        # Create Tag
        res = self.client.post(reverse('notes:tag_list'), {'name': 'Revision'})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Tag.objects.filter(user=self.user1, name='Revision').exists())

        # Delete Tag
        new_tag = Tag.objects.get(user=self.user1, name='Revision')
        res_del = self.client.post(reverse('notes:tag_delete', kwargs={'pk': new_tag.id}))
        self.assertEqual(res_del.status_code, 302)
        self.assertFalse(Tag.objects.filter(id=new_tag.id).exists())
