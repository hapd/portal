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
        "nurse_id": nurseId,
        "password": password
    }
    r = sendDataToAPI(data, "https://hapd.herokuapp.com", "/nurses/authenticate")
    if(r["fullfilmentText"] == "True"):
        session["logged_in"] = nurseId
        
        try:
            s = requests.get("http://hapd.herokuapp.com/nurses/%s"%(nurseId))
            print("Data from api:\n", s.text)
            if(json.loads(s.text)["fullfilmentText"] == "True"):
                with open("static/data/logged_in_nurse.json", "w") as f:
                    json.dump(json.loads(s.text), f, indent=4) 
            return redirect(url_for("home"))
        except:
            print("Couldn't send to webhook")
            return redirect(url_for("launch", session = session))
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
        "stage": result["stage"],
        "address": result["address"],
        "bloodgroup": result["bloodgroup"],
        "nurse": nurse["data"]["data"]["name"],
        "contact": nurse["data"]["data"]["contact"],
        "nurse_id": nurse["data"]["data"]["_id"],
        "password": result["password"],
        "image": encoded_string_image
    }
    
    r = sendDataToAPI(data, "https://hapd.herokuapp.com", "/patients")
    if(r["fullfilmentText"] == "True"):
        error.append(r["PID"])
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
    print(request.files)
    if('file' not in request.files):
        error = ["Bad Image error"]
        return render_template("successNewNurse.html", result = [False, error])
    else:
        file = request.files['file']
        if(file and allowed_file(file.filename)):
            f = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], f))
    image = cv2.imread("static/images/"+f)
    retval, buffer = cv2.imencode('.jpg', image)
    encoded = base64.b64encode(buffer)
    encoded_string_image = str(encoded)[2:-1]
    data = {
        "name": result["name"],
        "email": result["email"],
        "contact": result["contact"],
        "password": result["password"],
        "image": encoded_string_image
    }
    r = sendDataToAPI(data, 'https://hapd.herokuapp.com', '/nurses')
    if(r["fullfilmentText"] == "True"):
        return render_template("successNewNurse.html", result = [True, r["nurse_id"]])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("launch", session = session))

@app.route("/home")
def home():
    nurseId = session["logged_in"]
    result = []
    r = requests.get("https://hapd.herokuapp.com/nurses/"+nurseId)
    if(json.loads(r.text)["fullfilmentText"] == "True"):
        result.append(json.loads(r.text)['data']['data'])
    r = requests.get("https://hapd.herokuapp.com/patients/nurse/"+nurseId)
    patients = json.loads(r.text)['data']
    dataset = [0,0,0,0,0,0]
    for patient in patients:
        if(patient['age']<30):
            dataset[0] += 1
        elif(patient['age']>=30 and patient['age']<40):
            dataset[1] += 1
        elif(patient['age']>=40 and patient['age']<50):
            dataset[2] += 1
        elif(patient['age']>=50 and patient['age']<60):
            dataset[3] += 1
        elif(patient['age']>=60 and patient['age']<70):
            dataset[4] += 1
        elif(patient['age']>=70):
            dataset[5] += 1
    result.append(dataset)
    return render_template('nurse_home.html', result = result, session = session)

@app.route('/home/profile')
def profile():
    return render_template('nurse_profile.html')

if(__name__ == "__main__"):
    app.run()
