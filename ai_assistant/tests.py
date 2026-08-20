"""
AI Assistant — Test Suite
==========================
All tests use unittest.mock to patch the AI service functions.
No real API calls are made during testing.

Test coverage:
  1.  AI page requires login
  2.  Authenticated user can access AI page
  3.  AI service — missing API key raises AIServiceError
  4.  AI service — invalid/error response raises AIServiceError
  5.  Chat requires login
  6.  Chat validates empty input
  7.  Chat validates oversized input
  8.  Chat — success path persists ChatMessage records
  9.  Chat — AI failure returns JSON error, no messages saved
  10. Summarize — requires login
  11. Summarize — rejects another user's note (ownership check)
  12. Summarize — success path returns JSON with expected keys
  13. Summarize — AI failure returns JSON error
  14. Explain — success path
  15. Explain — rejects another user's note
  16. Generate Quiz — AI response validation (invalid structure rejected)
  17. Generate Quiz — malformed options list rejected
  18. Generate Quiz — correct_answer not in options rejected
  19. Generate Quiz — success path saves Quiz + Question records
  20. Generate Quiz — generated quiz belongs to requesting user
  21. Generate Quiz — AI failure shows error message, no quiz saved
  22. Generate Flashcards — success path saves Flashcard records
  23. Generate Flashcards — generated flashcards belong to requesting user
  24. Generate Flashcards — AI failure shows error, no flashcards saved
  25. Generate Flashcards — malformed AI response rejected
  26. Recommendation — requires login
  27. Recommendation — returns JSON with recommendations key
  28. Recommendation — data isolation: only current user's data used
  29. Another user cannot read first user's chat history via index
  30. Dashboard recommendation endpoint — requires login
  31. Dashboard recommendation endpoint — returns widget_text key
  32. Clear chat — deletes only current user's messages
"""

import json
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Category, Note
from quizzes.models import Flashcard, Question, Quiz

from .models import ChatMessage
from .services.ai_service import (
    AIServiceError,
    _parse_json_response,
    generate_flashcards,
    generate_quiz,
    summarize_note,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_user(username, password="testpass123"):
    return User.objects.create_user(username=username, password=password)


def _login(client, user, password="testpass123"):
    client.login(username=user.username, password=password)


VALID_QUIZ_JSON = json.dumps({
    "title": "Test Quiz",
    "questions": [
        {
            "question": "What is 2 + 2?",
            "options": ["2", "3", "4", "5"],
            "correct_answer": "4",
            "explanation": "Basic arithmetic.",
        }
    ],
})

VALID_FLASHCARD_JSON = json.dumps({
    "flashcards": [
        {"front": "What is Django?", "back": "A Python web framework."},
        {"front": "What is ORM?", "back": "Object-Relational Mapper."},
    ]
})

VALID_SUMMARY_JSON = json.dumps({
    "summary": "A concise summary.",
    "key_points": ["Point A", "Point B"],
    "important_terms": ["Term: definition"],
})

VALID_RECOMMENDATION_JSON = json.dumps({
    "recommendations": [
        {
            "subject": "Databases",
            "activity": "Review SQL joins",
            "duration_minutes": 45,
            "reason": "Your recent quiz score was low.",
        }
    ],
    "overall_tip": "Keep reviewing regularly.",
})


# ─────────────────────────────────────────────────────────────────────────────
# 1–2  AI index page access
# ─────────────────────────────────────────────────────────────────────────────

class AIIndexAccessTests(TestCase):

    def setUp(self):
        self.user = _make_user("alice")
        self.url  = reverse("ai_assistant:index")

    def test_1_index_requires_login(self):
        """Unauthenticated request redirects to login."""
        resp = self.client.get(self.url)
        self.assertRedirects(resp, f"{reverse('accounts:login')}?next={self.url}")

    def test_2_authenticated_user_can_access(self):
        """Authenticated user receives 200 on AI index page."""
        _login(self.client, self.user)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "ai_assistant/index.html")


# ─────────────────────────────────────────────────────────────────────────────
# 3–4  AI service unit tests (no HTTP, no real API)
# ─────────────────────────────────────────────────────────────────────────────

