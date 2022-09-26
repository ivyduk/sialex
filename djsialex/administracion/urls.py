from django import urls
from django.urls import path, include
from django.conf.urls import url
from django.urls import path
from django.contrib.auth import views as auth_views

from administracion.forms.autorizarForm import autorizadoExamenUpdate
from administracion.views.adminEstudiantes import escogerOpcionEstudiante, BuscarHistoriaAcademicaView, \
	mostrarHistoriaAcademica
from administracion.views.autorizadoExamen import autorizadoExamenCreateView, cargar_examenes_autorizado, \
	autorizadoExamenLoteView, AutorizadoExamenDelete, autorizadosExamenList
from administracion.views.beca import mostrarCampoBusqueda, nivelesBecaEstudiante, TipoBecaCreateView, TipoBecaListView, \
	TipoBecaDetailView, TipoBecaUpdateView, escogerOpcionAdministrarBeca, estudiantesBecaList, borrarBeca, \
	actualizarBeca
from administracion.views.calificaciones_curso.ObservacionMatricula import ObservacionMatriculaCreateView, \
	ObservacionMatriculaListView, ObservacionMatriculaUpdateView, eliminarObservacionMatricula
from administracion.views.calificaciones_curso.fallasAsistencia import FallaAsistenciaCreateView, \
	FallaAsistenciaListView, FallaAsistenciaUpdateView, eliminarFallaAsistencia
from administracion.views.calificarExamenClasificacion import calificarExamen, seleccionarIdiomaExamen
from administracion.views.calificaciones_curso.notasCurso import cursosAsociadosList, \
	listadoCalificacionesPorGrupo, calificarGrupo, listadoEstudiantesPorGrupo, actualizarEstadoMatriculas, \
	descargarNotasPorGrupo, actualizarEstadoMatriculasGrupos, descargarNotasGrupos
from administracion.views.historiaAcademica import miHistoriaAcademica, cursoCalificacionesDetalle, \
	cursoCalificacionesDetallePDF, misCursosList
from administracion.views.preinscripcionExamenClasificacion import preinscripcionExamenView, \
	preinscripcion_examen_fase_previa, PreinscripcionExamenDetailView, PreinscripcionExamenDelete

from .report import funcion
from .views.aplazar import aplazarCursoView
from .views.DocumentoDescuento import DocumentoDescuentoUpdateView
from .views.comprobantePago import ComprobantePagoCreateView

from administracion.views.preinscripciones.adminPreinscripciones import escogerOpcionPreinscripcion, liberarCuposOpcion, \
	liberarCuposCursoNivel1
from .views import *

from administracion.views.DatosEstudiantesView import DatosEstudiantesAPI

from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register('DatosEstudiantesModel',DatosEstudiantesAPI)

