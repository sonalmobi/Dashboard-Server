import random
import time
import math
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, Time
import os
import datetime

T1 = time.time()

# PgAdmin4 DB
# POSTGRES_URL = "localhost:5433"
# POSTGRES_USER = "postgres"
# POSTGRES_PW = "Astrome123"
# POSTGRES_DB = "APIdb"
# DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)

# SQLite DB
dataLocation = '/mnt/5a576321-1b84-46e6-ba92-46de6b117d92/Dump'
DB_URL = 'sqlite:///'+os.path.join(dataLocation, 'database.db')

app = Flask(__name__)
# app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL


db = SQLAlchemy(app)
allIds = [2,17,18,19]
allHosts = ["AstromePi02","Astrome15","Astrome15","AstromePi02"]
allMetrics = ["temp1","cpuutilpcent","temp1","cpuutilpcent"]
allLocations = ["SID-2","SID-2","SID-2","SID-2"]


# Database Models
class Idmetric(db.Model):
    __tablename__ = 'idmetric'
    id = Column(Integer, primary_key=True)
    hostname = Column(String)
    metric = Column(String)


class Idvalue(db.Model):
    __tablename__ = 'idvalue'
    time = Column(DateTime, primary_key=True)
    id = Column(Integer)
    value = Column(String)

class login(db.Model):
    __tablename__ = 'login'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)


# CLI functions
@app.cli.command('db_createCLI')
def db_createCLI():
    db.create_all()
    print('Database Created !')


@app.cli.command('db_dropCLI')
def db_dropCLI():
    db.drop_all()
    print('Database Dropped !')


# Helper functions
def db_create():
    db.create_all()
    print('Database Created !')


def db_drop():
    db.drop_all()
    print('Database Dropped !')


def db_seed():
    for i,a in enumerate(allIds):
        tableRow = Idmetric(id = a,
                    hostname = allHosts[i],
                    metric = allMetrics[i],
                    )
        db.session.add(tableRow)

    db.session.commit()

    print('Database Seeded !')


def addIdVal(id, val):
    idVal2 = Idvalue(id = id,
                    value = str(val),
                    time = datetime.datetime.now())

    db.session.add(idVal2)
    db.session.commit()


db_drop()
db_create()
db_seed()


# Routes
@app.route('/')
def hello_world():
    data = {}
    for i in allIds:

        print('Adding date to: {}'.format(i))
        time.sleep(0.1)
        t2 = time.time()
        val = math.sin((2*math.pi/30)  * (t2 - T1)) + random.random()
        addIdVal(i, val)
        data[i] = val
    return render_template("index.html", data=data)


if __name__ == '__main__':
    import webbrowser
    webbrowser.open("http://127.0.0.1:8000/")
    app.run(port='8000')
