import logging
from flask import Flask,render_template,request,json,Response,jsonify
from flask_mysqldb import MySQL
from dotenv import load_dotenv, find_dotenv
import os

file_handler= logging.FileHandler('Project.log')

app = Flask(__name__,template_folder="templates",static_folder='static')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO) 


load_dotenv(find_dotenv())
DB_NAME=os.getenv("DB_NAME")
DB_USERNAME=os.getenv("DB_USERNAME")
DB_PASSWORD=os.getenv("DB_PASSWORD")
DB_HOST=os.getenv("DB_HOST")

app.config['MYSQL_HOST'] = DB_HOST
app.config['MYSQL_USER'] = DB_USERNAME
app.config['MYSQL_PASSWORD'] = DB_PASSWORD
app.config['MYSQL_DB'] = DB_NAME
mysql = MySQL(app)


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status':404,
        'message':'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    if request.method=="POST":
        data=request.form
        username=data.get('username')
        password=data.get('password')
        
        q='''select name,type,id from User where username='{0}' and password='{1}' ;'''.format(username,password)
        cursor=mysql.connection.cursor()
        cursor.execute(q)
        record=cursor.fetchone()
        
        if record!=None:
            return render_template('home.html',user_data=record)
        else:
            return render_template('login.html',error="Incorrect Username Or password")
        
@app.route("/searchPatient",methods=['GET','POST'])
def searchPatient():
    ID=request.args.get('ID')
    name=request.args.get('name')
    atype=request.args.get('type')
         
    cursor=mysql.connection.cursor()
    
    if atype=="Patient":
        q='''select t1.disease_name,t2.name,t1.disease_detected_date,t1.treatment_end_date,t3.name,t5.test_name,t6.name,t4.amount from patient_history t1 inner 
        join doctors t2 on t1.doctor_ID=t2.doctor_ID inner join hospitals t3 on t1.hospital_ID=t3.hospital_ID inner join medical_test_history t4 on t1.record_ID=t4.record_ID 
        inner join pathological_labs t6 on t4.lab_ID=t6.lab_ID inner join medical_tests t5 on t5.test_ID=t4.test_ID where t1.patient_ID='{0}';'''.format(ID) 
        
    cursor.execute(q)
    record=cursor.fetchall()
    
    user_data=[name,atype,ID]
    
    return render_template('home.html',user_data=user_data,data=record)
if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0")