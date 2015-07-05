from app import db
from app.util import to_rfc3339

class Administrator(db.Model):
    __tablename__ = 'administrator'

    id = db.Column(
            db.Integer, primary_key=True
    )

    login_id = db.Column(
            db.Integer,
            db.ForeignKey('login.id', ondelete='CASCADE'),
            nullable=False,
            unique=True,
    )

    login = db.relationship(
            'Login',
            backref=db.backref('administrator_account', uselist=False),
    )

    def to_dict(self):
        return dict(
                id=self.id,
                username=self.login.username,
        )

class Manager(db.Model):
    __tablename__ = 'manager'

    id = db.Column(
            db.Integer,
            primary_key=True,
    )

    human_id = db.Column(
            db.Integer,
            db.ForeignKey('human.id'),
            nullable=False,
            unique=True,
    )

    login_id = db.Column(
            db.Integer,
            db.ForeignKey('login.id', ondelete='CASCADE'),
            nullable=False,
            unique=True,
    )

    businesses = db.relationship(
            'Business',
            secondary='managerset',
    )

    human = db.relationship(
            'Human',
            backref=db.backref('manager', uselist=False),
    )

    login = db.relationship(
            'Login',
            backref=db.backref('manager_account', uselist=False),
    )

    def to_dict(self):
        return dict(
                id=self.id,
                username=self.login.username,
                human=self.human.to_dict(),
        )

class Employee(db.Model):
    __tablename__ = 'employee'

    id = db.Column(
            db.Integer,
            primary_key=True,
    )

    login_id = db.Column(
            db.Integer,
            db.ForeignKey('login.id', ondelete='CASCADE'),
            nullable=False,
            unique=True,
    )

    is_verified = db.Column(
            db.Boolean,
            nullable=False,
    )

    human_id = db.Column(
            db.Integer,
            db.ForeignKey('human.id'),
            nullable=False,
            unique=True,
    )

    home_location_id = db.Column(
            db.Integer,
            db.ForeignKey('location.id'),
            nullable=False,
    )

    home_location = db.relationship(
            'Location',
    )

    languages = db.relationship(
            'Language',
            secondary='employeelanguageset',
    )

    human = db.relationship(
            'Human',
            backref='employee',
            uselist=False,
            lazy='joined',
    )

    login = db.relationship(
            'Login',
            backref=db.backref('employee_account', uselist=False),
    )

    applications = db.relationship(
            'Job',
            secondary='applicant',
    )

    def to_dict(self):
        return dict(
                id=self.id,
                username=self.login.username,
                is_verified=self.is_verified,
                human=self.human.to_dict(),
                home_location=self.home_location.to_dict(),
                languages=[
                    lang.to_dict()
                    for lang
                    in self.languages
                ],
        )

