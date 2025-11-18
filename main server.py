from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
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

        if username == VALID_USERNAME1 and password == VALID_PASSWORD1:
            return redirect(url_for('control'))
        elif username == VALID_USERNAME2 and password == VALID_PASSWORD2:
            return redirect(url_for('pilot'))
        else:
            return redirect(url_for('login?err=invalidLogin'))
    return render_template('login.html')

@app.route('/control')
def control():
    return render_template('control.html')

@app.route('/pilot')
def pilot():
    return render_template('pilot-stats.html')

if __name__ == '__main__':
    app.run(debug=True)