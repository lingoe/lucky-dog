from xml.dom.minidom import parse, parseString
from flask import Flask, render_template, json, request,redirect,session,jsonify, url_for,send_from_directory
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash,secure_filename
from werkzeug.wsgi import LimitedStream
import werkzeug.wsgi
import uuid
import os
import sys
import xml.etree.ElementTree as etree
import pandas as pd
from pandas import DataFrame,Series
import pandas.io.sql as sql
import datetime as dt

#UPLOAD_FOLDER = os.path.curdir + os.path.sep + 'tmp' + os.path.sep
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','html','xml','doc'])

mysql = MySQL()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/Uploads/'
app.config['DOWNLOAD_FOLDER'] = 'static/Downloads/'
app.secret_key = 'why would I tell you my secret key?'

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'kuangch'
app.config['MYSQL_DATABASE_PASSWORD'] = '123'
app.config['MYSQL_DATABASE_DB'] = 'bucketlist'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#newFile = os.listdir(app.config['UPLOAD_FOLDER'])[0]

#repname = os.path.splitext(newFile)[0]
#print("filename:",repname)
#fileext = os.path.splitext(newFile)[1]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/fileupload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploads',
                                    filename=filename))
    return render_template('fileupload.html')

@app.route('/uploads')
def uploads():
    #uploadFile = os.listdir('C:\\Users\\IBM_ADMIN\\Documents\\KUANGCH_WORK\\Training\\R_Python\\Py_project\\xmlapp v1\\static\\Uploads')[0]
    #print(uploadFile)
    return render_template('xmlparse.html')

@app.route('/parsexml')
def parsexml():
    newFile = os.listdir(app.config['UPLOAD_FOLDER'])[0]

    repname = os.path.splitext(newFile)[0]
    print("filename:", repname)
    fileext = os.path.splitext(newFile)[1]

    xmldoc = parse(app.config['UPLOAD_FOLDER'] + newFile)
    print(os.path.splitext(newFile)[0])

    ############parse data item#########################
    dataite = xmldoc.getElementsByTagName('expression')
    print("dataite:", len(dataite))
    dataitenum = len(dataite)
    # print("dataite:",dataite[1].childNodes[0].nodeValue)
    j = 0
    if j < dataitenum:
        for d in dataite:
            dataitemname = dataite[j].childNodes[0].nodeValue
            con = mysql.connect()
            cursor = con.cursor()
            cursor.execute("insert into cogxml_t(dataitem) values (%s)", (dataitemname))
            cursor.execute("update cogxml_t set reportname = %s where dataitem = %s", (repname,dataitemname))
            con.commit()
            cursor.close()
            con.close()
            #print(dataitemname)
            print(dataite[j].childNodes[0].nodeValue); j = j + 1

    ############parse model#########################
    model = xmldoc.getElementsByTagName('modelPath')
    print("model:", len(model))
    datamodelpath = model[0].childNodes[0].nodeValue
    con = mysql.connect()
    cursor = con.cursor()
    cursor.execute("insert into cogxml_t(modelpath) values (%s)", (datamodelpath))
    cursor.execute("update cogxml_t set reportname = %s where modelpath = %s", (repname,datamodelpath))
    con.commit()
    cursor.close()
    con.close()
    #print(datamodelpath)
    print(model[0].childNodes[0].nodeValue)

    ############parse query#########################

#    query = xmldoc.getElementsByTagName('query')
#    querynum = len(query)
#   print(querynum)
#    print("query:", len(query))
    #reportqueryname = query[0].attributes['name'].value
#    q = 0
#    if q < querynum:
#        for f in query:
#            reportqueryname = query[q].attributes['name'].value
#            print(query[q].childNodes[0].nodeValue)
#            q = q + 1
#            con = mysql.connect()
#            cursor = con.cursor()
#            cursor.execute("insert into cogxml_t(queryname) values (%s)", (reportqueryname))
#           cursor.execute("update cogxml_t set reportname = %s", (repname))
#            con.commit()
#            cursor.close()
#            con.close()
#            #print(reportqueryname)

    ############parse filter#########################
    filter = xmldoc.getElementsByTagName('filterExpression')
    filternum = len(filter)
    print(filternum)
    # print("filter:",filter[1].childNodes[0].nodeValue)
    updt = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(updt)
    i = 0
    if i < filternum:
        for f in filter:
            reportfiltername = filter[i].childNodes[0].nodeValue
            print(filter[i].childNodes[0].nodeValue)
            con = mysql.connect()
            cursor = con.cursor()
            cursor.execute("insert into cogxml_t(filtername) values (%s)", (reportfiltername))
            cursor.execute("update cogxml_t set reportname = %s,updatetime = %s where filtername = %s", (repname,updt,reportfiltername))
            con.commit()
            cursor.close()
            con.close()
            #print(reportfiltername)
            i = i + 1

    con = mysql.connect()
    cursor = con.cursor()
    cursor.execute("select * from cogxml_t where reportname = %s and updatetime = (select max(updatetime) from cogxml_t where reportname = %s)",(repname,repname))
    results = cursor.fetchall()
    #print("results:",results)
    #datasql = "select * from cogxml_t"
    #df = pd.read_sql(datasql,con)
    df = pd.DataFrame(list(results),columns = ['reportname','modelpath','dataitem','filter','updatetime'])
    datadownloadfile = df.to_excel(app.config['DOWNLOAD_FOLDER']+repname+'.xlsx')
    #print(df)
    #datadownload = pd.DataFrame(results,columns =['a','b','c','d','e'])
    con.commit()
    cursor.close()
    con.close()
    return render_template('finish.html')

@app.route('/doDelete')
def doDelete():
    newDir = os.listdir(app.config['UPLOAD_FOLDER'])[0]
    fullpath = app.config['UPLOAD_FOLDER']+newDir
    print(fullpath)
    #if os.path.isfile(fullpath):
        #os.remove(fullpath)
    return render_template('fileupload.html')


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('fileupload.html')
    else:
        return render_template('signin.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')



@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
        

        
        # connect to mysql

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()

        


        if len(data) > 0:
            if check_password_hash(str(data[0][3]),_password):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
            

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()


@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:
            
            # All Good, let's call MySQL
            
            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()


@app.route('/downloads',methods=['GET'])
def load():
    newDir = os.listdir(app.config['UPLOAD_FOLDER'])[0]
    repname = os.path.splitext(newDir)[0]
    fullpath = app.config['UPLOAD_FOLDER']+newDir
    print(fullpath)
    if os.path.isfile(fullpath):
        os.remove(fullpath)
    if request.method == "GET":
        if os.path.isfile(os.path.join(app.config['DOWNLOAD_FOLDER'],repname+'.xlsx')):
            return send_from_directory(app.config['DOWNLOAD_FOLDER'],repname+'.xlsx', as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5002,threaded = True,debug=True)
