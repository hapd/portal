# Import statements for Flask
import flask
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/dashboard")
def dashboard():
    return render_template('header.html', result = ['dashboard'])



if(__name__ == "__main__"):
    app.run()