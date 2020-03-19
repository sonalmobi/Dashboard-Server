from datetime import datetime as dt
from flask import Flask, jsonify, request,session,render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Time
import pandas as pd
import os
from flask_marshmallow import Marshmallow

# API settings
app = Flask(__name__)
app.debug = True

### PgAdmin4 DB settings
##  Astrome DB parameters
# POSTGRES_URL = "192.168.2.227"
# POSTGRES_USER = "sonal"
# POSTGRES_PW = "sonal"
# POSTGRES_DB = "tutorial"
## My DB parameters
# POSTGRES_URL = "localhost:5433"
# POSTGRES_USER = "postgres"
# POSTGRES_PW = "Astrome123"
# POSTGRES_DB = "APIdb"
# DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)

### sqlite DB settings
dataLocation = 'sqliteDB'
DB_URL = 'sqlite:///'+os.path.join(dataLocation, 'database.db')

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Idmetric(db.Model):
    __tablename__ = 'idmetric'
    id = Column(Integer, primary_key=True)
    hostname = Column(String)
    metric = Column(String)


class Idvalue(db.Model):
    __tablename__ = 'idvalue'
    time = Column(DateTime, primary_key=True)# Try DateTime if the database column type is DateTime
    id = Column(Integer)
    value = Column(String)


class login(db.Model):
    __tablename__ = 'login'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)


class IdmetricSchema(ma.Schema):
    class Meta:
        fields = ('id','hostname','metric','location')


class IdvalueSchema(ma.Schema):
    class Meta:
        fields = ('id','value','time')


idmetric_schema = IdmetricSchema(many = True)
idvalue_schema = IdvalueSchema(many = True)

# Routes
@app.route('/getIDs')
def getIDs():
    table = Idmetric.query.all()
    result = idmetric_schema.dump(table)
    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/getData')
def getData():
    request_id = request.args.get('id')
    request_count = int(request.args.get('nVals'))
    if 'fromDate' in request.args.keys():
        fromDate = dt.strptime(request.args.get('fromDate'),'%Y-%m-%dT%H:%M:%S')
        toDate = dt.strptime(request.args.get('toDate'),'%Y-%m-%dT%H:%M:%S')
        table = Idvalue.query.filter(Idvalue.id==request_id,
                                          Idvalue.time.between(fromDate,toDate))
        result = idvalue_schema.dump(table)
        if request_count > len(result):
            response = jsonify(result)
        else:
            steP = round(len(result)/request_count)
            resultSlice = result[-1:0:-steP][::-1]
            response = jsonify(resultSlice)

        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        table = Idvalue.query.filter(Idvalue.id==request_id)
        result = idvalue_schema.dump(table)
        response = jsonify(result[-1])
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route('/getDataLatest')
def getDataLatest():
    request_id = request.args.get('id')
    request_count = int(request.args.get('nVals'))
    table = Idvalue.query.filter(Idvalue.id==request_id)
    result = idvalue_schema.dump(table)
    response = jsonify(result[-request_count:])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    app.run(host="localhost",port='8001')
