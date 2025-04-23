
## version 1.12.2

### Update Pais, ciudad, Region with Codigo Hermes id
``` sql
ALTER TABLE administracion_pais
    ADD COLUMN hermes_id INTEGER default 0;

ALTER TABLE administracion_region
    ADD COLUMN hermes_id INTEGER default 0;

ALTER TABLE administracion_ciudad
    ADD COLUMN hermes_id INTEGER default 0;
```

### Update Datos Estudiantes Funcion
``` sql
create function datosestudiantes(fechainicial date, fechafinal date)
    returns TABLE(id_sub_proyecto_curso character varying, tipo_documento integer, numero_documento character varying, primer_nombre character varying, segundo_nombre character varying, primer_apellido character varying, segundo_apellido character varying, sexo_biologico integer, estado_civil integer, fecha_nacimiento date, pais_nacimiento integer, departamento_nacimiento integer, ciudad_nacimiento integer, nivel_formacion integer, egresado_un integer, vinculacion integer, telefono_fijo character varying, ext character varying, celular character varying, email character varying, direccion_residencia character varying, pais_residencia integer, departamento_residencia integer, ciudad_residencia integer, descuento integer, valor_inscripcion double precision, valor_pago double precision, fecha_pago date, no_soporte_de_pago character varying, tipo_pago integer, id integer, tarifa_materiales double precision)
    language sql
as
$$
SELECT ag.codigo_proyecto                   AS ID_SUB_PROYECTO_CURSO,
                    CASE
                        WHEN tipo_documento_id = 1 THEN 8 -- 'CC'
                        WHEN tipo_documento_id = 2 THEN 48 -- 'TI'
                        WHEN tipo_documento_id = 3 THEN 47 -- 'CE'
                        WHEN tipo_documento_id = 4 THEN 247 --'PT'
                        WHEN tipo_documento_id = 5 THEN 808 --'DE'
                        WHEN tipo_documento_id = 6 THEN 807 --'RC'
                        WHEN tipo_documento_id = 7 THEN 9 --'NIT'
                        WHEN tipo_documento_id = 8 THEN 241 --'CA'
                        WHEN tipo_documento_id = 9 THEN 246 --'NU'
                        END                              AS Tipo_Documento,
                    numero_documento,
                    primer_nombre,
                    segundo_nombre,
                    primer_apellido,
                    segundo_apellido,
                    CASE
                        WHEN perf.genero_sexual = 1 THEN 308 -- 'F'
                        WHEN perf.genero_sexual = 2 THEN 307 -- 'M'
                        END                              AS sexo_biologico,
                    CASE
                        WHEN perf.estado_civil = 1 THEN 810 -- SOLTERO(A)
                        WHEN perf.estado_civil = 2 THEN 811 -- CASADO (A)
                        WHEN perf.estado_civil = 3 THEN 812 -- DIVORCIADO (A)
                        WHEN perf.estado_civil = 4 THEN 813 -- VIUDO (A)
                        WHEN perf.estado_civil = 5 THEN 814 -- UNIÓN LIBRE
                        WHEN perf.estado_civil = 6 THEN 815 -- RELIGIOSO (A)
                        WHEN perf.estado_civil = 7 THEN 816 -- SEPARADO (A)
                        END                              AS estado_civil,
                    fecha_nacimiento,
                    apnac.hermes_id                             AS Pais_Nacimiento,
                    CASE
                        WHEN apnac.id = 47 THEN arnac.hermes_id
                        ELSE NULL
                        END                              AS Departamento_Nacimiento,
                    CASE
                        WHEN apnac.id = 47 THEN acnac.hermes_id
                        ELSE NULL
                        END                              AS Ciudad_Naciemiento,
                    CASE
                        WHEN perf.nivel_formacion = 1 THEN 15--'NO APLICA'
                        WHEN perf.nivel_formacion = 2 THEN 1 --'PREESCOLAR'
                        WHEN perf.nivel_formacion = 3 THEN 2 --'BÃSICA PRIMARIA'
                        WHEN perf.nivel_formacion = 4 THEN 3 --'BÃSICA SECUNDARIA'
                        WHEN perf.nivel_formacion = 5 THEN 4 --'BACHILLER'
                        WHEN perf.nivel_formacion = 6 THEN 5 --'FORMACIÃ“N TÃ‰CNICA PROFESIONAL'
                        WHEN perf.nivel_formacion = 7 THEN 6 --'TECNÃ“LOGO'
                        WHEN perf.nivel_formacion = 8 THEN 7 --'UNIVERSITARIA'
                        WHEN perf.nivel_formacion = 9 THEN 8 --'ESPECIALIZACIÃ“N TÃ‰CNICO PROFESIONAL'
                        WHEN perf.nivel_formacion = 10 THEN 9 --'ESPECIALIZACIÃ“N TECNOLÃ“GICA'
                        WHEN perf.nivel_formacion = 11 THEN 10 --'ESPECIALIZACIÃ“N UNIVERSITARIA'
                        WHEN perf.nivel_formacion = 12 THEN 11 --'ESPECIALIZACIÃ“N MÃ‰DICA'
                        WHEN perf.nivel_formacion = 13 THEN 12 --'MAESTRÃA'
                        WHEN perf.nivel_formacion = 14 THEN 13 --'DOCTORADO'
                        WHEN perf.nivel_formacion = 15 THEN 14 --'POSTDOCTORADO'
                        END                              AS Nivel_Formacion,
                    CASE
                        WHEN perf.es_egresado is true THEN 282 --'SI'
                        ELSE 283 --'NO'
                        END                              AS Egresado_UN,
                    CASE
                        WHEN perf.tipo_vinculacion_un = 1 THEN NULL--'NINGUNA'
                        WHEN perf.tipo_vinculacion_un = 2 THEN 647 -- 'ESTUDIANTE PREGRADO O POSGRADO'
                        WHEN perf.tipo_vinculacion_un = 4 THEN 648 -- 'EGRESADO'
                        WHEN perf.tipo_vinculacion_un = 5 THEN 649 -- 'PROFESOR'
                        WHEN perf.tipo_vinculacion_un = 6 THEN 650 -- 'ADMINISTRATIVO'
                        WHEN perf.tipo_vinculacion_un = 7 THEN 651 -- 'PARTICULAR'
                        END                              AS Vinculacion,
                    telefono_fijo                        AS telefono_fijo,
                    ''                                      EXT,
                    perf.telefono_celular                AS celular,
                    au.email,
                    direccion_residencia,
                    ap.hermes_id                                AS Pais_Residencia,
                    CASE
                        WHEN ap.id = 47 THEN ar.hermes_id
                        ELSE NULL
                        END                              AS Departamento_Residencia,
                    CASE
                        WHEN ap.id = 47 THEN ac.hermes_id
                        ELSE NULL
                        END                              AS Ciudad_Residencia,
                    CASE
                        WHEN recpre.descuento_id = 1 then 4 -- 'Estudiante pregrado UNAL'
                        WHEN recpre.descuento_id = 2 then 5 -- 'Estudiante de posgrado UNAL'
                        WHEN recpre.descuento_id = 3 then 3 -- 'Egresado de la Universidad Nacional de Colombia'
                        WHEN recpre.descuento_id = 4 then 3 -- 'Profesor de la UNAL'
                        WHEN recpre.descuento_id = 5 then 9 -- 'Hijo(a) de pensionado(a) UNAL'
                        WHEN recpre.descuento_id = 6 then 9 -- 'Hijo(a) de profesor(a) UNAL'
                        WHEN recpre.descuento_id = 8 then 9 -- 'Hijo(a) de funcionario(a) UNAL'
                        WHEN recpre.descuento_id = 9 then 9 -- 'Hijo(a) de contratista UNAL'
                        WHEN recpre.descuento_id = 10 then 9 -- 'Hijo(a) de estudiante UNAL'
                        WHEN recpre.descuento_id = 11 then 7 -- 'Grupos de 4 o mas personas'
                        WHEN recpre.descuento_id = 13 then 6 -- 'Personas que se inscriban en el marco de alianzas'
                        WHEN recpre.descuento_id = 14 then 10 --'Adultos mayores'
                        WHEN recpre.descuento_id = 15 then 10 -- 'NiÃ±os y adolescentes'
                        WHEN recpre.descuento_id = 16 then 10 -- 'Personas nivel 1 y 2 de l SISBEN'
                        WHEN recpre.descuento_id = 17 then 10 -- 'PoblaciÃ³n en situaciÃ³n de discapacidad'
                        WHEN recpre.descuento_id = 18 then 10 -- 'PoblaciÃ³n desplazada'
                        WHEN recpre.descuento_id = 19 then 11 -- 'Estudiantes de otras universidades'
                        WHEN recpre.descuento_id = 20 then 12 -- 'Extranjeros de paises de frontera'
                        WHEN recpre.descuento_id = 21 then 9 --'Estudiantes del Colegio IPARM'
                        WHEN recpre.descuento_id = 23 then 3 -- 'Funcionario de la UNAL'
                        WHEN recpre.descuento_id = 24 then 3 -- 'Contratista de la UNAL'
                        WHEN recpre.descuento_id = 26 then NULL --'Nivel asistencial u operativo'
                        WHEN recpre.descuento_id = 27 then NULL --'Nivel tÃ©cnico'
                        WHEN recpre.descuento_id = 28 then NULL --'Nivel profesional y EBBM'
                        WHEN recpre.descuento_id = 29 then NULL --'Nivel ejecutivo'
                        WHEN recpre.descuento_id = 30 then NULL --'Nivel asesor' -- ESTAS PERSONAS SALEN DE LA CONSULTA DEBIDO A TEMAS FUNCIONALES '' estan omitidos en en WHERE
                        WHEN recpre.descuento_id = 31
                            then NULL --'Docente'                     TODO: REEMPLAZAR NULOS POR LOS VALORES REQUERIDOS
                        WHEN recpre.descuento_id = NULL
                            then NULL --'Tarifa plena'
                        END                              AS Descuento,
                    -- *** las personas pueden aplicar a mas de un descuento a la vez Rta No
                    ao.tarifa as valor_inscripcion,
                    recpre.valor_pagado_usuario,
                    recpre.fecha_pago::date AS fecha_pago,        -- ****************************************** se puede tomar la fecha de inicio del curso ?
                    --- tomar fecha de pago del ultimo recibo
                    soportespago(preinscr.id)            AS NO_SOPORTE_DE_PAGO,
                    -- CONCATENAR LOS NUMEROS DE SOPORTES DE PAGO
                    (CASE WHEN preinscr.requiere_facturacion IS TRUE THEN 1667 ELSE 3732 END) AS TIPO_PAGO,
                    preinscr.id, --se puede revisar fecha de preinscripcion, identificador y estado
                    recpre.valor_materiales AS tarifa_materiales
        /* REVISAR, DADO QUE AQUI SE ESTA ASUMIENDO QUE SIALEX REPORTA PAGOS DEL TIPO Otro(ConsignaciÃ³n bancaria, Transferencia bancaria, cheque o factura) */
    FROM administracion_profile AS perf

             join administracion_ciudad ac ON ac.id = perf.ciudad_expedicion_documento_id
             join administracion_ciudad acnac ON acnac.id = perf.ciudad_nacimiento_id
             join administracion_region arnac ON arnac.id = acnac.region_id
             join administracion_pais apnac ON arnac.pais_id = apnac.id
             join administracion_region ar ON ar.id = ac.region_id
             join administracion_pais ap ON ar.pais_id = ap.id
             join auth_user au ON perf.usuario_id = au.id
             join administracion_preinscripcion preinscr on perf.id = preinscr.persona_id
             join administracion_preinscripcionhorariocurso prehc on preinscr.id = prehc.preinscripcion_ptr_id
             join administracion_recibopreinscripcion recpre on perf.id = recpre.preinscrito_id
                and recpre.preinscripcion_id = preinscr.id
             join administracion_matricula am ON perf.id = am.estudiante_id
             join administracion_grupoacademico ag ON (am.grupo_id = ag.id AND ag."horarioCurso_id" = prehc.horario_cupo_id)
             join administracion_horariocurso ahc ON prehc.horario_cupo_id = ahc.id
            join administracion_curso cur ON ahc.curso_id = cur.id
            join administracion_nivel nivel ON cur.nivel_id = nivel.id
            join administracion_ofertaacademica ao ON cur.oferta_academica_id = ao.id
            join administracion_periodo per ON ao.periodo_id = per.id        /*
    WHERE ag.nombre LIKE '%Introductorio%' AND (per.alias LIKE '2019%' OR per.alias LIKE '2020%' OR per.alias LIKE '2021%')
    */

    WHERE preinscr.estado_preinscripcion in (1, 3)
      AND preinscr.fecha_preinscripcion between fechaInicial and fechaFinal
      -- AND descap.descuento_id NOT IN ( 26, 27, 28, 29, 30 ) -- POR SOLICITUD ESPECIAL, LAS PERSONAS CON ESTOS DESCUENTOS NO VIAJAN POR EL WEB SERVICE Y LA DEPENDENCIA SE ENCARGA DE ENTREGARLOS A HERMES
    ORDER BY ID_SUB_PROYECTO_CURSO,
             Tipo_Documento, numero_documento, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
             sexo_biologico, estado_civil,
             fecha_nacimiento, Pais_Nacimiento, Departamento_Nacimiento, Ciudad_Naciemiento,
             Nivel_Formacion,
             direccion_residencia, Pais_Residencia, Departamento_Residencia, Ciudad_Residencia,
             Egresado_UN,
             Vinculacion,
             telefono_fijo,
             EXT,
             celular,
             au.email,
             VALOR_INSCRIPCION, fecha_pago,
             Descuento, NO_SOPORTE_DE_PAGO,
             TIPO_PAGO,
             preinscr.id
$$;
```

