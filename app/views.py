from app import app, forms, utils

from flask import render_template, request

from os import path
import os

from datetime import datetime

@app.route('/')
def index():
    return render_template('landing-page.html')

@app.route('/business/create-listing')
def business_create_listing():
    return render_template('create-listing.html')

@app.route('/opportunities')
def opportunities():
    return render_template('opportunities.html')

@app.route('/new-listing')
def new_listing():
    form = forms.NewListingForm()

    if form.validate_on_submit():
        return render_template('message.html', message='woot')

    return render_template('new-listing.html', form=form)
