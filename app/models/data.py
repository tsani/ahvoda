from app import db
from app.util import to_rfc3339

class Industry(db.Model):
    __tablename__ = 'industry'

    id = db.Column(
            db.Integer,
            primary_key=True,
    )

    name = db.Column(
            db.String,
            nullable=False,
    )

    def to_dict(self):
        return dict(
                id=self.id,
                name=self.name,
        )

class Language(db.Model):
    __tablename__ = 'language'

    id = db.Column(
            db.Integer,
            primary_key=True,
    )

    # Friendly name to show the user
    name = db.Column(
            db.String,
            nullable=False,
    )

    # ISO 639 code for the language
    iso_name = db.Column(
            db.String,
            nullable=False,
            unique=True,
    )

    employees = db.relationship(
            'Employee',
            secondary='employeelanguageset',
    )

    jobs = db.relationship(
            'Job',
            secondary='joblanguageset',
    )

    def to_dict(self):
        return dict(
                id=self.id,
                name=self.name,
                iso_name=self.iso_name,
        )

class Gender(db.Model):
    __tablename__ = 'gender'

    id = db.Column(
            db.Integer,
            primary_key=True,
    )

    name = db.Column(
            db.String,
            nullable=False,
    )

    def to_dict(self):
        return dict(
                id=self.id,
                name=self.name,
        )

class ContactInfo(db.Model):
    __tablename__ = 'contactinfo'

    id = db.Column(
            db.Integer,
            primary_key=True,
            nullable=False,
            unique=True,
    )

    phone_number = db.Column(
            db.String,
            nullable=False,
    )

    email_address = db.Column(
            db.String,
            nullable=False,
    )

    def to_dict(self):
        return dict(
                phone_number=self.phone_number,
                email_address=self.email_address,
        )

class Human(db.Model):
    __tablename__ = 'human'

    id = db.Column(
            db.Integer,
            primary_key=True,
            nullable=False,
            unique=True,
    )

    first_name = db.Column(
            db.String,
            nullable=False,
    )

    last_name = db.Column(
            db.String,
            nullable=False,
    )

    birth_date = db.Column(
            db.Date,
            nullable=False,
    )

    gender_id = db.Column(
            db.Integer,
            db.ForeignKey('gender.id'),
            nullable=True,
    )

    gender = db.relationship(
            'Gender',
            lazy='joined',
    )

    contact_info_id = db.Column(
            db.Integer,
            db.ForeignKey('contactinfo.id'),
            nullable=False,
    )

    contact_info = db.relationship(
            'ContactInfo',
            backref='human',
            uselist=False,
            lazy='joined',
    )

    def to_dict(self):
        return dict(
                first_name=self.first_name,
                last_name=self.last_name,
                birth_date=to_rfc3339(self.birth_date),
                gender=self.gender.to_dict(),
                contact_info=self.contact_info.to_dict(),
        )

    def is_employee(self):
        """ Whether the account associated with this human is an employee. """
        # The employee attribute comes from a backref given by the Employee
        # class.
        return self.employee is not None

    def is_manager(self):
        """ Whether the account associated with this human is a manager. """
        # The manager attribute comes from a backref given by the Manager
        # class.
        return self.manager is not None

    def get_account(self):
        """ Retrieve the account associated with this human. """
        account_possibilities = (
                (self.is_employee, lambda: self.employee),
                (self.is_manager, lambda: self.manager),
        )

        for predicate, thunk in account_possibilities:
            if predicate():
                return thunk()

        app.logger.warning('Human %d (%s %s) has no associated account.',
                (self.id, self.first_name, self.last_name))

        return None

