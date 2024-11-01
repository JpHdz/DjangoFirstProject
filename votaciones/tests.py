import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Question, Choice
from django.urls import reverse
# Create your tests here.

class QuestionModelTests(TestCase):
  def test_was_bulished_recently_with_future_question(self):
    time = timezone.now() + datetime.timedelta(days=30)
    future_question = Question(pub_date=time)
    self.assertIs(future_question.was_published_recently(),False)
    
  def test_was_published_recently_with_old_question(self):
    """
    was_published_recently() returns False for questions whose pub_date
    is older than 1 day.
    """
    time = timezone.now() - datetime.timedelta(days=1, seconds=1)
    old_question = Question(pub_date=time)
    self.assertIs(old_question.was_published_recently(), False)


  def test_was_published_recently_with_recent_question(self):
      """
      was_published_recently() returns True for questions whose pub_date
      is within the last day.
      """
      time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
      recent_question = Question(pub_date=time)
      self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("votaciones:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No hay votaciones disponibles.")
        self.assertListEqual(list(response.context["latest_question_list"]), [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("votaciones:index"))
        self.assertListEqual(list(
            response.context["latest_question_list"]),
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("votaciones:index"))
        self.assertContains(response, "No hay votaciones disponibles.")
        self.assertListEqual(list(response.context["latest_question_list"]), [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("votaciones:index"))
        self.assertListEqual(list(
            response.context["latest_question_list"]),
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("votaciones:index"))
        self.assertListEqual(
            list(response.context["latest_question_list"]),
            [question2, question1],
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("votaciones:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("votaciones:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
        


# class RespuestaModelTest(TestCase):
#     def test_future_question(self):
#         """
#         The detail view of a question with a pub_date in the future
#         returns a 404 not found.
#         """
#         future_question = create_question(question_text="Future question.", days=5)
#         url = reverse("votaciones:detail", args=(future_question.id,))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 404)

#         with self.assertRaises(Question.DoesNotExist):
#             Question.objects.get(pk=future_question.id)

#         with self.assertRaises(Question.DoesNotExist):
#             Question.objects.get(pk=future_question.id)


class RespuestaModelTest(TestCase):
    def test_crear_respuesta_para_pregunta(self):
        pregunta = Question(question_text="¿Te gusta viajar?", pub_date = timezone.now())
        pregunta.save()
        respuesta = Choice(question=pregunta, choice_text="Si", votes=0)
        respuesta.save()
        self.assertEqual(respuesta.question, pregunta)

    def test_eliminar_pregunta_con_sus_respuestas(self):
        pregunta = Question(question_text="What's up?", pub_date = timezone.now())
        pregunta.save()
        respuesta = Choice(question=pregunta, choice_text="Good", votes=0)
        respuesta.save()
        pregunta_id = pregunta.id
        respuesta_id = respuesta.id
        pregunta.delete()

        with self.assertRaises(Question.DoesNotExist):
            Question.objects.get(pk=pregunta_id)

        with self.assertRaises(Choice.DoesNotExist):
            Choice.objects.get(pk=respuesta_id)