class AIServiceUnitTests(TestCase):

    def test_3_missing_api_key_raises_error(self):
        """_get_client raises AIServiceError when AI_API_KEY is empty."""
        with self.settings(AI_API_KEY=""):
            with self.assertRaises(AIServiceError) as ctx:
                from ai_assistant.services import ai_service
                ai_service._get_client()
            self.assertIn("AI_API_KEY", str(ctx.exception))

    def test_4_parse_json_strips_markdown_fences(self):
        """_parse_json_response handles ```json ... ``` wrappers from the model."""
        raw = '```json\n{"key": "value"}\n```'
        result = _parse_json_response(raw)
        self.assertEqual(result, {"key": "value"})

    def test_4b_parse_json_raises_on_garbage(self):
        """_parse_json_response raises AIServiceError on non-JSON input."""
        with self.assertRaises(AIServiceError):
            _parse_json_response("This is not JSON at all.")


# ─────────────────────────────────────────────────────────────────────────────
# 5–9  Chat view
# ─────────────────────────────────────────────────────────────────────────────

class ChatViewTests(TestCase):

    def setUp(self):
        self.user = _make_user("bob")
        self.url  = reverse("ai_assistant:chat")

    def _post(self, payload):
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_CSRFTOKEN="test",
        )

    def test_5_chat_requires_login(self):
        resp = self._post({"message": "hello"})
        self.assertEqual(resp.status_code, 302)

    def test_6_chat_rejects_empty_message(self):
        _login(self.client, self.user)
        resp = self._post({"message": ""})
        data = resp.json()
        self.assertEqual(data["status"], "error")

    def test_7_chat_rejects_oversized_message(self):
        _login(self.client, self.user)
        huge = "x" * 2000
        resp = self._post({"message": huge})
        data = resp.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("long", data["message"].lower())

    @patch("ai_assistant.views.chat_with_ai", return_value="Test AI answer.")
    def test_8_chat_success_persists_messages(self, mock_ai):
        _login(self.client, self.user)
        resp = self._post({"message": "What is a function?"})
        data = resp.json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["answer"], "Test AI answer.")

        # Both user + AI messages must be saved
        msgs = ChatMessage.objects.filter(user=self.user)
        self.assertEqual(msgs.count(), 2)
        self.assertEqual(msgs.filter(role="user").count(), 1)
        self.assertEqual(msgs.filter(role="ai").count(), 1)

    @patch("ai_assistant.views.chat_with_ai", side_effect=AIServiceError("Provider down."))
    def test_9_chat_ai_failure_returns_error_no_messages(self, mock_ai):
        _login(self.client, self.user)
        resp = self._post({"message": "What is a loop?"})
        data = resp.json()

        self.assertEqual(data["status"], "error")
        self.assertIn("Provider down", data["message"])
        # No messages should have been persisted
        self.assertEqual(ChatMessage.objects.filter(user=self.user).count(), 0)


# ─────────────────────────────────────────────────────────────────────────────
# 10–13  Summarize view
# ─────────────────────────────────────────────────────────────────────────────

class SummarizeViewTests(TestCase):

    def setUp(self):
        self.owner = _make_user("carol")
        self.other = _make_user("dave")
        cat = Category.objects.create(user=self.owner, name="Math")
        self.note = Note.objects.create(
            user=self.owner, category=cat,
            title="Calculus", content="Derivatives and integrals."
        )
        self.url = reverse("ai_assistant:summarize")

    def test_10_summarize_requires_login(self):
        resp = self.client.post(self.url, {"note_id": self.note.pk})
        self.assertEqual(resp.status_code, 302)

    def test_11_summarize_rejects_other_users_note(self):
        """User B cannot summarize User A's note."""
        _login(self.client, self.other)
        resp = self.client.post(self.url, {"note_id": self.note.pk})
        self.assertEqual(resp.status_code, 404)

    @patch("ai_assistant.views.summarize_note")
    def test_12_summarize_success_returns_expected_keys(self, mock_fn):
        mock_fn.return_value = {
            "summary": "Short summary.",
            "key_points": ["Point 1"],
            "important_terms": ["Term: def"],
        }
        _login(self.client, self.owner)
        resp = self.client.post(self.url, {"note_id": self.note.pk})
        data = resp.json()

        self.assertEqual(data["status"], "ok")
        self.assertIn("summary", data)
        self.assertIn("key_points", data)
        self.assertIn("important_terms", data)
        self.assertEqual(data["summary"], "Short summary.")

    @patch("ai_assistant.views.summarize_note", side_effect=AIServiceError("Timeout."))
    def test_13_summarize_ai_failure_returns_json_error(self, mock_fn):
        _login(self.client, self.owner)
        resp = self.client.post(self.url, {"note_id": self.note.pk})
        data = resp.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("Timeout", data["message"])


