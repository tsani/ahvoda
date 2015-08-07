#!/bin/bash

source venv/bin/activate
exec gunicorn -n ahvodaproduction --pid /run/ahvoda/$AHVODATYPE-pid -b unix:/run/ahvoda/$AHVODATYPE-socket app:app 
