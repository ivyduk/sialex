from bootstrap_modal_forms.generic import BSModalUpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView

from administracion.forms.fallaAsistenciaForm import FallaAsistenciaForm, FallaAsistenciaUpdateForm
from administracion.models import Matricula, Profile, FallaAsistencia

def actualizarNumeroFallas(matricula_encontrada):

    fallas = FallaAsistencia.objects.filter(matricula=matricula_encontrada).aggregate(Sum('cantidad_fallas'))
    total_fallas = fallas['cantidad_fallas__sum']
    fallas_maximas_nivel = matricula_encontrada.grupo.horarioCurso.curso.nivel.fallas_maximas

    if total_fallas:
        matricula_encontrada.total_fallas = total_fallas
    else:
        matricula_encontrada.total_fallas = 0

    if matricula_encontrada.total_fallas > fallas_maximas_nivel:
        matricula_encontrada.estado_matricula = 8  # Reprobado por fallas

    matricula_encontrada.save()

class FallaAsistenciaCreateView(LoginRequiredMixin, CreateView):

    template_name = 'administracion/calificacionesCurso/falla_asistencia_form.html'
    form_class = FallaAsistenciaForm
    matricula = None

    def get(self, request, *args, **kwargs):

        data = {}
        form = FallaAsistenciaForm()
        self.matricula = Matricula.objects.get(id=kwargs['matricula'])

        context = {'form': form, 'matricula': self.matricula}
        data['html_form'] = render_to_string(self.template_name, context, request=request)
        return JsonResponse(data)

    def form_valid(self, form, **kwargs):

        matricula_encontrada = Matricula.objects.get(id=self.kwargs['matricula'])

        self.object = form.save(commit=False)
        self.object.persona_asignadora = Profile.objects.get(usuario = self.request.user)
        self.object.matricula = matricula_encontrada
        self.object.save()

        actualizarNumeroFallas(matricula_encontrada)

        return HttpResponseRedirect(self.get_success_url())


    def get_success_url(self):
        return reverse_lazy('mis-estudiantes', kwargs={'grupoacademico': self.object.matricula.grupo.id})

class FallaAsistenciaListView(LoginRequiredMixin, CreateView):

    template_name = 'administracion/calificacionesCurso/falla_asistencia_list.html'
    matricula = None

    def get(self, request, *args, **kwargs):

        self.matricula = Matricula.objects.get(id=kwargs['matricula'])
        inasistencias = FallaAsistencia.objects.filter(matricula=self.matricula).all()
        docentes_grupo = self.matricula.grupo.docentesgrupoacademico_set.all()
        docentes = {}
        for docente_grupo in docentes_grupo:
            if docente_grupo not in docentes:
                docentes[docente_grupo.docente.persona] = docente_grupo.tipo_docente

        context = {'inasistencias': inasistencias, 'matricula': self.matricula, 'docentes': docentes}

        return render(self.request, self.template_name, context)

class FallaAsistenciaUpdateView(LoginRequiredMixin,BSModalUpdateView):
    model = FallaAsistencia
    template_name = 'administracion/calificacionesCurso/falla_asistencia_update.html'
    form_class = FallaAsistenciaUpdateForm
    success_message = 'Datos de inasistencia actualizados'

    def get_success_url(self):
        return reverse_lazy('falla_asistencia_list', kwargs={'matricula': self.object.matricula.id})

    def form_valid(self, form):

        self.object = form.save()
        actualizarNumeroFallas(Matricula.objects.get(pk=self.object.matricula.id))

        return HttpResponseRedirect(self.get_success_url())

@login_required
def eliminarFallaAsistencia(request, falla):

    matricula_asociada = None
    try:
        falla = FallaAsistencia.objects.get(pk=falla)
    except FallaAsistencia.DoesNotExist:
        falla = None

    if falla:
        matricula_asociada = falla.matricula
        falla.delete()
        actualizarNumeroFallas(matricula_asociada)

    return redirect('falla_asistencia_list', matricula=matricula_asociada.id)




