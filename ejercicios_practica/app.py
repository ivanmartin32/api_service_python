#!/usr/bin/env python
'''
API Personas
---------------------------
Autor: Inove Coding School
Version: 1.2
 
Descripcion:
Se utiliza Flask para crear un WebServer que levanta los datos de
las personas registradas.

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

import numpy as np
from flask import Flask, request, jsonify, render_template, Response, redirect
import matplotlib
matplotlib.use('Agg')   # For multi thread, non-interactive backend (avoid run in main loop)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.image as mpimg

from persona import db
import persona

from config import config

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


@app.route("/")
def index():
    try:
        # Imprimir los distintos endopoints disponibles
        result = "<h1>Bienvenido!!</h1>"
        result += "<h2>Endpoints disponibles:</h2>"
        result += "<h3>[GET] /reset --> borrar y crear la base de datos</h3>"
        result += "<h3>[GET] /personas?limit=[]&offset=[] --> mostrar el listado de personas (limite and offset are optional)</h3>"
        result += "<h3>[POST] /registro --> ingresar nuevo registro de pulsaciones por JSON</h3>"
        result += "<h3>[GET] /comparativa --> mostrar un gráfico que compare cuantas personas hay de cada nacionalidad"
        
        return(result)
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/reset")
def reset():
    try:
        # Borrar y crear la base de datos
        persona.create_schema()
        result = "<h3>Base de datos re-generada!</h3>"
        return (result)
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/personas")
def personas():
    try:
        # Alumno:
        # Implementar la captura de limit y offset de los argumentos
        # de la URL
        # limit = ...
        # offset = ....
        limit_str = str(request.args.get('limit'))

        offset_str = str(request.args.get('offset'))

        # Debe verificar si el limit y offset son válidos cuando
        # no son especificados en la URL

        limit = 0
        offset = 0

        if (limit_str is not None) and ( limit_str.isdigit()):
            limit = int(limit_str)
        if (offset_str is not None) and (offset_str.isdigit()):
            offset = int(offset_str)

        result = persona.report(limit=limit, offset=offset)
        return jsonify(result)
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/comparativa")
def comparativa():
    try:
        # Alumno:

        x, y = persona.nationality_review()

        fig, ax = plt.subplots(figsize=(16, 9))
        ax.plot(x, y)
        ax.set_ylabel("Edad")
        ax.set_xlabel("ID")

        
        result = '''<h3>Implementar una función en persona.py
                    nationality_review</h3>'''
        result += '''<h3>El eje "X" del gráfico debe ser los IDs
                    de las personas y el eje "Y" deben ser sus
                    respectivas edades</h3>'''
        result += '''<h3>Esa funcion debe devolver los datos que necesite
                    para implementar el grafico a mostrar</h3>'''
        
        
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        plt.close(fig)  
        return Response(output.getvalue(), mimetype='image/png')

    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/registro", methods=['POST'])
def registro():
    if request.method == 'POST':
        try:
            # Alumno:
            # Obtener del HTTP POST JSON el nombre y los pulsos
            # name = ...
            # age = ...
            # nationality = ...

            # persona.insert(name, int(age), nationality)
            name = str(request.form.get('name'))
            age = str(request.form.get('age'))
            nationality = str(request.form.get('nationality'))

            persona.insert(name, int(age), nationality)

            return Response(status=200)
        
        except:
            return jsonify({'trace': traceback.format_exc()})
    

if __name__ == '__main__':
    print('Servidor arriba!')

    app.run(host=server_config['host'],
            port=server_config['port'],
            debug=True)