## version 1.12.0
### Update tipo de documento activo/no activo
``` sql
ALTER TABLE  administracion_tipodocumentoidentidad
    ADD COLUMN activo BOOLEAN default FALSE
```

### Update Datos Estudiantes Funcion
``` sql
create function datosestudiantes(fechainicial date, fechafinal date)
    returns TABLE(id_sub_proyecto_curso character varying, tipo_documento integer, numero_documento character varying, primer_nombre character varying, segundo_nombre character varying, primer_apellido character varying, segundo_apellido character varying, sexo_biologico integer, estado_civil integer, fecha_nacimiento date, pais_nacimiento integer, departamento_nacimiento integer, ciudad_nacimiento integer, nivel_formacion integer, egresado_un integer, vinculacion integer, telefono_fijo character varying, ext character varying, celular character varying, email character varying, direccion_residencia character varying, pais_residencia integer, departamento_residencia integer, ciudad_residencia integer, descuento integer, valor_inscripcion double precision, valor_pago double precision, fecha_pago date, no_soporte_de_pago character varying, tipo_pago integer, id integer, tarifa_materiales double precision)
    language sql
as
$$
SELECT ag.codigo_proyecto                   AS ID_SUB_PROYECTO_CURSO,
                    CASE
                        WHEN tipo_documento_id = 1 THEN 8 -- 'CC'
                        WHEN tipo_documento_id = 2 THEN 48 -- 'TI'
                        WHEN tipo_documento_id = 3 THEN 47 -- 'CE'
                        WHEN tipo_documento_id = 4 THEN 247 --'PT'
                        WHEN tipo_documento_id = 5 THEN 808 --'DE'
                        WHEN tipo_documento_id = 6 THEN 807 --'RC'
                        WHEN tipo_documento_id = 7 THEN 9 --'NIT'
                        WHEN tipo_documento_id = 8 THEN 241 --'CA'
                        WHEN tipo_documento_id = 9 THEN 246 --'NU'
                        END                              AS Tipo_Documento,
                    numero_documento,
                    primer_nombre,
                    segundo_nombre,
                    primer_apellido,
                    segundo_apellido,
                    CASE
                        WHEN perf.genero_sexual = 1 THEN 308 -- 'F'
                        WHEN perf.genero_sexual = 2 THEN 307 -- 'M'
                        END                              AS sexo_biologico,
                    CASE
                        WHEN perf.estado_civil = 1 THEN 810 -- SOLTERO(A)
                        WHEN perf.estado_civil = 2 THEN 811 -- CASADO (A)
                        WHEN perf.estado_civil = 3 THEN 812 -- DIVORCIADO (A)
                        WHEN perf.estado_civil = 4 THEN 813 -- VIUDO (A)
                        WHEN perf.estado_civil = 5 THEN 814 -- UNIÓN LIBRE
                        WHEN perf.estado_civil = 6 THEN 815 -- RELIGIOSO (A)
                        WHEN perf.estado_civil = 7 THEN 816 -- SEPARADO (A)
                        END                              AS estado_civil,
                    fecha_nacimiento,
                    apnac.id                             AS Pais_Nacimiento,
                    CASE
                        WHEN apnac.id = 47 THEN arnac.id
                        ELSE NULL
                        END                              AS Departamento_Nacimiento,
                    CASE
                        WHEN apnac.id = 47 THEN acnac.id
                        ELSE NULL
                        END                              AS Ciudad_Naciemiento,
                    CASE
                        WHEN perf.nivel_formacion = 1 THEN 15--'NO APLICA'
                        WHEN perf.nivel_formacion = 2 THEN 1 --'PREESCOLAR'
                        WHEN perf.nivel_formacion = 3 THEN 2 --'BÃSICA PRIMARIA'
                        WHEN perf.nivel_formacion = 4 THEN 3 --'BÃSICA SECUNDARIA'
                        WHEN perf.nivel_formacion = 5 THEN 4 --'BACHILLER'
                        WHEN perf.nivel_formacion = 6 THEN 5 --'FORMACIÃ“N TÃ‰CNICA PROFESIONAL'
                        WHEN perf.nivel_formacion = 7 THEN 6 --'TECNÃ“LOGO'
                        WHEN perf.nivel_formacion = 8 THEN 7 --'UNIVERSITARIA'
                        WHEN perf.nivel_formacion = 9 THEN 8 --'ESPECIALIZACIÃ“N TÃ‰CNICO PROFESIONAL'
                        WHEN perf.nivel_formacion = 10 THEN 9 --'ESPECIALIZACIÃ“N TECNOLÃ“GICA'
                        WHEN perf.nivel_formacion = 11 THEN 10 --'ESPECIALIZACIÃ“N UNIVERSITARIA'
                        WHEN perf.nivel_formacion = 12 THEN 11 --'ESPECIALIZACIÃ“N MÃ‰DICA'
                        WHEN perf.nivel_formacion = 13 THEN 12 --'MAESTRÃA'
                        WHEN perf.nivel_formacion = 14 THEN 13 --'DOCTORADO'
                        WHEN perf.nivel_formacion = 15 THEN 14 --'POSTDOCTORADO'
                        END                              AS Nivel_Formacion,
                    CASE
                        WHEN perf.es_egresado is true THEN 282 --'SI'
                        ELSE 283 --'NO'
                        END                              AS Egresado_UN,
                    CASE
                        WHEN perf.tipo_vinculacion_un = 1 THEN NULL--'NINGUNA'
                        WHEN perf.tipo_vinculacion_un = 2 THEN 647 -- 'ESTUDIANTE PREGRADO O POSGRADO'
                        WHEN perf.tipo_vinculacion_un = 4 THEN 648 -- 'EGRESADO'
                        WHEN perf.tipo_vinculacion_un = 5 THEN 649 -- 'PROFESOR'
                        WHEN perf.tipo_vinculacion_un = 6 THEN 650 -- 'ADMINISTRATIVO'
                        WHEN perf.tipo_vinculacion_un = 7 THEN 651 -- 'PARTICULAR'
                        END                              AS Vinculacion,
                    telefono_fijo                        AS telefono_fijo,
                    ''                                      EXT,
                    perf.telefono_celular                AS celular,
                    au.email,
                    direccion_residencia,
                    ap.id                                AS Pais_Residencia,
                    CASE
                        WHEN ap.id = 47 THEN ar.id
                        ELSE NULL
                        END                              AS Departamento_Residencia,
                    CASE
                        WHEN ap.id = 47 THEN ac.id
                        ELSE NULL
                        END                              AS Ciudad_Residencia,
                    CASE
                        WHEN recpre.descuento_id = 1 then 4 -- 'Estudiante pregrado UNAL'
                        WHEN recpre.descuento_id = 2 then 5 -- 'Estudiante de posgrado UNAL'
                        WHEN recpre.descuento_id = 3 then 3 -- 'Egresado de la Universidad Nacional de Colombia'
                        WHEN recpre.descuento_id = 4 then 3 -- 'Profesor de la UNAL'
                        WHEN recpre.descuento_id = 5 then 9 -- 'Hijo(a) de pensionado(a) UNAL'
                        WHEN recpre.descuento_id = 6 then 9 -- 'Hijo(a) de profesor(a) UNAL'
                        WHEN recpre.descuento_id = 8 then 9 -- 'Hijo(a) de funcionario(a) UNAL'
                        WHEN recpre.descuento_id = 9 then 9 -- 'Hijo(a) de contratista UNAL'
                        WHEN recpre.descuento_id = 10 then 9 -- 'Hijo(a) de estudiante UNAL'
                        WHEN recpre.descuento_id = 11 then 7 -- 'Grupos de 4 o mas personas'
                        WHEN recpre.descuento_id = 13 then 6 -- 'Personas que se inscriban en el marco de alianzas'
                        WHEN recpre.descuento_id = 14 then 10 --'Adultos mayores'
                        WHEN recpre.descuento_id = 15 then 10 -- 'NiÃ±os y adolescentes'
                        WHEN recpre.descuento_id = 16 then 10 -- 'Personas nivel 1 y 2 de l SISBEN'
                        WHEN recpre.descuento_id = 17 then 10 -- 'PoblaciÃ³n en situaciÃ³n de discapacidad'
                        WHEN recpre.descuento_id = 18 then 10 -- 'PoblaciÃ³n desplazada'
                        WHEN recpre.descuento_id = 19 then 11 -- 'Estudiantes de otras universidades'
                        WHEN recpre.descuento_id = 20 then 12 -- 'Extranjeros de paises de frontera'
                        WHEN recpre.descuento_id = 21 then 9 --'Estudiantes del Colegio IPARM'
                        WHEN recpre.descuento_id = 23 then 3 -- 'Funcionario de la UNAL'
                        WHEN recpre.descuento_id = 24 then 3 -- 'Contratista de la UNAL'
                        WHEN recpre.descuento_id = 26 then NULL --'Nivel asistencial u operativo'
                        WHEN recpre.descuento_id = 27 then NULL --'Nivel tÃ©cnico'
                        WHEN recpre.descuento_id = 28 then NULL --'Nivel profesional y EBBM'
                        WHEN recpre.descuento_id = 29 then NULL --'Nivel ejecutivo'
                        WHEN recpre.descuento_id = 30 then NULL --'Nivel asesor' -- ESTAS PERSONAS SALEN DE LA CONSULTA DEBIDO A TEMAS FUNCIONALES '' estan omitidos en en WHERE
                        WHEN recpre.descuento_id = 31
                            then NULL --'Docente'                     TODO: REEMPLAZAR NULOS POR LOS VALORES REQUERIDOS
                        WHEN recpre.descuento_id = NULL
                            then NULL --'Tarifa plena'
                        END                              AS Descuento,
                    -- *** las personas pueden aplicar a mas de un descuento a la vez Rta No
                    ao.tarifa as valor_inscripcion,
                    recpre.valor_requerido,
                    recpre.fecha_pago::date AS fecha_pago,        -- ****************************************** se puede tomar la fecha de inicio del curso ?
                    --- tomar fecha de pago del ultimo recibo
                    soportespago(preinscr.id)            AS NO_SOPORTE_DE_PAGO,
                    -- CONCATENAR LOS NUMEROS DE SOPORTES DE PAGO
                    (CASE WHEN preinscr.requiere_facturacion IS TRUE THEN 1667 ELSE 3732 END) AS TIPO_PAGO,
                    preinscr.id, --se puede revisar fecha de preinscripcion, identificador y estado
                    recpre.valor_materiales AS tarifa_materiales
        /* REVISAR, DADO QUE AQUI SE ESTA ASUMIENDO QUE SIALEX REPORTA PAGOS DEL TIPO Otro(ConsignaciÃ³n bancaria, Transferencia bancaria, cheque o factura) */
    FROM administracion_profile AS perf

             join administracion_ciudad ac ON ac.id = perf.ciudad_expedicion_documento_id
             join administracion_ciudad acnac ON acnac.id = perf.ciudad_nacimiento_id
             join administracion_region arnac ON arnac.id = acnac.region_id
             join administracion_pais apnac ON arnac.pais_id = apnac.id
             join administracion_region ar ON ar.id = ac.region_id
             join administracion_pais ap ON ar.pais_id = ap.id
             join auth_user au ON perf.usuario_id = au.id
             join administracion_preinscripcion preinscr on perf.id = preinscr.persona_id
             join administracion_preinscripcionhorariocurso prehc on preinscr.id = prehc.preinscripcion_ptr_id
             join administracion_recibopreinscripcion recpre on perf.id = recpre.preinscrito_id
                and recpre.preinscripcion_id = preinscr.id
             join administracion_matricula am ON perf.id = am.estudiante_id
             join administracion_grupoacademico ag ON (am.grupo_id = ag.id AND ag."horarioCurso_id" = prehc.horario_cupo_id)
             join administracion_horariocurso ahc ON prehc.horario_cupo_id = ahc.id
            join administracion_curso cur ON ahc.curso_id = cur.id
            join administracion_nivel nivel ON cur.nivel_id = nivel.id
            join administracion_ofertaacademica ao ON cur.oferta_academica_id = ao.id
            join administracion_periodo per ON ao.periodo_id = per.id        /*
    WHERE ag.nombre LIKE '%Introductorio%' AND (per.alias LIKE '2019%' OR per.alias LIKE '2020%' OR per.alias LIKE '2021%')
    */

    WHERE preinscr.estado_preinscripcion in (1, 3)
      AND preinscr.fecha_preinscripcion between fechaInicial and fechaFinal
      -- AND descap.descuento_id NOT IN ( 26, 27, 28, 29, 30 ) -- POR SOLICITUD ESPECIAL, LAS PERSONAS CON ESTOS DESCUENTOS NO VIAJAN POR EL WEB SERVICE Y LA DEPENDENCIA SE ENCARGA DE ENTREGARLOS A HERMES
    ORDER BY ID_SUB_PROYECTO_CURSO,
             Tipo_Documento, numero_documento, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
             sexo_biologico, estado_civil,
             fecha_nacimiento, Pais_Nacimiento, Departamento_Nacimiento, Ciudad_Naciemiento,
             Nivel_Formacion,
             direccion_residencia, Pais_Residencia, Departamento_Residencia, Ciudad_Residencia,
             Egresado_UN,
             Vinculacion,
             telefono_fijo,
             EXT,
             celular,
             au.email,
             VALOR_INSCRIPCION, fecha_pago,
             Descuento, NO_SOPORTE_DE_PAGO,
             TIPO_PAGO,
             preinscr.id
$$;
```

