from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)
TESTUser = 'A'
TESTPassword = 'A'
TESTUser2 = 'B'
TESTPassword2 = 'B'
VALID_USERNAME1 = 'Prog_derailles'
VALID_PASSWORD1 = 'siperprogrammeur'
VALID_USERNAME2 = 'pilot_derailles'
VALID_PASSWORD2 = 'siperpilote'

DB_NAME = 'user.db'

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
            temps INT NOT NULL,
            FOREIGN KEY (id_velo) REFERENCES velos(id)
       )
       ''')
        cursor.execute('''
        CREATE TABLE points(
            id_parcours INT NOT NULL,
            temps INT NOT NULL,
            battery INT,
            FOREIGN KEY (id_parcours) REFERENCES parcours(id)
        )
        ''')
    conn.commit()
    conn.close()
init_db()

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
def db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    #render des 2 databases pour la page HTML
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
            existing_user = cursor.fetchone()
            if existing_user:
                return redirect(url_for('DB', err='invalidModele'))
            else:
                cursor.execute("INSERT INTO velos (modele) VALUES (?)", (modele,))
            conn.commit()
            conn.close()
            return redirect('/DB')
    return render_template('DB.html', velos=velos, parcours=parcours)

if __name__ == '__main__':
    app.run(debug=True)