import pandas as pd
import logging
import os
import sys
import django
from django.db import transaction
from django.db.models import Q  # Para mejorar la búsqueda

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Asegura la ruta del proyecto
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djsialex.settings")  # Reemplaza con el nombre correcto de tu proyecto
django.setup()

from administracion.models import Region, Ciudad  # Importamos los modelos de Django


# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def cargar_datos():
    # Cargar archivo Hermes-Colombia
    hermes_df = pd.read_csv("tmp/Hermes-Colombia.csv")
    return hermes_df


def normalizar_nombre(nombre):
    return nombre.strip().lower()


def actualizar_regiones(hermes_df):
    sin_coincidencia = []

    with transaction.atomic():  # Asegurar integridad de la base de datos
        for index, row in hermes_df.iterrows():
            hermes_id = row["ID"]
            tipo = row["SUPER_TIPO"]
            nombre = normalizar_nombre(row["NOMBRE"])

            if tipo == 2:
                region = Region.objects.filter(Q(nombre__iexact=nombre) | Q(nombre__icontains=nombre)).first()
                if region:
                    region.hermes_id = hermes_id
                    region.save()
                else:
                    sin_coincidencia.append({"archivo_id": hermes_id, "tipo": tipo, "nombre": nombre, "error": "Departamento no encontrado"})
                    logging.info("Region sin coincidencia. archivo id: {}".format(hermes_id))
            elif tipo != 1 and tipo != 0:
                ciudad = Ciudad.objects.filter(Q(nombre__iexact=nombre) | Q(nombre__icontains=nombre)).first()
                if ciudad:
                    ciudad.hermes_id = hermes_id
                    ciudad.save()
                else:
                    sin_coincidencia.append({"archivo_id": hermes_id, "tipo": tipo, "nombre": nombre, "error": "Ciudad no encontrada"})
                    logging.info("Ciudad Sin coincidencia. archivo id: {}".format(hermes_id))

    return sin_coincidencia


def guardar_resultados(sin_coincidencia):
    pd.DataFrame(sin_coincidencia).to_csv("tmp/registros_sin_coincidencia.csv", index=False)
    logging.info("Proceso finalizado. Archivo de registros sin coincidencia guardado.")


if __name__ == "__main__":
    hermes_df = cargar_datos()
    sin_coincidencia = actualizar_regiones(hermes_df)
    guardar_resultados(sin_coincidencia)
