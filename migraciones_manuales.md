### version 1.8.0

``` sql
ALTER TABLE public.administracion_profile
ADD COLUMN direccion_sin_formato varchar(1000);
```

``` sql
update  public.administracion_profile
set direccion_sin_formato = CONCAT('||||||||||', direccion_residencia::varchar)
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
ALTER TABLE public.administracion_profile
ADD COLUMN discapacidad_id integer;
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


