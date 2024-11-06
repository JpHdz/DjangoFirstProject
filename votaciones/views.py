from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from .models import Question, Choice
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required


class IndexView(generic.ListView):
   template_name = "votaciones/index.html"
   context_object_name = "latest_question_list"

   def get_queryset(self):
      return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]
      # return []
      # return Question.objects.order_by("-pub_date")[:5]

class DetailView(generic.DetailView):
   model = Question
   template_name = "votaciones/detail.html"
   def get_queryset(self):
       return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
   model = Question
   template_name = "votaciones/results.html"
   
@login_required
def vote(request, pregunta_id):
    pregunta = get_object_or_404(Question, pk=pregunta_id)
    try:
        respuesta_seleccionada = pregunta.respuesta_set.get(pk=request.POST["respuesta"])
    except (KeyError,Choice.DoesNotExist):
        return render(request, "votaciones/detalle.html", {"pregunta":pregunta, "error_message": "No has seleccionado una respuesta"})
    else:
        respuesta_seleccionada.votos = F("votos") + 1
        respuesta_seleccionada.save()
        return HttpResponseRedirect(reverse("votaciones:results", args=(pregunta.id,)))
    #//return HttpResponse("Estas votando en la pregunta %s" % pregunta_id)

   


# Create your views here.
def index(request):
  latest_question_list = Question.objects.order_by("-pub_date")[:5]
  # output = ", ".join([q.question_text for q in latest_question_list])
  template = loader.get_template("votaciones/index.html")
  context = {
    "latest_question_list": latest_question_list
  }
  # Render view WITHOUT shortcut 
  # return HttpResponse(template.render(context,request))
  # Render view WITH shortcut
  return render(request, "votaciones/index.html",context)

def detail(request, question_id):
  # Manage Error WITHOUT SHORTCUT
  # try:
  #   question = Question.objects.get(pk=question_id)
  # except Question.DoesNotExist:
  #   raise Http404("Question does not exist")
  # return render(request, "votaciones/detail.html",{"question": question})
  # return HttpResponse("You are looking at question %s." % question_id)
  # Manage error WITH shortcut
  question = get_object_or_404(Question,pk=question_id)
  return render(request,"votaciones/detail.html", {"question": question}) 


def results(request,question_id):
      question = get_object_or_404(Question, pk=question_id)
      return render(request, "votaciones/results.html", {"question": question})
  # response = "You're looking at the results of question %s."
  # return HttpResponse(response % question_id)

def vote(request,question_id):
  question = get_object_or_404(Question, pk=question_id)
  try:
    selected_choice = question.choice_set.get(pk=request.POST["choice"])
  except (KeyError, Choice.DoesNotExist):
    return render (request, "votaciones/detail.html", {
      "question": question,
      "error_message": "Your didnt select a choice"
    })
  else:
    selected_choice.votes = F("votes") + 1
    selected_choice.save()
    return HttpResponseRedirect(reverse("votaciones:results", args=(question.id,)))
  # return HttpResponse("You're voting on question %s." % question_id)


