Manual de despligue entorno de desarrollo.

1. Instalar Python 3.6 > 
2. Instalar programa Virtualenv
3. Instalar getText (Fedora)
4. Clonar el proyecto: ssh git@168.176.84.61:idioma/sialex.git
5. Crear entorno virtual 
   Comando: virtualenv -p python3.6 ve-sialex
6. Activar entorno virtual
   Comando: source ve-sialex/bin/activate
7. En el entorno virtual, instalar dependencias:
   pip install -r sialex/requirements.txt
8. Corre aplicación por consola en directorio sialex/djsialex/
   Comando: python manage.py makemigrations
   Comando: python manage.py migrate
   Comando: python manage.py createsuperuser
   Comando: python manage.py runserver
  
   