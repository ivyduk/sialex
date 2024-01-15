### Queries reporte financiero Hermes 


#Query que filtra todos los estudiantes formalizados en un intervalo de tiempo específico
``` sql
SELECT
  profile.numero_documento,
  profile.primer_nombre,
  profile.primer_apellido,
  curso.nombre AS curso_inscrito
FROM
 administracion_profile AS profile
 JOIN administracion_preinscripcion AS preinscripcion ON profile.id = preinscripcion.persona_id
 JOIN administracion_preinscripcionhorariocurso AS preinscripcion_horario ON preinscripcion.id = preinscripcion_horario.preinscripcion_ptr_id
 JOIN administracion_horariocurso AS horario_curso ON preinscripcion_horario.horario_cupo_id = horario_curso.id
 JOIN administracion_curso AS curso ON horario_curso.curso_id = curso.id
WHERE
 preinscripcion.estado_preinscripcion IN (1, 3)
 AND preinscripcion.fecha_preinscripcion BETWEEN '2022-01-01' AND '2023-01-01'
 AND preinscripcion.requiere_facturacion IS TRUE;
 ```

#Query que filtra a todos los estudiantes  en un periodo de tiempo. Además filtra la información de descuento si el estudiante ha aplicado a alguno. 

``` sql	
SELECT
   profile.numero_documento,
   profile.primer_nombre,
   profile.primer_apellido,
   curso.nombre AS curso_inscrito,
   descap.descuento_id AS descuento_id,
   descuento.nombre AS nombre_descuento,
   descuento.porcentaje AS porcentaje_descuento
FROM
  administracion_profile AS profile
  JOIN administracion_preinscripcion AS preinscripcion ON profile.id = preinscripcion.persona_id
  JOIN administracion_preinscripcionhorariocurso AS preinscripcion_horario ON preinscripcion.id = preinscripcion_horario.preinscripcion_ptr_id
  JOIN administracion_horariocurso AS horario_curso ON preinscripcion_horario.horario_cupo_id = horario_curso.id
  JOIN administracion_curso AS curso ON horario_curso.curso_id = curso.id
  LEFT JOIN administracion_descuentoaplicado AS descap ON preinscripcion.id = descap.preinscripcion_generada_id
  LEFT JOIN administracion_descuento AS descuento ON descap.descuento_id = descuento.id
WHERE
  preinscripcion.estado_preinscripcion IN (1, 3)
  AND preinscripcion.fecha_preinscripcion BETWEEN '2022-01-01' AND '2023-01-01'
  AND preinscripcion.requiere_facturacion IS TRUE;
  ```
  
#Query Tarifa Plena: Query que filtra a todos los estudiantes  en un periodo de tiempo que no aplica  a ningún tipo de descuento, ni a ninguna beca y por lo tanto tienen tarifa plena.

``` sql
SELECT
 profile.numero_documento,
 profile.primer_nombre,
 profile.primer_apellido,
 curso.nombre AS curso_inscrito,
 descuento.nombre AS nombre_descuento
FROM
administracion_profile AS profile
JOIN administracion_preinscripcion AS preinscripcion ON profile.id = preinscripcion.persona_id
JOIN administracion_preinscripcionhorariocurso AS preinscripcion_horario ON preinscripcion.id = preinscripcion_horario.preinscripcion_ptr_id
JOIN administracion_horariocurso AS horario_curso ON preinscripcion_horario.horario_cupo_id = horario_curso.id
JOIN administracion_curso AS curso ON horario_curso.curso_id = curso.id
LEFT JOIN administracion_descuentoaplicado AS descap ON preinscripcion.id = descap.preinscripcion_generada_id
LEFT JOIN administracion_descuento AS descuento ON descap.descuento_id = descuento.id
WHERE
preinscripcion.estado_preinscripcion IN (1, 3)
AND preinscripcion.fecha_preinscripcion BETWEEN '2022-01-01' AND '2023-01-01'
AND preinscripcion.requiere_facturacion IS TRUE
AND descuento.nombre IS NULL;
``` 

#Query Tarifa Plena Cursos Niños: Query que filtra a todos los estudiantes de cursos dirigidos a niños  en un periodo de tiempo que no aplica  a ningún tipo de descuento, ni a ninguna beca y por lo tanto tienen tarifa plena.

