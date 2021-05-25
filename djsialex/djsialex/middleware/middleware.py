import hashlib

from django.http import HttpResponse


class FilterLoginMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):

        if(request.path_info=="/acceso/login/"):
            myDict = dict(request.POST)
            if 'periodo' in myDict.keys():
                if not request.POST._mutable:
                    request.POST._mutable = True
                request.POST['username'] =  myDict['numero_documento'][0]
                request.session["periodo_contextualizado_id"] = myDict['periodo'][0]






