DIAS = [
  (1, ("Lunes")),
  (2, ("Martes")),
  (3, ("Miercoles")),
  (4, ("Jueves")),
  (5, ("Viernes")),
  (6, ("Sabado")),
  (7, ("Domingo")),
]

ESTADOS_ADMINISTRATIVOS_PREINSCRIPCION = [
    (1, ("Inscrito")), # formalizado y entregó documentos completos
    (2, ("Aplazada por usuario")), # si aplaza por decisión de usuario, luego de formalizar con matrícula
    (3, ("Pendiente")), # formalizado y tiene pendientes documentos o pagos
    (4, ("Aplazada por departamento")), # si aplaza por decisión de usuario, luego de formalizar con matrícula
    (5, ("Preinscrito")), # no ha formalizado
    (6, ("Cancelado")), # cancela preinscripcion x usuario o x departamento sin formalizar
    (7, ("Cancelado en formalización")) # cancela preinscripcion  con formalización
]

ESTADOS_ACADEMICOS_MATRICULA = [
    (1, ("No definida")),
    (2, ("Aprobado")),
    (3, ("Reprobado por calificación")),
    (4, ("Cancelado")),
    (5, ("Aplazado por usuario")),
    (6, ("Aplazado por departamento")),
    (7, ("En curso")),
    (8, ("Reprobado por inasistencia")),
    (9, ("Aprobado - Pendiente en formalización")),
]

GENERO_SEXUAL = [
    (1, ("F")),
    (2, ("M"))
]

TIPOS_NOTA = [
    (1, ("General")),
    (2, ("Especializada"))
]

TIPOS_SANGRE = [
  (1, ("A+")),
  (2, ("A-")),
  (3, ("B+")),
  (4, ("B-")),
  (5, ("AB+")),
  (6, ("AB-")),
  (7, ("O-")),
  (8, ("O+")),
]

EVENTOS_NUEVOS_CURSOS = [
    (1,("Inscripción en línea")),
    (2,("Formalización")),
    (3,("Liberación Cupos")),
    (4,("Inscripción en línea - cupos libres")),
    (5,("Formalización")),
    (6,("Inicio de clases")),
    (7,("Fin de clases")),
    (8,("Retroalimentacion"))
]

EVENTOS_ANTIGUOS_CURSOS = [
    (1,("Inscripción en línea")),
    (2,("Formalización")),
    (3,("Inicio de clases")),
    (4,("Fin de clases")),
    (5,("Retroalimentacion"))
]

ESTADOS_AUTORIZADO = [
    (1,("AUTORIZADO")),
    (2,("AUTORIZACIÓN COMPLETA")),
    (3,("AUTORIZACIÓN CANCELADA"))
]

PARENTESCO = [
    (1,("PADRE")),
    (2,("MADRE")),
    (3,("ABUELO")),
    (4,("ABUELA")),
    (5,("HERMANO")),
    (6,("HERMANA")),
    (7,("TÍO")),
    (8,("TÍA")),
    (9,("ESPOSO")),
    (10,("ESPOSA")),
    (11,("AMIGO")),
    (12,("OTRO")),

]

ESTADOS_DESCUENTO = [
    (1, ("SELECCIONADO")), #En preinscripción
    (2, ("APLICADO")), #En formalización
    (3, ("CANCELADO")),# Por cancelación Inscripción o error de usuario
    (4, ("PENDIENTE")),# Cuando hay más de un documento requerido por descuento
]

ESTADOS_BECA = [
    (1, ("ASIGNADA")), #Asignada por administrativo
    (2, ("PENDIENTE")), #En Preinscripción
    (3, ("APLICADA"))  #En Formalización
]

ESTADOS_RECIBO = [
    (1, ("CANCELADO")), #Por eliminación en Preinscripción o Formalización. En liberacion de cupos
    (2, ("PENDIENTE")), #Con pagos pendientes
    (3, ("PAGADO")),  #Sin saldo Pendiente
    (4, ("DEVUELTO")),  #Aplicación de proceso de devolución
]

TIPOS_COMPROBANTE = [
    (1, ("CONSIGNACIÓN")), 
    (2, ("PAGO ELECTRÓNICO")),
    (3, ("OTRO"))
]

TIPOS_PREINSCRIPCION = [
    (1, ("PREINSCRIPCIÓN CURSO")), 
    (2, ("PREINSCRIPCIÓN EXAMEN"))
]


ESTADOS_PAGO = [
    (1, ("SELECCIONADO")), 
    (2, ("APLICADO"))
]

TIPOS_VINCULACION = [
    (1, ("PARTICULAR")),
    (2, ("ESTUDIANTE PREGRADO O POSGRADO")),
    (4, ("EGRESADO")),
    (5, ("PROFESOR")),
    (6, ("ADMINISTRATIVO"))
]

NIVEL_FORMACION = [
    (1, ("NO APLICA")),
    (2, ("PREESCOLAR")),
    (3, ("BÁSICA PRIMARIA")),
    (4, ("BÁSICA SECUNDARIA")),
    (5, ("BACHILLER")),
    (6, ("FORMACIÓN TÉCNICA PROFESIONAL")),
    (7, ("TECNÓLOGO")),
    (8, ("UNIVERSITARIA")),
    (9, ("ESPECIALIZACIÓN TÉCNICO PROFESIONAL")),
    (10,("ESPECIALIZACIÓN TECNOLÓGICA")),
    (11,("ESPECIALIZACIÓN UNIVERSITARIA")),
    (12,("ESPECIALIZACIÓN MÉDICA")),
    (13,("MAESTRÍA")),
    (14,("DOCTORADO")),
    (15,("POSTDOCTORADO"))
]

COHORTE = [
    (1, ('Primer cohorte')),
    (2, ('Segundo cohorte'))
]

ESTADOS_GRUPO_ACADEMICO = [
    (0, ('Regular')),
    (1, ('Aplazado'))
]

ESTADO_CIVIL = [
    (1, ("SOLTERO(A)")),
    (2, ("CASADO(A)")),
    (3, ("DIVORCIADO(A)")),
    (4, ("VIUDO(A)")),
    (5, ("UNIÓN LIBRE")),
    (6, ("RELIGIOSO(A)")),
    (7, ("SEPARADO(A)"))
]

DISCAPACIDAD = [
    (1, ("NO APLICA")),
    (2, ("CIEGO(A)")),
    (3, ("SORDO(A)")),
    (4, ("MUDO(A)"))
]