## version 1.11.0
###Migracion agregada para link de carga de documentos en un periodo academico
``` sql
ALTER TABLE administracion_informacionpreinscripcionformalizacion 
ADD COLUMN link_carga_documentos VARCHAR(300);
```

###Migracion codigo Hermes examen de clasificacion
``` sql
ALTER TABLE administracion_examenclasificacion ADD COLUMN codigo_proyecto INTEGER NULL;
```

###Migracion campo observaciones en preinscripcion
``` sql
ALTER TABLE administracion_preinscripcion ADD COLUMN observaciones TEXT NULL;
``` 


## version 1.10.4
``` sql
ALTER TABLE administracion_recibopreinscripcion
    ADD COLUMN valor_pagado_usuario DOUBLE PRECISION default 0;
```

``` sql
ALTER TABLE administracion_recibopreinscripcion
    ADD COLUMN valor_pagado_beca DOUBLE PRECISION default 0;
```

``` sql
ALTER TABLE administracion_recibopreinscripcion
    ADD COLUMN valor_pagado_descuento DOUBLE PRECISION default 0;
```

``` sql
ALTER TABLE administracion_recibopreinscripcion
    ADD COLUMN descuento_id INTEGER default NULL;
```

``` sql
ALTER TABLE administracion_recibopreinscripcion
    ADD COLUMN valor_pagado_saldo DOUBLE PRECISION default 0;
```

