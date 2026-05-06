# SIALEX - Sistema de Información para Gestión de Cursos de Lenguas Extranjeras

SIALEX es un sistema de información diseñado para administrar, gestionar y controlar los cursos dictados en el departamento de lenguas extranjeras.

## Arquitectura (Modelo-Vista-Controlador / MVT en Django)

El proyecto se estructura con una arquitectura basada en componentes, equivalente al patrón Modelo-Vista-Controlador (MVC/MVP), adaptado al estilo Modelo-Vista-Template (MVT) natural de Django. Esta arquitectura fomenta la separación de responsabilidades y facilita la escalabilidad.

### Estructura de Carpetas Asociada
```text
sialex/
 ├── djsialex/                # Core principal y configuraciones de Django
 │    ├── administracion/     # Aplicación principal del sistema
 │    │    ├── models.py      # [MODELO]: Definición de datos y ORM asociado a la base de datos
 │    │    ├── views/         # [PRESENTADOR/CONTROLADOR]: Lógica de negocio y manejo de peticiones
 │    │    ├── templates/     # [VISTA]: (Ubicado en ../templates) Archivos HTML renderizados
 │    │    ├── forms/         # Validaciones y manejo de formularios
 │    │    ├── tests/         # Pruebas unitarias y de integración
 │    │    └── urls.py        # Enrutamiento de URLs a las Vistas/Presentadores
 │    ├── settings.py         # Configuraciones globales
 │    └── wsgi.py             # Entrypoint para servidores de producción (Gunicorn)
 ├── requirements.txt         # Dependencias del proyecto
 ├── Dockerfile               # Configuración para contenerización de la app
 └── docker-compose.yml       # Orquestador local con Nginx + Gunicorn
```

## Manual de Despliegue - Entorno de Desarrollo (Linux/Windows)

### Prerrequisitos
1. Python 3.6 o superior
2. Gestor de base de datos local (ej. PgAdmin4 o DataGrip)
3. `virtualenv` instalado

### Instrucciones paso a paso
1. **Configurar Base de Datos:**
   Verificar nombre de BD y datos de acceso en el archivo `settings.py`.
2. **Clonar proyecto:**
   ```bash
   git clone https://github.com/ivyduk/sialex.git
   ```
3. **Crear entorno virtual:**
   ```bash
   virtualenv -p python3.6 ve-sialex
   ```
4. **Activar entorno virtual:**
   * **Linux/Mac:** `source ve-sialex/bin/activate`
   * **Windows/VS Code PowerShell:** `.\ve-sialex\Scripts\activate` (Nota: Si hay problemas de permisos ejecutar `Set-ExecutionPolicy Unrestricted -Scope CurrentUser` como administrador).
5. **Instalar dependencias:**
   ```bash
   pip install -r sialex/requirements.txt
   ```
6. **Ejecutar migraciones y servidor local:**
   *Ir al directorio `sialex/djsialex/`*
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

  
