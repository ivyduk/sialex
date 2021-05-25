from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from ..models import ContenidoNivelVersion

@login_required
def showContentFile(request, id):
    data = get_object_or_404(ContenidoNivelVersion,pk=id)
    with open("media/"+str(data.documento), 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=programa-academico-'+str(data).upper()+'.pdf'
        return response
    pdf.closed