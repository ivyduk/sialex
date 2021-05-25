from bootstrap_modal_forms.generic import BSModalUpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from administracion.forms.observacionMatriculaForms import ObservacionMatriculaForm, ObservacionMatriculaUpdateForm
from administracion.models import Matricula, Profile, FallaAsistencia, Observacion

from datetime import datetime

class ObservacionMatriculaCreateView(LoginRequiredMixin, CreateView):

    template_name = 'administracion/calificacionesCurso/observacion_matricula_form.html'
    form_class = ObservacionMatriculaForm
    matricula = None

    def get(self, request, *args, **kwargs):

        data = {}
        form = ObservacionMatriculaForm()
        self.matricula = Matricula.objects.get(id=kwargs['matricula'])

        context = {'form': form, 'matricula': self.matricula}
        data['html_form'] = render_to_string(self.template_name, context, request=request)
        return JsonResponse(data)

    def form_valid(self, form, **kwargs):

        matricula_encontrada = Matricula.objects.get(id=self.kwargs['matricula'])
        self.object = form.save(commit=False)
        self.object.persona_asignadora = Profile.objects.get(usuario = self.request.user)
        self.object.matricula = matricula_encontrada
        self.object.fecha_actualizacion = datetime.now()
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('mis-estudiantes', kwargs={'grupoacademico': self.object.matricula.grupo.id})

class ObservacionMatriculaListView(LoginRequiredMixin, ListView):

    template_name = 'administracion/calificacionesCurso/observacion_matricula_list.html'
    matricula = None

    def get(self, request, *args, **kwargs):

        self.matricula = Matricula.objects.get(id=kwargs['matricula'])
        docentes_grupo = self.matricula.grupo.docentesgrupoacademico_set.all()
        docentes = {}
        for docente_grupo in docentes_grupo:
            if docente_grupo not in docentes:
                docentes[docente_grupo.docente.persona] = docente_grupo.tipo_docente
        observaciones = Observacion.objects.filter(matricula=self.matricula).order_by('cohorte', 'fecha_actualizacion').all()
        context = {'observaciones': observaciones, 'matricula': self.matricula, 'docentes': docentes}

        return render(self.request, self.template_name, context)

class ObservacionMatriculaUpdateView(LoginRequiredMixin,BSModalUpdateView):
    model = Observacion
    template_name = 'administracion/calificacionesCurso/observacion_matricula_update.html'
    form_class = ObservacionMatriculaUpdateForm
    success_message = 'Registro de observación actualizados'

    def get_success_url(self):
        return reverse_lazy('observacion_matricula_list', kwargs={'matricula': self.object.matricula.id})

    def form_valid(self, form):
        self.object.fecha_actualizacion = datetime.now()
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

@login_required
def eliminarObservacionMatricula(request, observacion):

    matricula_asociada = None
    try:
        observacion_obj = Observacion.objects.get(pk=observacion)
    except Observacion.DoesNotExist:
        observacion_obj = None

    if observacion_obj:
        matricula_asociada = observacion_obj.matricula
        observacion_obj.delete()

    return redirect('observacion_matricula_list', matricula=matricula_asociada.id)


