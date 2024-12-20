
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden


from administracion.models import Periodo


@receiver(user_logged_in, sender=User)
def sig_user_logged_in(sender, user, request, **kwargs):
    if not request.POST._mutable:
        request.POST._mutable = True
    periodo = Periodo.objects.filter(activo=True, finalizado=False).order_by('fecha_final').last()
    if periodo:
        request.session["periodo_contextualizado"] = periodo.nombre
        request.session["periodo_contextualizado_id"] = str(periodo.id)
    else:
        return HttpResponseForbidden("You are not allowed to use this profile.")


class FilterLoginMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):

        if(request.path_info=="/acceso/login/"):
            myDict = dict(request.POST)
            if 'numero_documento' in myDict.keys():
                if not request.POST._mutable:
                    request.POST._mutable = True
                request.POST['username'] = myDict['numero_documento'][0]