# ─────────────────────────────────────────────────────────────────────────────
# 14–15  Explain view
# ─────────────────────────────────────────────────────────────────────────────

class ExplainViewTests(TestCase):

    def setUp(self):
        self.owner = _make_user("eve")
        self.other = _make_user("frank")
        self.note  = Note.objects.create(
            user=self.owner, title="Physics",
            content="Newton's laws of motion."
        )
        self.url = reverse("ai_assistant:explain")

    @patch("ai_assistant.views.explain_note", return_value="Simple explanation here.")
    def test_14_explain_success(self, mock_fn):
        _login(self.client, self.owner)
        resp = self.client.post(
            self.url, {"note_id": self.note.pk, "style": "beginner"}
        )
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["explanation"], "Simple explanation here.")

    def test_15_explain_rejects_other_users_note(self):
        _login(self.client, self.other)
        resp = self.client.post(
            self.url, {"note_id": self.note.pk, "style": "beginner"}
        )
        self.assertEqual(resp.status_code, 404)


# ─────────────────────────────────────────────────────────────────────────────
# 16–21  AI service — quiz validation + generate_quiz view
# ─────────────────────────────────────────────────────────────────────────────

class GenerateQuizServiceTests(TestCase):
    """Unit tests for the service-layer validation logic — no HTTP."""

    def test_16_invalid_structure_raises_error(self):
        """generate_quiz raises AIServiceError if 'questions' key is missing."""
        with patch("ai_assistant.services.ai_service._call_ai",
                   return_value='{"title":"Q"}'):
            with self.assertRaises(AIServiceError):
                generate_quiz("Note", "Content", 3)

    def test_17_wrong_option_count_skips_question(self):
        """Questions with != 4 options are silently skipped; if all skipped, raises error."""
        bad_json = json.dumps({
            "title": "Quiz",
            "questions": [
                {
                    "question": "Only 2 options?",
                    "options": ["A", "B"],
                    "correct_answer": "A",
                    "explanation": "Wrong count.",
                }
            ],
        })
        with patch("ai_assistant.services.ai_service._call_ai", return_value=bad_json):
            with self.assertRaises(AIServiceError) as ctx:
                generate_quiz("Note", "Content", 1)
            self.assertIn("validation", str(ctx.exception).lower())

    def test_18_correct_answer_not_in_options_skips(self):
        """Questions where correct_answer is not in options are skipped."""
        bad_json = json.dumps({
            "title": "Quiz",
            "questions": [
                {
                    "question": "Bad answer ref?",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "Z",   # not in options
                    "explanation": "Mismatch.",
                }
            ],
        })
        with patch("ai_assistant.services.ai_service._call_ai", return_value=bad_json):
            with self.assertRaises(AIServiceError):
                generate_quiz("Note", "Content", 1)


class GenerateQuizViewTests(TestCase):

    def setUp(self):
        self.user  = _make_user("grace")
        self.other = _make_user("henry")
        self.note  = Note.objects.create(
            user=self.user, title="Python Basics",
            content="Variables, loops, functions."
        )
        self.url = reverse("ai_assistant:generate_quiz")

    @patch("ai_assistant.views.generate_quiz")
    def test_19_quiz_success_saves_quiz_and_questions(self, mock_fn):
        mock_fn.return_value = {
            "title": "Python Quiz",
            "questions": [
                {
                    "question": "What is a variable?",
                    "options": ["A container", "A loop", "A function", "A class"],
                    "correct_answer": "A container",
                    "explanation": "Variables store data.",
                },
            ],
        }
        _login(self.client, self.user)
        resp = self.client.post(self.url, {"note_id": self.note.pk, "count": "5"})

        # Should redirect to the new quiz detail page
        self.assertEqual(resp.status_code, 302)

        quiz = Quiz.objects.filter(user=self.user, title="Python Quiz").first()
        self.assertIsNotNone(quiz)
        self.assertEqual(quiz.questions.count(), 1)
        self.assertEqual(quiz.questions.first().correct_answer, "A container")

    def test_20_generated_quiz_belongs_to_requesting_user(self):
        """Quiz is assigned to the logged-in user, not the note owner."""
        with patch("ai_assistant.views.generate_quiz") as mock_fn:
            mock_fn.return_value = {
                "title": "Ownership Quiz",
                "questions": [
                    {
                        "question": "Q?",
                        "options": ["1", "2", "3", "4"],
                        "correct_answer": "1",
                        "explanation": "Because.",
                    }
                ],
            }
            _login(self.client, self.user)
            self.client.post(self.url, {"note_id": self.note.pk, "count": "5"})

        quiz = Quiz.objects.filter(title="Ownership Quiz").first()
        self.assertEqual(quiz.user, self.user)

    @patch("ai_assistant.views.generate_quiz",
           side_effect=AIServiceError("AI unavailable."))
    def test_21_quiz_ai_failure_no_quiz_saved(self, mock_fn):
        _login(self.client, self.user)
        quiz_count_before = Quiz.objects.count()
        self.client.post(self.url, {"note_id": self.note.pk, "count": "5"})
        self.assertEqual(Quiz.objects.count(), quiz_count_before)