``` sql
ALTER TABLE administracion_recibopreinscripcion
    ADD COLUMN valor_materiales DOUBLE PRECISION default 0;
```

``` sql
ALTER TABLE  administracion_recibopreinscripcion
    ADD COLUMN fecha_pago timestamptz;
```

``` sql
ALTER TABLE  administracion_recibopreinscripcion
    ADD COLUMN migrado BOOLEAN default FALSE;
```

#### Update datos estudiantes funcion 
``` sql
create or replace function datosestudiantes(fechainicial date, fechafinal date)
    returns TABLE(id_sub_proyecto_curso character varying, tipo_documento integer, numero_documento character varying, primer_nombre character varying, segundo_nombre character varying, primer_apellido character varying, segundo_apellido character varying, sexo_biologico integer, estado_civil integer, fecha_nacimiento date, pais_nacimiento integer, departamento_nacimiento integer, ciudad_nacimiento integer, nivel_formacion integer, egresado_un integer, vinculacion integer, telefono_fijo character varying, ext character varying, celular character varying, email character varying, direccion_residencia character varying, pais_residencia integer, departamento_residencia integer, ciudad_residencia integer, descuento integer, valor_inscripcion double precision, valor_pago double precision, fecha_pago date, no_soporte_de_pago character varying, tipo_pago integer, id integer, tarifa_materiales double precision)
    language sql
as
$$
SELECT ag.codigo_proyecto                   AS ID_SUB_PROYECTO_CURSO,
                    CASE
                        WHEN tipo_documento_id = 1 THEN 8 -- 'CC'
                        WHEN tipo_documento_id = 2 THEN 48 -- 'TI'
                        WHEN tipo_documento_id = 3 THEN 47 -- 'CE'
                        WHEN tipo_documento_id = 4 THEN 247 --'PT'
                        END                              AS Tipo_Documento,
                    numero_documento,
                    primer_nombre,
                    segundo_nombre,
                    primer_apellido,
                    segundo_apellido,
                    CASE
                        WHEN perf.genero_sexual = 1 THEN 308 -- 'F'
                        WHEN perf.genero_sexual = 2 THEN 307 -- 'M'
                        END                              AS sexo_biologico,
                    CASE
                        WHEN perf.estado_civil = 1 THEN 810 -- SOLTERO(A)
                        WHEN perf.estado_civil = 2 THEN 811 -- CASADO (A)
                        WHEN perf.estado_civil = 3 THEN 812 -- DIVORCIADO (A)
                        WHEN perf.estado_civil = 4 THEN 813 -- VIUDO (A)
                        WHEN perf.estado_civil = 5 THEN 814 -- UNIÓN LIBRE
                        WHEN perf.estado_civil = 6 THEN 815 -- RELIGIOSO (A)
                        WHEN perf.estado_civil = 7 THEN 816 -- SEPARADO (A)
                        END                              AS estado_civil,
                    fecha_nacimiento,
                    apnac.id                             AS Pais_Nacimiento,
                    CASE
                        WHEN apnac.id = 47 THEN arnac.id
                        ELSE NULL
                        END                              AS Departamento_Nacimiento,
                    CASE
                        WHEN apnac.id = 47 THEN acnac.id
                        ELSE NULL
                        END                              AS Ciudad_Naciemiento,
                    CASE
                        WHEN perf.nivel_formacion = 1 THEN 15--'NO APLICA'
                        WHEN perf.nivel_formacion = 2 THEN 1 --'PREESCOLAR'
                        WHEN perf.nivel_formacion = 3 THEN 2 --'BÃSICA PRIMARIA'
                        WHEN perf.nivel_formacion = 4 THEN 3 --'BÃSICA SECUNDARIA'
                        WHEN perf.nivel_formacion = 5 THEN 4 --'BACHILLER'
                        WHEN perf.nivel_formacion = 6 THEN 5 --'FORMACIÃ“N TÃ‰CNICA PROFESIONAL'
                        WHEN perf.nivel_formacion = 7 THEN 6 --'TECNÃ“LOGO'
                        WHEN perf.nivel_formacion = 8 THEN 7 --'UNIVERSITARIA'
                        WHEN perf.nivel_formacion = 9 THEN 8 --'ESPECIALIZACIÃ“N TÃ‰CNICO PROFESIONAL'
                        WHEN perf.nivel_formacion = 10 THEN 9 --'ESPECIALIZACIÃ“N TECNOLÃ“GICA'
                        WHEN perf.nivel_formacion = 11 THEN 10 --'ESPECIALIZACIÃ“N UNIVERSITARIA'
                        WHEN perf.nivel_formacion = 12 THEN 11 --'ESPECIALIZACIÃ“N MÃ‰DICA'
                        WHEN perf.nivel_formacion = 13 THEN 12 --'MAESTRÃA'
                        WHEN perf.nivel_formacion = 14 THEN 13 --'DOCTORADO'
                        WHEN perf.nivel_formacion = 15 THEN 14 --'POSTDOCTORADO'
                        END                              AS Nivel_Formacion,
                    CASE
                        WHEN perf.es_egresado is true THEN 282 --'SI'
                        ELSE 283 --'NO'
                        END                              AS Egresado_UN,
                    CASE
                        WHEN perf.tipo_vinculacion_un = 1 THEN NULL--'NINGUNA'
                        WHEN perf.tipo_vinculacion_un = 2 THEN 647 -- 'ESTUDIANTE PREGRADO O POSGRADO'
                        WHEN perf.tipo_vinculacion_un = 4 THEN 648 -- 'EGRESADO'
                        WHEN perf.tipo_vinculacion_un = 5 THEN 649 -- 'PROFESOR'
                        WHEN perf.tipo_vinculacion_un = 6 THEN 650 -- 'ADMINISTRATIVO'
                        WHEN perf.tipo_vinculacion_un = 7 THEN 651 -- 'PARTICULAR'
                        END                              AS Vinculacion,
                    telefono_fijo                        AS telefono_fijo,
                    ''                                      EXT,
                    perf.telefono_celular                AS celular,
                    au.email,
                    direccion_residencia,
                    ap.id                                AS Pais_Residencia,
                    CASE
                        WHEN ap.id = 47 THEN ar.id
                        ELSE NULL
                        END                              AS Departamento_Residencia,
                    CASE
                        WHEN ap.id = 47 THEN ac.id
                        ELSE NULL
                        END                              AS Ciudad_Residencia,
                    CASE
                        WHEN recpre.descuento_id = 1 then 4 -- 'Estudiante pregrado UNAL'
                        WHEN recpre.descuento_id = 2 then 5 -- 'Estudiante de posgrado UNAL'
                        WHEN recpre.descuento_id = 3 then 3 -- 'Egresado de la Universidad Nacional de Colombia'
                        WHEN recpre.descuento_id = 4 then 3 -- 'Profesor de la UNAL'
                        WHEN recpre.descuento_id = 5 then 9 -- 'Hijo(a) de pensionado(a) UNAL'
                        WHEN recpre.descuento_id = 6 then 9 -- 'Hijo(a) de profesor(a) UNAL'
                        WHEN recpre.descuento_id = 8 then 9 -- 'Hijo(a) de funcionario(a) UNAL'
                        WHEN recpre.descuento_id = 9 then 9 -- 'Hijo(a) de contratista UNAL'
                        WHEN recpre.descuento_id = 10 then 9 -- 'Hijo(a) de estudiante UNAL'
                        WHEN recpre.descuento_id = 11 then 7 -- 'Grupos de 4 o mas personas'
                        WHEN recpre.descuento_id = 13 then 6 -- 'Personas que se inscriban en el marco de alianzas'
                        WHEN recpre.descuento_id = 14 then 10 --'Adultos mayores'
                        WHEN recpre.descuento_id = 15 then 10 -- 'NiÃ±os y adolescentes'
                        WHEN recpre.descuento_id = 16 then 10 -- 'Personas nivel 1 y 2 de l SISBEN'
                        WHEN recpre.descuento_id = 17 then 10 -- 'PoblaciÃ³n en situaciÃ³n de discapacidad'
                        WHEN recpre.descuento_id = 18 then 10 -- 'PoblaciÃ³n desplazada'
                        WHEN recpre.descuento_id = 19 then 11 -- 'Estudiantes de otras universidades'
                        WHEN recpre.descuento_id = 20 then 12 -- 'Extranjeros de paises de frontera'
                        WHEN recpre.descuento_id = 21 then 9 --'Estudiantes del Colegio IPARM'
                        WHEN recpre.descuento_id = 23 then 3 -- 'Funcionario de la UNAL'
                        WHEN recpre.descuento_id = 24 then 3 -- 'Contratista de la UNAL'
                        WHEN recpre.descuento_id = 26 then NULL --'Nivel asistencial u operativo'
                        WHEN recpre.descuento_id = 27 then NULL --'Nivel tÃ©cnico'
                        WHEN recpre.descuento_id = 28 then NULL --'Nivel profesional y EBBM'
                        WHEN recpre.descuento_id = 29 then NULL --'Nivel ejecutivo'
                        WHEN recpre.descuento_id = 30 then NULL --'Nivel asesor' -- ESTAS PERSONAS SALEN DE LA CONSULTA DEBIDO A TEMAS FUNCIONALES '' estan omitidos en en WHERE
                        WHEN recpre.descuento_id = 31
                            then NULL --'Docente'                     TODO: REEMPLAZAR NULOS POR LOS VALORES REQUERIDOS
                        WHEN recpre.descuento_id = NULL
                            then NULL --'Tarifa plena'
                        END                              AS Descuento,
                    -- *** las personas pueden aplicar a mas de un descuento a la vez Rta No
                    ao.tarifa as valor_inscripcion,
                    recpre.valor_requerido,
                    recpre.fecha_pago::date AS fecha_pago,        -- ****************************************** se puede tomar la fecha de inicio del curso ?
                    --- tomar fecha de pago del ultimo recibo
                    soportespago(preinscr.id)            AS NO_SOPORTE_DE_PAGO,
                    -- CONCATENAR LOS NUMEROS DE SOPORTES DE PAGO
                    1667                                 AS TIPO_PAGO,
                    preinscr.id, --se puede revisar fecha de preinscripcion, identificador y estado
                    recpre.valor_materiales AS tarifa_materiales
        /* REVISAR, DADO QUE AQUI SE ESTA ASUMIENDO QUE SIALEX REPORTA PAGOS DEL TIPO Otro(ConsignaciÃ³n bancaria, Transferencia bancaria, cheque o factura) */
    FROM administracion_profile AS perf

             join administracion_ciudad ac ON ac.id = perf.ciudad_expedicion_documento_id
             join administracion_ciudad acnac ON acnac.id = perf.ciudad_nacimiento_id
             join administracion_region arnac ON arnac.id = acnac.region_id
             join administracion_pais apnac ON arnac.pais_id = apnac.id
             join administracion_region ar ON ar.id = ac.region_id
             join administracion_pais ap ON ar.pais_id = ap.id
             join auth_user au ON perf.usuario_id = au.id
             join administracion_preinscripcion preinscr on perf.id = preinscr.persona_id
             join administracion_preinscripcionhorariocurso prehc on preinscr.id = prehc.preinscripcion_ptr_id
             join administracion_recibopreinscripcion recpre on perf.id = recpre.preinscrito_id
                and recpre.preinscripcion_id = preinscr.id
             join administracion_matricula am ON perf.id = am.estudiante_id
             join administracion_grupoacademico ag ON (am.grupo_id = ag.id AND ag."horarioCurso_id" = prehc.horario_cupo_id)
             join administracion_horariocurso ahc ON prehc.horario_cupo_id = ahc.id
            join administracion_curso cur ON ahc.curso_id = cur.id
            join administracion_nivel nivel ON cur.nivel_id = nivel.id
            join administracion_ofertaacademica ao ON cur.oferta_academica_id = ao.id
            join administracion_periodo per ON ao.periodo_id = per.id        /*
    WHERE ag.nombre LIKE '%Introductorio%' AND (per.alias LIKE '2019%' OR per.alias LIKE '2020%' OR per.alias LIKE '2021%')
    */

    WHERE preinscr.estado_preinscripcion in (1, 3)
      AND preinscr.fecha_preinscripcion between fechaInicial and fechaFinal
      AND preinscr.requiere_facturacion IS TRUE
      -- AND descap.descuento_id NOT IN ( 26, 27, 28, 29, 30 ) -- POR SOLICITUD ESPECIAL, LAS PERSONAS CON ESTOS DESCUENTOS NO VIAJAN POR EL WEB SERVICE Y LA DEPENDENCIA SE ENCARGA DE ENTREGARLOS A HERMES
    ORDER BY ID_SUB_PROYECTO_CURSO,
             Tipo_Documento, numero_documento, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
             sexo_biologico, estado_civil,
             fecha_nacimiento, Pais_Nacimiento, Departamento_Nacimiento, Ciudad_Naciemiento,
             Nivel_Formacion,
             direccion_residencia, Pais_Residencia, Departamento_Residencia, Ciudad_Residencia,
             Egresado_UN,
             Vinculacion,
             telefono_fijo,
             EXT,
             celular,
             au.email,
             VALOR_INSCRIPCION, fecha_pago,
             Descuento, NO_SOPORTE_DE_PAGO,
             TIPO_PAGO,
             preinscr.id
$$;
```

