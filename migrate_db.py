#!/usr/bin/env python

import imp
import os
from migrate.versioning import api
from app import db
from secret_config import SQLALCHEMY_DATABASE_URI
from secret_config import SQLALCHEMY_MIGRATE_REPO

if __name__ == "__main__":
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)

    migration = os.path.join(
            SQLALCHEMY_MIGRATE_REPO,
            'versions/%03d_migration.py' % (v+1))

    tmp_module = imp.new_module('old_model')
    old_model = api.create_model(
            SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)

    exec(old_model, tmp_module.__dict__)

    script = api.make_update_script_for_model(
            SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO,
            tmp_module.meta, db.metadata)

    with open(migration, "wt") as m:
        m.write(script)

    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)

    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)

    print('New migration saved as ', migration)
    print('Current database version:', v)
