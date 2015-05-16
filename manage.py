#!/usr/bin/env python

from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand

from app import app
from app import db

manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
