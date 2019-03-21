# Import statements for system libraries
import json
import os
import requests
import time
import datetime

# Import statements for Flask
import flask
from flask import Flask, render_template, request, redirect, url_for, session

# Import statements for local modules
#from functions.func import sendDataToAPI

def sendDataToAPI(data, url, route):
    data = json.dumps(data)
    headers = {'Authorization' : '', 'Accept' : 'application/json', 'Content-Type' : 'application/json'}
    try:
        r = requests.post(url+route, data=data, headers=headers)
        print("Data from api:\n", r.text)
        return json.loads(r.text)
    except:
        print("Couldn't send to webhook")

# Global values
url = 'https://hapd-api.herokuapp.com'
app = Flask(__name__)
app.secret_key = 'mAJORPROJECT19'
@app.route("/")
def launch():
    return render_template('launch.html', session = session)

@app.route("/authNurse", methods=['POST'])
def authNurse():
    result = request.form
    nurseId = result["nurseId"]
    password = result["nursePassword"]
    data = {
        "id": nurseId,
        "password": password
    }
    r = sendDataToAPI(data, url, "/authenticateNurse")
    if(r["fullfilmentText"] == "Access Granted"):
        session["logged_in"] = nurseId
        return redirect(url_for("home"))
    else:
        return redirect(url_for("launch", session = session))

@app.route("/registerNewPatient", methods=['POST'])
def registerNewPatient():
    result = request.form
    error = ["No error"]
    try:
        datetime.datetime.strptime(result["date"],'%d/%m/%Y')
    except ValueError:
        error = ["Date of Birth Error"]
        return render_template("registerNewUser.html", error = error)
    data = {
        "name": result["name"],
        "dob": result["date"],
        "gender": result["gender"],
        "address": result["address"],
        "bloodgroup": result["bloodgroup"]
    }
    r = sendDataToAPI(data, url, "/addUser")
    if(r["fullfilmentText"] == "Account creation successful"):
        error.append(r["PID"])
        return render_template("registerNewUser.html", error = error)
    else:
        error = ["API error"]
        return render_template("registerNewUser.html", error = error)



@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    return redirect(url_for("launch", session = session))

@app.route("/home")
def home():
    return render_template('nurse_home.html', result = ['dashboard'])





if(__name__ == "__main__"):
    app.run()
