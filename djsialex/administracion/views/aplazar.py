from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

from ..models import PreinscripcionHorarioCurso, ReciboPreinscripcion, PreinscripcionExamen, Pago, \
    SaldoAFavor, Matricula, GrupoAcademico, Beca, AutorizadoCurso
from ..forms.aplazarForm import AplazarCursoForm, AplazarExamenForm
from ..modules import check_saldo_cargado


@login_required
def aplazarCursoView(request, pk):

    preinscripcionhorariocurso = PreinscripcionHorarioCurso.objects.get(pk=pk)
    recibopreinscripcion = get_object_or_404(ReciboPreinscripcion, preinscripcion=preinscripcionhorariocurso)
    pagos = Pago.objects.filter(recibo_preinscripcion=recibopreinscripcion)
    periodo_id = request.session["periodo_contextualizado_id"]
    pagado = 0
    if pagos:
        for pago in pagos:
            if pago.tipo == 'Pago Usuario' or pago.tipo == 'Saldo a favor':
                pagado += pago.financiero.valor
    if request.method == 'GET':
        form = AplazarCursoForm()
    else:
        form = AplazarCursoForm(request.POST)

        if form.is_valid():
            if check_saldo_cargado(recibopreinscripcion):
                saldo = SaldoAFavor.objects.get(recibo_preinscripcion_generado=recibopreinscripcion)
                saldo.activo = False
                saldo.save()
            saldo_a_favor = request.POST['valor_saldo_a_favor']
            motivo = request.POST['motivo']
            if float(saldo_a_favor) > pagado:
                messages.add_message(request, messages.SUCCESS, 'El valor a retornar no puede ser mayor al pagado por el usuario')
                return HttpResponseRedirect(request.path_info)
            else:
                saldo_nuevo = SaldoAFavor(beneficiario=preinscripcionhorariocurso.persona,periodo_generado_id=periodo_id, valor=float(saldo_a_favor),activo=True, recibo_preinscripcion_generado=recibopreinscripcion)
                saldo_nuevo.save()
                try:
                    beca = Beca.objects.get(estado_beca__in=[2,3] , beneficiario= preinscripcionhorariocurso.persona, nivel_idioma=preinscripcionhorariocurso.horario_cupo.curso.nivel)
                    beca.valor = 0
                    beca.estado_beca = 1
                    beca.save()
                except Beca.DoesNotExist:
                    beca = None
                preinscripcionhorariocurso.estado_preinscripcion = int(motivo)
                preinscripcionhorariocurso.save()
                autorizado_curso = AutorizadoCurso.objects.filter(numero_documento=preinscripcionhorariocurso.persona.numero_documento,
                                                                  periodo_id=periodo_id, curso_autorizado=preinscripcionhorariocurso.horario_cupo.curso,
                                                                  estado=2).all().first()
                if autorizado_curso:
                    autorizado_curso.estado = 3
                    autorizado_curso.save()
                try:
                    matricula = Matricula.objects.get(estudiante=preinscripcionhorariocurso.persona,
                                                      grupo__horarioCurso=preinscripcionhorariocurso.horario_cupo)
                except Matricula.DoesNotExist:
                    matricula = None
                if matricula:
                    if int(motivo) == 2:
                        matricula.estado_matricula = 5
                    elif int(motivo) == 4:
                        matricula.estado_matricula = 6
                    matricula.save()
                return redirect('formalizar-curso', pk=pk)
    return render(request, 'administracion/inscripcion/aplazar_curso.html', {'form': form, 'preinscripcionhorariocurso' : preinscripcionhorariocurso, 'pagado' : pagado })

