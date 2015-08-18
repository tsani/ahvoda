from flask import request, Response

from app import (
        app,
        db,
        util,
        models,
        basedir,
        redis,
)

from app.api_spec import (
        load_api,
        register_all,
)

from app.util import (
        ignored,
        decorate_with,
        from_rfc3339,
        jsonify,
)

from app.geocoding import (
        Geocoding,
)

from binascii import hexlify

from . import endpoints

### Manager

@decorate_with(
        endpoints['manager']['business']['collection'].handles_action('GET')
)
def get_managed_businesses(manager_name, login):
    if login.is_manager():
        manager = login.get_account()
    else:
        manager_login = models.auth.Login.query.filter_by(
                username=manager_name
        ).first()
        if manager_login is None or not manager_login.is_manager():
            return util.json_die(
                    "No such manager.",
                    404,
            )
        manager = manager_login.get_account()

    return jsonify(
            [
                business.to_dict()
                for business
                in manager.businesses
            ],
    )

@decorate_with(
        endpoints['manager']['collection'].handles_action('GET'),
)
def get_managers(login):
    app.logger.debug('getting managers')
    managers = models.accounts.Manager.query.all()

    try:
        business_id = request.args['business']
        business_id = int(business_id)
    except AttributeError:
        pass
    except ValueError:
        return util.json_die(
                'Invalid business identifier "%s".' % (
                    business_id,
                ),
                400,
        )
    else:
        # TODO refactor this to use a JOIN in the database.
        managers = [
                m
                for m
                in managers
                if any(
                    b.id == business_id
                    for b
                    in m.businesses
                )
        ]

    return jsonify(
            [
                m.to_dict()
                for m
                in managers
            ],
    )

@decorate_with(
        endpoints['manager']['collection'].handles_action('POST'),
)
def new_manager(login):
    data = request.get_json()

    gender = models.data.Gender.query.get(
            data['gender_id'],
    )

    if gender is None:
        return util.json_die(
                "No such gender.",
                404,
        )

    contact_info = models.data.ContactInfo(
            email_address=data['email_address'],
            phone_number=data['phone_number'],
    )

    human = models.data.Human(
        first_name=data['first_name'],
        last_name=data['last_name'],
        birth_date=from_rfc3339(data['birth_date']),
        gender=gender,
        contact_info=contact_info,
    )

    hashed_password, salt = util.crypto.make_password(data['password'])

    new_login = models.auth.Login(
            username=data['username'],
            password=hexlify(hashed_password).decode('utf-8'),
            password_salt=hexlify(salt).decode('utf-8'),
    )

    manager = models.accounts.Manager(
        human=human,
        login=new_login,
    )

    db.session.add(manager)
    db.session.commit()

    return jsonify(
            manager.to_dict(),
    )

@decorate_with(
        endpoints['manager']['instance'].handles_action('GET'),
)
def get_manager(manager_username, login):
    manager_login = models.auth.Login.query.filter_by(
            username=manager_username,
    ).first()

    if manager_login is None or not manager_login.is_manager():
        return util.json_die(
                "No such manager.",
                404,
        )

    account = manager_login.get_account()
    return jsonify(
            account.to_dict(),
    )
