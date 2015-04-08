#!/usr/bin/python

import os 
import string
import random 
import psycopg2



from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename 

class UploadForm(Form):
    
	cv = FileField('Your CV',[(validators.regexp(u'^[^/\\]\.pdf|.doc|.docx$'))])	
	
	email=TextField('Your email',[validators.DataRequired(),validators.Email()])
	
	#description = TextAreaField(u'CV file')
    
	#def validate_Upload(form,field):
    #   if field.data:
    #     field.data = re.sub(r'[^a-z0-9_.-]','_',field.data)		


UPLOAD_FOLDER = '/path/uploadfolder' # Need to set path variable 
#ALLOWED_EXTENTIONS = set (['pdf','doc','docx'])
connection= psycopg2.connect("dbname=ahvoda user=postgres")
cur= connection.cursor()

app = Flask(_name_)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['ALLOWED_EXTENTIONS'] = ALLOWED_EXTENTIONS

def random_id(size=6,char=string.ascii_uppercase+string.digits):
    return ''.join(random.choice(chars) for _ in range(size))



#def allowed_file(filename):
 #   return '.' in filename and \
	#  filename.rsplit('.',1)[1] in app.config['ALLOWED_EXTENTIONS']

	  
@app.route('/', methods=['GET', 'POST'])
def upload():
   if request.method == 'POST':  
     form = UploadForm(request.POST)
     if form.validate_on_submit():
         fileName = secure_filename(UploadForm.cv.data.filename)
		 rand = random_id()
		 cur.execute("INSERT INTO ahvoda (email,random,cv) VALUES (%s,%s,%s)",(UploadForm.email.data,rand,fileName)
         open(os.path.join(UPLOAD_PATH, UploadForm.cv.data), 'w').write(rand)    
           

