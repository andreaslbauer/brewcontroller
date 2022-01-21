

#
# Flask Web App to implement web pages and REST endpoints for measurement display
# Requires Flask and Flask-Rest
#

import logging
from flask import Flask, jsonify
from flask import render_template
from flask_restful import Resource, Api, fields, marshal_with, reqparse, marshal
from flask_executor import Executor
# logging facility: https://realpython.com/python-logging/
import os
import time
import datetime
from brewdata import apis, brewcontroller

OurHostName = ''

# sqlite3 access API

import datetime


app = Flask(__name__)
api = Api(app)
executor = Executor(app)
parser = reqparse.RequestParser()
parser.add_argument('target')
OurHostname = ""


def shutdownCMD():
    time.sleep(2)
    logging.info("Shutting down...")
    os.system('sudo shutdown 1')


def rebootCMD():
    time.sleep(2)
    logging.info("Rebooting...")
    os.system('sudo reboot 1')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/reboot')
def reboot():
    executor.submit(rebootCMD)
    return render_template('reboot.html')


@app.route('/shutdown')
def shutdown():
    executor.submit(shutdownCMD)
    return render_template('shutdown.html')


@app.route('/controller')
def summarycharts():
    return render_template('controller.html')


@app.route('/programs')
def detailedcharts():
    return render_template('programs.html')

@app.route('/data')
def data():
    return render_template('data.html')

@app.route('/chart')
def chart():
    return render_template('chart.html')


@app.route('/webapplog')
def webapplog():
    f = open("/tmp/brewcontroller.log", "r")

    page = "<!DOCTYPE html>"
    page = page + "<html><h1>Web App Log</h1><hr><br><pre>"

    for line in f:
        page = page + line

    page = page + "</pre></html>"
    return page


@app.route('/summary')
def summary():
    page = "<!DOCTYPE html>"
    page = page + "<html><h1>Web Thermometer Sensor Summary</h1><hr><br>"

    db = sqlhelper.createConnection(sqlhelper.dbfilename)
    rowCount = sqlhelper.countRows(db)
    page = page + "Number of data points in table: " + str(rowCount) + '<p>'
    row = sqlhelper.getRow(db, rowCount)

    # display how many sensor are collecting data
    sensorCount = infohelper.numberSensors(db)
    page = page + "Number of sensors: " + str(sensorCount) + '<p>'

    # display how many sensor are collecting data
    rateOfChange = infohelper.getRateOfChange(db)
    page = page + "Rate of change: " + str(rateOfChange) + '<p>'

    # display time elapsed between sensor writes
    timeBetweenReads = infohelper.timeBetweenSensorReads(db)
    page = page + "Time between sensor reads: " + str(timeBetweenReads) + '<p>'

    # display trends over past 10 mins

    rows = sqlhelper.getRows(db, rowCount - 12, rowCount)
    page = page + "Last 12 rows: <p>"
    for r in rows:
        page = page + str(r) + '<p>'

    page = page + "Last data point: " + str(row) + '<p>'
    db.close()

    page = page + "</html>"
    return page


@app.route('/changes')
def changes():
    db = sqlhelper.createConnection(sqlhelper.dbfilename)
    a = infohelper.getChanges(db, 10, 10 * 60)

    return render_template('changes.html', data=a, lastupdated=a[0][0])


resourceFields = {
    'channelid':    fields.Integer,
    'temperature':       fields.Float,
    'target': fields.Float,
    'status':     fields.String,
    'program':     fields.String,
    'time': fields.String,
}

# Data Point object.  Use to marshal a data row
class ControllerValues(Resource):

    @marshal_with(resourceFields)
    def get(self, sensorid):
        brewcontroller.controller.channels[sensorid - 1].update()
        return brewcontroller.controller.channels[sensorid - 1]

    @marshal_with(resourceFields)
    def post(self, sensorid):
        parsed_args = parser.parse_args()
        target = parsed_args['target']
        brewcontroller.controller.channels[sensorid - 1].target = float(target)
        logging.debug("Set target to %f for channel %i", int(target), sensorid)
        brewcontroller.controller.channels[sensorid - 1].store()


class ServerInfo(Resource):

    def get(self):
        global OurHostName
        return jsonify({'hostname': OurHostName})


class TableValues(Resource):

    def get(self):
        table = {}

        # build the header row
        header = []
        header.append("Date/Time")
        header.append("Sensor 1")
        header.append("Changes 1")
        header.append("Sensor 2")
        header.append("Changes 2")

        rowCount = 6
        sensorCount = 2

        # build the data array
        tabledata = []

        data = []
        for sensorId in range (1, sensorCount + 1):
            data.append(apis.getValueArray(sensorId, rowCount, 160))

        for i in range(0, rowCount):
            row = []
            for s in range(0, sensorCount):
                if (s == 0):
                    row.append(data[s][i]["time"])

                row.append(data[s][i]["value"])

                if (i > 0):
                    row.append(data[s][i]["value"]- data[s][i - 1]["value"])
                else:
                    row.append("")

            tabledata.append(row)

        table["header"] = header
        table["data"] = tabledata
        return jsonify(table)


# add REST end points
api.add_resource(ControllerValues, '/values/<int:sensorid>')
api.add_resource(ServerInfo, '/serverinfo')
api.add_resource(TableValues, '/tablevalues')




