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
        
        q='''select username,type,id,name,email,contact,userId,image from User where username='{0}' and password='{1}' ;'''.format(username,password)
        cursor=mysql.connection.cursor()
        cursor.execute(q)
        record=cursor.fetchone()
        
        
        if record!=None:
            if record[1]=='Patient':
                q='''select * from patients where patient_ID='{}';'''.format(record[2])
            if record[1]=='Doctor':
                q='''select * from doctors where doctor_ID='{}';'''.format(record[2])
            if record[1]=='Hospital':
                q='''select * from hospitals where hospital_ID='{}';'''.format(record[2])
            if record[1]=='Chemist':
                q='''select * from pathological_labs where lab_ID='{}';'''.format(record[2])
            
            cursor.execute(q)
            user_info=cursor.fetchone()
            return render_template('home.html',user_data=record,user_info=user_info)
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
    
    cursor=mysql.connection.cursor()
    
    if atype=="Patient":
        q='''select t1.disease_name,t2.name,t1.disease_detected_date,t1.treatment_end_date,t3.name,t1.record_ID,t1.patient_ID from patient_history t1 inner 
        join doctors t2 on t1.doctor_ID=t2.doctor_ID inner join hospitals t3 on t1.hospital_ID=t3.hospital_ID where t1.patient_ID='{0}' order by t1.record_ID;'''.format(ID) 
    if atype=="Doctor":
        q='''select t1.disease_name,t2.name,t1.disease_detected_date,t1.treatment_end_date,t3.name,t1.record_ID,t1.patient_ID from patient_history t1 inner 
        join doctors t2 on t1.doctor_ID=t2.doctor_ID inner join hospitals t3 on t1.hospital_ID=t3.hospital_ID where t1.doctor_ID='{0}' order by t1.record_ID;'''.format(ID) 
    if atype=="Hospital":
        q='''select * from doctors_work_in_hospital t1 inner join doctors t2 on t1.doctor_ID=t2.doctor_ID where t1.hospital_ID='{}';'''.format(ID)
    if atype=="Chemist":
        q='''select * from patient_history where record_ID='{}';'''.format(recordId) 
    
    cursor.execute(q)
    record=cursor.fetchall()
    
    new_data=[]
    
    if atype=="Doctor" or atype=="Patient":
        for r in record:
            print(r)
            if r[5]!=None:
                q3='''select amount,test_ID,lab_ID from medical_test_history where record_ID='{}';'''.format(r[5])
                cursor.execute(q3)
                r3=cursor.fetchone()
            else:
                r3=[None,None,None]
            
            if r3!=None:
                q1='''select test_name from medical_tests where test_ID='{}';'''.format(r3[1])
                cursor.execute(q1)
                r1=cursor.fetchone()
            else:
                r3=[None,None,None]
                r1=[None]
                
            if r1!=None:
                q2='''select name from pathological_labs where lab_ID='{}';'''.format(r3[2])
                cursor.execute(q2)
                r2=cursor.fetchone()
            else:
                r2=[None]
            
            temp=[]
            
            for i in r[:-2]:
                temp.append(i)
            if r3!=None:
                temp.append(r3[0])
            else:
                temp.append(None)
                
            if r1!=None:
                temp.append(r1[0])
            else:
                temp.append(None)
                
            if r2!=None:
                temp.append(r2[0])
            else:
                temp.append(None)
                
            temp.append(r[5])
            temp.append(r[6])
            new_data.append(temp)
            
            record=new_data
    
    q2='''select username,type,id,name,email,contact,userId,image  from user where userId='{}';'''.format(userId)
    cursor.execute(q2)
    user_data=cursor.fetchone()
    
    
    if user_data[1]=='Patient':
        q='''select * from patients where patient_ID='{}';'''.format(user_data[2])
    if user_data[1]=='Doctor':
        q='''select * from doctors where doctor_ID='{}';'''.format(user_data[2])
    if user_data[1]=='Hospital':
        q='''select * from hospitals where hospital_ID='{}';'''.format(user_data[2])
    if user_data[1]=='Chemist':
        q='''select * from pathological_labs where lab_ID='{}';'''.format(user_data[2])
    
    cursor.execute(q)
    user_info=cursor.fetchone()
    
    return render_template('home.html',user_data=user_data,data=record,user_info=user_info)
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
    
    
    if user_data[1]=='Patient':
        q='''select * from patients where patient_ID='{}';'''.format(user_data[2])
    if user_data[1]=='Doctor':
        q='''select * from doctors where doctor_ID='{}';'''.format(user_data[2])
    if user_data[1]=='Hospital':
        q='''select * from hospitals where hospital_ID='{}';'''.format(user_data[2])
    if user_data[1]=='Chemist':
        q='''select * from pathological_labs where lab_ID='{}';'''.format(user_data[2])
    
    cursor.execute(q)
    user_info=cursor.fetchone()
    
    return render_template('home.html',user_data=user_data,symtomdata=record,user_info=user_info)
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
        
        
        if user_data[1]=='Patient':
            q='''select * from patients where patient_ID='{}';'''.format(user_data[2])
        if user_data[1]=='Doctor':
            q='''select * from doctors where doctor_ID='{}';'''.format(user_data[2])
        if user_data[1]=='Hospital':
            q='''select * from hospitals where hospital_ID='{}';'''.format(user_data[2])
        if user_data[1]=='Chemist':
            q='''select * from pathological_labs where lab_ID='{}';'''.format(user_data[2])
            
        cursor.execute(q)
        user_info=cursor.fetchone()
        
        return render_template('addpatient.html',user_data=user_data,user_info=user_info)
    
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
        # hospitalId=request.form.get('hospitalId')
        
        q2=''' select max(record_ID) from patient_history;'''
        cursor.execute(q2)
        recordId=int(cursor.fetchone()[0])+1
        
        q3='''select hospital_ID from doctors_work_in_hospital where doctor_ID='{}';'''.format(userId)
        cursor.execute(q3)
        hospitalId=cursor.fetchone()[0]
        
        q=''' INSERT INTO patient_history (disease_name, patient_ID, doctor_ID, hospital_ID,prescription_report,record_ID) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}');
        '''.format(disease_name,patientId,ID,hospitalId,prescription_report,recordId)
        cursor.execute(q)
        
        if detection_date!='':
            q=''' update patient_history set disease_detected_date='{0}' where record_ID={1};'''.format(detection_date,recordId)
            cursor.execute(q)
        
        if treatment_end_date!='':
            q=''' update patient_history set treatment_end_date='{0}' where record_ID={1};'''.format(treatment_end_date,recordId)
            cursor.execute(q)
        mysql.connection.commit()
        
        
        q2='''select username,type,id,name,email,contact,userId,image from user where userId='{}';'''.format(userId)
        cursor.execute(q2)
        user_data=cursor.fetchone()
        
        
        if user_data[1]=='Patient':
            q='''select * from patients where patient_ID='{}';'''.format(user_data[2])
        if user_data[1]=='Doctor':
            q='''select * from doctors where doctor_ID='{}';'''.format(user_data[2])
        if user_data[1]=='Hospital':
            q='''select * from hospitals where hospital_ID='{}';'''.format(user_data[2])
        if user_data[1]=='Chemist':
            q='''select * from pathological_labs where lab_ID='{}';'''.format(user_data[2])
        
        cursor.execute(q)
        user_info=cursor.fetchone()
    
        return render_template('home.html',user_data=user_data,user_info=user_info,alert="True")

if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0")