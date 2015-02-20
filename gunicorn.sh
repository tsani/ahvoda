#!/bin/bash

exec gunicorn -n ahvoda -b 127.0.0.1:8765 app:app
