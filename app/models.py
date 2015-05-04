from app import db

class Availability(db.Model):
    __tablename__ = 'availability'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

class Industry(db.Model):
    __tablename__ = 'industry'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

class Language(db.Model):
    __tablename__ = 'language'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    testlogin_users = relationship('testlogin',
            secondary='languagetestloginassociation')

class LanguageTestLoginAssociation(db.Model):
    __tablename__ = 'languagetestloginassociation'

    language_id = db.Column(
            db.Integer, db.ForeignKey('language'), nullable=False)
    login_id = db.Column(
            db.Integer, db.ForeignKey('testlogin'), nullable=False)

class SchoolFaculty(db.Model):
    __tablename__ = 'schoolfaculty'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

class TestLogin(db.Model):
    __tablename__ = 'testlogin'

    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=True)
    password_salt = db.Column(db.String, nullable=True)

    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    gender_id = db.Column(db.Integer, ForeignKey('gender'))
    gender = relationship('gender')
    date_of_birth = db.Column(db.DateTime, nullable=False)

    address_line_1 = db.Column(db.String, nullable=False)
    address_line_2 = db.Column(db.Stirng, nullable=False)
    postal_code = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)

    cv_original_name = db.Column(db.String, nullable=False)
    cv_name = db.Column(db.String, nullable=False)

    is_student = db.Column(db.Boolean, nullable=False)
    faculty_id = db.Column(db.Integer, nullable=True)
    faculty = relationship('SchoolFaculty')
    year = db.Column(db.Integer, nullable=True)

    canadian_citizen(db.Boolean, nullable=False)
    canadian_work(db.Boolean, nullable=False)

    availability_id = db.Column(
            db.Integer, ForeignKey('availability'), nullable=False)
    availability = relationship('availability')

    industry_1_id = db.Column(
            db.Integer, ForeignKey('industry'), nullable=False)
    # TODO figure out how to separate these
    industry_1 = relationship('industry')
    industry_2_id = db.Column(
            db.Integer, ForeignKey('industry'), nullable=False)
    industry_2 = relationship('industry')
    industry_3_id = db.Column(
            db.Integer, ForeignKey('industry'), nullable=False)
    industry_3 = relationship('industry')


class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    businesses = db.relationship('business', backref='company')

class Business(db.Model):
    __tablename__ = 'business'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location_longitude = db.Column(db.Float, nullable=False)
    location_latitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.String, nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False)

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'),
            nullable=True)

    managers = db.relationship('Mmnager', secondary='manager_set')

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
    login = db.relationship('login', backref='managers')

    businesses = db.relationship('Business', secondary='manager_set')

class ManagerSet(db.Model):
    __tablename__ = 'manager_set'

    manager_id = db.Column(
            db.Integer, db.ForeignKey('manager.id'), primary_key=True)
    business_id = db.Column(
            db.Integer, db.ForeignKey('business.id'), primary_key=True)

    manager_set_name = db.Column(
            db.String, nullable=False)
    manager_set_level = db.Column(
            db.Integer, nullable=False)

class Employee(db.Model):
    __tablename__ = 'employee'

    id = db.Column(
            db.Integer, primary_key=True)

    first_name = db.Column(
            db.String, nullable=False)
    last_name = db.Column(
            db.String, nullable=False)

    birth_date = db.Column(
            db.DateTime)

    home_address = db.Column(
            db.String, nullable=False)
    home_latitude = db.Column(
            db.Float, # TODO figure out how to make floats work with migrate
            # TODO figure out how to make constraints work with migrate
            #db.CheckConstraint(
            #    'home_latitude > -90.0 AND home_latitude < 90.0'),
            nullable=False)
    home_longitude = db.Column(
            db.Float,
            #db.CheckConstraint(
            #    'home_longitude > -180.0 AND home_longitude < 180.0'),
            nullable=False)
    home_city = db.Column(
            db.String, nullable=False)

    gender_id = db.Column(
            db.Integer, db.ForeignKey('gender.id'), nullable=False)
    gender = db.relationship('gender')

    login_id = db.Column(
            db.Integer, db.ForeignKey('login.id'), nullable=False)
    login = db.relationship('login', backref='employees')

class Job(db.Model):
    __tablename__ = 'job'

    id = db.Column(
            db.Integer, primary_key=True)

    start_date = db.Column(
            db.DateTime, nullable=True)
    end_date = db.Column(
            db.DateTime, nullable=True)
    is_available = db.Column(
            db.Boolean, nullable=False)

    salary = db.Column(
            db.Float, nullable=True)

    details = db.Column(
            db.String, nullable=False)

    create_date = db.Column(
            db.DateTime, nullable=False)

    position_id = db.Column(
            db.Integer, db.ForeignKey('position.id'), nullable=True)

    application_deadline = db.Column(
            db.DateTime, nullable=True)

    employee_id = db.Column(
            db.Integer, db.ForeignKey('employee.id'), nullable=True)

    employee = db.relationship('employee', backref='jobs')

    # TODO ON DELETE SET NULL
    manager_id = db.Column(
            db.Integer, db.ForeignKey('manager.id'), nullable=True)

    manager = db.relationship('manager', backref='listings')

class Position(db.Model):
    __tablename__ = 'position'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    create_date = db.Column(db.Date, nullable=False)

    business_id = db.Column(db.Integer, db.ForeignKey('business.id'),
            nullable=False)
    business = db.relationship('business', backref='positions')

    manager_id = db.Column(db.Integer,
            db.ForeignKey('manager.id'))
    manager = db.relationship('manager', backref='created_positions')