``` sql
SELECT
profile.numero_documento,
profile.primer_nombre,
profile.primer_apellido,
curso.nombre AS curso_inscrito,
descuento.nombre AS nombre_descuento
FROM
administracion_profile AS profile
JOIN administracion_preinscripcion AS preinscripcion ON profile.id = preinscripcion.persona_id
JOIN administracion_preinscripcionhorariocurso AS preinscripcion_horario ON preinscripcion.id = preinscripcion_horario.preinscripcion_ptr_id
JOIN administracion_horariocurso AS horario_curso ON preinscripcion_horario.horario_cupo_id = horario_curso.id
JOIN administracion_curso AS curso ON horario_curso.curso_id = curso.id
LEFT JOIN administracion_descuentoaplicado AS descap ON preinscripcion.id = descap.preinscripcion_generada_id
LEFT JOIN administracion_descuento AS descuento ON descap.descuento_id = descuento.id
WHERE
preinscripcion.estado_preinscripcion IN (1, 3)
AND preinscripcion.fecha_preinscripcion BETWEEN '2022-01-01' AND '2023-01-01'
AND preinscripcion.requiere_facturacion IS TRUE
AND LOWER(curso.nombre) LIKE '%niños%';
``` 

 
#Query  Cursos ELE: Query que filtra a todos los estudiantes de cursos ELE  en un periodo de tiempo.

``` sql
SELECT
 profile.numero_documento,
 profile.primer_nombre,
 profile.primer_apellido,
 curso.nombre AS curso_inscrito
FROM
administracion_profile AS profile
JOIN administracion_preinscripcion AS preinscripcion ON profile.id = preinscripcion.persona_id
JOIN administracion_preinscripcionhorariocurso AS preinscripcion_horario ON preinscripcion.id = preinscripcion_horario.preinscripcion_ptr_id
JOIN administracion_horariocurso AS horario_curso ON preinscripcion_horario.horario_cupo_id = horario_curso.id
JOIN administracion_curso AS curso ON horario_curso.curso_id = curso.id
WHERE
preinscripcion.estado_preinscripcion IN (1, 3)
AND preinscripcion.fecha_preinscripcion BETWEEN '2022-01-01' AND '2023-01-01'
AND preinscripcion.requiere_facturacion IS TRUE
AND curso.nombre LIKE '%ELE%';
``` 


#Query Tipo Código: Query que filtra a todos los estudiantes formalizados en un periodo de tiempo. Filtrando por tipo de descuento.  
Query que ejemplifica el caso donde el tipo de descuento es el 
correspondiente al código 21(Estudiantes del colegio IPARM)

``` sql
SELECT
   profile.numero_documento,
   profile.primer_nombre,
   profile.primer_apellido,
   curso.nombre AS curso_inscrito,
   descap.descuento_id AS descuento_id,
   descuento.nombre AS nombre_descuento,
   descuento.porcentaje AS porcentaje_descuento
FROM
  administracion_profile AS profile
  JOIN administracion_preinscripcion AS preinscripcion ON profile.id = preinscripcion.persona_id
  JOIN administracion_preinscripcionhorariocurso AS preinscripcion_horario ON preinscripcion.id = preinscripcion_horario.preinscripcion_ptr_id
  JOIN administracion_horariocurso AS horario_curso ON preinscripcion_horario.horario_cupo_id = horario_curso.id
  JOIN administracion_curso AS curso ON horario_curso.curso_id = curso.id
  LEFT JOIN administracion_descuentoaplicado AS descap ON preinscripcion.id = descap.preinscripcion_generada_id
  LEFT JOIN administracion_descuento AS descuento ON descap.descuento_id = descuento.id
WHERE
  preinscripcion.estado_preinscripcion IN (1, 3)
  AND preinscripcion.fecha_preinscripcion BETWEEN '2022-01-01' AND '2023-01-01'
  AND preinscripcion.requiere_facturacion IS TRUE
  AND descap.descuento_id = 21;  --El codigo 21 es estudiante del IPARM
  ``` 


Los diferentes tipos de descuento los podemos ver en la tabla administracion_descuento con la siguiente query 

``` sql
SELECT id, nombre
FROM administracion_descuento;
``` 
el resultado muestra los ids y nombres de los diferentes descuentos.

#Códigos de descuento