# ─────────────────────────────────────────────────────────────────────────────
# 22–25  Generate Flashcards
# ─────────────────────────────────────────────────────────────────────────────

class GenerateFlashcardsServiceTests(TestCase):

    def test_25_malformed_flashcard_response_raises(self):
        """generate_flashcards raises AIServiceError when 'flashcards' key is absent."""
        with patch("ai_assistant.services.ai_service._call_ai",
                   return_value='{"wrong_key": []}'):
            with self.assertRaises(AIServiceError):
                generate_flashcards("Title", "Content", 3)


class GenerateFlashcardsViewTests(TestCase):

    def setUp(self):
        self.user  = _make_user("iris")
        self.other = _make_user("james")
        self.note  = Note.objects.create(
            user=self.user, title="Biology",
            content="Cell structure and DNA."
        )
        self.url = reverse("ai_assistant:generate_flashcards")

    @patch("ai_assistant.views.generate_flashcards")
    def test_22_flashcards_success_saves_records(self, mock_fn):
        mock_fn.return_value = [
            {"front": "What is a cell?",  "back": "The basic unit of life."},
            {"front": "What is DNA?",     "back": "Genetic material."},
        ]
        _login(self.client, self.user)
        resp = self.client.post(self.url, {"note_id": self.note.pk, "count": "5"})

        self.assertEqual(resp.status_code, 302)
        cards = Flashcard.objects.filter(user=self.user, source_note=self.note)
        self.assertEqual(cards.count(), 2)

    def test_23_generated_flashcards_belong_to_requesting_user(self):
        with patch("ai_assistant.views.generate_flashcards") as mock_fn:
            mock_fn.return_value = [
                {"front": "Q", "back": "A"},
            ]
            _login(self.client, self.user)
            self.client.post(self.url, {"note_id": self.note.pk, "count": "5"})

        card = Flashcard.objects.filter(source_note=self.note).first()
        self.assertEqual(card.user, self.user)

    @patch("ai_assistant.views.generate_flashcards",
           side_effect=AIServiceError("Rate limited."))
    def test_24_flashcard_ai_failure_no_cards_saved(self, mock_fn):
        _login(self.client, self.user)
        count_before = Flashcard.objects.count()
        self.client.post(self.url, {"note_id": self.note.pk, "count": "5"})
        self.assertEqual(Flashcard.objects.count(), count_before)


# ─────────────────────────────────────────────────────────────────────────────
# 26–28  Recommendation view
# ─────────────────────────────────────────────────────────────────────────────

