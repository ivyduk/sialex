FROM python:3.6-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update \
    && apt-get install -y gcc libpq-dev gettext \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY sialex/requirements.txt /app/

# Instalar librerías de python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

# Copiar proyecto
COPY sialex/ /app/

WORKDIR /app/djsialex

# Comando gunicorn por defecto
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "djsialex.wsgi:application"]
