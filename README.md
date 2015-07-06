Setup
=====

Create a python3 virtualenv

    virtualenv venv
    source venv/bin/activate

Build the app

    make

Get a `secret_config.py` file and tweak it. The important properties are

* `SQLALCHEMY_DATABASE_URI`: describes where the database is.

The rest don't require tweaking, but contain sensitive information.

Contact
=======

    jake@mail.ahvoda.com
