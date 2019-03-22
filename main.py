'''
Major project CSE-D (203, 221, 246, 249)
'''
# Import statements for system libraries
import json
import os
import requests
import time
import datetime
import base64

# Import statements for Flask
import flask
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

# Import statements for data-analytics and opencv
import cv2
import numpy as np

# Global values
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
url = 'https://hapd-api.herokuapp.com'
app = Flask(__name__)
app.secret_key = 'mAJORPROJECT19'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Redundant functions
def sendDataToAPI(data, url, route):
    data = json.dumps(data)
    headers = {'Authorization' : '', 'Accept' : 'application/json', 'Content-Type' : 'application/json'}
    try:
        r = requests.post(url+route, data=data, headers=headers)
        print("Data from api:\n", r.text)
        return json.loads(r.text)
    except:
        print("Couldn't send to webhook")

def allowed_file(filename):
    return ('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)

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
        temp = {
            "req_type": "read_nurse",
            "data": {
                "nurseId": nurseId
            }
        }
        s = sendDataToAPI(temp, url, "/nurse")
        if(s["fullfilmentText"] == "True"):
            with open("static/data/logged_in_nurse.json", "w") as f:
                json.dump(s["data"], f, indent=4)     
        return redirect(url_for("home"))
    else:
        return redirect(url_for("launch", session = session))

@app.route("/registerNewPatient", methods=['POST'])
def registerNewPatient():
    result = request.form
    print(request.files)
    if('file' not in request.files):
        error = ["Bad Image error"]
        return render_template("registerNewUser.html", error = error)
    else:
        file = request.files['file']
        if(file and allowed_file(file.filename)):
            f = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], f))
    image = cv2.imread("static/images/"+f)
    retval, buffer = cv2.imencode('.jpg', image)
    encoded = base64.b64encode(buffer)
    encoded_string_image = str(encoded)[2:-1]
    result = request.form
    error = ["No error"]
    try:
        datetime.datetime.strptime(result["date"],'%d/%m/%Y')
    except ValueError:
        error = ["Date of Birth Error"]
        return render_template("registerNewUser.html", error = error)
    with open('static/data/logged_in_nurse.json', 'r') as f:
        nurse = json.load(f)
    data = {
        "name": result["name"],
        "dob": result["date"],
        "gender": result["gender"],
        "address": result["address"],
        "bloodgroup": result["bloodgroup"],
        "nurse": nurse["name"],
        "contact": nurse["contact"],
        "nurseId": nurse["nurseId"],
        "pin": result["password"],
        "image": encoded_string_image
    }
    r = sendDataToAPI(data, url, "/addUser")
    if(r["fullfilmentText"] == "Account creation successful"):
        error.append(r["PID"])
        data = {
            "req_type": "increment_nop",
            "data": {
                "nurseId": nurse["nurseId"]
            }
        }
        r = sendDataToAPI(data, url, '/nurse')
        return render_template("registerNewUser.html", error = error)
    else:
        error = ["API error"]
        return render_template("registerNewUser.html", error = error)

@app.route('/registerNewNurse')
def registerNewNurse():
    return render_template('register_nurse.html', session = session)

@app.route('/registerNurse', methods=['POST'])
def registerNurse():
    result = request.form
    data = {
        "name": result["name"],
        "email": result["email"],
        "contact": result["contact"],
        "password": result["password"]
    }
    d = {
        "req_type": "add_nurse",
        "data": data
    }
    r = sendDataToAPI(d, url, '/nurse')
    if(r["fullfilmentText"] == "True"):
        return render_template("successNewNurse.html", result = [r["nurseId"]])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("launch", session = session))

@app.route("/home")
def home():
    nurseId = session["logged_in"]
    temp = {
            "req_type": "read_nurse",
            "data": {
                "nurseId": nurseId
            }
    }
    s = sendDataToAPI(temp, url, "/nurse")
    if(s["fullfilmentText"] == "True"):
        result = s["data"]
    return render_template('nurse_home.html', result = [result])





if(__name__ == "__main__"):
    app.run()
