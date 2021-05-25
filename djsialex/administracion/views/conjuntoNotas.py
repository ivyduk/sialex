from django.contrib import messages

from ..forms import ConjuntoNotasForm, NotaParcialFormset
from django.db import transaction, IntegrityError

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import  UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect

from ..models import ConjuntoNotas
from django.http import HttpResponseRedirect


class ConjuntoNotasCreate(LoginRequiredMixin, CreateView):
    template_name = 'administracion/conjuntoNotas/conjuntonotas_form.html'
    form_class = ConjuntoNotasForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(ConjuntoNotasCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['conjunto_notas_form'] = data['form']
            data['notas_formset'] = NotaParcialFormset(self.request.POST)
        else:
            data['conjunto_notas_form'] = self.form_class
            data['notas_formset'] = NotaParcialFormset()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        notas = context['notas_formset']
        try:
            with transaction.atomic():
                self.object = form.save(commit=False)
                if notas.is_valid():
                    suma_ponderacion = 0
                    lista_ordenes = []
                    for f in notas:
                        if f.is_valid():
                            f.save(commit=False)
                            if f['ponderacion'].value():
                                suma_ponderacion += int(f['ponderacion'].value())
                            if f['orden_nota_conjunto'].value():
                                lista_ordenes.append(int(f['orden_nota_conjunto'].value()))
                    if suma_ponderacion==100:
                        if sorted(lista_ordenes) == list(range(min(lista_ordenes), max(lista_ordenes)+1)) and min(lista_ordenes)==1:
                            self.object.save()
                            notas.instance = self.object
                            notas.save()
                            return super(ConjuntoNotasCreate, self).form_valid(form)
                        else:
                            messages.error(self.request, 'El orden de las notas debe ser consecutivo e iniciar en 1')
                            return HttpResponseRedirect(reverse('conjuntonotas_create'), {'form': form})
                    else:
                        messages.error(self.request, 'La suma de las ponderaciones de las notas debe ser 100')
                        return HttpResponseRedirect(reverse('conjuntonotas_create'), {'form': form})
                else:
                    messages.error(self.request, 'Todos Los campos son requeridos para poder actualizar las notas ')
                    return HttpResponseRedirect(reverse('conjuntonotas_create'), {'form': form})
        except IntegrityError:
            messages.error(self.request, 'Hubo un error al guardar el conjunto de notas')
            return HttpResponseRedirect(self.template_name, {'form': form})


    def get_success_url(self):
        return reverse_lazy('conjunto_notas-detail', kwargs={'pk': self.object.id})

class ConjuntoNotasUpdate(LoginRequiredMixin,UpdateView):
    model = ConjuntoNotas
    template_name = 'administracion/conjuntoNotas/conjuntonotas_form.html'
    form_class = ConjuntoNotasForm

    def get_context_data(self, **kwargs):
        data = super(ConjuntoNotasUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['conjunto_notas_form'] = data['form']
            data['notas_formset'] = NotaParcialFormset(self.request.POST, instance=self.object)
        else:
            data['conjunto_notas_form'] = data['form']
            data['notas_formset'] = NotaParcialFormset(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        notas = context['notas_formset']
        try:
            with transaction.atomic():
                self.object = form.save(commit=False)
                if notas.is_valid():
                    suma_ponderacion = 0
                    lista_ordenes = []
                    for f in notas:
                        if f.is_valid():
                            f.save(commit=False)
                            if f['ponderacion'].value():
                                suma_ponderacion += int(f['ponderacion'].value())
                            if f['orden_nota_conjunto'].value():
                                lista_ordenes.append(int(f['orden_nota_conjunto'].value()))
                    if suma_ponderacion==100:
                        if sorted(lista_ordenes) == list(range(min(lista_ordenes), max(lista_ordenes)+1)) and min(lista_ordenes)==1:
                            self.object.save()
                            notas.instance = self.object
                            notas.save()
                            return super(ConjuntoNotasUpdate, self).form_valid(form)
                        else:
                            messages.error(self.request, 'El orden de las notas debe ser consecutivo e iniciar en 1')
                            return HttpResponseRedirect(reverse('conjuntonotas_update', kwargs={'pk': self.object.id}), {'form': form})        
                    else:
                        messages.error(self.request, 'La suma de las ponderaciones de las notas debe ser 100')
                        return HttpResponseRedirect(reverse('conjuntonotas_update', kwargs={'pk': self.object.id}), {'form': form})
                else:
                    messages.error(self.request, 'Todos Los campos son requeridos para poder actualizar las notas ')
                    return HttpResponseRedirect(reverse('conjuntonotas_update', kwargs={'pk': self.object.id}), {'form': form})
                self.object.save()
        except IntegrityError:
            messages.error(self.request, 'Hubo un error al guardar el conjunto de notas')
            return redirect(reverse('conjunto_notas-detail', kwargs={'pk': self.object.id}))

    def get_success_url(self):
        return reverse_lazy('conjunto_notas-detail', kwargs={'pk': self.object.id})

class ConjuntoNotasListView(LoginRequiredMixin, generic.ListView):
    model = ConjuntoNotas
    template_name = 'administracion/conjuntoNotas/conjuntonotas_list.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'

class ConjuntoNotasDetailView(LoginRequiredMixin,generic.DetailView):
    model = ConjuntoNotas
    template_name = 'administracion/conjuntoNotas/conjuntonotas_detail.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'


class ConjuntoNotasDelete(LoginRequiredMixin,DeleteView):
    model = ConjuntoNotas
    template_name = 'administracion/conjuntoNotas/conjuntonotas_confirm_delete.html'
    success_url = reverse_lazy('conjunto-notas')