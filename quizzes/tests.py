from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from quizzes.models import Quiz, Question, Flashcard, StudySession
from notes.models import Category

class QuizzesSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='quiz_user_a', email='qa@example.com', password='Password123!')
        self.user2 = User.objects.create_user(username='quiz_user_b', email='qb@example.com', password='Password123!')

        self.quiz1 = Quiz.objects.create(
            user=self.user1,
            title='Python Programming Basics'
        )
        self.question1 = Question.objects.create(
            quiz=self.quiz1,
            question_text='What is the output of print(2 * 3)?',
            options=['5', '6', '8', '9'],
            correct_answer='6'
        )
        self.question2 = Question.objects.create(
            quiz=self.quiz1,
            question_text='Is Python compiled or interpreted?',
            options=['Compiled', 'Interpreted', 'Both', 'Neither'],
            correct_answer='Interpreted'
        )
        # Update question counts
        self.quiz1.total_questions = 2
        self.quiz1.save()

        # Quiz 2 for User 2
        self.quiz2_user2 = Quiz.objects.create(
            user=self.user2,
            title='Advanced Java'
        )

        # Flashcards
        self.card1 = Flashcard.objects.create(
            user=self.user1,
            front='What does HTML stand for?',
            back='HyperText Markup Language',
            known=False
        )
        self.card2_user2 = Flashcard.objects.create(
            user=self.user2,
            front='Java OOP concept',
            back='Encapsulation, Inheritance, Polymorphism',
            known=False
        )

        # Study Sessions
        self.cat1 = Category.objects.create(user=self.user1, name='Web Dev')

    def test_01_quiz_page_requires_login(self):
        response = self.client.get(reverse('quizzes:quiz_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_02_quiz_ownership_isolation_detail(self):
        self.client.login(username='quiz_user_a', password='Password123!')
        response = self.client.get(reverse('quizzes:quiz_detail', kwargs={'pk': self.quiz2_user2.id}))
        self.assertEqual(response.status_code, 404)

    def test_03_question_display(self):
        self.client.login(username='quiz_user_a', password='Password123!')
        response = self.client.get(reverse('quizzes:quiz_take', kwargs={'pk': self.quiz1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'What is the output of print(2 * 3)?')
        self.assertNotContains(response, 'correct_answer') # Ensure answer not exposed

    def test_04_quiz_submission_and_scores(self):
        self.client.login(username='quiz_user_a', password='Password123!')
        # Post answers (1 correct, 1 incorrect)
        response = self.client.post(reverse('quizzes:quiz_submit', kwargs={'pk': self.quiz1.id}), {
            f"question_{self.question1.id}": '6',          # correct
            f"question_{self.question2.id}": 'Compiled',   # incorrect
        })
        self.assertEqual(response.status_code, 302)
        
        self.quiz1.refresh_from_db()
        self.assertTrue(self.quiz1.completed)
        self.assertEqual(self.quiz1.correct_answers, 1)
        self.assertEqual(self.quiz1.total_questions, 2)
        self.assertEqual(self.quiz1.score, 50.0)

    def test_05_result_page_display(self):
        self.client.login(username='quiz_user_a', password='Password123!')
        # Complete quiz
        self.quiz1.completed = True
        self.quiz1.score = 100.0
        self.quiz1.correct_answers = 2
        self.quiz1.save()

        response = self.client.get(reverse('quizzes:quiz_result', kwargs={'pk': self.quiz1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '100.0%')
        self.assertContains(response, 'Python Programming Basics')

    def test_06_user_cannot_access_another_users_quiz_submission(self):
        self.client.login(username='quiz_user_a', password='Password123!')
        response = self.client.post(reverse('quizzes:quiz_submit', kwargs={'pk': self.quiz2_user2.id}), {})
        self.assertEqual(response.status_code, 404)

    def test_07_flashcard_ownership_isolation(self):
        self.client.login(username='quiz_user_a', password='Password123!')
        response = self.client.get(reverse('quizzes:flashcard_edit', kwargs={'pk': self.card2_user2.id}))
        self.assertEqual(response.status_code, 404)

    def test_08_flashcard_crud(self):
        self.client.login(username='quiz_user_a', password='Password123!')
        # Create
        response = self.client.post(reverse('quizzes:flashcard_create'), {
            'front': 'CSS stands for?',
            'back': 'Cascading Style Sheets'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Flashcard.objects.filter(user=self.user1, front='CSS stands for?').exists())

        card = Flashcard.objects.get(user=self.user1, front='CSS stands for?')
        # Edit
        response = self.client.post(reverse('quizzes:flashcard_edit', kwargs={'pk': card.id}), {
            'front': 'CSS stands for? (Updated)',
            'back': 'Cascading Style Sheets!'
        })
        self.assertEqual(response.status_code, 302)
        card.refresh_from_db()
        self.assertEqual(card.front, 'CSS stands for? (Updated)')

        # Delete
        response = self.client.post(reverse('quizzes:flashcard_delete', kwargs={'pk': card.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Flashcard.objects.filter(id=card.id).exists())

    def test_09_flashcard_review_logic(self):
        self.client.login(username='quiz_user_a', password='Password123!')
        response = self.client.get(reverse('quizzes:flashcard_review'))
        self.assertEqual(response.status_code, 200)
        # Should contain the unmastered card Front text
        self.assertContains(response, 'What does HTML stand for?')

    def test_10_start_study_session(self):
        self.client.login(username='quiz_user_a', password='Password123!')
        response = self.client.post(reverse('quizzes:session_start'), {
            'subject': 'Database Indexing',
            'category': self.cat1.id,
            'notes': 'Goal: Understand B-Tree indexes'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(StudySession.objects.filter(user=self.user1, end_time__isnull=True).exists())

    def test_11_end_study_session_and_duration_calculation(self):
        self.client.login(username='quiz_user_a', password='Password123!')
        # Seed an active session manually
        session = StudySession.objects.create(
            user=self.user1,
            subject='Algorithms',
            start_time=timezone.now() - timedelta(minutes=45)
        )
        response = self.client.post(reverse('quizzes:session_end'))
        self.assertEqual(response.status_code, 302)
        
        session.refresh_from_db()
        self.assertIsNotNone(session.end_time)
        self.assertEqual(session.duration_minutes, 45)

    def test_12_prevent_multiple_active_sessions(self):
        self.client.login(username='quiz_user_a', password='Password123!')
        # Start first session
        self.client.post(reverse('quizzes:session_start'), {'subject': 'Session 1'})
        # Start second session
        response = self.client.post(reverse('quizzes:session_start'), {'subject': 'Session 2'})
        # Should output a warning message or stay inside active
        active_count = StudySession.objects.filter(user=self.user1, end_time__isnull=True).count()
        self.assertEqual(active_count, 1)

    def test_13_study_session_ownership_isolation(self):
        # Create user 2 session
        session_user2 = StudySession.objects.create(
            user=self.user2,
            subject='Java Advanced',
            start_time=timezone.now()
        )
        self.client.login(username='quiz_user_a', password='Password123!')
        # End session shouldn't affect user 2's session
        response = self.client.post(reverse('quizzes:session_end'))
        # User 2 session should remain active (end_time null)
        session_user2.refresh_from_db()
        self.assertIsNone(session_user2.end_time)

    def test_14_dashboard_analytics_integration(self):
        self.client.login(username='quiz_user_a', password='Password123!')
        # Submit complete quiz
        self.quiz1.completed = True
        self.quiz1.score = 80.0
        self.quiz1.correct_answers = 2
        self.quiz1.save()

        # Submit study session
        StudySession.objects.create(
            user=self.user1,
            subject='Python Basics',
            start_time=timezone.now() - timedelta(minutes=30),
            end_time=timezone.now(),
            duration_minutes=30
        )

        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_quizzes'], 1)
        self.assertEqual(response.context['average_quiz_score'], 80.0)
        self.assertEqual(response.context['best_quiz_score'], 80.0)
        self.assertEqual(response.context['total_study_sessions'], 1)
        self.assertEqual(response.context['total_study_time'], 30)
