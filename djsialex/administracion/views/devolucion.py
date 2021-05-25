from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect,render
from django.views import generic

from ..models import SaldoAFavor, Profile, Periodo, Devolucion, ReservasSaldo

from ..forms.devolucionForms import DevolucionForm

class BuscarSaldosView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'administracion/devolucion/buscar_saldos.html'

class SaldosAFavorPersonaView(LoginRequiredMixin, generic.ListView):
    model = SaldoAFavor
    template_name = 'administracion/devolucion/saldos_a_favor.html'
    login_url = '/acceso/login'
    redirect_field_name = 'redirect_to'
    persona = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona'] = self.persona
        if self.persona:
            context['usuario'] = True
        else:
            context['usuario'] = False
        return context

    def get_queryset(self):
        periodo_id = self.request.session["periodo_contextualizado_id"]
        query = self.request.GET.get('q')
        try:
            persona = Profile.objects.get(numero_documento=query)
        except Profile.DoesNotExist:
            persona = None
        try:
            periodo = Periodo.objects.get(pk=periodo_id)
        except Periodo.DoesNotExist:
            periodo = None
        self.persona = persona
        saldos_dic = {}
        saldos_activos = SaldoAFavor.objects.filter(beneficiario=persona,activo=True, periodo_generado__inicio__gte=periodo.inicio-4)
        saldos = SaldoAFavor.objects.filter(beneficiario=persona).order_by('periodo_generado')
        devoluciones  = Devolucion.objects.filter(persona=persona)
        saldos_dic['activos'] = saldos_activos
        saldos_dic['saldos'] = saldos
        saldos_dic['devoluciones'] = devoluciones
        return saldos_dic

@login_required
def devolucionView(request, pk):
    saldo = SaldoAFavor.objects.get(pk=pk)
    reservas = ReservasSaldo.objects.filter(saldo=saldo, pagado=False)
    valor_reservado = 0
    if reservas:
        for r in reservas:
            if r.valor > 0:
                valor_reservado += r.valor
    valor_disponible = saldo.valor - valor_reservado
    if request.method == 'GET':
        form = DevolucionForm()
    else:
        form = DevolucionForm(request.POST)
        if form.is_valid():
            porcentaje = request.POST['porcentaje']
            observacion = request.POST['observacion']
            saldo.activo = False
            saldo.devuelto = True
            saldo.save()
            valor_devolucion = (valor_disponible * float(porcentaje)/100)
            devolucion = Devolucion(persona=saldo.beneficiario, valor=valor_devolucion, saldo_a_favor=saldo, porcentaje=porcentaje, observacion=observacion, encargado_id =request.user.profile.id)
            devolucion.save()
            return redirect('buscar-saldos')
    return render(request, 'administracion/devolucion/devolucion.html', {'form': form, 'saldo' : saldo, 'valor_disponible' : valor_disponible, 'reservas' : reservas })