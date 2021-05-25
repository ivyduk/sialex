# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext


def activar_plantillas(modeladmin, request, queryset):
    """
    Mark the given survey as published
    """
    count = queryset.update(is_published=True)
    message = ungettext(
        "%(count)d plantilla fue activada de manera satisfactoria.",
        "%(count)d plantillas fueron activadas de manera satisfactoria.",
        count,
    ) % {"count": count}
    modeladmin.message_user(request, message)
    activar_plantillas.short_description = _("Marca las plantillas como activas")
