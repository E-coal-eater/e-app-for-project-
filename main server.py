from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
import serial
import threading


app = Flask(__name__)
DB_NAME = 'user.db'

#---------------- Database initialisation ---------------------------
def init_db():
    # si le fichier de base de données n'existe pas : on crée la base de données
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
        CREATE TABLE parcours (
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
            FOREIGN KEY (id_parcours) REFERENCES parcours(id)
        )
        ''')
        conn.commit()
        conn.close()
init_db()

#------------------------ Arduino Part -----------------------------------

SERIAL_PORT = 'COM31'
BAUDRATE = 9600

reccording = False
current_parcours_id = None
last_temps = 0

def serial_listener():
    global reccording, current_parcours_id, last_temps

    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    except:
        print("Serial not connected")
        return
    
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys ON")

    while True:
        line = ser.readline().decode().strip()
        if not line:
            continue
        
        if line == 'BTN':

            if not reccording:
                reccording = True

                cursor.execute("SELECT id FROM velos ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                if not row:
                    print("no velo in DB")
                    reccording = False
                    continue
                
                last_velo_id = row[0]

                cursor.execute("INSERT INTO parcours(id_velo, temps) VALUE(?, NULL)", (last_velo_id))
                current_parcours_id = cursor.lastrowid
                conn.commit()

                print("Started Parcours", current_parcours_id)
            else:
                reccording = False

                cursor.execute("""
                UPDATE parcours
                SET temps = ?
                WHERE id = ?
                """, (last_temps, current_parcours_id))
                
                conn.commit()
                print("Parcours stopped", current_parcours_id, "Final Time:", last_temps)
                current_parcours_id = None
        elif line.startswith("DATA") and reccording:
            _, temps, battery = line.split(",")

            last_temps = int(temps)

            cursor.execute("""
            INSERT INTO points (id_parcours, temps, battery)
            VALUES (?,?,?)
            """, (current_parcours_id, temps, battery))
            conn.commit()

threading.Thread(target=serial_listener, daemon=True) .start()

#------------------------Web Part ----------------------------------------
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
    return render_template('control.html')

@app.route('/pilot')
def pilot():
    return render_template('pilot-stats.html')

@app.route('/DB', methods=['GET', 'POST'])
def DB():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    #render des 3 databases pour la page HTML
    cursor.execute("SELECT * FROM velos")
    velos = cursor.fetchall()

    cursor.execute("SELECT * FROM parcours")
    parcours = cursor.fetchall()

    cursor.execute("SELECT * FROM points")
    points = cursor.fetchall()

    conn.close()

    if request.method == 'POST':
        modele = request.form.get('modele')
        parcours_id = request.form.get('id_parcours')
        if modele:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM velos WHERE modele = ?", (modele,))
            existing_user = cursor.fetchone()
            if existing_user:
                return redirect(url_for('DB', err='invalidModele'))
            else:
                cursor.execute("INSERT INTO velos (modele) VALUES (?)", (modele,))
            conn.commit()
            conn.close()
        return redirect(url_for('DB'))
    err = request.args.get('err')
    return render_template('DB.html', velos=velos, parcours=parcours, err=err)

@app.route('livePoints')
def livePoints():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT points.id, points.id_parcours, points.temps, points.battery
    FROM points
    ORDER BY points.id ASC
    """)
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return data
if __name__ == '__main__':
    app.run(debug=True)