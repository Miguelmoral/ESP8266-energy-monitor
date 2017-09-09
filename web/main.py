from flask import Flask
from flask import request, session
from pymongo import MongoClient
from flask import render_template
import time
import datetime
#from datetime import datetime
from pytz import timezone
import pytz
import json
from flask import Blueprint
from flask_paginate import Pagination
import calendar

client = MongoClient('localhost',27017)
db = client.test

app = Flask(__name__)
app.secret_key = 'adadasasd9sd9d9dsss'
@app.route('/', methods = ['GET'])
def index():
    # myCursor = db.restaurants.find({"sensorType":"Power"})
    #--------------------Busqueda fecha-----------------------
    start = datetime.datetime(2017, 05, 04, 19, 28, 07)
    end = datetime.datetime(2017, 05, 04, 23, 28, 35)
    myCursor = db.restaurants.find({'date': {'$lt': end, '$gte': start}})
    return render_template('index.html', myCursor=myCursor)

@app.route('/postjson', methods = ['GET','POST'])
def postJsonHandler():
    # contenido = request.get_json()
    # #contenido = json.loads(data)
    # return (contenido)

    content = request.get_json()
    # tiempo = {}
    # tiempo = time.strftime("%c")
    if content:
        # content['date'] = time.strftime("%c")
        raw = datetime.datetime.now(pytz.utc)
        tiempo = raw.astimezone(pytz.timezone('Europe/Brussels'))
        content['date'] = tiempo
        result = db.pruebas.insert_one(content)
    print result
    print tiempo
    return 'JSON posted'

