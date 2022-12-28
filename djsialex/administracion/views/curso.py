from django.contrib import messages

from ..forms.cursoForms import CursoModelForm, HorarioCursoFormset
from ..models import Curso, Periodo, OfertaAcademica
from django.db import transaction, IntegrityError

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import  UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect


class CursoCreate(LoginRequiredMixin, CreateView):
    model = Curso
    template_name = 'administracion/curso/curso_horarios_form.html'
    form_class = CursoModelForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(CursoCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['cursoForm'] = data['form']
            data['formset'] = HorarioCursoFormset(self.request.POST)
        else:
            data['cursoForm'] = self.form_class
            data['formset'] = HorarioCursoFormset()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        horarioscursos = context['formset']
        if len(horarioscursos.forms) == 1 and horarioscursos.forms[0].has_changed() == False:
            messages.warning(self.request, 'Se requiere al menos un horario para la creación del curso')
            return redirect(reverse('curso_create'))
        elif horarioscursos.forms[0].has_changed()==True and 'DELETE' in horarioscursos.forms[0].changed_data:
            messages.warning(self.request, 'Se requiere al menos un horario para la creación del curso')
            return redirect(reverse('curso_create'))
        else:
            try:
                with transaction.atomic():
                    self.object = form.save()
                    if horarioscursos.is_valid():
                        for f in horarioscursos:
                            if f.is_valid():
                                horariocurso = f.save(commit=False)
                                horariocurso.cupo_disponible = horariocurso.cupo_inicial
                                horariocurso.cupo_disponible_autorizados = horariocurso.cupo_autorizados
                        horarioscursos.instance = self.object
                        horarioscursos.save()
                        return super(CursoCreate, self).form_valid(form)
                    else:
                        return redirect(reverse('curso_create'))
            except IntegrityError:
                messages.warning(self.request, 'Hubo un error al guardar el curso, revise que no exista el curso y que los campos estén correctamente diligenciados')
                return redirect(reverse('curso_create'))
    def get_success_url(self):
        return reverse_lazy('curso-detail', kwargs={'pk': self.object.id})


class CursoUpdate(LoginRequiredMixin, UpdateView):
    model = Curso
    template_name = 'administracion/curso/curso_horarios_form.html'
    form_class = CursoModelForm

    def get_form_kwargs(self):
        kwargs = super(CursoUpdate, self).get_form_kwargs()
        kwargs['periodo_contextualizado_id'] = self.request.session["periodo_contextualizado_id"]
        return kwargs

    def get_context_data(self, **kwargs):
        data = super(CursoUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['cursoForm'] = data['form']
            data['formset'] = HorarioCursoFormset(self.request.POST, instance=self.object)
        else:
            data['cursoForm'] = data['form']
            data['formset'] = HorarioCursoFormset(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        horarioscursos = context['formset']
        if len(horarioscursos.forms) == 1 and horarioscursos.forms[0].has_changed() == False:
            messages.warning(self.request, 'Se requiere al menos un horario para la actualización del curso')
            return redirect(reverse('curso_update', kwargs={'pk': self.object.id}))
        elif horarioscursos.forms[0].has_changed() == True and 'DELETE' in horarioscursos.forms[0].changed_data:
            messages.warning(self.request, 'Se requiere al menos un horario para la actualización del curso')
            return redirect(reverse('curso_update', kwargs={'pk': self.object.id}))
        else:
            try:
                with transaction.atomic():
                    self.object = form.save()
                    if horarioscursos.is_valid():
                        for f in horarioscursos:
                            if f.is_valid():
                                horariocurso = f.save(commit=False)
                                horariocurso.cupo_disponible = horariocurso.cupo_inicial
                                horariocurso.cupo_disponible_autorizados = horariocurso.cupo_autorizados
                        horarioscursos.instance = self.object
                        horarioscursos.save()
                        return super(CursoUpdate, self).form_valid(form)
                    else:
                        return redirect(reverse('curso_update', kwargs={'pk': self.object.id}))
            except IntegrityError:
                messages.warning(self.request, 'Hubo un error al guardar el curso, revise que no exista el curso y que los campos estén correctamente diligenciados')
                return redirect(reverse('curso_update', kwargs={'pk': self.object.id}))

    def get_success_url(self):
        return reverse_lazy('curso-detail', kwargs={'pk': self.object.id})


class CursoListView(LoginRequiredMixin, generic.ListView):
    model = Curso
    template_name = 'administracion/curso/curso_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        periodo_id = self.request.session["periodo_contextualizado_id"]
        curso_list = []
        try:
            periodo = Periodo.objects.get(pk=periodo_id)
        except Periodo.DoesNotExist:
            periodo = None
        ofertas = OfertaAcademica.objects.filter(periodo=periodo)
        if periodo:
            curso_list = Curso.objects.filter(oferta_academica__in=ofertas).order_by('nivel__idioma__nombre', 'nivel__orden')
        return curso_list

class CursoDetailView(LoginRequiredMixin,generic.DetailView):
    model = Curso
    template_name = 'administracion/curso/curso_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'


class CursoDelete(LoginRequiredMixin, DeleteView):
    model = Curso
    template_name = 'administracion/curso/curso_confirm_delete.html'
    success_url = reverse_lazy('cursos')