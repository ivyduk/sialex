from django.views.generic import TemplateView
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.urls import reverse

from ..models import Survey, Category,AsociarEncuesta, Encuesta, Question, Matricula
from ..forms.encuestaForms import ResponseForm, AsociacionEncuestaForm

class ConfirmView(LoginRequiredMixin, TemplateView):

    template_name = "administracion/encuesta/confirm.html"

    def get_context_data(self, **kwargs):
        context = super(ConfirmView, self).get_context_data(**kwargs)
        context["uuid"] = kwargs["uuid"]
        return context

class IndexView(LoginRequiredMixin,TemplateView):
    template_name = "administracion/encuesta/list.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        surveys = Survey.objects.filter(is_published=True, is_plantilla=True)
        context["surveys"] = surveys
        return context

class MisEncuestasView(LoginRequiredMixin, TemplateView):
    template_name = "administracion/encuesta/list.html"

    def get_context_data(self, **kwargs):
        context = super(MisEncuestasView, self).get_context_data(**kwargs)
        matriculas = Matricula.objects.filter(estudiante=self.request.user.profile)
        programas = []
        for m in matriculas:
            programas.append(m.grupo.horarioCurso.curso.oferta_academica.programa.id)
        surveys = Encuesta.objects.filter(is_published=True, is_plantilla=False, programa__id__in=programas)
        context["surveys"] = surveys
        return context

class SurveyCompleted(LoginRequiredMixin,TemplateView):

    template_name = "administracion/encuesta/completed.html"

    def get_context_data(self, **kwargs):
        context = {}
        survey = get_object_or_404(Survey, is_published=True, id=kwargs["id"])
        context["survey"] = survey
        return context