ID    nombre 
4     Profesor de la UNAL
5     Hijo(a) de pensionado(a) UNAL
6     Hijo(a) de profesor(a) UNAL
8     Hijo(a) de funcionario(a) UNAL
10   Hijo(a) de estudiante UNAL
23   Funcionario de la UNAL
1     Estudiante pregrado UNAL
14   Adultos mayores
15   Niños y adolescentes
21   Estudiantes del Colegio IPARM
17   Población en situación de discapacidad
18   Población desplazada
19   Estudiantes de otras universidades
24   Contratista de la UNAL
3     Egresado de la Universidad Nacional de Colombia
16   Personas nivel 1 y 2 del SISBEN
9     Hijo(a) de contratista UNAL
11   Grupos de 4 o más personas
2     Estudiante de posgrado UNAL
20   Extranjeros de países de frontera
13   Personas que se inscriban en el marco de alianzas
27   Funcionario UNAL - Nivel técnico
30   Funcionario UNAL - Nivel asesor
31   Funcionario UNAL - Docente
29   Funcionario UNAL - Nivel ejecutivo
28   Funcionario UNAL - Nivel profesional y EBBM
26   Funcionario UNAL - Nivel asistencial u operativo

Nota:  En la linea  AND descap.descuento_id = 21;     
           reemplazar 21 por el código que se quiera consultar en la lista anterior.


#Query Tipo Like: Query que filtra estudiantes preinscritos por diferentes tipos de cursos como dirigidos a niños o de cierto idioma. 

Ejemplo query que filtra todos los cursos de francés para niños(recordar las tildes en el texto que se quiere filtrar del curso)

``` sql
SELECT
  profile.numero_documento,
  profile.primer_nombre,
  profile.primer_apellido,
  curso.nombre AS curso_inscrito
FROM
  administracion_profile AS profile
  JOIN administracion_preinscripcion AS preinscripcion ON profile.id = preinscripcion.persona_id
  JOIN administracion_preinscripcionhorariocurso AS preinscripcion_horario ON preinscripcion.id = preinscripcion_horario.preinscripcion_ptr_id
  JOIN administracion_horariocurso AS horario_curso ON preinscripcion_horario.horario_cupo_id = horario_curso.id
  JOIN administracion_curso AS curso ON horario_curso.curso_id = curso.id
WHERE
  preinscripcion.estado_preinscripcion IN (1, 3) --Inscrito y pendiente
  AND preinscripcion.fecha_preinscripcion BETWEEN '2022-01-01' AND '2023-01-01'
  AND preinscripcion.requiere_facturacion IS TRUE
  AND LOWER(curso.nombre) LIKE '%francés%'
  AND LOWER(curso.nombre) LIKE '%niños%';
  ``` 


#Query Tipo Beca: Query que filtra estudiantes que tengan alguna beca aplicada(hay dos tipos de beca media beca y media media beca)

``` sql
SELECT
 beca.financiero_ptr_id AS beneficiario_id,
 beneficiario.numero_documento AS numero_documento,
 beneficiario.primer_nombre AS primer_nombre,
 beneficiario.primer_apellido AS primer_apellido,
 curso.nombre AS curso_inscrito,
 tipo_beca.nombre AS tipo_de_beca,
 'aplicada' AS estado_beca
FROM
 administracion_beca AS beca
 JOIN administracion_financiero AS financiero ON beca.financiero_ptr_id = financiero.id
 JOIN administracion_profile AS beneficiario ON financiero.beneficiario_id = beneficiario.id
 JOIN administracion_preinscripcion AS preinscripcion ON beneficiario.id = preinscripcion.persona_id
 JOIN administracion_preinscripcionhorariocurso AS preinscripcion_horario ON preinscripcion.id = preinscripcion_horario.preinscripcion_ptr_id
 JOIN administracion_horariocurso AS horario_curso ON preinscripcion_horario.horario_cupo_id = horario_curso.id
 JOIN administracion_curso AS curso ON horario_curso.curso_id = curso.id
 JOIN administracion_tipobeca AS tipo_beca ON beca.tipo_beca_id = tipo_beca.id
WHERE
   preinscripcion.estado_preinscripcion IN (1, 3)
  AND preinscripcion.fecha_preinscripcion BETWEEN '2022-01-01' AND '2023-01-01'
  AND preinscripcion.requiere_facturacion IS TRUE
  AND beca.estado_beca = 3
GROUP BY
 beca.financiero_ptr_id,
 beneficiario.numero_documento,
 beneficiario.primer_nombre,
 beneficiario.primer_apellido,
 curso.nombre,
 tipo_beca.nombre;
``` 

