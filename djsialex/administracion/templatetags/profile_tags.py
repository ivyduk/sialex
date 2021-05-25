from django import template

from administracion.enums import ESTADOS_ACADEMICOS_MATRICULA, COHORTE

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
     return user.groups.filter(name=group_name).exists()

@register.filter
def get_type(value):
    return type(value)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def getEstadoMatricula(estado):
    for e in ESTADOS_ACADEMICOS_MATRICULA:
        if e[0] == estado:
            return e[1]

@register.filter
def getColorEstadoMatricula(estado):

    if estado in [1,2,7]: #No definida, Aprobada, En curso :
        return 1
    elif estado in [3,4,8]: #Reprobada, Cancelada, Reprobado por fallas
        return 2
    else: # Aplazada por usuario, Aplazada por departamento,
        return 3

@register.filter
def getCohorte(cohorte):

    for c in COHORTE:
        if c[0] == cohorte:
            return c[1]

@register.filter
def isMatriculaValida(estado):

    if estado in [2,3,7,8]: #Aprobado, reprobado por calificacion, en curso, reprobado por inasistencia
        return True
    return False