class RecommendViewTests(TestCase):

    def setUp(self):
        self.user  = _make_user("kate")
        self.other = _make_user("leo")
        self.url   = reverse("ai_assistant:recommend")

    def test_26_recommend_requires_login(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 302)

    @patch("ai_assistant.views.get_study_recommendation")
    @patch("ai_assistant.views.build_study_data_for_user")
    def test_27_recommend_returns_json_with_recommendations(self, mock_build, mock_rec):
        mock_build.return_value = {}
        mock_rec.return_value   = {
            "recommendations": [
                {"subject": "Math", "activity": "Practice problems",
                 "duration_minutes": 30, "reason": "Low quiz score."}
            ],
            "overall_tip": "Keep going!",
        }
        _login(self.client, self.user)
        resp = self.client.post(self.url)
        data = resp.json()

        self.assertEqual(data["status"], "ok")
        self.assertIn("recommendations", data)
        self.assertEqual(len(data["recommendations"]), 1)
        self.assertIn("overall_tip", data)

    @patch("ai_assistant.views.get_study_recommendation")
    @patch("ai_assistant.views.build_study_data_for_user")
    def test_28_recommendation_data_isolation(self, mock_build, mock_rec):
        """
        build_study_data_for_user must be called with the requesting user,
        not any other user object.
        """
        mock_build.return_value = {}
        mock_rec.return_value   = {"recommendations": [], "overall_tip": ""}

        _login(self.client, self.user)
        self.client.post(self.url)

        # The function must have been called exactly once with self.user
        mock_build.assert_called_once_with(self.user)


# ─────────────────────────────────────────────────────────────────────────────
# 29  Chat history isolation
# ─────────────────────────────────────────────────────────────────────────────

class ChatHistoryIsolationTests(TestCase):

    def setUp(self):
        self.alice = _make_user("alice2")
        self.bob   = _make_user("bob2")
        # Seed Alice's chat messages
        ChatMessage.objects.create(user=self.alice, role="user",    content="Alice question")
        ChatMessage.objects.create(user=self.alice, role="ai",      content="Alice answer")
        # Seed Bob's chat messages
        ChatMessage.objects.create(user=self.bob,   role="user",    content="Bob question")

    def test_29_user_cannot_see_other_users_chat_history(self):
        """
        Bob's session on the AI index page must only expose Bob's messages
        in context, never Alice's.
        """
        _login(self.client, self.bob)
        resp = self.client.get(reverse("ai_assistant:index"))
        self.assertEqual(resp.status_code, 200)

        chat_history = resp.context["chat_history"]
        for msg in chat_history:
            self.assertEqual(msg.user, self.bob,
                             f"Expected Bob's message but got user={msg.user}")


# ─────────────────────────────────────────────────────────────────────────────
# 30–31  Dashboard recommendation endpoint
# ─────────────────────────────────────────────────────────────────────────────

class DashboardRecommendationTests(TestCase):

    def setUp(self):
        self.user = _make_user("mia")
        self.url  = reverse("ai_assistant:dashboard_recommendation")

    def test_30_dashboard_rec_requires_login(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)

    @patch("ai_assistant.views.get_study_recommendation")
    @patch("ai_assistant.views.build_study_data_for_user")
    def test_31_dashboard_rec_returns_widget_text(self, mock_build, mock_rec):
        mock_build.return_value = {}
        mock_rec.return_value   = {
            "recommendations": [
                {"subject": "Chemistry", "activity": "Review notes",
                 "duration_minutes": 40, "reason": "Upcoming deadline."}
            ],
            "overall_tip": "Stay consistent!",
        }
        _login(self.client, self.user)
        resp = self.client.get(self.url)
        data = resp.json()

        self.assertIn("widget_text", data)
        self.assertIn("recommendations", data)
        self.assertIn("overall_tip", data)
        # widget_text should mention the subject
        self.assertIn("Chemistry", data["widget_text"])


# ─────────────────────────────────────────────────────────────────────────────
# 32  Clear chat
# ─────────────────────────────────────────────────────────────────────────────

class ClearChatTests(TestCase):

    def setUp(self):
        self.alice = _make_user("alice3")
        self.bob   = _make_user("bob3")
        ChatMessage.objects.create(user=self.alice, role="user", content="Q")
        ChatMessage.objects.create(user=self.alice, role="ai",   content="A")
        ChatMessage.objects.create(user=self.bob,   role="user", content="Bob Q")
        self.url = reverse("ai_assistant:clear_chat")

    def test_32_clear_chat_deletes_only_current_users_messages(self):
        _login(self.client, self.alice)
        resp = self.client.post(self.url)

        self.assertRedirects(resp, reverse("ai_assistant:index"))
        # Alice's messages gone
        self.assertEqual(ChatMessage.objects.filter(user=self.alice).count(), 0)
        # Bob's message untouched
        self.assertEqual(ChatMessage.objects.filter(user=self.bob).count(), 1)
