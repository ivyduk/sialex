# Change Log

## 1.12.3
- Ajustar cancelacion examen de clasificacion

## 1.12.2
- Agregar codigo hermes para pais, ciudad y region
- Actualizar reporte hermes para tomar el nuevo codigo

## 1.12.1
- Agregar validacion cuando se desactivan todos los periodos

## 1.12.0
- Se removió la selección de período al ingresar a la plataforma para no contextualizar a los usuarios de tipo aspirante y estudiante
- Agregar a formulario de preinscripción un campo filtro por periodo antes de seleccion de idioma
- Agregar a formulario de preinscripción en examen de clasificación un campo filtro por periodo antes de seleccion de idioma
- El sistema al ingresar a la consulta de personas inmediatamente carga la BD completa en lugar de únicamente dejar la caja de búsqueda, esto representa un problema pues toda la información de los usuarios queda expuesta, además toma tiempo la carga y consume recursos innecesariamente.
- Se agregan modelos al superadministrador para gestión directa de las siguientes tablas
- Agregar link corregido a formulario de pre inscripcion con informacion de descuentos
- Agregar activo para mostrar o no Tipos de documento
- Agregar codigos mapeo Hermes en tipo de documento
- Agregar codigos mapeo Hermes en No facturacion

## 1.11.0
- Agregar campo de URL para formulario de captura de documentos en mensaje de formalización
- Enviar un correo de formalización al usuario una vez se realice el proceso
- Agregar código hermes para los exámenes de clasificación
- Agregar filtro para calificaciones de exámenes
- Agregar campo de texto para registrar observaciones en los datos de preinscripción.
- Ajustar mensajes de error en formulario de preinscripción

## 1.10.4
- Agregar script para agregar información de pagos en recibo de preinscripción y migrarla

## 1.10.3
- Reactivar envios de correo y activación de los usuarios en dos pasos al registrarse

## 1.10.2
- Agregar columna tarifa_materiales a reporte hermes

## 1.10.1
- Arreglar filtro de examenes de clasificación por periodo en obtener presinscritos a examen
- Arreglar renderización de mensaje de formalización en preinscripcion de cursos


## 1.10.0
- Agregar descargo de Responsabilidad en vista de inicio 
- Agregar especificación de egresado Unal
- Eliminar obligatoriedad en campo de código hermes para grupos
- Asignar Estudiantes por edad en la creación de grupos
- Mostrar placeholder de contraseña en el formulario de autenticación
- Remover el campo tipo de documento que no cumple función en la validación
- Mostrar Edad calculada de usuario en vistas de preinscripción y formalización
- Eliminar Mensaje de preferencia correo gmail para formulario de registro


## 1.9.0
- Agregada fechas para el generación de reporte y servicio web que se integra con Hermes
- Agregar funcionalidad para exportar en csv el mismo reporte que se envía a través del servicio web con Hermes
- Agregar campo de especificación de curso de niños en el formulario de programa académico para renderizar diferente el boletín de notas
- Agregados filtros de programa académico por periodo en creacion de cursos

## 1.8.0
- Agregado el forzar formato de dirección de colombia para las direcciones de los usuarios
- Agregado campo de relación de discapacidad para los datos de los usuarios
- Se arregló Bug en la asignación de docente titular y docente de clase especializada
- Se fijaron las 3 primeras columnas en la vista del docente para agregar calificaciones
- Se agregó función para actualizar el documento del estudiantes desde la vista de formalización 
para poner estudiante en pendiente después de formalizado
- Se agregó función para facilitar que la planilla de notas se pueda descargar en PDF
- Se agrego fecha en perido para permitir o no la publicacion de notas
- Se ajustó formato del boletín exportado a pdf de los estudiantes


## 1.7.0
- Agregados fecha inicio y fecha final en periodo Academico
- Agregados campos de fecha inicio, fecha final y enlace virtual en grupo academico
- Agregado para editar codigo proyecto en grupo academico
- Agregado tipo de documento en vista de formalizacion
- Agregado filtros para exportar listas de preinscritos por curso y por examen
- Ajuste vista para aplazar estudiante
- Cambio en nombre de coordinadora para exportar boletines
- Agregado fecha en período para notificar a la dependencia si hay estudiantes preinscritos en estado pendiente
- Agregada la edición deshabilitada de notas para estudiantes pendientes
- Ajustes lista de niveles disponibles para beca

## 1.6.0
- Ajustes de validaciones e incluidos errores en formulario de preinscripción
- Desactivado boton de envío de preisncripción una vez se ha hecho click
- Agregados filtros para periodo, oferta académica y examen de clasificación
- Agregada función de creación de descuento en vista de formalización

## 1.5.2
- agregada lista para visualizar cursos activos en vista de estudiante
- agregados enlaces al website de extension en pagina principal

## 1.5.2
- ajustes en validación para preinscripción de idiomas
- ajustes en actualizacion de campo requiere_facturacion
- arreglado reporte de notas en estado final del curso
- Agregado campo nombre a periodo

## 1.5.1
- Ajustes en validación para preinscripción de antiguos y cambio de fechas para el servicio web con Hermes

## 1.5.0
- agregado mensaje para formalización en niveles y sino período como defecto
- habilitación a inscripción de estudiantes basado en el resultado del examen de calificación
- Validación de documento de identidad desde la vista de formalizar examen de calificación
- Ajustes en filtros de preinscripciones

## 1.4.1
- Arreglo a la validacion de preinscripciones en el mismo período donde se va a crear una preinscripcion

## 1.4.0
- Agregados campos es egresado y estado civil a formulario de personas
- Validación para teléfonos celulares
- Removida opción de no aplica en campo de tipo de vinculación a UN
- Incluida opción de descuento obligatorio y validación por edad para mensaje de 
sugerencia a la hora de preinscribirse a un curso
- Removida validación para presincribirse a misma modalidad por período
- Agregada opción de modificar y eliminar descuentos durante la formalización

## 1.3.0
- Editar y eliminar comprobantes de pago antes de formalización
- Inclusión campo de requiere facturación
- Valores de recibo de consignación cargados dinámicamente en concepto de pago para formalización
- Carga y redirección directa a formalización en la validación del documento de identidad 

## 1.2.1
- Ajustes en formato y flujos en Módulo financiero 

## 1.2.0
- Servicios que conectan con sistema HERMES

## 1.1.0
- Módulos de sialex requeridos para inscripción, formalización y registro de calificaciones

  
