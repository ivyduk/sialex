from urllib.parse import urlparse # for python 3
from .models import Url,EventoPeriodo, Periodo, InformacionPreinscripcionFormalizacion
from datetime import datetime
from django.db.models import Q

now = datetime.now()


def evento_permiso(request):
    urls_objetos = ['/docente/cursos/mis-estudiantes']
    available = True
    periodo_nulo = False
    if "periodo_contextualizado_id" in request.session:
        periodo = request.session["periodo_contextualizado_id"]
    else:
        periodo = None
        periodo_nulo = True

    FULL_URL_WITH_QUERY_STRING = request.build_absolute_uri()
    parsed_url = urlparse(FULL_URL_WITH_QUERY_STRING)
    current_url = parsed_url.path

    for i in urls_objetos:
        if i in current_url:
            current_url = i
    #get url by name
    u = Url.objects.filter(url_path=current_url)

    if u and periodo:
        #si url tiene eventos traer lista eventos id
        url = u[0]
        eventos = url.eventos.all()
        #para cada evento buscar si hay evento periodo fuera de la fecha actual en evento periodo
        for ev in eventos:
            a = EventoPeriodo.objects.filter(Q(fecha_final__lt=now) | Q(fecha_inicio__gt=now), evento=ev,
                                             periodo=Periodo.objects.get(pk=periodo))
            if a:
                available = False
                global_data = {'url': current_url, "full": FULL_URL_WITH_QUERY_STRING, 'available' : available, 'periodo_nulo' : periodo_nulo}
                return {'FULL_DATA': global_data}
    global_data = {
        'url': current_url, "full" : FULL_URL_WITH_QUERY_STRING, 'available' : available, 'periodo_nulo' : periodo_nulo}
    return {'FULL_DATA': global_data}


#def mensaje_formalizacion(request):
#    return {'mensaje_formalizacion': InformacionPreinscripcionFormalizacion.load()}