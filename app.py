import datetime
import paho.mqtt.client as mqtt
import sshtunnel
from flask import Flask
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sshtunnel import SSHTunnelForwarder
import logging

"""
Requirements:
pip3 install Flask
pip3 install paho.mqtt
pip3 install flask_sqlalchemy
pip3 install mysqlclient
pip3 install sshtunnel

Start VEnv (in Project Dir):
. bin/activate
OR
source pwr/bin/activate

Run MQTT Broker:
sudo systemctl start mosquitto
"""

app = Flask(__name__)

tunnel = SSHTunnelForwarder(
    ('docker.cees.com.de', 18402),
    ssh_username="StoltmannB",
    ssh_password="Westonmare01762529",
    remote_bind_address=('127.0.0.1', 3306),
    local_bind_address=('127.0.0.1', 3306)
)
#tunnel.start()

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://pwradmin:dbpwrad@127.0.0.1:3306/pwrdata"
db = SQLAlchemy(app)

logging.basicConfig(filename="webserver.log", level=logging.DEBUG)

msg = "Testing in progress..."


def on_connect(client, userdata, flags, rc):
    print("Connected!")
    client.subscribe("testtopic")


def on_message(client, userdata, message):
    payload = list(message.payload)
    myGyro = Gyro(time=datetime.datetime.now(), x_axis=(payload[0] * 256 + payload[1]),
                  y_axis=(payload[2] * 256 + payload[3]), z_axis=(payload[4] * 256 + payload[5]))
    acc = Acc(time=datetime.datetime.now(), x_axis=(payload[6] * 256 + payload[7]),
              y_axis=(payload[8] * 256 + payload[9]), z_axis=(payload[10] * 256 + payload[11]))
    #db.session.add(myGyro)
    #db.session.add(acc)
    #db.session.commit()
    print(acc)


class Gyro(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    time = db.Column(db.TIMESTAMP)
    x_axis = db.Column(db.INTEGER)
    y_axis = db.Column(db.INTEGER)
    z_axis = db.Column(db.INTEGER)

    def serialize(self):
        return {
            'id': self.id,
            'time': self.time,
            'x_axis': self.x_axis,
            'y_axis': self.y_axis,
            'z_axis': self.z_axis
        }


class Acc(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    time = db.Column(db.TIMESTAMP)
    x_axis = db.Column(db.INTEGER)
    y_axis = db.Column(db.INTEGER)
    z_axis = db.Column(db.INTEGER)

    def serialize(self):
        return {
            'id': self.id,
            'time': self.time,
            'x_axis': self.x_axis,
            'y_axis': self.y_axis,
            'z_axis': self.z_axis
        }


@app.route('/')
def hello_world():
    # DB Operatioen
    return msg


@app.route('/acc/all', methods=['GET'])
def allAccData():
    return jsonify(acc=[e.serialize() for e in Acc.query.all()])


@app.route('/gyro/all', methods=['GET'])
def allGyroData():
    return jsonify(gyro=[e.serialize() for e in Gyro.query.all()])


if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("192.168.0.46", 1883, 60)
    client.loop_start()
    
    app.run(debug=True, host="0.0.0.0")
