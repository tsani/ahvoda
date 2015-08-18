#!/bin/bash

source venv/bin/activate

python job-emailer.py &
python job-dispatcher.py &
python job-matcher.py &

gunicorn \
    -n ahvodaproduction \
    --pid /run/ahvoda/$AHVODATYPE-pid \
    -b unix:/run/ahvoda/$AHVODATYPE-socket \
    app:app
