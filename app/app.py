from flask import Flask, render_template, jsonify, request
from flask_mysqldb import MySQL
import paho.mqtt.client as mqtt_client
import json
import requests
import datetime

# Config
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'projek1'
mysql = MySQL(app)

def sendMsg(msg):
    url = 'https://app.whacenter.com/api/send'
    files = {
        "number" :"081358522935",
        'message': msg,
        'device_id' : '2d1957b59eee663a75eacff834f2fc33',
        }
    x = requests.post(url, data=files)
    print(x.text)
    
@app.route('/about', methods=['GET'])  
def index():
    
    return render_template('about.html')

#Mengambil data
@app.route('/dash', methods=['GET'])
def dashboard(): 
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM suhu')
    data = cur.fetchall()
    cur2 = mysql.connection.cursor()
    cur2.execute('SELECT * FROM suhu ORDER BY id DESC LIMIT 1')
    temp = cur2.fetchone()
    return render_template('dashboard.html', data=data, temp=temp)

@app.route('/dataa', methods=['GET'])
def dataa(): 
    cur2 = mysql.connection.cursor()
    cur2.execute('SELECT * FROM suhu ORDER BY id DESC LIMIT 1')
    data = cur2.fetchone()
    return data

@app.route('/datatabel', methods=['GET'])
def datatabel(): 
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM suhu')
    tabel = cur.fetchall()
    return tabel

# Fungsi untuk mengubah data dashboard dalam format JSON
def to_json(temp, hum, getstatus):
    data = {'temp': temp, 'hum': hum, 'getstatus': getstatus}
    return json.dumps(data)

# Fungsi untuk mengubah data tabel dalam format JSON
def to_json_tabel(tabel):
    data = []
    for t in tabel:
        data.append({'id': t[0], 'tanggal': str(t[1]), 'temp': t[2], 'hum': t[3], 'status': t[4] })
    return json.dumps(data)

@app.route('/data', methods=['GET'])
def data():
    # Kirim data suhu dan kelembaban dari database MySQL ke halaman website
    data = dataa()
    temp = data[2]
    hum = data[3]
    getstatus = data[4]
    data = to_json(temp, hum, getstatus)
    return data

@app.route('/datat', methods=['GET'])
def datat():
    # Kirim data suhu dan kelembaban dari database MySQL ke halaman website
    tabel = datatabel()
    data = to_json_tabel(tabel)
    return data

@app.route('/coba')
def coba(): 
    return render_template('coba.html')

#Mengambil data untuk table
@app.route('/jsontable', methods=['GET'])
def tablechart():
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM suhu ORDER BY id DESC LIMIT 100")
    tabel = cur.fetchall()
    data = []
    for t in tabel:
        data.append({'id': t[0], 'tanggal': str(t[1]), 'temp': t[2], 'hum': t[3], 'status': t[4] })
    return jsonify({'data':data})

@app.route('/json-table/<tanggal>', methods=['GET'])
def table(tanggal):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM suhu where DATE(tanggal) = '{tanggal}' ORDER BY id DESC LIMIT 100")
    row_headers=[x[0] for x in cur.description] #this will extract row headers
    rv = cur.fetchall()
    json_data=[]
    f = '%Y-%m-%d %H:%M:%S'
    for result in rv:
            lst = list(result)
            lst[1] = result[1].strftime(f)
            result = tuple(lst)
            json_data.append(dict(zip(row_headers,result)))
    return json.dumps({'data' : json_data})
    
@app.route('/apihistory/<start>/<end>', methods=['GET'])
def history(start,end):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM suhu where tanggal BETWEEN '{start}' and '{end}'")
    row_headers=[x[0] for x in cur.description] #this will extract row headers
    rv = cur.fetchall()
    json_data=[]
    f = '%Y-%m-%d %H:%M:%S'
    for result in rv:
            lst = list(result)
            lst[1] = result[1].strftime(f)
            result = tuple(lst)
            json_data.append(dict(zip(row_headers,result)))
    return json.dumps({'data' : json_data})

@app.route('/history/<start>/<end>', methods=['GET'])
def datahistory(start,end):
    
   return render_template('history.html')
                

#Mengambil data untuk grafik
@app.route('/json-chart', methods=['GET'])
def x_chart():
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM suhu ORDER BY id DESC LIMIT 100")
    r = [dict((cur.description[i][0], value)
                for i, value in enumerate(row)) for row in cur.fetchall()]
    return jsonify({'data' : r})

