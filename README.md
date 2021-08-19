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
2. Instalar PgAdmin4 o DataGrip: Recomendado tener la base de datos local para ambiente de desarrollo
3. Verificar nombre de base de datos y datos de acceso en archivo settings.py que coincidan con la configuracion ![image](https://user-images.githubusercontent.com/84890580/130123437-6659c3f9-a6ce-4f81-b192-60fc7895fc3c.png)
4. Instalar programa Virtualenv (verificar que la version sea para Python 3.6 o compatible)
5. Instalar Visual Studio Code
   Para poder ejecutar en consola de VS Code, seguir https://es.stackoverflow.com/questions/321611/problema-con-scripts-en-visual-studio-code con permisos de Administrador
4. Clonar el proyecto: ssh https://github.com/desarrollofchbog/sialex.git
5. Crear entorno virtual 
   Comando: virtualenv -p python3.6 ve-sialex
6. Activar entorno virtual
   ir a la ruta ve-sialex/Scritps
   Ejecutar: ./activate
   Ejemplo
   -> PS C:\Users\CompuGamer\Documents\ve-sialex\Scripts> ./activate
7. En el entorno virtual, instalar dependencias:
   pip install -r sialex/requirements.txt
8. Corre aplicación por consola en directorio sialex/djsialex/
   Comando: python manage.py makemigrations
   Comando: python manage.py migrate
   Comando: python manage.py createsuperuser
   Comando: python manage.py runserver
   
   Ejemplo: python .\manage.py runserver

  
