from django.http import HttpResponse
import csv

class CSVWriter:

    """
        data: Diccionario de la forma {i: [fila1, fila2, ..., fila n]}
        header: Lista de la forma: [titulo1, titulo2, ..., titulo n]
        file_name: Nombre del archivo de salida
    """
    def download_csv_file(self, data, header, file_name):

        if not file_name or file_name == '':
            file_name = 'salida'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="' + file_name + '.csv"'

        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))

        writer.writerow([title for title in header])

        for d in data:
            writer.writerow([d] + data[d])

        return response