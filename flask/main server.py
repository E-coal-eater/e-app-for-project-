from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
import threading
import time
import serial

app = Flask(__name__)
DB_NAME = 'user.db'
arduino_connected = False
ser = None
bluetooth_connected = False
acquisition_running = False

# ---------------- Database Initialization ----------------
def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        
        cursor.execute('''
        CREATE TABLE velos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modele TEXT NOT NULL UNIQUE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE parcours(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_velo INT,
            temps INT,
            FOREIGN KEY (id_velo) REFERENCES velos(id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE points(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_parcours INT NOT NULL,
            temps INT,
            battery INT,
            position TEXT,
            FOREIGN KEY (id_parcours) REFERENCES parcours(id)
        )
        ''')
        
        conn.commit()
        conn.close()

init_db()

# ---------------- Arduino acquisition --------------
def connect_arduino():
    global ser, arduino_connected
    try:
        ser = serial.Serial("COM3", 9600, timeout=1)  # ← change COM port
        arduino_connected = True
        print("Arduino connected")
    except:
        arduino_connected = False
        ser = None
        print("Arduino NOT connected")

connect_arduino()
# ---------------- Pilot Acquisition ----------------
acquisition_running = False

def acquisition_loop():
    global acquisition_running
    
    while True:
        if acquisition_running:
            # Placeholder for Bluetooth acquisition
            data = None
            if data is not None:
                # Insert real data here
                pass
            else:
                # No data yet → do nothing
                pass
        time.sleep(1)

threading.Thread(target=acquisition_loop, daemon=True).start()

# ---------------- Authentication ----------------
TESTUser = 'A'
TESTPassword = 'A'
TESTUser2 = 'B'
TESTPassword2 = 'B'
VALID_USERNAME1 = 'Prog_derailles'
VALID_PASSWORD1 = 'siperprogrammeur'
VALID_USERNAME2 = 'pilot_derailles'
VALID_PASSWORD2 = 'siperpilote'

@app.route('/')
def enter():
    return render_template('main-page.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if (username == VALID_USERNAME1 and password == VALID_PASSWORD1) or (username == TESTUser and password == TESTPassword):
            return redirect(url_for('control'))
        elif (username == VALID_USERNAME2 and password == VALID_PASSWORD2) or (username == TESTUser2 and password == TESTPassword2):
            return redirect(url_for('pilot'))
        else:
            return redirect(url_for('login', err='invalidLogin'))
    
    err = request.args.get('err')
    return render_template('login.html', err=err)

@app.route('/control')
def control():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM velos")
    velos = cursor.fetchall()

    cursor.execute("SELECT * FROM parcours")
    parcours = cursor.fetchall()

    cursor.execute("SELECT * FROM points")
    points = cursor.fetchall()

    conn.close()

    if request.method == 'POST':
        modele = request.form.get('modele')
        if modele:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM velos WHERE modele = ?", (modele,))
            if cursor.fetchone():
                conn.close()
                return redirect(url_for('DB', err='invalidModele'))
            cursor.execute("INSERT INTO velos (modele) VALUES (?)", (modele,))
            conn.commit()
            conn.close()
            return redirect(url_for('DB'))

    err = request.args.get('err')
    return render_template('control.html', velos=velos, parcours=parcours, points=points, err=err)

# ---------------- Pilot Page ----------------
@app.route('/pilot')
def pilot():
    return render_template('pilot-stats.html', acquisition_running=acquisition_running)

@app.route('/toggle_acquisition', methods=['POST'])
def toggle_acquisition():
    global acquisition_running
    
    # No Bluetooth / hardware yet
    if not bluetooth_connected:
        return {"ok": False, "error": "No Bluetooth device connected"}

    acquisition_running = not acquisition_running
    return {"ok": True, "running": acquisition_running}

@app.route('/acquisition_status')
def acquisition_status():
    return {"running": acquisition_running,
            "connected" : bluetooth_connected}
    
# ---------------- DB JSON Endpoint for AJAX ----------------
@app.route('/db_data')
def db_data():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM velos")
    velos = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM parcours")
    parcours = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM points")
    points = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {"velos": velos, "parcours": parcours, "points": points}

# ---------------- Run Flask ----------------
if __name__ == '__main__':
    app.run(debug=True)