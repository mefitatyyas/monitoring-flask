from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import paho.mqtt.client as mqtt
from datetime import datetime

# Config
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'projek1'
mysql = MySQL(app)

@app.route('/', methods=['GET'])
def index():
    temperature = 12
    humimidty = 88
    return render_template('about.html', temp=temperature, hum=humimidty)

@app.route('/dash', methods=['GET'])
def dashboard(): 
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM suhu')
    data = cur.fetchall()
    cur2 = mysql.connection.cursor()
    cur2.execute('SELECT * FROM suhu ORDER BY id DESC LIMIT 1')
    temp = cur2.fetchone()     
    return render_template('dashboard.html',data=data,temp=temp)
        
@app.route('/dashgenset', methods=['GET'])
def dashboardgenset(): 
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM voltage')
    gen = cur.fetchall()
    cur2 = mysql.connection.cursor()
    cur2.execute('SELECT * FROM voltage ORDER BY idvolt DESC LIMIT 1')
    volt = cur2.fetchone()    
    return render_template('dashboardgenset.html', gen=gen,volt=volt)


@app.route('/insert/<temp>/<hum>/<getstatus>', methods=['GET'])
def insert(temp,hum,getstatus):
    temp = float(temp)
    hum = float(hum)
    getstatus = str(getstatus)
    cur = mysql.connection.cursor()
    cur.execute(f"INSERT INTO suhu (temp, hum, status) VALUES ({temp}, {hum}, '{getstatus}')")
    mysql.connection.commit()
    cur.close()
    return 'Data berhasil ditambahkan'


@app.route('/genset/kamera', methods=['POST'])
def genset():
    data = request.form['img']
    cur = mysql.connection.cursor()
    cur.execute(f"INSERT INTO `genset` (`id_data`, `gambar`) VALUES (NULL, '{data}')")
    mysql.connection.commit()
    cur.close()
    return 'Data Berhasil Ditambahkan'

@app.route('/genset/volt', methods=['POST'])
def gensetV():
    data = request.form['volt']
    bv,sv,lv,c,p = data.split(',')
    cur = mysql.connection.cursor()
    cur.execute(f"INSERT INTO `voltage` (`idvolt`,`bv`, `sv`, `lv`, `c`, `p`) VALUES (NULL, '{bv}', '{sv}', '{lv}', '{c}', '{p}')")
    mysql.connection.commit()
    cur.close()
    return 'Data Berhasil Ditambahkan'


if __name__ == '__main__':
    app.run(debug=True,)
