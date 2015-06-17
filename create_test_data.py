from app import db, models
from app.util import crypto

from datetime import datetime, date

from binascii import hexlify

import sys

asdf_password, asdf_password_salt = [
        hexlify(s).decode('utf-8')
        for s
        in crypto.make_password('asdf')
]

def make(cls, select, create):
    return cls.query.filter_by(**select).first() or cls(**create)

def make_easy(cls, **kwargs):
    return make(cls, kwargs, kwargs)

if __name__ == '__main__':
    db.session.autoflush = False

    [male, female, other_gender] = [
            make_easy(models.Gender, **d)
            for d
            in [
                dict(
                    name='male',
                ),
                dict(
                    name='female',
                ),
                dict(
                    name='other',
                )
            ]
    ]

    db.session.add(male)
    db.session.add(female)
    db.session.add(other_gender)

    db.session.commit()

    [canada] = [
            make_easy(models.Country, **d)
            for d
            in [
                dict(
                    name='Canada',
                ),
            ]
    ]

    db.session.add(canada)

    db.session.commit()

    [quebec, ontario] = [
            make_easy(models.State, **d)
            for d
            in [
                dict(
                    name='Quebec',
                    country=canada,
                ),
                dict(
                    name='Ontario',
                    country=canada,
                ),
            ]
    ]

    db.session.add(quebec)
    db.session.add(ontario)

    db.session.commit()

    [montreal] = [
            make_easy(models.City, **d)
            for d
            in [
                dict(
                    name='Montreal',
                    state=quebec,
                ),
            ]
    ]

    db.session.add(montreal)

    db.session.commit()

    [english, french] = [
            make_easy(models.Language, **d)
            for d
            in [
                dict(
                    name='English',
                    iso_name='en',
                ),
                dict(
                    name='French',
                    iso_name='fr',
                ),
            ]
    ]

    db.session.add(english)
    db.session.add(french)

    db.session.commit()

    [fooddrink, nightlife] = [
            make_easy(models.Industry, **d)
            for d
            in [
                dict(
                    name='fooddrink',
                ),
                dict(
                    name='nightlife',
                ),
            ]
    ]

    db.session.add(fooddrink)
    db.session.add(nightlife)

    db.session.commit()

    employee_contact_info = make(
            models.ContactInfo,
            dict(
                phone_number='5140000001',
            ),
            dict(
                phone_number='5140000001',
                email_address='employee@test.com',
            ),
    )

    manager_contact_info = make(
            models.ContactInfo,
            dict(
                phone_number='5140000002',
            ),
            dict(
                phone_number='5140000002',
                email_address='manager@test.com',
            ),
    )

    business_contact_info = make(
            models.ContactInfo,
            dict(
                phone_number='5140000003',
            ),
            dict(
                phone_number='5140000003',
                email_address='business@test.com',
            ),
    )

    db.session.add(employee_contact_info)
    db.session.add(manager_contact_info)
    db.session.add(business_contact_info)

    db.session.commit()

    human_employee = make(
            models.Human,
            dict(
                first_name='fname-employee',
            ),
            dict(
                first_name='fname-employee',
                last_name='lname-employee',
                birth_date=date(1995, 1, 10),
                gender=male,
                contact_info=employee_contact_info,
            ),
    )

    human_manager = make(
            models.Human,
            dict(
                first_name='fname-manager',
            ),
            dict(
                first_name='fname-manager',
                last_name='lname-manager',
                birth_date=date(1995, 1, 10),
                gender=male,
                contact_info=manager_contact_info,
            ),
    )

    db.session.add(human_employee)
    db.session.add(human_manager)

    home_location = make(
            models.Location,
            dict(
                address='1105 rue Woodland',
            ),
            dict(
                address='1105 rue Woodland',
                city=montreal,
                latitude=45.0,
                longitude=-73,
                postal_code='h0h0h0',
            ),
    )

    business_location = make(
            models.Location,
            dict(
                address="404 rue de l'Introuvable",
            ),
            dict(
                address="404 rue de l'Introuvable",
                city=montreal,
                latitude=45.0,
                longitude=-73,
                postal_code='h0h0h0',
            ),
    )

    db.session.add(home_location)
    db.session.add(business_location)

    employee = make(
            models.Employee,
            dict(
                human=human_employee,
            ),
            dict(
                human=human_employee,
                is_verified=True,
                home_location=home_location,
                languages=[
                    english,
                    french,
                ],
            )
    )

    business = make(
            models.Business,
            dict(
                name='Test Business',
            ),
            dict(
                name='Test Business',
                description='We serve test burgers.',
                location=business_location,
                is_verified=True,
                industry=fooddrink,
                contact_info=business_contact_info,
            )
    )

    company = make(
            models.Company,
            dict(
                name='Awesomecorp',
            ),
            dict(
                name='Awesomecorp',
                businesses=[
                    business
                ],
            )
    )

    manager = make(
            models.Manager,
            dict(
                human=human_manager,
            ),
            dict(
                human=human_manager,
                businesses=[
                    business
                ],
            ),
    )

    administrator = \
            models.Administrator.query.first() or models.Administrator()

    employee_login = make(
            models.Login,
            dict(
                username='test-employee',
            ),
            dict(
                username='test-employee',
                password=asdf_password,
                password_salt=asdf_password_salt,
                employee_account=employee,
            ),
    )

    manager_login = make(
            models.Login,
            dict(
                username='test-manager',
            ),
            dict(
                username='test-manager',
                password=asdf_password,
                password_salt=asdf_password_salt,
                manager_account=manager,
            ),
    )

    administrator_login = make(
            models.Login,
            dict(
                username='test-administrator',
            ),
            dict(
                username='test-administrator',
                password=asdf_password,
                password_salt=asdf_password_salt,
                administrator_account=administrator,
            ),
    )

    db.session.add(manager)
    db.session.add(employee)
    db.session.add(administrator)
    db.session.add(employee_login)
    db.session.add(manager_login)
    db.session.add(administrator_login)

    db.session.commit()
