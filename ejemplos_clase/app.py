#!/usr/bin/env python
'''
API Monitor cardíaco
---------------------------
Autor: Inove Coding School
Version: 1.2
 
Descripcion:
Se utiliza Flask para crear un WebServer que levanta los datos de
las personas que registran su ritmo cardíaco.

Ejecución: Lanzar el programa y abrir en un navegador la siguiente dirección URL
NOTA: Si es la primera vez que se lanza este programa crear la base de datos
entrando a la siguiente URL
http://127.0.0.1:5000/reset

Ingresar a la siguiente URL para ver los endpoints disponibles
http://127.0.0.1:5000/
'''

__author__ = "Inove Coding School"
__email__ = "INFO@INOVE.COM.AR"
__version__ = "1.2"

# Realizar HTTP POST --> post.py

import traceback
import io
import sys
import os
import base64
import json
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

from flask import Flask, request, jsonify, render_template, Response, redirect
import matplotlib
matplotlib.use('Agg')   # Para multi-thread, non-interactive backend (avoid run in main loop)
import matplotlib.pyplot as plt
# Para convertir matplotlib a imagen y luego a datos binarios
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.image as mpimg

from heart import db
import heart

from config import config

# Crear el server Flask
app = Flask(__name__)

# Obtener la path de ejecución actual del script
script_path = os.path.dirname(os.path.realpath(__file__))

# Obtener los parámetros del archivo de configuración
config_path_name = os.path.join(script_path, 'config.ini')
db_config = config('db', config_path_name)
server_config = config('server', config_path_name)

# Indicamos al sistema (app) de donde leer la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_config['database']}"
# Asociamos nuestro controlador de la base de datos con la aplicacion
db.init_app(app)


# Ruta que se ingresa por la ULR 127.0.0.1:5000
@app.route("/")
def index():
    try:
        # Imprimir los distintos endopoints disponibles
        result = "<h1>Bienvenido!!</h1>"
        result += "<h2>Endpoints disponibles:</h2>"
        result += "<h3>[GET] /reset --> borrar y crear la base de datos</h3>"
        result += "<h3>[GET] /pulsaciones?limit=[]&offset=[] --> mostrar últimas pulsaciones registradas (limite and offset are optional)</h3>"
        result += "<h3>[GET] /pulsaciones/{name}/historico --> mostrar el histórico de pulsaciones de una persona</h3>"
        result += "<h3>[POST] /registro --> ingresar nuevo registro de pulsaciones por JSON</h3>"
        return(result)
    except:
        return jsonify({'trace': traceback.format_exc()})

# Ruta que se ingresa por la ULR 127.0.0.1:5000/reset
@app.route("/reset")
def reset():
    try:
        # Borrar y crear la base de datos
        heart.create_schema()
        result = "<h3>Base de datos re-generada!</h3>"
        return (result)
    except:
        return jsonify({'trace': traceback.format_exc()})

# Ruta que se ingresa por la ULR 127.0.0.1:5000/pulsaciones
@app.route("/pulsaciones")
def pulsaciones():
    try:
        # Obtener de la query string los valores de limit y offset
        limit_str = str(request.args.get('limit'))
        offset_str = str(request.args.get('offset'))

        limit = 0
        offset = 0

        if(limit_str is not None) and (limit_str.isdigit()):
            limit = int(limit_str)

        if(offset_str is not None) and (offset_str.isdigit()):
            offset = int(offset_str)

        # Obtener el reporte
        data = heart.report(limit=limit, offset=offset)

        # Transformar json a json string
        return jsonify(data)
    except:
        return jsonify({'trace': traceback.format_exc()})


# Ruta que se ingresa por la ULR 127.0.0.1:5000/pulsaciones/{nombre}/historico
@app.route("/pulsaciones/<name>/historico")
def pulsaciones_historico(name):
    try:
        # Obtener el historial de la persona
        time, heartrate = heart.chart(name)

        # Crear el grafico que se desea mostrar
        fig, ax = plt.subplots(figsize=(16, 9))
        ax.plot(time, heartrate)
        ax.get_xaxis().set_visible(False)

        # Convertir ese grafico en una imagen para enviar por HTTP
        # y mostrar en el HTML
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        plt.close(fig)  # Cerramos la imagen para que no consuma memoria del sistema
        return Response(output.getvalue(), mimetype='image/png')
    except:
        return jsonify({'trace': traceback.format_exc()})

# Ruta que se ingresa por la ULR 127.0.0.1:5000/registro
@app.route("/registro", methods=['POST'])
def registro():
    if request.method == 'POST':
        # Obtener del HTTP POST JSON el nombre y los pulsos
        nombre = str(request.form.get('name'))
        pulsos = str(request.form.get('heartrate'))

        if(nombre is None or pulsos is None or pulsos.isdigit() is False):
            # Datos ingresados incorrectos
                return Response(status=400)
        time = datetime.now()
        heart.insert(time, nombre, int(pulsos))
        return Response(status=200)


if __name__ == '__main__':
    print('Inove@Monitor Cardíaco start!')

    # Lanzar server
    app.run(host=server_config['host'],
            port=server_config['port'],
            debug=True)
