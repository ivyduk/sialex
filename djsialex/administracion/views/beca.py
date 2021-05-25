from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from administracion.forms.becaForms import TipoBecaForm
from administracion.models import Profile, Matricula, Idioma, Nivel, Beca, TipoBeca
from datetime import datetime

from administracion.views import BusquedaGenerica

@login_required
def escogerOpcionAdministrarBeca(request):
    return render(request, 'administracion/beca/beca_opciones.html')

@login_required
def mostrarCampoBusqueda(request):
    return render(request, 'administracion/beca/buscar_estudiantes.html')

def calcularEdad(fechaNacimiento):

    fechaNacimiento = datetime.strptime(str(fechaNacimiento), "%Y-%m-%d")
    now = datetime.now()
    diferencia = now - fechaNacimiento

    return int((diferencia.days + diferencia.seconds/86400.0) / 365.2425)

@login_required
def borrarBeca(request,beca):
    try:
        beca_encontrada = Beca.objects.get(pk=beca)
    except Beca.DoesNotExist:
        beca_encontrada = None
    context = {}

    if request.method == 'GET':

        if beca_encontrada:
            if beca_encontrada.estado_beca in [2,3]:  #Pendiente (Pendiente (en preinscripcion) o Aplicada (en formalizacion)
                messages.add_message(request, messages.WARNING,
                                     'Esta beca no puede ser borrada porque ya fue validada durante preinscripción o formalización')
                return redirect('becados')

            context = {'beca': beca_encontrada}

        return render(request, 'administracion/beca/beca_delete_confirm.html', context)

    elif request.method == 'POST':

        beca_encontrada.delete()
        messages.add_message(request, messages.SUCCESS, 'Se ha borrado la beca exitosamente')
        return redirect('becados')

    return render(request, 'administracion/beca/estudiantes_beca_list.html')

def getNiveles(persona):

    idiomas = Idioma.objects.all()
    grupo_estudiante = Group.objects.get(name='Estudiante')
    niveles = []
    es_estudiante = False

    if grupo_estudiante in persona.usuario.groups.all():
        es_estudiante = True
        for idioma in idiomas:
            matriculas = Matricula.objects.filter(estudiante=persona, grupo__horarioCurso__curso__nivel__idioma=idioma,
                                                  estado_matricula__in=[2,9])  # Aprobado, Aprobado - Pendiente en formalizacion
            if matriculas:
                nivel_maximo_aprobado = matriculas.values('grupo__horarioCurso__curso__nivel').annotate(
                    max=Max('grupo__horarioCurso__curso__nivel__orden'))
                try:
                    nivel_maximo_aprobado = Nivel.objects.get(
                        pk=nivel_maximo_aprobado[0]['grupo__horarioCurso__curso__nivel'])
                except Nivel.DoesNotExist:
                    nivel_maximo_aprobado = None
                try:
                    nivel_posterior = Nivel.objects.filter(predecesor=nivel_maximo_aprobado).all()
                except Nivel.DoesNotExist:
                    nivel_posterior = None

            else:
                fecha_nacimiento = persona.fecha_nacimiento
                edad_persona = calcularEdad(fecha_nacimiento)
                nivel_posterior = Nivel.objects.filter(idioma=idioma, activo=True, orden=1, edad_minima__lte=edad_persona, edad_maxima__gt=edad_persona).all()
            if nivel_posterior:
                for nivel in nivel_posterior:
                    niveles.append(nivel)
    return es_estudiante, niveles

@login_required
def actualizarBeca(request, beca):

    try:
        beca_encontrada = Beca.objects.get(pk=beca)
    except Beca.DoesNotExist:
        beca_encontrada = None
    context = {}

    if request.method == 'GET':

        if beca_encontrada:
            if beca_encontrada.estado_beca == 3: #Aplicada (en formalizacion)
                messages.add_message(request, messages.WARNING,
                                     'La persona que escogió NO puede ser modificada porque la beca ya fue validada durante la formalización')
                return redirect('beca-opciones')

            es_estudiante, niveles = getNiveles(beca_encontrada.beneficiario)
            niveles_seleccionados = beca_encontrada.nivel_idioma.all()

            context = {'estudiante': beca_encontrada.beneficiario, 'niveles': niveles,
                       'tipos_beca': TipoBeca.objects.all(), 'es_estudiante': es_estudiante,
                       'niveles_seleccionados': niveles_seleccionados,
                       'tipo_beca_seleccionada': beca_encontrada.tipo_beca}

        return render(request, 'administracion/beca/seleccionar_nivel.html', context)

    elif request.method == 'POST':

        niveles = request.POST.getlist('nivel_idioma')
        tipo_beca = request.POST['tipo_beca']
        estudiante_id = request.POST['std']

        try:
            estudiante = Profile.objects.get(pk=estudiante_id)
        except Profile.DoesNotExist:
            estudiante = None

        try:
            persona_asignadora = Profile.objects.get(usuario=request.user)
        except Profile.DoesNotExist:
            persona_asignadora = None

        try:
            tipo_beca = TipoBeca.objects.get(pk=tipo_beca)
        except TipoBeca.DoesNotExist:
            tipo_beca = None

        if estudiante and persona_asignadora and tipo_beca:

            beca_encontrada.tipo_beca = tipo_beca
            beca_encontrada.fecha_asignacion = datetime.now()
            beca_encontrada.asignada_por = persona_asignadora
            beca_encontrada.save()
            beca_encontrada.nivel_idioma.set(Nivel.objects.filter(id__in=niveles))
            beca_encontrada.save()
            messages.add_message(request, messages.SUCCESS, 'Se ha modificado la beca de tipo ' + tipo_beca.nombre +
                                 ' asignada al estudiante ' + estudiante.getNombreCompleto())
        else:
            messages.add_message(request, messages.WARNING,
                                 'Ha ocurrido un error durante la asignación de la beca, por favor inténtelo '
                                 'de nuevo')
        return redirect('becados')
    return render(request, 'administracion/beca/seleccionar_nivel.html', context)

