from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
VALID_USERNAME = 'cygo'
VALID_PASSWORD = '1234'

@app.route('/')
def enter():
    return render_template('main-page.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == VALID_USERNAME and password == VALID_PASSWORD:
            return redirect(url_for('home', username=username))
        else:
            return redirect(url_for('login?err=invalidLogin'))
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')
    
if __name__ == '__main__':
    app.run(debug=True)