## version 1.9.0

``` sql
CREATE TABLE administracion_reportehermesconfiguracion (
	id uuid PRIMARY KEY NOT NULL,
	fecha_inicio DATE,
	fecha_final DATE
);
```

``` sql
ALTER TABLE administracion_matricula ADD COLUMN preinscripcion_generada_id integer;
```

``` sql
ALTER TABLE administracion_reportehermesconfiguracion OWNER TO sialex;
```

``` sql
INSERT INTO administracion_reportehermesconfiguracion (id, fecha_inicio, fecha_final) VALUES ('0e2b51a1-9646-423d-8796-75c18fb067db'::uuid, '2022-01-01'::date, '2022-12-31'::date);
```

``` sql
ALTER TABLE administracion_programaacademico ADD COLUMN para_ninios boolean;
```

``` sql
ALTER TABLE public.administracion_profile
ADD COLUMN direccion_sin_formato varchar(1000);
```

``` sql
update  public.administracion_profile
set direccion_sin_formato = CONCAT('||||||||||', direccion_residencia::varchar);
```

``` sql
CREATE TABLE public.administracion_discapacidad (
   id integer NOT NULL ,
   nombre character varying(200) NOT NULL
);
```

``` sql
CREATE SEQUENCE public.administracion_discapacidad_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
```