@login_required
def nivelesBecaEstudiante(request):

    template_name = 'administracion/beca/seleccionar_nivel.html'
    context = {}
    if request.method == 'GET':
        documento = request.GET.get('q')
        if documento and documento != '':
            documento = documento.strip()
            try:
                persona = Profile.objects.get(numero_documento=documento)
            except Profile.DoesNotExist:
                persona = None

            if persona:
                es_estudiante, niveles = getNiveles(persona)
                context = {'estudiante': persona, 'niveles': niveles,
                           'tipos_beca': TipoBeca.objects.all(), 'es_estudiante': es_estudiante, 'niveles_seleccionados': []}
            else:
                messages.add_message(request, messages.WARNING,
                                     'La persona con documento ' + documento + ' no se encuentra registrada en el sistema.')
                return redirect('buscar-estudiante')

        else:
            messages.add_message(request, messages.WARNING,
                                 'Ingrese el número de documento para realizar la búsqueda')
            return redirect('buscar-estudiante')
    elif request.method == 'POST':
        niveles = request.POST.getlist('nivel_idioma')
        tipo_beca = request.POST['tipo_beca']
        estudiante_id = request.POST['std']

        try:
            estudiante = Profile.objects.get(pk=estudiante_id)
        except Profile.DoesNotExist:
            estudiante = None

        try:
            persona_asignadora = Profile.objects.get(usuario=request.user)
        except Profile.DoesNotExist:
            persona_asignadora = None

        try:
            tipo_beca = TipoBeca.objects.get(pk=tipo_beca)
        except TipoBeca.DoesNotExist:
            tipo_beca = None

        if estudiante and persona_asignadora and tipo_beca:

            beca_encontrada = Beca.objects.filter(beneficiario=estudiante, periodo_generado_id=request.session["periodo_contextualizado_id"], tipo_beca=tipo_beca)
            if not beca_encontrada:
                beca = Beca(beneficiario=estudiante, periodo_generado_id=request.session["periodo_contextualizado_id"], valor=0.0,
                        tipo_beca=tipo_beca, asignada_por=persona_asignadora, fecha_asignacion=datetime.now())
                beca.save()
                beca.nivel_idioma.set(Nivel.objects.filter(id__in=niveles))
                beca.save()
                messages.add_message(request, messages.SUCCESS, 'Se ha asignado una beca de tipo ' + tipo_beca.nombre +
                                 ' al estudiante ' + estudiante.getNombreCompleto())
            else:
                messages.add_message(request, messages.WARNING,
                                     'Una beca del mismo tipo en este periodo ya ha sido asignada para ' + estudiante.numero_documento + ' ' + estudiante.getNombreCompleto())
        else:
            messages.add_message(request, messages.WARNING, 'Ha ocurrido un error durante la asignación de la beca, por favor inténtelo '
                                                            'de nuevo')
        return redirect('becados')
    return render(request, template_name, context)


@login_required
def estudiantesBecaList(request):
    campos = ['beneficiario__tipo_documento__nombre',
              'beneficiario__numero_documento',
              'periodo_generado__alias',
              'valor',
              'tipo_beca__nombre',
              'tipo_beca__porcentaje',
              'asignada_por__primer_nombre',
              'asignada_por__segundo_nombre',
              'asignada_por__primer_apellido',
              'asignada_por__segundo_apellido',
              'nivel_idioma__nombre',
              'nivel_idioma__orden',
              'nivel_idioma__idioma__nombre',
              'fecha_asignacion',
              'estado_beca',
              ]

    busqueda_generica = BusquedaGenerica()
    object_list = Beca.objects.all()
    query_string = request.GET.get('q')

    if query_string:
        query_string = query_string.strip()
        consulta = busqueda_generica.get_query(query_string, campos)
        object_list = object_list.filter(consulta).order_by('periodo_generado','beneficiario__numero_documento').distinct()

    page = request.GET.get('page')
    paginator = Paginator(object_list, 30)
    try:
        becas = paginator.page(page)
    except PageNotAnInteger:
        becas = paginator.page(1)
    except EmptyPage:
        becas = paginator.page(paginator.num_pages)

    return render(request, 'administracion/beca/estudiantes_beca_list.html',
                  {'object_list': becas, 'total': len(object_list)})

class TipoBecaCreateView(LoginRequiredMixin,CreateView):
    form_class = TipoBecaForm
    template_name = 'administracion/beca/tipoBeca/tipo_beca_form.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class TipoBecaUpdateView(LoginRequiredMixin, UpdateView):
    model = TipoBeca
    form_class = TipoBecaForm
    template_name = 'administracion/beca/tipoBeca/tipo_beca_form.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class TipoBecaListView(LoginRequiredMixin, ListView):
    model = TipoBeca
    template_name = 'administracion/beca/tipoBeca/tipo_beca_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class TipoBecaDetailView(LoginRequiredMixin, DetailView):
    model = TipoBeca
    template_name = 'administracion/beca/tipoBeca/tipo_beca_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'