@app.route('/history_chart/<start>/<end>', methods=['GET'])
def history_chart(start,end):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM suhu where tanggal BETWEEN '{start}' and '{end}'")
    row_headers=[x[0] for x in cur.description] #this will extract row headers
    rv = cur.fetchall()
    json_data=[]
    f = '%Y-%m-%d %H:%M:%S'
    for result in rv:
            lst = list(result)
            lst[1] = result[1].strftime(f)
            result = tuple(lst)
            json_data.append(dict(zip(row_headers,result)))
    return json.dumps({'data' : json_data})

@app.route('/example', methods=['GET']) 
def example():
    return render_template('example.html')

@app.route('/send', methods=['GET']) 
def sendWa():
    sendMsg("ok")
    return "ok"

#Mengirim data ke database
@app.route('/insert/<temp>/<hum>/<getstatus>', methods=['GET'])
def insert(temp,hum,getstatus):
    temp = float(temp)
    hum = float(hum)
    getstatus = str(getstatus)
    cur = mysql.connection.cursor()
    cur.execute(f"INSERT INTO suhu (temp, hum, status) VALUES ({temp}, {hum},'{getstatus}')")
    mysql.connection.commit()
    cur.close()
    return 'Data berhasil ditambahkan'

# GENSET (mengirim data ke database)
@app.route('/dashgenset', methods=['GET'])
def dashboardgenset(): 
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM voltage')
    gen = cur.fetchall()
    cur2 = mysql.connection.cursor()
    cur2.execute('SELECT * FROM voltage ORDER BY idvolt DESC LIMIT 1')
    volt = cur2.fetchone()    
    cur3 = mysql.connection.cursor()
    cur3.execute('SELECT * FROM genset ORDER BY id_data DESC LIMIT 1')
    gambar = cur3.fetchone()
        
    return render_template('dashboardgenset.html', gen=gen,volt=volt, gambar=gambar[1])

@app.route('/datagenset', methods=['GET'])
def datagenset(): 
    cur2 = mysql.connection.cursor()
    cur2.execute('SELECT * FROM voltage ORDER BY idvolt DESC LIMIT 1')
    volt = cur2.fetchone()
    return volt

@app.route('/realtime', methods=['GET'])
def realtime(): 
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM voltage')
    tabel = cur.fetchall()
    return tabel

# Fungsi untuk mengubah data dashboard dalam format JSON
def to_jsongenset(bv, sv, lv, c, p):
    volt = {'bv': bv, 'sv': sv, 'lv': lv, 'c': c, 'p': p}
    return json.dumps(volt)

# Fungsi untuk mengubah data tabel dalam format JSON
def to_json_tabelgenset(tabel):
    volt = []
    for t in tabel:
        volt.append({'idvolt': t[0], 'date': str(t[1]), 'bv': t[2], 'sv': t[3], 'lv': t[4], 'c': t[5], 'p': t[6] })
    return json.dumps(volt)

@app.route('/datag', methods=['GET'])
def datag():
    # Kirim data suhu dan kelembaban dari database MySQL ke halaman website
    volt = datagenset()
    bv = volt[2]
    sv = volt[3]
    lv = volt[4]
    c = volt[5]
    p = volt[6]
    volt = to_jsongenset(bv, sv, lv, c, p)
    return volt

@app.route('/datagen', methods=['GET'])
def datagen():
    # Kirim data suhu dan kelembaban dari database MySQL ke halaman website
    tabel = realtime()
    data = to_json_tabelgenset(tabel)
    return data

@app.route('/dashgenset2', methods=['GET'])
def dashboardgenset2(): 
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM voltage')
    gen = cur.fetchall()
    cur2 = mysql.connection.cursor()
    cur2.execute('SELECT * FROM voltage1 ORDER BY idvolt1 DESC LIMIT 1')
    volt = cur2.fetchone()    
    cur3 = mysql.connection.cursor()
    cur3.execute('SELECT * FROM genset1 ORDER BY id_data1 DESC LIMIT 1')
    gambar = cur3.fetchone()
        
    return render_template('dashgenset2.html', gen=gen,volt=volt, gambar=gambar[1])

@app.route('/datagenset2', methods=['GET'])
def datagenset2(): 
    cur2 = mysql.connection.cursor()
    cur2.execute('SELECT * FROM voltage ORDER BY idvolt DESC LIMIT 1')
    volt2 = cur2.fetchone()
    return volt2

