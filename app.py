import logging
from flask import Flask,render_template,request,json,Response,jsonify,redirect
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
        
        q='''select username,type,id,name,email,contact,userId,image  from User where username='{0}' and password='{1}' ;'''.format(username,password)
        cursor=mysql.connection.cursor()
        cursor.execute(q)
        record=cursor.fetchone()
        
        if record!=None:
            return render_template('home.html',user_data=record)
        else:
            return render_template('login.html',error="Incorrect Username Or password")

@app.route("/",methods=['GET','POST'])
def main():
    return redirect('/login')
@app.route("/searchPatient",methods=['GET','POST'])
def searchPatient():
    ID=request.args.get('ID')
    name=request.args.get('name')
    atype=request.args.get('type')
    recordId=request.args.get('recordId')
    userId=request.args.get('userId')

    print(request.args)
    
    cursor=mysql.connection.cursor()
    
    if atype=="Patient":
        q='''select t1.disease_name,t2.name,t1.disease_detected_date,t1.treatment_end_date,t3.name,t5.test_name,t6.name,t4.amount,t1.patient_ID from patient_history t1 inner 
        join doctors t2 on t1.doctor_ID=t2.doctor_ID inner join hospitals t3 on t1.hospital_ID=t3.hospital_ID inner join medical_test_history t4 on t1.record_ID=t4.record_ID 
        inner join pathological_labs t6 on t4.lab_ID=t6.lab_ID inner join medical_tests t5 on t5.test_ID=t4.test_ID where t1.patient_ID='{0}';'''.format(ID) 
    if atype=="Doctor":
        q='''select t1.disease_name,t2.name,t1.disease_detected_date,t1.treatment_end_date,t3.name,t5.test_name,t6.name,t4.amount,t1.patient_ID from patient_history t1 inner 
        join doctors t2 on t1.doctor_ID=t2.doctor_ID inner join hospitals t3 on t1.hospital_ID=t3.hospital_ID inner join medical_test_history t4 on t1.record_ID=t4.record_ID 
        inner join pathological_labs t6 on t4.lab_ID=t6.lab_ID inner join medical_tests t5 on t5.test_ID=t4.test_ID where t1.doctor_ID='{0}';'''.format(ID) 
    if atype=="Hospital":
        q='''select * from doctors_work_in_hospital t1 inner join doctors t2 on t1.doctor_ID=t2.doctor_ID where t1.hospital_ID='{}';'''.format(ID)
    if atype=="Chemist":
        q='''select * from patient_history where record_ID='{}';'''.format(recordId) 
    
    cursor.execute(q)
    record=cursor.fetchall()
    
    q2='''select username,type,id,name,email,contact,userId,image  from user where userId='{}';'''.format(userId)
    cursor.execute(q2)
    user_data=cursor.fetchone()
    
    return render_template('home.html',user_data=user_data,data=record)
@app.route("/searchSymtoms",methods=['GET','POST'])
def searchSymtoms():
    ID=request.args.get('ID')
    name=request.args.get('name')
    atype=request.args.get('type')
    symptomname=request.args.get('symptomname')
         
    userId=request.args.get('userId')
    cursor=mysql.connection.cursor()
    
    q='''select * from diseases where symptoms like '%{}%';'''.format(symptomname)
    cursor.execute(q)
    record=cursor.fetchall()
    
    q2='''select username,type,id,name,email,contact,userId,image   from user where userId='{}';'''.format(userId)
    cursor.execute(q2)
    user_data=cursor.fetchone()
    
    return render_template('home.html',user_data=user_data,symtomdata=record)
@app.route("/addPatient",methods=['GET','POST'])
def addPatient():
    
    cursor=mysql.connection.cursor()

    if request.method=='GET':
        ID=request.args.get('ID')
        name=request.args.get('name')
        atype=request.args.get('type')
        userId=request.args.get('userId')
        
        q2='''select username,type,id,name,email,contact,userId,image   from user where userId='{}';'''.format(userId)
        cursor.execute(q2)
        user_data=cursor.fetchone()
        return render_template('addpatient.html',user_data=user_data)
    
    if request.method=='POST':
        ID=request.form.get('ID')
        name=request.form.get('name')
        atype=request.form.get('type')
        userId=request.form.get('userId')
        
        disease_name=request.form.get('disease_name')
        patientId=request.form.get('patientId')
        prescription_report=request.files.get('prescription_report')
        detection_date=request.form.get('detection_date')
        treatment_end_date=request.form.get('treatment_end_date')
        hospitalId=request.form.get('hospitalId')
        
        q2=''' select max(record_ID) from patient_history;'''
        cursor.execute(q2)
        recordId=int(cursor.fetchone()[0])+1
        
        q=''' INSERT INTO patient_history (disease_name, patient_ID, doctor_ID, disease_detected_date, 
        treatment_end_date, hospital_ID,prescription_report,record_ID) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}','{6}','{7}');
        '''.format(disease_name,patientId,ID,detection_date,treatment_end_date,hospitalId,prescription_report,recordId)
        cursor.execute(q)
        mysql.connection.commit()
        
        
        q2='''select username,type,id,name,email,contact,userId,image   from user where userId='{}';'''.format(userId)
        cursor.execute(q2)
        user_data=cursor.fetchone()
    
        return render_template('home.html',user_data=user_data)

if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0")