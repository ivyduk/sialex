from datetime import datetime

# Diccionario de abreviaturas a nombres de días completos
DIAS_MAP = {
    "LU": "Lunes",
    "MA": "Martes",
    "MC": "Miércoles",
    "JU": "Jueves",
    "VI": "Viernes",
    "SA": "Sábado",
    "DO": "Domingo"
}

# Orden correcto de los días para detección de secuencias
DIAS_ORDEN = ["LU", "MA", "MC", "JU", "VI", "SA", "DO"]

def formatear_hora(hora_str):
    hora = datetime.strptime(hora_str, "%H:%M")
    return hora.strftime("%I%p").lstrip("0").replace("AM", "AM").replace("PM", "PM")

def humanizar_horario(cadena):
    try:
        cadena_lista = cadena.split(":")
        horario, dias = cadena_lista[0] + ':' + cadena_lista[1] + ':' + cadena_lista[2], cadena_lista[3]
        # Extraer hora de inicio y fin, y los días
        hora_inicio, hora_fin = horario.split("-")
        dias_abrev = dias.split(",")

        # Ordenar los días según la semana
        dias_ordenados = sorted(dias_abrev, key=lambda x: DIAS_ORDEN.index(x))

        if len(dias_ordenados) == 1:
            dias_str = DIAS_MAP[dias_ordenados[0]]
        else:
            # Detectar si son consecutivos
            indices = [DIAS_ORDEN.index(d) for d in dias_ordenados]
            consecutivos = all(indices[i] + 1 == indices[i+1] for i in range(len(indices) - 1))

            if consecutivos:
                dias_str = f"{DIAS_MAP[dias_ordenados[0]]} a {DIAS_MAP[dias_ordenados[-1]]}"
            else:
                # Separar con coma y 'y' al final si son múltiples días no consecutivos
                nombres_dias = [DIAS_MAP[d] for d in dias_ordenados]
                if len(nombres_dias) == 2:
                    dias_str = " y ".join(nombres_dias)
                else:
                    dias_str = ", ".join(nombres_dias[:-1]) + " y " + nombres_dias[-1]

        return f"{dias_str} de {formatear_hora(hora_inicio)} a {formatear_hora(hora_fin)}"
    
    except Exception as e:
        print(f"Error al procesar la cadena '{cadena}': {e}")
        return f"[Formato inválido: {cadena}]"