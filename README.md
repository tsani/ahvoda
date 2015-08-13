Setup
=====

Get a `secret_config.py` file and tweak it to account for the location of your
database and cache.

Build the application.

    make all

This will set up a Python virtualenv called venv (if necessary), install all
python dependencies to it, install all npm dependencies to `app/node_modules`,
build all the frontend JavaScript and LESS, and run any pending database
migrations.

Contact
=======

    jake@mail.ahvoda.com
