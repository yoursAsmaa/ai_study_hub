from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.signing import TimestampSigner
from accounts.models import Profile

class AuthenticationAndProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='Password123!'
        )
        self.user2 = User.objects.create_user(
            username='student2',
            email='student2@example.com',
            password='Password123!'
        )
        self.signer = TimestampSigner()

    def test_01_user_registration_success(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newstudent',
            'email': 'newstudent@example.com',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newstudent').exists())
        new_user = User.objects.get(username='newstudent')
        self.assertTrue(hasattr(new_user, 'profile'))

    def test_02_duplicate_username_prevention(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'student1', # duplicate
            'email': 'different@example.com',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!'
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('username', form.errors)
        self.assertIn('A user with that username already exists.', form.errors['username'])


    def test_03_password_mismatch_and_weak_password_validation(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'testuser3',
            'email': 'testuser3@example.com',
            'password': '123', # weak
            'confirm_password': '456' # mismatch
        })
        self.assertEqual(response.status_code, 200)

    def test_04_login_success(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'student1',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard:index'))

    def test_05_login_failure(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'student1',
            'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username/email or password.')

    def test_06_logout(self):
        self.client.login(username='student1', password='Password123!')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))

    def test_07_profile_access_authenticated(self):
        self.client.login(username='student1', password='Password123!')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'student1')

    def test_08_profile_update(self):
        self.client.login(username='student1', password='Password123!')
        response = self.client.post(reverse('accounts:edit_profile'), {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'student1@example.com',
            'university': 'Tech University',
            'major': 'Computer Science',
            'phone': '1234567890',
            'bio': 'Learning AI and Web Dev'
        })
        self.assertEqual(response.status_code, 302)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'Jane')
        self.assertEqual(self.user1.profile.university, 'Tech University')

    def test_09_password_change(self):
        self.client.login(username='student1', password='Password123!')
        response = self.client.post(reverse('accounts:password_change'), {
            'old_password': 'Password123!',
            'new_password1': 'NewStrongPass123!',
            'new_password2': 'NewStrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        # Verify new password works
        self.client.logout()
        login_res = self.client.post(reverse('accounts:login'), {
            'username': 'student1',
            'password': 'NewStrongPass123!'
        })
        self.assertEqual(login_res.status_code, 302)

    def test_10_email_verification(self):
        token = self.signer.sign(self.user1.pk)
        response = self.client.get(reverse('accounts:verify_email', kwargs={'token': token}))
        self.assertEqual(response.status_code, 302)
        self.user1.profile.refresh_from_db()
        self.assertTrue(self.user1.profile.is_email_verified)

    def test_11_unauthorized_access_redirection(self):
        # Unauthenticated user trying to access profile & dashboard
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

        dash_res = self.client.get(reverse('dashboard:index'))
        self.assertEqual(dash_res.status_code, 302)
        self.assertIn(reverse('accounts:login'), dash_res.url)

    from django.test import override_settings

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_12_password_reset_request(self):
        from django.core import mail
        response = self.client.post(reverse('accounts:password_reset'), {
            'email': 'student1@example.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:password_reset_done'))
        # Verify password reset email was generated and queued in outbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('AI Study Hub Password Reset Request', mail.outbox[0].subject)
        self.assertIn('student1@example.com', mail.outbox[0].to)
        self.assertIn('/accounts/password-reset-confirm/', mail.outbox[0].body)