#Query de estudiantes que tiene una beca junto con una columna donde se muestra si aplica o no a algún tipo de descuento.

``` sql
SELECT
 beca.financiero_ptr_id AS beneficiario_id,
 beneficiario.numero_documento AS numero_documento,
 beneficiario.primer_nombre AS primer_nombre,
 beneficiario.primer_apellido AS primer_apellido,
 curso.nombre AS curso_inscrito,
 tipo_beca.nombre AS tipo_de_beca,
 descuento.nombre AS nombre_descuento
FROM
 administracion_beca AS beca
 JOIN administracion_financiero AS financiero ON beca.financiero_ptr_id = financiero.id
 JOIN administracion_profile AS beneficiario ON financiero.beneficiario_id = beneficiario.id
 JOIN administracion_preinscripcion AS preinscripcion ON beneficiario.id = preinscripcion.persona_id
 JOIN administracion_preinscripcionhorariocurso AS preinscripcion_horario ON preinscripcion.id = preinscripcion_horario.preinscripcion_ptr_id
 JOIN administracion_horariocurso AS horario_curso ON preinscripcion_horario.horario_cupo_id = horario_curso.id
 JOIN administracion_curso AS curso ON horario_curso.curso_id = curso.id
 JOIN administracion_tipobeca AS tipo_beca ON beca.tipo_beca_id = tipo_beca.id
 LEFT JOIN administracion_descuentoaplicado AS descap ON preinscripcion.id = descap.preinscripcion_generada_id
 LEFT JOIN administracion_descuento AS descuento ON descap.descuento_id = descuento.id
WHERE
   preinscripcion.estado_preinscripcion IN (1, 3)
 AND preinscripcion.fecha_preinscripcion BETWEEN '2022-01-01' AND '2023-01-01'
 AND preinscripcion.requiere_facturacion IS TRUE
 AND beca.estado_beca = 3  --Estado de beca "aplicada"
GROUP BY
 beca.financiero_ptr_id,
 beneficiario.numero_documento,
 beneficiario.primer_nombre,
 beneficiario.primer_apellido,
 curso.nombre,
 tipo_beca.nombre,
 descuento.nombre;
 ``` 

 
#Query Tipo Beca-Descuento: Query para filtrar estudiantes que tengan beca y algún tipo de descuento(esto con el fin de calcular el  porcentaje total de descuento )

``` sql
SELECT
 beca.financiero_ptr_id AS beneficiario_id,
 beneficiario.numero_documento AS numero_documento,
 beneficiario.primer_nombre AS primer_nombre,
 beneficiario.primer_apellido AS primer_apellido,
 curso.nombre AS curso_inscrito,
 tipo_beca.nombre AS tipo_de_beca,
 descuento.nombre AS nombre_descuento
FROM
 administracion_beca AS beca
 JOIN administracion_financiero AS financiero ON beca.financiero_ptr_id = financiero.id
 JOIN administracion_profile AS beneficiario ON financiero.beneficiario_id = beneficiario.id
 JOIN administracion_preinscripcion AS preinscripcion ON beneficiario.id = preinscripcion.persona_id
 JOIN administracion_preinscripcionhorariocurso AS preinscripcion_horario ON preinscripcion.id = preinscripcion_horario.preinscripcion_ptr_id
 JOIN administracion_horariocurso AS horario_curso ON preinscripcion_horario.horario_cupo_id = horario_curso.id
 JOIN administracion_curso AS curso ON horario_curso.curso_id = curso.id
 JOIN administracion_tipobeca AS tipo_beca ON beca.tipo_beca_id = tipo_beca.id
 JOIN administracion_descuentoaplicado AS descap ON preinscripcion.id = descap.preinscripcion_generada_id
 JOIN administracion_descuento AS descuento ON descap.descuento_id = descuento.id
WHERE
   preinscripcion.estado_preinscripcion IN (1, 3)
 AND preinscripcion.fecha_preinscripcion BETWEEN '2022-01-01' AND '2023-01-01'
 AND preinscripcion.requiere_facturacion IS TRUE
 AND beca.estado_beca = 3  --Estado de beca "aplicada"
GROUP BY
 beca.financiero_ptr_id,
 beneficiario.numero_documento,
 beneficiario.primer_nombre,
 beneficiario.primer_apellido,
 curso.nombre,
 tipo_beca.nombre,
 descuento.nombre;
 ``` 