``` sql
ALTER TABLE public.administracion_discapacidad OWNER TO sialex;
```

``` sql
ALTER TABLE public.administracion_discapacidad_id_seq OWNER TO sialex;
```

``` sql
ALTER TABLE administracion_profile ADD COLUMN discapacidad_id integer;
```

``` sql
ALTER SEQUENCE public.administracion_discapacidad_id_seq OWNED BY public.administracion_discapacidad.id;
```

``` sql
INSERT INTO public.administracion_discapacidad (id, nombre) VALUES (1, 'Discapacidad Física');
INSERT INTO public.administracion_discapacidad (id, nombre) VALUES (2, 'Discapacidad Auditiva');
INSERT INTO public.administracion_discapacidad (id, nombre) VALUES (3, 'Discapacidad Visual');
INSERT INTO public.administracion_discapacidad (id, nombre) VALUES (4, 'Sordoceguera');
INSERT INTO public.administracion_discapacidad (id, nombre) VALUES (5, 'Discapacidad Intelectual');
INSERT INTO public.administracion_discapacidad (id, nombre) VALUES (6, 'Discapacidad Psicosocial (Mental)');
INSERT INTO public.administracion_discapacidad (id, nombre) VALUES (7, 'Discapacidad Múltiple');
INSERT INTO public.administracion_discapacidad (id, nombre) VALUES (8, 'Otra');
```

``` sql
ALTER TABLE ONLY public.administracion_discapacidad ALTER COLUMN id SET DEFAULT nextval('public.administracion_discapacidad_id_seq'::regclass);
```

``` sql
ALTER TABLE administracion_periodo ADD COLUMN fecha_calificacion DATE;
```

``` sql
ALTER TABLE administracion_periodo ADD COLUMN fecha_inicio DATE;
```

``` sql
ALTER TABLE administracion_periodo ADD COLUMN fecha_final DATE;
```

``` sql
ALTER TABLE administracion_periodo ADD COLUMN fecha_pendientes DATE;
```

### Migraciones agregadas a la tabla administracion_grupoacademico

``` sql
ALTER TABLE administracion_grupoacademico ADD COLUMN fecha_inicio DATE;
```

``` sql
ALTER TABLE administracion_grupoacademico ADD COLUMN fecha_final DATE;
```

``` sql
ALTER TABLE administracion_grupoacademico ADD COLUMN enlace_virtual TEXT;
```

