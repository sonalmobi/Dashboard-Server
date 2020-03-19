import requests, json
import io
import time
from datetime import datetime as dt
from datetime import timedelta
from flask import Flask, render_template, Response, request, redirect,url_for,session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, create_engine
from functools import wraps

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
import seaborn as sns
sns.set()
sns.set_context("notebook", font_scale=0.95, rc={"lines.linewidth": 1.5})
#sns.set_style("ticks", {"xtick.major.size": 8, "ytick.major.size": 8,'axes.facecolor': '#EAEAF2'})
#sns.set_style("dark")

from flask_change_password import ChangePassword, ChangePasswordForm, SetPasswordForm

app = Flask(__name__)
app.debug = True
APIurl = 'http://127.0.0.1:8001/'
numOfPoints = 20

app.secret_key = 'my precious'


def createPlot(df2plot):
    df2plot['time'] = pd.to_datetime(df2plot['time'])
    fig = Figure()
    fig.set_facecolor('white')
    axis = fig.add_subplot(1, 1, 1)
    df2plot.plot(x='time',y='value',ax=axis, color='#007bff', xticks=df2plot['time'][::2],style='.-',ms=15)
    df2plot.plot.area(x='time',y='value',ax=axis, color='#007bff',alpha=0.2,legend=False,stacked=False)
    axis.tick_params(axis = 'x', rotation = 0)
    axis.set_xticklabels(df2plot['time'][::2].map(lambda x: dt.strftime(x, '%I:%M %p')))
    output = io.BytesIO()
    return fig, output


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route('/')
@login_required
def index():
    response = requests.get(APIurl + 'getIDs')
    df = pd.read_json(response.text)
    data = df['hostname'].unique()
    return render_template("index.html",data=data)


@app.route("/index/host-<name>")
def showHostIds(name):
    response = requests.get(APIurl + 'getIDs')
    df = pd.read_json(response.text)
    allIds = df.loc[df['hostname']==name][['hostname','id','metric']]
    idList = allIds['id'].values.tolist()
    return render_template("displayIDs.html",data = allIds.values.tolist(), idList = idList)


@app.route('/index/chartJS-<int:id>-<metric>')
def chartJS(id,metric):
    return render_template('individualChart.html', id = id, metric=metric)


@app.route('/index/buttons')
def buttons():
    return render_template('buttons.html')


@app.route("/numberOfDataPoints-<int:id>", methods=['POST'])
def hello(id):
    global numOfPoints
    myvariable = request.form.get("timeDropdown")
    numOfPoints = myvariable
    return redirect("/index/idvalue-{}".format(id))


@app.route("/idvalue-<int:id>.svg")
def plot_png(id):
    response = requests.get(APIurl + 'getDataLatest?id={}&nVals={}'.format(id,10))
    data = pd.read_json(response.text)
    fig, output = createPlot(data)

    FigureCanvasSVG(fig).print_svg(output)
    return Response(output.getvalue(), mimetype="image/svg+xml")


@app.route("/idvalueExpand-<int:id>.svg")
def expand_png(id):
    response = requests.get(APIurl + 'getData?id={}&nVals={}'.format(id,numOfPoints))
    data = pd.read_json(response.text)
    fig, output = createPlot(data)

    FigureCanvasSVG(fig).print_svg(output)
    return Response(output.getvalue(), mimetype="image/svg+xml")


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            flash('You were just logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    flash('You were just logged out')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(port='8002')
