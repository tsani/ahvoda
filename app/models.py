from app import db

class Rating(db.Model):
    __tablename__ = 'rating'

    job_id = db.Column(
            db.Integer, db.ForeignKey('job.id'), primary_key=True)

    job = db.relationship(
            'Job', lazy='joined', uselist=False)

    employee_rating = db.Column(
            db.Float, nullable=False)

    employee_comment = db.Column(
            db.String, nullable=True)

    job_rating = db.Column(
            db.Float, nullable=False)

    job_comment = db.Column(
            db.String, nullable=True)

class Industry(db.Model):
    __tablename__ = 'industry'

    id = db.Column(
            db.Integer, primary_key=True)

    name = db.Column(
            db.String, nullable=False)

    businesses = db.relationship(
            'Business')

class Language(db.Model):
    __tablename__ = 'language'

    id = db.Column(
            db.Integer, primary_key=True)

    # Friendly name to show the user
    name = db.Column(
            db.String, nullable=False)

    # ISO 639 code for the language
    iso_name = db.Column(
            db.String, nullable=True, unique=True)

    employees = db.relationship(
            'Employee', secondary='employeelanguageset')

    jobs = db.relationship(
            'Job', secondary='joblanguageset')

class EmployeeLanguageSet(db.Model):
    __tablename__ = 'employeelanguageset'

    __table_args__ = (
            db.PrimaryKeyConstraint('language_id', 'employee_id'),
    )

    language_id = db.Column(
            db.Integer, db.ForeignKey('language.id', ondelete='CASCADE'),
            nullable=False)

    employee_id = db.Column(
            db.Integer, db.ForeignKey('employee.id', ondelete='CASCADE'),
            nullable=False)

class JobLanguageSet(db.Model):
    __tablename__ = 'joblanguageset'

    __table_args__ = (
            db.PrimaryKeyConstraint('language_id', 'job_id'),
    )

    language_id = db.Column(
            db.Integer, db.ForeignKey('language.id', ondelete='CASCADE'),
            nullable=False)

    job_id = db.Column(
            db.Integer, db.ForeignKey('job.id', ondelete='CASCADE'),
            nullable=False)

class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(
            db.Integer, primary_key=True)

    name = db.Column(
            db.String, nullable=False)

    businesses = db.relationship(
            'Business', backref='company')

class City(db.Model):
    __tablename__ = 'city'

    id = db.Column(
            db.Integer, primary_key=True)

    name = db.Column(
            db.String, nullable=False)

class Country(db.Model):
    __tablename__ = 'country'

    id = db.Column(
            db.Integer, primary_key=True)

    name = db.Column(
            db.String, nullable=False)

class Location(db.Model):
    __tablename__ = 'location'

    id = db.Column(
            db.Integer, primary_key=True)

    address = db.Column(
            db.String, nullable=False)

    city_id = db.Column(
            db.Integer, db.ForeignKey('city.id'), nullable=False)

    city = db.relationship(
            'City')

    country_id = db.Column(
            db.Integer, db.ForeignKey('country.id'), nullable=False)

    country = db.relationship(
            'Country')

    latitude = db.Column(
            db.Float,
            db.CheckConstraint(
                'latitude > -90.0 AND latitude < 90.0'),
            nullable=False)

    longitude = db.Column(
            db.Float,
            db.CheckConstraint(
                'longitude > -180.0 AND longitude < 180.0'),
            nullable=False)

class BusinessLocationSet(db.Model):
    __tablename__ = 'businesslocationset'

    business_id = db.Column(
            db.Integer, nullable=False, primary_key=True)

    location_id = db.Column(
            db.Integer, nullable=False, primary_key=True)

class Business(db.Model):
    __tablename__ = 'business'

    id = db.Column(
            db.Integer, primary_key=True)

    name = db.Column(
            db.String, nullable=False)

    description = db.Column(
            db.String, nullable=False)


    location_longitude = db.Column(
            db.Float, nullable=False)

    location_latitude = db.Column(
            db.Float, nullable=False)

    is_verified = db.Column(
            db.Boolean, nullable=False)

    industry_id = db.Column(
            db.Integer, db.ForeignKey('industry.id'), nullable=False)

    industry = db.relationship(
            'Industry')

    company_id = db.Column(
            db.Integer, db.ForeignKey('company.id'), nullable=True)

    managers = db.relationship(
            'Manager', secondary='managerset')

class Gender(db.Model):
    __tablename__ = 'gender'

    id = db.Column(
            db.Integer, primary_key=True)

    name = db.Column(
            db.String, nullable=False)