urlpatterns = [
	url(r'^$', HomePageView.as_view(), name='index'),
	url(r'^i18n/', include('django.conf.urls.i18n')),

	path('',include(router.urls)),

	path('about/', AboutPageView.as_view(), name='about'),
	path('administracion/', HomePageView.as_view(), name='home'),

	url(r'^administracion/periodos/$', PeriodoListView.as_view(), name='periodos'),
	url(r'^administracion/periodo/(?P<pk>[0-9a-f-]+)$', PeriodoDetailView.as_view(), name='periodo-detail'),
	path('administracion/periodo/crear/', PeriodoCreate.as_view(), name='periodo_create'),
	path('administracion/periodo/editar/<uuid:pk>', PeriodoUpdate.as_view(), name='periodo_update'),
	path('administracion/periodo/borrar/<uuid:pk>', PeriodoDelete.as_view(), name='periodo_delete'),

	url(r'^administracion/periodicidades/$', PeriodicidadListView.as_view(), name='periodicidades'),
	url(r'^administracion/periodicidad/(?P<pk>[0-9]+)$', PeriodicidadDetailView.as_view(), name='periodicidad-detail'),
	path('administracion/periodicidad/crear/', PeriodicidadCreate.as_view(), name='periodicidad_create'),
	path('administracion/periodicidad/editar/<pk>', PeriodicidadUpdate.as_view(), name='periodicidad_update'),
	path('administracion/periodicidad/borrar/<pk>', PeriodicidadDelete.as_view(), name='periodicidad_delete'),


	url(r'^administracion/idiomas/$', IdiomaListView.as_view(), name='idiomas'),
	url(r'^administracion/idioma/(?P<pk>[0-9a-f-]+)$', IdiomaDetailView.as_view(), name='idioma-detail'),
	path('administracion/idioma/crear/', IdiomaCreate.as_view(), name='idioma_create'),
    path('administracion/idioma/editar/<uuid:pk>', IdiomaUpdate.as_view(), name='idioma_update'),
    path('administracion/idioma/borrar/<uuid:pk>', IdiomaDelete.as_view(), name='idioma_delete'),

	url(r'^administracion/niveles/$', NivelListView.as_view(), name='niveles'),
	url(r'^administracion/nivel/(?P<pk>[0-9a-f-]+)$', NivelDetailView.as_view(), name='nivel-detail'),
	path('administracion/nivel/crear/', NivelCreate.as_view(), name='nivel_create'),
    path('administracion/nivel/editar/<uuid:pk>', NivelUpdate.as_view(), name='nivel_update'),
    path('administracion/nivel/borrar/<uuid:pk>', NivelDelete.as_view(), name='nivel_delete'),

    url(r'^administracion/programas/$', ProgramaAcademicoListView.as_view(), name='programas'),
	url(r'^administracion/programa/(?P<pk>[0-9a-f-]+)$', ProgramaAcademicoDetailView.as_view(), name='programa-detail'),
	path('administracion/programa/crear/', ProgramaAcademicoCreate.as_view(), name='programa_create'),
    path('administracion/programa/editar/<uuid:pk>', ProgramaAcademicoUpdate.as_view(), name='programa_update'),
    path('administracion/programa/borrar/<uuid:pk>', ProgramaAcademicoDelete.as_view(), name='programa_delete'),

    url(r'^administracion/contextualizar_periodo/$', contextualizarPeriodo, name="contextualizar_periodo"),
	url(r'^administracion/descontextualizar_periodo/$', descontextualizarPeriodo, name="descontextualizar_periodo"),

	url(r'^administracion/contenido-nivel/$', ContenidoNivelListView.as_view(), name='contenido-niveles'),
	url(r'^administracion/contenido-nivel/(?P<pk>[0-9]+)$', ContenidoNivelDetailView.as_view(), name='contenido-nivel-detail'),
	#path('administracion/contenido-nivel/crear/', ContenidoCreate.as_view(), name='contenido_nivel_create'),
    path('administracion/contenido-nivel/editar/<pk>', ContenidoNivelUpdate.as_view(), name='contenido-nivel_update'),

	url(r'^administracion/escala-nota/$', EscalaNotaListView.as_view(), name='escala-notas'),
	url(r'^administracion/escala-nota/(?P<pk>[0-9]+)$', EscalaNotaDetailView.as_view(), name='escala-nota-detail'),
	path('administracion/escala-nota/crear/', EscalaNotaCreate.as_view(), name='escala-nota_create'),
    path('administracion/escala-nota/editar/<pk>', EscalaNotaUpdate.as_view(), name='escala-nota_update'),
    path('administracion/escala-nota/borrar/<pk>', EscalaNotaDelete.as_view(), name='escala-nota_delete'),

	url(r'^administracion/documento-requerido/$', DocumentoRequeridoListView.as_view(), name='documentos-requeridos'),
	url(r'^administracion/documento-requerido/(?P<pk>[0-9]+)$', DocumentoRequeridoDetailView.as_view(), name='documento-requerido-detail'),
	path('administracion/documento-requerido/crear/', DocumentoRequeridoCreate.as_view(), name='documento-requerido_create'),
    path('administracion/documento-requerido/editar/<pk>', DocumentoRequeridoUpdate.as_view(), name='documento-requerido_update'),
    path('administracion/documento-requerido/borrar/<pk>', DocumentoRequeridoDelete.as_view(), name='documento-requerido_delete'),

	url(r'^administracion/descuento/$', DescuentoListView.as_view(), name='descuentos'),
	url(r'^administracion/descuento/(?P<pk>[0-9]+)$', DescuentoDetailView.as_view(), name='descuento-detail'),
	path('administracion/descuento/crear/', DescuentoCreate.as_view(), name='descuento_create'),
    path('administracion/descuento/editar/<pk>', DescuentoUpdate.as_view(), name='descuento_update'),
    path('administracion/descuento/borrar/<pk>', DescuentoDelete.as_view(), name='descuento_delete'),

	url(r'^administracion/examenclasificacion/$', ExamenClasificacionListView.as_view(), name='examenes-clasificacion'),
	url(r'^administracion/examenclasificacion/opciones$', examenClasificacionOpciones, name='examen-clasificacion-opciones'),
	url(r'^administracion/examenclasificacion/(?P<pk>[0-9a-f-]+)$', ExamenClasificacionDetailView.as_view(), name='examen-clasificacion-detail'),
	path('administracion/examenclasificacion/crear/', ExamenClasificacionCreate.as_view(), name='examen-clasificacion_create'),
    path('administracion/examenclasificacion/editar/<uuid:pk>', ExamenClasificacionUpdate.as_view(), name='examen-clasificacion_update'),
    path('administracion/examenclasificacion/borrar/<uuid:pk>', ExamenClasificacionDelete.as_view(), name='examen-clasificacion_delete'),
	url(r'^administracion/examenclasificacion/calificaciones/$', calificacionesExamenClasificacionList, name='calificacion-examen-list'),
	url(r'^administracion/examenclasificacion/descarga/calificaciones/$', descargarCalificacionesExamen, name='calificacion-examen-csv'),
	url(r'^administracion/examenclasificaciones/ver-preinscritos/(?P<examen>[0-9a-f-]+)$', verPreinscritosExamen, name='examen-clasificacion-preinscritos'),
	url(r'^administracion/examenclasificacion/preinscritos/descarga/(?P<examen>[0-9a-f-]+)$', descargarPreinscritosExamen,
		name='examen-clasificacion-preinscritos-csv'),

	url(r'^administracion/horario/$', HorarioListView.as_view(), name='horarios'),
	url(r'^administracion/horario/(?P<pk>[0-9]+)$', HorarioDetailView.as_view(), name='horario-detail'),
	path('administracion/horario/crear/', horarioCreateForm, name='horario_create'),
    path('administracion/horario/editar/<pk>', HorarioUpdate.as_view(), name='horario_update'),
    path('administracion/horario/borrar/<pk>', HorarioDelete.as_view(), name='horario_delete'),

	url(r'^administracion/oferta/$', OfertaAcademicaListView.as_view(), name='ofertas'),
	url(r'^administracion/oferta/(?P<pk>[0-9a-f-]+)$', OfertaAcademicaDetailView.as_view(), name='oferta-detail'),
	path('administracion/oferta/crear/', OfertaAcademicaCreate.as_view(), name='oferta_create'),
	path('administracion/oferta/editar/<uuid:pk>', OfertaAcademicaUpdate.as_view(), name='oferta_update'),
	path('administracion/oferta/borrar/<uuid:pk>', OfertaAcademicaDelete.as_view(), name='oferta_delete'),

	url(r'^administracion/curso/$', CursoListView.as_view(), name='cursos'),
	url(r'^administracion/curso/(?P<pk>[0-9a-f-]+)$', CursoDetailView.as_view(), name='curso-detail'),
	path('administracion/curso/create', CursoCreate.as_view(), name='curso_create'),
	path('administracion/curso/editar/<uuid:pk>', CursoUpdate.as_view(), name='curso_update'),
	path('administracion/curso/borrar/<uuid:pk>', CursoDelete.as_view(), name='curso_delete'),

	url(r'^administracion/eventoperiodo/$', EventoPeriodoListView.as_view(), name='eventosPeriodo'),
	url(r'^administracion/eventoperiodo/(?P<pk>[0-9]+)$', EventoPeriodoDetailView.as_view(), name='eventoperiodo-detail'),
	path('administracion/eventoperiodo/create', EventoPeriodoCreate.as_view(), name='eventoperiodo_create'),
	path('administracion/eventoperiodo/editar/<pk>', EventoPeriodoUpdate.as_view(), name='eventoperiodo_update'),
	path('administracion/eventoperiodo/borrar/<pk>', EventoPeriodoDelete.as_view(), name='eventoperiodo_delete'),

	url(r'^administracion/evento/$', EventoListView.as_view(), name='eventos'),
	url(r'^administracion/evento/(?P<pk>[0-9a-f-]+)$', EventoDetailView.as_view(), name='evento-detail'),
	path('administracion/evento/create', EventoCreate.as_view(), name='evento_create'),
	path('administracion/evento/editar/<uuid:pk>', EventoUpdate.as_view(), name='evento_update'),
	path('administracion/evento/borrar/<uuid:pk>', EventoDelete.as_view(), name='evento_delete'),

	url(r'^administracion/url/$', UrlListView.as_view(), name='urls'),
	url(r'^administracion/url/(?P<pk>[0-9]+)$', UrlDetailView.as_view(), name='url-detail'),
	path('administracion/url/create', UrlCreate.as_view(), name='url_create'),
	path('administracion/url/editar/<pk>', UrlUpdate.as_view(), name='url_update'),
	path('administracion/url/borrar/<pk>', UrlDelete.as_view(), name='url_delete'),

	url(r'^administracion/franja/$', FranjaListView.as_view(), name='franjas'),
	url(r'^administracion/franja/(?P<pk>[0-9]+)$', FranjaDetailView.as_view(), name='franja-detail'),
	path('administracion/franja/create', FranjaCreate.as_view(), name='franja_create'),
	path('administracion/franja/editar/<pk>', FranjaUpdate.as_view(), name='franja_update'),
	path('administracion/franja/borrar/<pk>', FranjaDelete.as_view(), name='franja_delete'),

	url(r'^administracion/conjuntonotas/$', ConjuntoNotasListView.as_view(), name='conjunto-notas'),
	url(r'^administracion/conjuntonotas/(?P<pk>[0-9]+)$', ConjuntoNotasDetailView.as_view(), name='conjunto_notas-detail'),
	path('administracion/conjuntonotas/create', ConjuntoNotasCreate.as_view(), name='conjuntonotas_create'),
	path('administracion/conjuntonotas/editar/<pk>', ConjuntoNotasUpdate.as_view(), name='conjuntonotas_update'),
	path('administracion/conjuntonotas/borrar/<pk>',  ConjuntoNotasDelete.as_view(), name='conjuntonotas_delete'),


	#Administracion de autorizados
    url(r'^administracion/autorizado/$',   autorizadosCursoList, name='autorizados'),
	path('administracion/autorizado/lote/', autorizadoLoteView, name='autorizado_lote'),
	#url(r'^administracion/oferta/(?P<pk>[0-9a-f-]+)$', OfertaAcademicaDetailView.as_view(), name='oferta-detail'),
	path('administracion/autorizado/crear/', autorizadoCreateView, name='autorizado_create'),
    path('administracion/autorizado/opciones/', escogerOpcionAutorizado, name='autorizado_opciones'),
    path('administracion/autorizado/editar/<uuid:pk>', autorizadoUpdate, name='autorizado_update'),
	path('administracion/autorizado/borrar/<uuid:pk>', AutorizadoDelete.as_view(), name='autorizado_delete'),

	path('ajax/cargar-programas-autorizado/', cargar_programas_academicos_autorizado, name='ajax_cargar_programas_autorizado'),
	path('ajax/cargar-cursos-autorizado/', cargar_cursos_autorizado, name='ajax_cargar_cursos_autorizado'),
	path('ajax/cargar-horarios-autorizado/', cargar_horarios_autorizado, name='ajax_cargar_horarios_autorizado'),

	##########################################################################################################################
	#Administracion de autorizado a examen de clasificación
	url(r'^administracion/autorizado-examen/$',  autorizadosExamenList, name='autorizados-examen'),
	path('administracion/autorizado-examen/lote/', autorizadoExamenLoteView, name='autorizado-examen-lote'),
	path('administracion/autorizado-examen/crear/', autorizadoExamenCreateView, name='autorizado_examen_create'),
    path('administracion/autorizado-examen/editar/<uuid:pk>', autorizadoExamenUpdate, name='autorizado-examen-update'),
	path('administracion/autorizado-examen/borrar/<uuid:pk>', AutorizadoExamenDelete.as_view(), name='autorizado-examen-delete'),

	path('ajax/cargar-examenes-autorizado/', cargar_examenes_autorizado, name='ajax_cargar_examenes_autorizado'),


	###################JSONWEBSERVICES##########################
	url(r'^administracion/webservices/public/periodo_webservice/(?P<periodo>[0-9a-f-]+)$', periodoWebservice, name="periodo_webservice"),

	###################FILES##########################
	url(r'^administracion/downloads/viewer/(?P<id>[0-9a-f-]+)$', showContentFile, name='archivos-show'),
	#url(r'^administracion/downloads/downloader/(?P<id>[0-9a-f-]+)$', showContentFile, name='archivos-download'),

	url(r'^administracion/contenidonivelversion/create/(?P<contenidonivel>[-\w]+)', ContenidoNivelVersionCreateView.as_view(), name='contenidonivelversion_create'),
	path('administracion/contenidonivelversion/editar/<pk>', ContenidoNivelVersionUpdateView.as_view(), name='contenidonivelversion_update'),

	url(r'^signup/$', signup, name='signup'),
	url(r'^account_activation_sent/$', account_activation_sent, name='account_activation_sent'),
	url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', activate, name='activate'),
	url(r'^administracion/usuario/editarperfil/$', completeProfile, name='complete-profile'),
	url(r'^administracion/usuario/cambiarpassword/$', changeSelfUserPassword, name='change_password'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

	#Administrar preinscripciones
	path('administracion/preinscripciones/opciones/', escogerOpcionPreinscripcion, name='preinscripcion_opciones'),
	path('administracion/preinscripciones/liberarcupos-opcion/', liberarCuposOpcion, name='liberarcupos_opcion'),
	path('administracion/preinscripciones/liberarcupos/', liberarCuposCursoNivel1, name='liberarcupos'),
	path('administracion/preinscripciones/curso/lote/', preinscripcion_curso_lote, name='preinscripcion-curso-lote'),

	# Preinscripcion curso

	url(r'^administracion/mis-inscripciones/$', PreinscripcionCursoListView.as_view(), name='mis-preinscripciones'),
	url(r'^administracion/buscar-inscripciones/$', BuscarPreinscripcionesView.as_view(), name='buscar-preinscripciones'),
	url(r'^administracion/inscripciones/$', PreinscripcionesPersonaView.as_view(), name='preinscripciones-persona'),
	url(r'^inscripcion/curso/$', preinscripcionView, name='preinscripcion-curso'),
	url(r'^inscripcion/curso/(?P<pk>[0-9]+)$', PreinscripcionCursoDetailView.as_view(), name='preinscripcion-detail'),
    url(r'^inscripcion/curso/formalizar/(?P<pk>[0-9]+)$', formalizar_vista, name='formalizar-curso'),
	url(r'^inscripcion/examen/formalizar/(?P<pk>[0-9]+)$', formalizar_vista_examen, name='formalizar-examen'),
	path('inscripcion/curso/borrar/<pk>', CancelPreinscripcion.as_view(), name='preinscripcion_delete'),
	path('inscripcion/descuento/borrar/<pk>', CancelDescuento.as_view(), name='descuento_aplicado_borrar'),
	path('inscripcion/descuento/crear/<pk>', CrearDescuento.as_view(), name='descuento_aplicado_crear'),
	path('inscripcion/descuento/editar/<pk>', ModificarDescuento.as_view(), name='descuento_aplicado_editar'),
	path('ajax/cargar-programas/', cargar_programas_academicos, name='ajax_cargar_programas'),  # <-- this one here
	path('ajax/cargar-niveles/', cargar_niveles, name='ajax_cargar_niveles'),  # <-- this one here
	path('ajax/cargar-horarios/', cargar_horarios_disponibles, name='ajax_cargar_horarios'),  # <-- this one here
	path('ajax/cargar-descuentos/', cargar_descuentos, name='ajax_cargar_descuentos'),  # <-- this one here
	path('ajax/preinsripcion-fase-previa/', preinscripcion_fase_previa, name='preinscripcion_fase_previa'),  # <-- this one here
	url(r'^inscripcion/curso/aplazar_curso/(?P<pk>[0-9]+)$', aplazarCursoView, name='aplazar-curso'),
	url(r'^inscripcion/curso/aplazar_examen/(?P<pk>[0-9]+)$', aplazarExamenView, name='aplazar-examen'),
	url(r'^inscripcion/curso/cargarSaldo/(?P<pk>[0-9a-f-]+)$', cargarSaldoFavor, name='aplicar-saldo'),
	url(r'^inscripcion/saldo/aplicar/(?P<pk>[0-9]+)$', aplicarSaldoPago, name='saldo_aplicar'),
	url(r'^inscripcion/beca/aplicar/(?P<pk>[0-9]+)$', aplicarBecaPago, name='beca_aplicar'),

	# Preinscripcion examen

	url(r'^inscripcion/examen-clasificacion/$', preinscripcionExamenView, name='preinscripcion-examen'),
	url(r'^inscripcion/examen-clasificacion/(?P<pk>[0-9]+)$', PreinscripcionExamenDetailView.as_view(), name='preinscripcion-examen-detail'),
	path('inscripcion/examen-clasificacion/borrar/<pk>',  PreinscripcionExamenDelete.as_view(), name='preinscripcion_examen_delete'),
	path('ajax/cargar-examenes-disponibles/', cargar_examenes_disponibles, name='ajax_cargar_examenes_disponibles'),
	path('ajax/preinsripcion-examen-fase-previa/', preinscripcion_examen_fase_previa, name='preinscripcion_examen_fase_previa'),

	url(r'^administracion/buscar-examen/$', seleccionarIdiomaExamen, name='buscar-examen'),
	url(r'^administracion/examen-clasificacion/calificar/', calificarExamen, name='calificar_examen'),

	path('webservices/private/desplegable/paises/', webservice_desplegable_paises, name='webservice_desplegable_paises'),
	path('webservices/private/desplegable/regiones/', webservice_desplegable_regiones, name='webservice_desplegable_regiones'),
	path('webservices/private/desplegable/ciudades/', webservice_desplegable_ciudades, name='webservice_desplegable_ciudades'),
	path('webservices/private/pais_region_ciudad/', webservice_pais_region_ciudad, name='webservice_pais_region_ciudad'),
	path('webservices/private/webservice_niveles_idioma/', webservice_niveles_idioma, name='webservice_niveles_idioma'),
	path('webservices/private/webservice_salones_edificio/', webservice_salones_edificio, name='webservice_salones_edificio'),

	#Administracion de personas
	url(r'^administracion/persona/$', personas_list, name='personas'),
	url(r'^administracion/persona/(?P<pk>[0-9a-f-]+)$', PersonaDetailView.as_view(), name='persona-detail'),
	url(r'^administracion/persona/editar/(?P<pk>[0-9a-f-]+)$', EditarPersona.as_view(), name='persona-detail-update'),
	url(r'^administracion/persona/editar_documento/(?P<pk>[0-9a-f-]+)/(?P<preinscripcion>[-\w]+)',
		EditarPersonaDocumentoEntregado.as_view(), name='persona-document-update-pre'),


	#Documentos requeridos
	path('administracion/documento-descuento-requerido/editar/<pk>', DocumentoDescuentoUpdateView.as_view(), name='documento-descuento-requerido_update'),

	#Documentos requeridosb
	url(r'^administracion/comprobante-pago/crear/(?P<preinscripcionhorariocurso>[-\w]+)', ComprobantePagoCreateView.as_view(), name='comprobante_pago_create'),
	url(r'^administracion/comprobante-pago/editar/(?P<pk>[0-9]+)/(?P<preinscripcionhorariocurso>[-\w]+)', ComprobantePagoUpdateView.as_view(), name='comprobante_pago_update'),
	url(r'^administracion/comprobante-pago/borrar/(?P<pk>[0-9]+)', ComprobantePagoDeleteView.as_view(), name='comprobante_pago_delete'),


	#Configuracion mensaje de formalizacion
	path('administracion/mensajesformalizacion', MensajeFormalizacionList.as_view(), name='mensajeformalizacion_list'),
	path('administracion/mensajeformalizacion/crear', MensajeFormalizacionCreate.as_view(), name='mensajeformalizacion_create'),
	path('administracion/mensajeformalizacion/editar/<pk>', MensajeFormalizacionUpdate.as_view(), name='mensajeformalizacion_update'),

    # reportes
    url(r'^administracion/reportes/', include('explorer.urls')),

	url(r'^administracion/grupos/seleccion_oferta', seleccionOfertaAcademica, name='seleccion_oferta'),
	url(r'^administracion/grupos/asignar', asignarGrupos, name='asignar_grupos'),
	url(r'^administracion/grupos/crear/(?P<horariocurso>[-\w]+)', GrupoAcademicoCreateView.as_view(), name='grupo_create'),
	url(r'^administracion/grupos/mover/(?P<nivel>[-\w]+)', cambiarGrupo, name='cambiar_grupos'),
	url(r'^administracion/grupos/borrar/(?P<pk>[0-9a-f-]+)$', GrupoAcademicoDeleteView.as_view(), name='grupo_delete'),
	url(r'^administracion/grupos/matriculas-list/(?P<grupoacademico>[-\w]+)', matriculaPorGrupoAcademicoList, name='grupo-detail'),
	url(r'^administracion/grupos/estudiantes/(?P<grupoacademico>[-\w]+)', descargarListaPorGrupo, name='estudiantes-grupo-csv'),
	url(r'^administracion/grupos/docente-salon/(?P<grupoacademico>[-\w]+)', asignarDocenteSalonAGrupo, name='docente-salon'),
	url(r'^administracion/grupos/docente-salon-correo/(?P<grupoacademico>[-\w]+)', informacionDocenteSalonAGrupo, name='docente-salon-correo'),
	url(r'^administracion/grupos/eliminar-docente-grupo/(?P<grupoacademico>[-\w]+)/(?P<docente>[-\w]+)', eliminarDocenteDeGrupo, name='eliminar-docente-grupo'),
	url(r'^administracion/grupos/eliminar-salon-grupo/(?P<grupoacademico>[-\w]+)/(?P<salon>[-\w]+)', eliminarSalonDeGrupo, name='eliminar-salon-grupo'),
	url(r'^administracion/grupos/aplazar-grupo/(?P<grupoacademico>[-\w]+)', aplazarCursoLoteView, name='aplazar-grupo'),

	#calificacion de cursos
	url(r'^docente/cursos/mis-cursos', cursosAsociadosList, name='mis-cursos'),
    url(r'^docente/cursos/mis-estudiantes/(?P<grupoacademico>[-\w]+)', listadoEstudiantesPorGrupo, name='mis-estudiantes'),
    url(r'^docente/cursos/calificaciones-estudiantes/(?P<grupoacademico>[-\w]+)', listadoCalificacionesPorGrupo, name='calificaciones-estudiantes'),
	url(r'^docente/cursos/calificar-grupo/(?P<grupoacademico>[-\w]+)', calificarGrupo, name='calificar-grupo'),
	url(r'^docente/cursos/actualizar-estados-todos', actualizarEstadoMatriculasGrupos, name='actualizar-estados-todos'),
	url(r'^docente/cursos/actualizar-estados/(?P<grupoacademico>[-\w]+)', actualizarEstadoMatriculas,name='actualizar-estados'),
	url(r'^administracion/descargar-calificaciones-grupo/(?P<grupoacademico>[-\w]+)', descargarNotasPorGrupo, name='calificaciones-grupo-csv'),
	url(r'^administracion/descargar-calificaciones-grupos', descargarNotasGrupos, name='calificaciones-csv'),

	#fallas asistencia
	url(r'^administracion/falla-asistencia/crear/(?P<matricula>[-\w]+)', FallaAsistenciaCreateView.as_view(), name='falla_asistencia_create'),
	url(r'^administracion/falla-asistencia/list/(?P<matricula>[-\w]+)', FallaAsistenciaListView.as_view(), name='falla_asistencia_list'),
	path('administracion/falla-asistencia/editar/<pk>', FallaAsistenciaUpdateView.as_view(), name='falla_asistencia_update'),
	url(r'^administracion/falla-asistencia/eliminar/(?P<falla>[-\w]+)', eliminarFallaAsistencia, name='falla_asistencia_delete'),

	#Observaciones matrícula
	url(r'^administracion/observacion-matricula/crear/(?P<matricula>[-\w]+)', ObservacionMatriculaCreateView.as_view(), name='observacion_matricula_create'),
	url(r'^administracion/observacion-matricula/list/(?P<matricula>[-\w]+)', ObservacionMatriculaListView.as_view(), name='observacion_matricula_list'),
	url(r'^administracion/observacion-matricula/editar/(?P<pk>[-\w]+)', ObservacionMatriculaUpdateView.as_view(), name='observacion_matricula_update'),
	url(r'^administracion/observacion-matricula/eliminar/(?P<observacion>[-\w]+)', eliminarObservacionMatricula, name='observacion_matricula_delete'),

	# historia academica
	url(r'^administracion/historia-academica', miHistoriaAcademica, name='mi_historia_academica'),
	url(r'^administracion/cursos-progreso', misCursosList, name='mis_cursos_en_progreso'),
	url(r'^administracion/mis-calificaciones/(?P<matricula>[-\w]+)/(?P<opcion>[0-9]+)', cursoCalificacionesDetalle, name='calificaciones-detalle'),
	url(r'^administracion/mis-calificaciones-pdf/(?P<matricula>[-\w]+)/(?P<opcion>[0-9]+)', cursoCalificacionesDetallePDF, name='calificaciones-detalle-pdf'),

	#beca
	url(r'^administracion/beca/opciones', escogerOpcionAdministrarBeca, name='beca-opciones'),
    url(r'^administracion/beca/estudiantes', estudiantesBecaList, name='becados'),
	url(r'^administracion/beca/buscar-estudiante', mostrarCampoBusqueda, name='buscar-estudiante'),
	url(r'^administracion/beca/niveles-beca-estudiante', nivelesBecaEstudiante, name='niveles-beca-estudiante'),
	url(r'^administracion/beca/borrar/(?P<beca>[0-9]+)$', borrarBeca, name='beca-delete'),
	url(r'^administracion/beca/editar/(?P<beca>[0-9]+)$', actualizarBeca, name='beca-update'),

	#tipo beca
	url(r'^administracion/tipo-beca/$', TipoBecaListView.as_view(), name='tipos-beca'),
	url(r'^administracion/tipo-beca/(?P<pk>[0-9]+)$', TipoBecaDetailView.as_view(), name='tipo-beca-detail'),
	path('administracion/tipo-beca/crear/', TipoBecaCreateView.as_view(), name='tipo-beca-create'),
	path('administracion/tipo-beca/editar/<pk>', TipoBecaUpdateView.as_view(), name='tipo-beca-update'),

	#encuesta
    url(r'^administracion/encuestas/$', IndexView.as_view(), name="survey-list"),
	url(r'^administracion/mis-encuestas/$', MisEncuestasView.as_view(), name="mysurvey-list"),
    url(r'^administracion/encuestas/(?P<id>\d+)/', SurveyDetail.as_view(), name="survey-detail"),
    url(r'^administracion/encuestas/(?P<id>\d+)/completed/', SurveyCompleted.as_view(), name="survey-completed"),
    url(r'^administracion/encuestas/(?P<id>\d+)-(?P<step>\d+)/',
        SurveyDetail.as_view(),
        name="survey-detail-step",
    ),
    url(r'^administracion/encuestas/confirm/(?P<uuid>\w+)/', ConfirmView.as_view(), name="survey-confirmation"),

	#asociar_encuesta
	url(r'^administracion/asociar/$', AsociarEncuestaListView.as_view(), name='asociaciones'),
	path('administracion/asociar/crear/', AsociarEncuestaCreate.as_view(), name='asociar_create'),
	path('administracion/asociar/editar/<pk>', AsociarEncuestaUpdate.as_view(), name='asociar_update'),
	path('administracion/asociar/borrar/<pk>', OfertaAcademicaDelete.as_view(), name='asociar_delete'),


	#devolucion
	url(r'^administracion/buscar-saldos/$', BuscarSaldosView.as_view(),name='buscar-saldos'),
	url(r'^administracion/saldos/$', SaldosAFavorPersonaView.as_view(), name='saldos-persona'),
	url(r'^inscripcion/saldos/devolucion/(?P<pk>[0-9]+)$', devolucionView, name='devolucion'),

	# Administrar estudiantes
	path('administracion/estudiantes/opciones/', escogerOpcionEstudiante, name='estudiantes_opciones'),
	url(r'^administracion/buscar-historias-academicas/$', BuscarHistoriaAcademicaView.as_view(),
		name='buscar-historias-academicas'),
	url(r'^administracion/estudiantes/$', mostrarHistoriaAcademica, name='historias-academicas'),

	#Preinscritos cursos
	url(r'^administracion/grupos/ver-preinscritos/(?P<horario_curso>[0-9a-f-]+)$', verPreinscritosCurso, name='horario-curso-preinscritos'),
	url(r'^administracion/grupos/preinscritos-sin-matricula/(?P<horario_curso>[0-9a-f-]+)$', verPreinscritosSinMatriculaCurso, name='preinscritos-sin-matricula'),

]


