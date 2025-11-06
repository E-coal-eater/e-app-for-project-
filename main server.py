from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
VALID_USERNAME = 'les-déraillés'
VALID_PASSWORD = 'Paulette'

@app.route('/')
def enter():
    return render_template('main-page.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == VALID_USERNAME and password == VALID_PASSWORD:
            return redirect(url_for('control', username=username))
        else:
            return redirect(url_for('login?err=invalidLogin'))
    return render_template('login.html')

@app.route('/control')
def home():
    return render_template('control.html')
    
if __name__ == '__main__':
    app.run(debug=True)