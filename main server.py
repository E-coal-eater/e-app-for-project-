from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import sqlite3
import threading
import time
import serial
import math

app = Flask(__name__)
DB_NAME = 'user.db'
arduino_connected = False
ser = None
bluetooth_connected = False
acquisition_running = False
last_gps_point = None
current_parcours_id = None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

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
            vitesse_moyenne_parcours REAL,
            FOREIGN KEY (id_velo) REFERENCES velos(id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE points(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_parcours INT NOT NULL,
            chrono INT,
            battery INT,
            position TEXT,
            distance REAL,
            vitesse REAL,
            vitesse_moyenne REAL,
            FOREIGN KEY (id_parcours) REFERENCES parcours(id)
        )
        ''')
        
        conn.commit()
        conn.close()

init_db()

@app.route('/reset_db', methods=['POST'])
def reset_db():
    global current_parcours_id, parcours_start_time, last_gps_point
    current_parcours_id = None
    parcours_start_time = None
    last_gps_point = None
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS points")
    cursor.execute("DROP TABLE IF EXISTS parcours")
    cursor.execute("DROP TABLE IF EXISTS velos")
    
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
            vitesse_moyenne_parcours REAL,
            FOREIGN KEY (id_velo) REFERENCES velos(id)
        )
        ''')
        
    cursor.execute('''
        CREATE TABLE points(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_parcours INT NOT NULL,
            chrono INT,
            battery INT,
            position TEXT,
            distance REAL,
            vitesse REAL,
            vitesse_moyenne REAL,
            FOREIGN KEY (id_parcours) REFERENCES parcours(id)
        )
        ''')
    conn.commit()
    conn.close()
    return redirect(url_for('control'))
        
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
parcours_start_time = None
@app.route('/start_parcours', methods=['POST'])
def start_parcours():
    global current_parcours_id, parcours_start_time

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get last added velo
    cursor.execute("SELECT id FROM velos ORDER BY id DESC LIMIT 1")
    last_velo = cursor.fetchone()
    id_velo = last_velo[0] if last_velo else None

    # Always create a fresh parcours row
    cursor.execute("INSERT INTO parcours (id_velo) VALUES (?)", (id_velo,))
    conn.commit()
    current_parcours_id = cursor.lastrowid
    parcours_start_time = time.time()
    conn.close()

    return {"ok": True, "parcours_id": current_parcours_id}


@app.route('/stop_parcours', methods=['POST'])
def stop_parcours():
    global current_parcours_id, parcours_start_time

    if not current_parcours_id:
        return {"ok": False, "error": "No parcours running"}

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    temps = int(time.time() - parcours_start_time) if parcours_start_time else 0

    cursor.execute(
        "SELECT AVG(vitesse_moyenne) FROM points WHERE id_parcours = ?",
        (current_parcours_id,)
    )
    row = cursor.fetchone()
    avg_speed = row[0] if row and row[0] is not None else 0

    cursor.execute(
        "UPDATE parcours SET temps = ?, vitesse_moyenne_parcours = ? WHERE id = ?",
        (temps, avg_speed, current_parcours_id)
    )
    conn.commit()
    conn.close()

    current_parcours_id = None
    parcours_start_time = None

    return {"ok": True}

# New route: return points for a specific parcours
@app.route('/parcours/<int:parcours_id>/points')
def parcours_points(parcours_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM points WHERE id_parcours = ?", (parcours_id,))
    points = cursor.fetchall()
    conn.close()

    if not points:
        return {"points": [], "count": 0}

    return {
        "points": [dict(p) for p in points],
        "count": len(points)
    }

@app.route("/gps_update", methods=['POST'])
def gps_update():
    global last_gps_point, current_parcours_id, parcours_start_time

    # If no parcours is running, store nothing
    if not current_parcours_id:
        return jsonify({"status": "no_parcours"})

    data = request.json
    lat = data["latitude"]
    lon = data["longitude"]
    instant_speed = data["instant_speed_ms"]
    average_speed = data["average_speed_ms"]

    # Chrono = seconds elapsed since parcours started
    chrono = int(time.time() - parcours_start_time) if parcours_start_time else 0

    # Distance from last point using haversine
    distance = 0.0
    if last_gps_point:
        distance = haversine(
            last_gps_point["lat"],
            last_gps_point["lon"],
            lat,
            lon
        )

    last_gps_point = {"lat": lat, "lon": lon}

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO points (id_parcours, chrono, battery, position, distance, vitesse, vitesse_moyenne)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        current_parcours_id,
        chrono,                     # elapsed seconds since start
        None,                       # battery — not yet wired
        f"{lat},{lon}",             # position as "lat,lon"
        round(distance, 4),
        round(instant_speed, 4),
        round(average_speed, 4)
    ))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok", "chrono": chrono, "distance": distance})

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

@app.route('/control', methods=['GET','POST'])
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
        parcours = request.form.get('parcours')
        if modele:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM velos WHERE modele = ?", (modele,))
            if cursor.fetchone():
                conn.close()
                return redirect(url_for('control', err='invalidModele'))
            cursor.execute("INSERT INTO velos (modele) VALUES (?)", (modele,))
            conn.commit()
            conn.close()
            return redirect(url_for('control'))
        
        elif parcours:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO parcours DEFAULT VALUES")
            conn.commit()
            conn.close()
            return redirect(url_for('control'))

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
    #if not bluetooth_connected:
    #    return {"ok": False, "error": "No Bluetooth device connected"}

    acquisition_running = not acquisition_running
    return {"ok": True, "running": acquisition_running}

@app.route('/acquisition_status')
def acquisition_status():
    return {"running": acquisition_running, "connected": bluetooth_connected}

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
    app.run(host="0.0.0.0", port=5000, debug=True)