class SurveyDetail(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        survey = get_object_or_404(Survey, is_published=True, id=kwargs["id"])
        template_name = "administracion/encuesta/one_page_survey.html"
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        categories = Category.objects.filter(survey=survey).order_by("order")
        form = ResponseForm(
            survey=survey, user=request.user, step=kwargs.get("step", 0)
        )
        encuesta = Encuesta.objects.filter(id=survey.id)
        if encuesta:
            tipo = 'encuesta'
        else:
            tipo = 'plantilla'
        context = {"response_form": form, "survey": survey, "categories": categories, 'tipo' : tipo}

        return render(request, template_name, context)

    def post(self, request, *args, **kwargs):
        survey = get_object_or_404(Survey, is_published=True, id=kwargs["id"])
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        categories = Category.objects.filter(survey=survey).order_by("order")
        form = ResponseForm(
            request.POST, survey=survey, user=request.user, step=kwargs.get("step", 0)
        )
        context = {"response_form": form, "survey": survey, "categories": categories}
        if form.is_valid():
            session_key = "survey_%s" % (kwargs["id"],)
            if session_key not in request.session:
                request.session[session_key] = {}
            for key, value in list(form.cleaned_data.items()):
                request.session[session_key][key] = value
                request.session.modified = True

            next_url = form.next_step_url()
            response = None
            response = form.save()

            if next_url is not None:
                return redirect(next_url)
            else:
                del request.session[session_key]
                if response is None:
                    return redirect("/")
                else:
                    next_ = request.session.get("next", None)
                    if next_ is not None:
                        if "next" in request.session:
                            del request.session["next"]
                        return redirect(next_)
                    else:
                        return redirect(
                            "survey-confirmation", uuid=response.interview_uuid
                        )
        template_name = "administracion/encuesta/one_page_survey.html"
        return render(request, template_name, context)

class AsociarEncuestaListView(LoginRequiredMixin, generic.ListView):
    model = AsociarEncuesta
    template_name = 'administracion/asociarEncuesta/asociar_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class AsociarEncuestaCreate(LoginRequiredMixin, CreateView):
    model = AsociarEncuesta
    form_class = AsociacionEncuestaForm
    template_name = 'administracion/asociarEncuesta/asociar_form.html'
    success_url = reverse_lazy('asociaciones')

    def form_valid(self, form):
        periodo = form.cleaned_data['periodo']
        plantilla = form.cleaned_data['plantilla']
        asociar_creada = AsociarEncuesta.objects.filter(periodo=periodo, plantilla=plantilla)
        if asociar_creada:
            messages.warning(self.request, 'Ya existe asociación con esta plantilla y periodo en la base de datos')
            return redirect(reverse('asociar_create'))
        else:
            asociar = form.save()
            programas = form.cleaned_data['programas']
            for programa in programas:
                nueva_encuesta = Encuesta(name=(periodo.alias +'-'+ programa.nombre +'-'+ plantilla.name), description=plantilla.description, is_published=plantilla.is_published, is_plantilla=False, asociada=asociar, programa=programa)
                nueva_encuesta.save()
                categorias_plantilla = Category.objects.filter(survey=asociar.plantilla)
                preguntas_excluir = []
                for c in categorias_plantilla:
                    preguntas_plantilla = Question.objects.filter(category=c)
                    category = Category(name=c.name, survey=nueva_encuesta, order=c.order, description=c.description)
                    category.save()
                    for p in preguntas_plantilla:
                        nueva_pregunta = Question(text=p.text, order=p.order, required=p.required, category=category, survey=nueva_encuesta, type=p.type, choices=p.choices)
                        nueva_pregunta.save()
                        preguntas_excluir.append(p.id)
                preguntas_sin_categoria = Question.objects.filter(survey=asociar.plantilla).exclude(id__in=preguntas_excluir)
                for psc in preguntas_sin_categoria:
                    nueva_pregunta = Question(text=psc.text, order=psc.order, required=psc.required, category=psc.category,
                                              survey=nueva_encuesta, type=psc.type, choices=psc.choices)
                    nueva_pregunta.save()
        return super(AsociarEncuestaCreate, self).form_valid(form)

class AsociarEncuestaUpdate(LoginRequiredMixin, UpdateView):
    model = AsociarEncuesta
    form_class = AsociacionEncuestaForm
    template_name = 'administracion/asociarEncuesta/asociar_form.html'
    success_url = reverse_lazy('asociaciones')

    def form_valid(self, form):
        periodo = form.cleaned_data['periodo']
        plantilla = form.cleaned_data['plantilla']
        asociar_creada = AsociarEncuesta.objects.filter(periodo=periodo, plantilla=plantilla).exclude(pk=self.object.id)
        if asociar_creada:
            messages.warning(self.request, 'Ya existe asociación con esta plantilla y periodo en la base de datos')
            return redirect(reverse('asociar_update', kwargs={'pk': self.object.id}))
        else:
            programas = form.cleaned_data['programas']
            programas_previos =  self.object.programas.all()
            encuestas_programas_borrar = []
            for p in programas_previos:
                if p not in programas:
                    encuestas_programas_borrar.append(p)
            for programa in programas:
                if programa not in programas_previos:
                    nueva_encuesta = Encuesta(name=(periodo.alias + '-' + programa.nombre + '-' + plantilla.name),
                                              description=plantilla.description, is_published=plantilla.is_published,
                                              is_plantilla=False, asociada=self.object, programa=programa)
                    nueva_encuesta.save()
                    categorias_plantilla = Category.objects.filter(survey=self.object.plantilla)
                    preguntas_excluir = []
                    for c in categorias_plantilla:
                        preguntas_plantilla = Question.objects.filter(category=c)
                        category = Category(name=c.name, survey=nueva_encuesta, order=c.order,
                                            description=c.description)
                        category.save()
                        for p in preguntas_plantilla:
                            nueva_pregunta = Question(text=p.text, order=p.order, required=p.required,
                                                      category=category, survey=nueva_encuesta, type=p.type,
                                                      choices=p.choices)
                            nueva_pregunta.save()
                            preguntas_excluir.append(p.id)
                    preguntas_sin_categoria = Question.objects.filter(survey=self.object.plantilla).exclude(
                        id__in=preguntas_excluir)
                    for psc in preguntas_sin_categoria:
                        nueva_pregunta = Question(text=psc.text, order=psc.order, required=psc.required,
                                                  category=psc.category,
                                                  survey=nueva_encuesta, type=psc.type, choices=psc.choices)
                        nueva_pregunta.save()
            for pb in encuestas_programas_borrar:
                Encuesta.objects.filter(programa=pb).delete()
        return super(AsociarEncuestaUpdate, self).form_valid(form)


class OfertaAcademicaDelete(LoginRequiredMixin, DeleteView):
    model = AsociarEncuesta
    template_name = 'administracion/asociarEncuesta/asociar_confirm_delete.html'
    success_url = reverse_lazy('asociaciones')