@app.route('/realtime2', methods=['GET'])
def realtime2(): 
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM voltage1')
    tabel2 = cur.fetchall()
    return tabel2

# Fungsi untuk mengubah data dashboard dalam format JSON
def to_jsongenset2(BV, SV, LV, C, P):
    volt2 = {'BV': BV, 'SV': SV, 'LV': LV, 'C': C, 'P': P}
    return json.dumps(volt2)

# Fungsi untuk mengubah data tabel dalam format JSON
def to_json_tabelgenset2(tabel):
    volt2 = []
    for t in tabel:
        volt2.append({'idvolt1': t[0], 'date': str(t[1]), 'BV': t[2], 'SV': t[3], 'LV': t[4], 'C': t[5], 'P': t[6] })
    return json.dumps(volt2)

@app.route('/datag2', methods=['GET'])
def datag2():
    # Kirim data suhu dan kelembaban dari database MySQL ke halaman website
    volt2 = datagenset2()
    BV = volt2[2]
    SV = volt2[3]
    LV = volt2[4]
    C = volt2[5]
    P = volt2[6]
    volt2 = to_jsongenset2(BV, SV, LV, C, P)
    return volt2

@app.route('/datagen2', methods=['GET'])
def datagen2():
    # Kirim data suhu dan kelembaban dari database MySQL ke halaman website
    tabel = realtime2()
    data2 = to_json_tabelgenset2(tabel)
    return data2

@app.route('/genset/kamera', methods=['POST'])
def genset():
    data = request.form['img']
    cur = mysql.connection.cursor()
    cur.execute(f"INSERT INTO `genset` (`id_data`, `gambar`) VALUES (NULL, '{data}')")
    mysql.connection.commit()
    cur.close()
    return 'Data Berhasil Ditambahkan'

@app.route('/genset/camera', methods=['POST'])
def genset1():
    data = request.form['img']
    cur = mysql.connection.cursor()
    cur.execute(f"INSERT INTO `genset1` (`id_data1`, `picture`) VALUES (NULL, '{data}')")
    mysql.connection.commit()
    cur.close()
    return 'Data Berhasil Ditambahkan'

# link untuk mengambil gambar genset 1
@app.route('/genset/camera/get')
def getFromCam():
    client = mqtt_client.Client("bmkguser123")
    client.connect('broker.emqx.io', 1883)

    client.publish("bmkg/ambilcamera", "?ambilfoto")
    return 'Data Berhasil Ditambahkan'

@app.route('/genset/camera/flash/<value>')
def getFlashCam(value):
    client = mqtt_client.Client("bmkguser123")
    client.connect('broker.emqx.io', 1883)

    client.publish("bmkg/ambilcamera", f"?flash={value}")
    return 'Data Berhasil Ditambahkan'

# link untuk mengambil gambar genset 2
@app.route('/genset/camera2/get')
def getFromCam2():
    client = mqtt_client.Client("bmkguser123")
    client.connect('broker.emqx.io', 1883)

    client.publish("bmkg/ambilcamera2", "?ambilfoto")
    return 'Data Berhasil Ditambahkan'

@app.route('/genset/camera2/flash/<value>')
def getFlashCam2(value):
    client = mqtt_client.Client("bmkguser123")
    client.connect('broker.emqx.io', 1883)

    client.publish("bmkg/ambilcamera2", f"?flash={value}")
    return 'Data Berhasil Ditambahkan'


# voltage genset
@app.route('/genset/volt', methods=['POST'])
def gensetV():
    data = request.form['volt']
    bv,sv,lv,c,p = data.split(',')
    cur = mysql.connection.cursor()
    cur.execute(f"INSERT INTO `voltage` (`idvolt`,`bv`, `sv`, `lv`, `c`, `p`) VALUES (NULL, '{bv}', '{sv}', '{lv}', '{c}', '{p}')")
    mysql.connection.commit()
    cur.close()
    return 'Data Berhasil Ditambahkan'

@app.route('/genset/voltage1', methods=['POST'])
def gensetV1():
    data = request.form['volt']
    bv,sv,lv,c,p = data.split(',')
    cur = mysql.connection.cursor()
    cur.execute(f"INSERT INTO `voltage1` (`idvolt1`,`BV`, `SV`, `LV`, `C`, `P`) VALUES (NULL, '{bv}', '{sv}', '{lv}', '{c}', '{p}')")
    mysql.connection.commit()
    cur.close()
    return 'Data Berhasil Ditambahkan'



if __name__ == '__main__':
    app.run(debug=True,)
