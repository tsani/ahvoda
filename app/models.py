from app import db

class Position(db.Model):
    __tablename__ = 'position'

    positionId = db.Column(db.Integer, primary_key=True)
    positionName = db.Column(db.String, nullable=False)
    create_date = db.Column(db.Date, nullable=False)

    businessId = db.Column(db.Integer, db.ForeignKey('business.id'),
            nullable=False)
    business = db.relationship('business',
            backref=db.backref('positions', order_by=positionId))

    managerId = db.Column(db.Integer,
            db.ForeignKey('manager.id'))
    manager = db.relationship('manager',
            backref=db.backref('manager', order_by=managerId))

class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

class Business(db.Model):
    __tablename__ = 'business'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location_longitude = db.Column(db.Float, nullable=False)
    location_latitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.String, nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False)

    companyId = db.Column('companyid', db.Integer, db.ForeignKey('company.id'),
            nullable=True)
    company = db.relationship('company',
            backref='companyId')

class Gender(db.Model):
    __tablename__ = 'gender'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

class Login(db.Model):
    __tablename__ = 'login'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    password_salt = db.Column(db.String, nullable=False)
    create_date = db.Column(db.DateTime, nullable=False)

class Manager(db.Model):
    __tablename__ = 'manager'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)

    gender_id = db.Column(db.Integer, db.ForeignKey('gender.id'),
            nullable=True)
    gender = db.relationship('gender')

    login_id = db.Column(db.Integer, db.ForeignKey('login.id'),
            nullable=False)
    login = db.relationship('login',
            backref=db.backref('account', uselist=False))