class Login(db.Model):
    __tablename__ = 'login'

    id = db.Column(
            db.Integer, primary_key=True)

    username = db.Column(
            db.String, nullable=False)

    email = db.Column(
            db.String, nullable=False)

    password = db.Column(
            db.String, nullable=True)

    password_salt = db.Column(
            db.String, nullable=True)

    phone_number = db.Column(
            db.String, nullable=False)

    postal_code = db.Column(
            db.String, nullable=False)

    create_date = db.Column(
            db.DateTime, nullable=False, server_default=db.func.now())

    employee_account = db.relationship(
            'Employee', uselist=False, backref='login', lazy='joined')
    manager_account = db.relationship(
            'Manager', uselist=False, backref='login', lazy='joined')

    def is_employee(self):
        return bool(self.employee_account)

    def is_manager(self):
        return bool(manager_account)

    def get_account(self):
        """ Get the account associated with this Login.

        Returns:
            Either a Manager or Employee instance.
        """
        return self.employee_account or self.manager_account

class Manager(db.Model):
    __tablename__ = 'manager'

    id = db.Column(
            db.Integer, primary_key=True)

    first_name = db.Column(
            db.String, nullable=False)

    last_name = db.Column(
            db.String, nullable=False)

    birth_date = db.Column(
            db.Date, nullable=False)

    gender_id = db.Column(
            db.Integer, db.ForeignKey('gender.id'), nullable=True)

    gender = db.relationship(
            'Gender', lazy='joined')

    login_id = db.Column(
            db.Integer, db.ForeignKey('login.id', ondelete='CASCADE'), nullable=False)

    businesses = db.relationship(
            'Business', secondary='managerset')

class ManagerSet(db.Model):
    __tablename__ = 'managerset'

    manager_id = db.Column(
            db.Integer, db.ForeignKey('manager.id', ondelete='CASCADE'), primary_key=True)

    business_id = db.Column(
            db.Integer, db.ForeignKey('business.id', ondelete='CASCADE'), primary_key=True)

    manager_set_name = db.Column(
            db.String, nullable=False)

    manager_set_level = db.Column(
            db.Integer, nullable=False)

class EmployeeLocationSet(db.Model):
    __tablename__ = 'employeelocationset'

    employee_id = db.Column(
            db.Integer, primary_key=True)

    location_id = db.Column(
            db.Integer, primary_key=True)

class Employee(db.Model):
    __tablename__ = 'employee'

    id = db.Column(
            db.Integer, primary_key=True)

    first_name = db.Column(
            db.String, nullable=False)

    last_name = db.Column(
            db.String, nullable=False)

    birth_date = db.Column(
            db.Date, nullable=False)

    gender_id = db.Column(
            db.Integer, db.ForeignKey('gender.id'), nullable=True)

    gender = db.relationship(
            'Gender', lazy='joined')

    login_id = db.Column(
            db.Integer, db.ForeignKey('login.id', ondelete='CASCADE'), nullable=False)

    languages = db.relationship(
            'Language', secondary='employeelanguageset')

    is_verified = db.Column(
            db.Boolean, nullable=False)

class Job(db.Model):
    __tablename__ = 'job'

    id = db.Column(
            db.Integer, primary_key=True)

    date = db.Column(
            db.DateTime, nullable=False)

    is_available = db.Column(
            db.Boolean, nullable=False)

    pay = db.Column(
            db.Float, nullable=False)

    details = db.Column(
            db.String, nullable=True)

    create_date = db.Column(
            db.DateTime, nullable=False, server_default=db.func.now())

    position_id = db.Column(
            db.Integer, db.ForeignKey('position.id'), nullable=True)

    position = db.relationship(
            'Position', lazy='joined')

    employee_id = db.Column(
            db.Integer, db.ForeignKey('employee.id', ondelete='SET NULL'), nullable=True)

    employee = db.relationship(
            'Employee', backref='job', uselist=False)

    manager_id = db.Column(
            db.Integer, db.ForeignKey('manager.id', ondelete='SET NULL'),
            nullable=True)

    manager = db.relationship(
            'Manager', backref='listings', uselist=False, lazy='joined')

    languages = db.relationship(
            'Language', secondary='joblanguageset')

class Position(db.Model):
    __tablename__ = 'position'

    id = db.Column(
            db.Integer, primary_key=True)

    name = db.Column(
            db.String, nullable=False)

    create_date = db.Column(
            db.Date, nullable=False, server_default=db.func.now())

    business_id = db.Column(
        db.Integer, db.ForeignKey('business.id'), nullable=False)

    business = db.relationship(
            'Business', backref='positions', lazy='joined')

    manager_id = db.Column(
            db.Integer, db.ForeignKey('manager.id'))

    manager = db.relationship(
            'Manager', backref='created_positions')
