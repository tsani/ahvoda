from app import app, forms, utils

from flask import render_template, request

from os import path
import os

from datetime import datetime

@app.route('/')
def index():
    return render_template('landing-page.html')

@app.route('/business')
def business():
    return render_template('business-landing-page.html')
