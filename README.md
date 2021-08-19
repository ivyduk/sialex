rebase

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
  
   
  Despliegue en Windows + VS CODE
1. Instalar Python 3.6 > 
2. Instalar programa Virtualenv
3. Instalar Visual Studio Code
   Para poder ejecutar en consola de VS Code, seguir https://es.stackoverflow.com/questions/321611/problema-con-scripts-en-visual-studio-code con permisos de Administrador
4. Clonar el proyecto: ssh https://github.com/desarrollofchbog/sialex.git
5. Crear entorno virtual 
   Comando: virtualenv -p python3.6 ve-sialex
6. Activar entorno virtual
   ir a la ruta ve-sialex/Scritps
   Comando: source ./activate
7. En el entorno virtual, instalar dependencias:
   pip install -r sialex/requirements.txt
8. Corre aplicación por consola en directorio sialex/djsialex/
   Comando: python manage.py makemigrations
   Comando: python manage.py migrate
   Comando: python manage.py createsuperuser
   Comando: python manage.py runserver

  
