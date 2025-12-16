from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)
VALID_USERNAME1 = 'Prog_derailles'
VALID_PASSWORD1 = 'siperprogrammeur'
VALID_USERNAME2 = 'pilot_derailles'
VALID_PASSWORD2 = 'siperpilote'

def init_db():
    # si le fichier de base de données n'existe pas : on crée la base de données
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE velos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modele TEXT,
            parcours_id INTEGER NOT NULL,
            FOREIGN KEY (parcours_id) REFERENCES parcours(id)
        );
        ''')
        cursor.execute('''
        CREATE TABLE parcours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_velo INTEGER NOT NULL,
            FOREIGN KEY (id_velo) REFERENCES velos(id),
            temps INT,
            vitesse INT,
            location TEXT,
            battery INT
        );
        ''')
        conn.commit
        conn.close
init_db

@app.route('/')
def enter():
    return render_template('main-page.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == VALID_USERNAME1 and password == VALID_PASSWORD1:
            return redirect(url_for('control'))
        elif username == VALID_USERNAME2 and password == VALID_PASSWORD2:
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

@app.route('/db_test')
def db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor

    #render des 2 databases pour la page HTML
    cursor.execute("SELECT * FROM velos")
    velos = cursor.fetchall()

    cursor.execute("SELECT * FROM parcours")
    parcours = cursor.fetchall()

    conn.close()
    
    return render_template('db_test.hmtl', velos=velos, parcours=parcours)


if __name__ == '__main__':
    app.run(debug=True)