#Query que filtra los curso donde se exigen materiales 

``` sql
SELECT
 curso.nombre AS curso_con_materiales,
 nivel.nombre AS nombre_nivel
FROM
 administracion_curso AS curso
 JOIN administracion_nivel AS nivel ON curso.nivel_id = nivel.id
WHERE
 nivel.costo_materiales > 0;
 ``` 
   
#Query Materiales: Query que filtra los estudiantes inscritos en cursos pertenecientes a niveles donde se piden materiales

``` sql	
	SELECT   
  profile.numero_documento,
  profile.primer_nombre,
  profile.primer_apellido,
  curso.nombre AS curso_inscrito,
  nivel.costo_materiales
FROM
 administracion_profile AS profile
 JOIN administracion_preinscripcion AS preinscripcion ON profile.id = preinscripcion.persona_id
 JOIN administracion_preinscripcionhorariocurso AS preinscripcion_horario ON preinscripcion.id = preinscripcion_horario.preinscripcion_ptr_id
 JOIN administracion_horariocurso AS horario_curso ON preinscripcion_horario.horario_cupo_id = horario_curso.id
 JOIN administracion_curso AS curso ON horario_curso.curso_id = curso.id
 JOIN administracion_nivel AS nivel ON curso.nivel_id = nivel.id  -- Agregar un JOIN a la tabla Nivel
WHERE
 preinscripcion.estado_preinscripcion IN (1, 3)
 AND preinscripcion.fecha_preinscripcion BETWEEN '2022-01-01' AND '2023-01-01'
 AND preinscripcion.requiere_facturacion IS TRUE
 AND nivel.costo_materiales > 0;  -- Filtrar por cursos que requieren materiales
```

#Query Materiales Cursos IPARM: Query que filtra los estudiantes inscritos en cursos dirigidos  estudiantes del IPARM  pertenecientes a niveles donde se piden materiales.

``` sql	
	SELECT
 profile.numero_documento,
 profile.primer_nombre,
 profile.primer_apellido,
 curso.nombre AS curso_inscrito,
 nivel.costo_materiales
FROM
administracion_profile AS profile
JOIN administracion_preinscripcion AS preinscripcion ON profile.id = preinscripcion.persona_id
JOIN administracion_preinscripcionhorariocurso AS preinscripcion_horario ON preinscripcion.id = preinscripcion_horario.preinscripcion_ptr_id
JOIN administracion_horariocurso AS horario_curso ON preinscripcion_horario.horario_cupo_id = horario_curso.id
JOIN administracion_curso AS curso ON horario_curso.curso_id = curso.id
JOIN administracion_nivel AS nivel ON curso.nivel_id = nivel.id  -- Agregar un JOIN a la tabla Nivel
WHERE
preinscripcion.estado_preinscripcion IN (1, 3)
AND preinscripcion.fecha_preinscripcion BETWEEN '2022-01-01' AND '2023-01-01'
AND preinscripcion.requiere_facturacion IS TRUE
AND UPPER(curso.nombre) LIKE '%IPARM%'
AND nivel.costo_materiales > 0;
``` 

#Query Examen Clasificación:  Query que filtra todos los estudiantes preinscritos en un examen de clasificación en un periodo de tiempo.

``` sql
SELECT
 profile.numero_documento,
 profile.primer_nombre,
 profile.primer_apellido,
 examen_clasificacion.nombre AS curso_inscrito
FROM
administracion_profile AS profile
JOIN administracion_preinscripcion AS preinscripcion ON profile.id = preinscripcion.persona_id
JOIN administracion_preinscripcionexamen AS preinscripcion_examen ON preinscripcion.id = preinscripcion_examen.preinscripcion_ptr_id
JOIN administracion_examenclasificacion AS examen_clasificacion ON preinscripcion_examen.examen_id = examen_clasificacion.id
WHERE
preinscripcion.estado_preinscripcion IN (1, 3)
AND preinscripcion.fecha_preinscripcion BETWEEN '2022-01-01' AND '2023-01-01'
AND preinscripcion.requiere_facturacion IS TRUE;
```
