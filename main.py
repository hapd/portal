# Import statements for Flask
import flask
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def launch():
    return render_template('launch.html')

@app.route("/home")
def dashboard():
    return render_template('nurse_home.html', result = ['dashboard'])

@app.route("/authNurse", methods=['POST'])
def authNurse():
    return render_template("header.html")




if(__name__ == "__main__"):
    app.run()