@login_required
def aplazarExamenView(request, pk):

    preinscripcionexamen = PreinscripcionExamen.objects.get(pk=pk)
    recibopreinscripcion = get_object_or_404(ReciboPreinscripcion, preinscripcion=preinscripcionexamen)
    pagos = Pago.objects.filter(recibo_preinscripcion=recibopreinscripcion)
    periodo_id = request.session["periodo_contextualizado_id"]
    pagado = 0
    if pagos:
        for pago in pagos:
            if pago.tipo == 'Pago Usuario' or pago.tipo == 'Saldo a favor':
                pagado += pago.financiero.valor
    if request.method == 'GET':
        form = AplazarExamenForm()
    else:
        form = AplazarExamenForm(request.POST)

        if form.is_valid():
            if check_saldo_cargado(recibopreinscripcion):
                saldo = SaldoAFavor.objects.get(recibo_preinscripcion_generado=recibopreinscripcion)
                saldo.activo = False
                saldo.save()
            saldo_a_favor = request.POST['valor_saldo_a_favor']
            motivo = request.POST['motivo']
            if int(saldo_a_favor) > pagado:
                messages.add_message(request, messages.SUCCESS, 'El valor a retornar no puede ser mayor al pagado por el usuario')
                return HttpResponseRedirect(request.path_info)
            else:
                saldo_nuevo = SaldoAFavor(beneficiario=preinscripcionexamen.persona,
                                          periodo_generado_id=periodo_id, valor=float(saldo_a_favor), activo=True,
                                          recibo_preinscripcion_generado=recibopreinscripcion)
                saldo_nuevo.save()
                preinscripcionexamen.estado_preinscripcion = int(motivo)
                preinscripcionexamen.save()
                return redirect('formalizar-examen', pk=pk)
    return render(request, 'administracion/inscripcion/aplazar_examen.html', {'form': form, 'preinscripcionexamen' : preinscripcionexamen, 'pagado' : pagado })


@login_required
def aplazarCursoLoteView(request, grupoacademico):
    grupo  = GrupoAcademico.objects.get(pk=grupoacademico)
    matriculas = Matricula.objects.filter(grupo_id=grupoacademico, estado_matricula__in=[1,2,7,8])
    periodo_id = request.session["periodo_contextualizado_id"]
    if request.method == 'POST':
        for m in matriculas:
            try:
                preinscripcionhorariocurso = PreinscripcionHorarioCurso.objects.get(horario_cupo__curso__nivel=m.grupo.horarioCurso.curso.nivel, persona=m.estudiante, estado_preinscripcion__in=[1,3,5])
            except PreinscripcionHorarioCurso.DoesNotExist:
                preinscripcionhorariocurso = None
            if preinscripcionhorariocurso:
                recibopreinscripcion = get_object_or_404(ReciboPreinscripcion,
                                                         preinscripcion=preinscripcionhorariocurso)
                pagos = Pago.objects.filter(recibo_preinscripcion=recibopreinscripcion)
                pagado = 0
                if pagos:
                    for pago in pagos:
                        if pago.tipo == 'Pago Usuario' or pago.tipo == 'Saldo a favor':
                            pagado += pago.financiero.valor
                if check_saldo_cargado(recibopreinscripcion):
                    saldo = SaldoAFavor.objects.get(recibo_preinscripcion_generado=recibopreinscripcion)
                    saldo.activo = False
                    saldo.save()
                motivo = 4
                saldo_nuevo = SaldoAFavor(beneficiario=preinscripcionhorariocurso.persona,
                                              periodo_generado_id=periodo_id, valor=float(pagado), activo=True,
                                              recibo_preinscripcion_generado=recibopreinscripcion)
                saldo_nuevo.save()
                preinscripcionhorariocurso.estado_preinscripcion = int(motivo)
                preinscripcionhorariocurso.save()
                autorizado_curso = AutorizadoCurso.objects.filter(
                    numero_documento=preinscripcionhorariocurso.persona.numero_documento,
                    periodo_id=periodo_id, curso_autorizado=preinscripcionhorariocurso.horario_cupo.curso,
                    estado=2).all().first()
                if autorizado_curso:
                    autorizado_curso.estado = 3
                    autorizado_curso.save()
                try:
                    matricula = Matricula.objects.get(estudiante=preinscripcionhorariocurso.persona,
                                                      grupo__horarioCurso=preinscripcionhorariocurso.horario_cupo)
                except Matricula.DoesNotExist:
                    matricula = None
                if matricula:
                    matricula.estado_matricula = 6
                    matricula.save()
        grupo.estado = 1
        grupo.save()
        return redirect('seleccion_oferta')
    return render(request, 'administracion/inscripcion/aplazar_curso_lote.html',
                  {'matriculas': matriculas, 'grupo' : grupo})
