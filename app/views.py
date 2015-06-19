from app import app, forms, util

from flask import render_template, request

from os import path
import os

from datetime import datetime

@app.route('/')
def index():
    return util.render_template_with_data('landing-page.html')

@app.route('/business')
def business():
    return util.render_template_with_data('business-landing-page.html')