@app.route('/graficas', methods = ['GET','POST'])
def graficas():

    if request.form.getlist('checkbox2'):
        session['fecha_inicio'] = request.form['fecha_inicio']
        session['fecha_final'] = request.form['fecha_final']

    fecha_inicio = session['fecha_inicio']
    fecha_final = session['fecha_final']
    anio_inicio = fecha_inicio[0:4]
    mes_inicio = fecha_inicio[5:7]
    dia_inicio = fecha_inicio[8:10]
    anio_final = fecha_final[0:4]
    mes_final = fecha_final[5:7]
    dia_final = fecha_final[8:10]


    start = datetime.datetime(int(anio_inicio), int(mes_inicio), int(dia_inicio), 00, 00, 00)
    end = datetime.datetime(int(anio_final), int(mes_final), int(dia_final), 23, 00, 00)
    myCursor = db.pruebas.find({'date': {'$lt': end, '$gte': start}})
    myCursoraux = db.pruebas.find({'date': {'$lt': end, '$gte': start}})
    numero_datos = db.pruebas.count({'date': {'$lt': end, '$gte': start}})

    #----------------------Paginacion-------------------------------------------
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get('page', type=int, default=1)
    pagination = Pagination(page=page, total=numero_datos, search=search, record_name='data', css_framework='bootstrap3')
    offset = (page - 1) * 10
    objetos = myCursor.skip(offset).limit(10)

    #--------------------------Fin paginacion-----------------------------------


    #---------------------------Calculo medias----------------------------------
    sum_real_power = 0
    sum_irms = 0
    media_real_power = 0
    media_irms = 0
    datosgraf_irms = []
    datosgraf_power = []

    if numero_datos != 0:
        for i in myCursoraux:
            sum_irms = sum_irms + i["values"][0]
            sum_real_power = sum_real_power + i["values"][1]
            datosgraf_irms.insert(0, i["values"][0])
            datosgraf_power.insert(0, i["values"][1])

        media_real_power = sum_real_power/numero_datos
        media_irms = sum_irms/numero_datos

    datos = [media_irms, media_real_power]
    #--------------------------Fin calculo medias-------------------------------
    #--------------------------Highcharts---------------------------------------
    #Datos siguientes
    if int(mes_inicio)+1 > 12:
            start_siguiente = datetime.datetime(int(anio_inicio)+1, 01, 01, 00, 00, 00)
            end_siguiente = datetime.datetime(int(anio_inicio)+1, 01, calendar.monthrange(int(anio_inicio)+1,01)[1], 23, 00, 00)
    else:
        start_siguiente = datetime.datetime(int(anio_inicio), int(mes_inicio)+1, 1, 00, 00, 00)
        end_siguiente = datetime.datetime(int(anio_inicio), int(mes_inicio)+1, calendar.monthrange(int(anio_inicio),int(mes_inicio)+1)[1], 23, 00, 00)
    myCursor_sig = db.pruebas.find({'date': {'$lt': end_siguiente, '$gte': start_siguiente}})
    numero_datos_sig = db.pruebas.count({'date': {'$lt': end_siguiente, '$gte': start_siguiente}})

    sum_real_power_sig = 0
    sum_irms_sig = 0
    media_real_power_sig = 0
    media_irms_sig = 0

    if numero_datos_sig != 0:
        for i in myCursor_sig:
            sum_irms_sig = sum_irms_sig + i["values"][0]
            sum_real_power_sig = sum_real_power_sig + i["values"][1]

        media_real_power_Sig = sum_real_power_sig/numero_datos_sig
        media_irms_sig = sum_irms_sig/numero_datos_sig

    datos_sig = [media_irms_sig, media_real_power_sig]

    #datos anteriores
    if int(mes_inicio)-1 == 0:
            start_anterior = datetime.datetime(int(anio_inicio)-1, 12, 01, 00, 00, 00)
            end_anterior = datetime.datetime(int(anio_inicio)-1, 12, calendar.monthrange(int(anio_inicio)-1,12)[1], 23, 00, 00)
    else:
        start_anterior = datetime.datetime(int(anio_inicio), int(mes_inicio)-1, 01, 00, 00, 00)
        end_anterior = datetime.datetime(int(anio_inicio), int(mes_inicio)-1, calendar.monthrange(int(anio_inicio),int(mes_inicio)-1)[1], 23, 00, 00)
    myCursor_ant = db.pruebas.find({'date': {'$lt': end_anterior, '$gte': start_anterior}})
    numero_datos_ant = db.pruebas.count({'date': {'$lt': end_anterior, '$gte': start_anterior}})

    sum_real_power_ant = 0
    sum_irms_ant = 0
    media_real_power_ant = 0
    media_irms_ant = 0

    if numero_datos_ant != 0:
        for i in myCursor_ant:
            sum_irms_ant = sum_irms_ant + i["values"][0]
            sum_real_power_ant = sum_real_power_ant + i["values"][1]

        media_real_power_ant = sum_real_power_ant/numero_datos_ant
        media_irms_ant = sum_irms_ant/numero_datos_ant

    datos_ant = [media_irms_ant, media_real_power_ant]

    #datos actuales

    start_actual = datetime.datetime(int(anio_inicio), int(mes_inicio), 01, 00, 00, 00)
    end_actual = datetime.datetime(int(anio_inicio), int(mes_inicio), calendar.monthrange(int(anio_inicio),int(mes_inicio))[1], 23, 00, 00)
    myCursor_actual = db.pruebas.find({'date': {'$lt': end_actual, '$gte': start_actual}})
    numero_datos_actual = db.pruebas.count({'date': {'$lt': end_actual, '$gte': start_actual}})

    sum_real_power_actual = 0
    sum_irms_actual = 0
    media_real_power_actual = 0
    media_irms_actual = 0

    if numero_datos_actual != 0:
        for i in myCursor_actual:
            sum_irms_actual = sum_irms_actual + i["values"][0]
            sum_real_power_actual = sum_real_power_actual + i["values"][1]

        media_real_power_actual = sum_real_power_actual/numero_datos_actual
        media_irms_actual = sum_irms_actual/numero_datos_actual

    datos_actual = [media_irms_actual, media_real_power_actual]

    #-------------------------Fin Highcharts------------------------------------
    salida = calendar.monthrange(int(anio_inicio),int(mes_inicio))[1]
    print "endsiguiente"
    print numero_datos_actual
    print "end:"
    print end

    return render_template('graficas.html', myCursor=objetos, datos = datos, pagination=pagination, datos_ant = datos_ant, datos_sig = datos_sig, mes_inicio = int(mes_inicio), datos_actual = datos_actual, datosgraf_irms = datosgraf_irms, datosgraf_power = datosgraf_power)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)  # 0.0.0.0 para permitir conexiones
                                         #         desde cualquier sitio.
                                         #         Ojo, peligroso en solo
                                         #         en modo debug
