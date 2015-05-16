from app import db

class Experience(db.Model):
    __tablename__ = 'experience'

    __table_args__ = (
            db.PrimaryKeyConstraint('employee_id', 'industry_id'),
    )

    employee_id = db.Column(
            db.Integer, db.ForeignKey('employee.id'), nullable=False)

    industry_id = db.Column(
            db.Integer, db.ForeignKey('industry.id'), nullable=False)

    value = db.Column(
            db.Float, nullable=False)

class Rank(db.Model):
    __tablename__ = 'rank'

    __table_args__ = (
            db.PrimaryKeyConstraint('employee_id', 'industry_id'),
    )

    employee_id = db.Column(
            db.Integer, db.ForeignKey('employee.id'), nullable=False)

    industry_id = db.Column(
            db.Integer, db.ForeignKey('industry.id'), nullable=False)

    value = db.Column(
            db.Integer, nullable=False)

class Availability(db.Model):
    __tablename__ = 'availability'

    id = db.Column(
            db.Integer, primary_key=True)

    name = db.Column(
            db.String, nullable=False)

class Industry(db.Model):
    __tablename__ = 'industry'

    id = db.Column(
            db.Integer, primary_key=True)

    name = db.Column(
            db.String, nullable=False)

class Language(db.Model):
    __tablename__ = 'language'

    id = db.Column(
            db.Integer, primary_key=True)

    name = db.Column(
            db.String, nullable=False)

    employees = db.relationship(
            'Employee', secondary='languageset')

class LanguageSet(db.Model):
    __tablename__ = 'languageset'

    __table_args__ = (
            db.PrimaryKeyConstraint('language_id', 'employee_id'),
    )

    language_id = db.Column(
            db.Integer, db.ForeignKey('language.id', ondelete='CASCADE'),
            nullable=False)

    employee_id = db.Column(
            db.Integer, db.ForeignKey('employee.id', ondelete='CASCADE'),
            nullable=False)

class SchoolFaculty(db.Model):
    __tablename__ = 'schoolfaculty'

    id = db.Column(
            db.Integer, primary_key=True)

    name = db.Column(
            db.String, nullable=False)

class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(
            db.Integer, primary_key=True)

    name = db.Column(
            db.String, nullable=False)

    businesses = db.relationship(
            'Business', backref='company')

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
            'Manager', secondary='manager_set')

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
            'Gender')

    login_id = db.Column(
            db.Integer, db.ForeignKey('login.id', ondelete='CASCADE'), nullable=False)

    login = db.relationship(
            'Login', backref='managers')

    businesses = db.relationship(
            'Business', secondary='manager_set')

class ManagerSet(db.Model):
    __tablename__ = 'manager_set'

    manager_id = db.Column(
            db.Integer, db.ForeignKey('manager.id', ondelete='CASCADE'), primary_key=True)

    business_id = db.Column(
            db.Integer, db.ForeignKey('business.id', ondelete='CASCADE'), primary_key=True)

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
            db.Date, nullable=False)

    home_address = db.Column(
            db.String, nullable=True)

    home_latitude = db.Column(
            db.Float,
            db.CheckConstraint(
                'home_latitude > -90.0 AND home_latitude < 90.0'),
            nullable=False)

    home_longitude = db.Column(
            db.Float,
            db.CheckConstraint(
                'home_longitude > -180.0 AND home_longitude < 180.0'),
            nullable=False)

    home_city = db.Column(
            db.String, nullable=False)

    gender_id = db.Column(
            db.Integer, db.ForeignKey('gender.id'), nullable=True)

    gender = db.relationship('Gender')

    cv_name = db.Column(
            db.String, nullable=False)

    cv_original_name = db.Column(
            db.String, nullable=False)

    is_student = db.Column(
            db.Boolean, nullable=False)

    faculty_id = db.Column(
            db.Integer, db.ForeignKey('schoolfaculty.id'), nullable=True)

    faculty = db.relationship('SchoolFaculty')

    graduation_year = db.Column(
            db.String, nullable=True)

    canadian_citizen = db.Column(
            db.Boolean, nullable=False)

    canadian_work = db.Column(
            db.Boolean, nullable=False)

    login_id = db.Column(
            db.Integer, db.ForeignKey('login.id', ondelete='CASCADE'), nullable=False)

    login = db.relationship(
            'Login', backref='employees')

    languages = db.relationship(
            'Language', secondary='languageset')

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
            db.DateTime, nullable=False, server_default=db.func.now())

    position_id = db.Column(
            db.Integer, db.ForeignKey('position.id'), nullable=True)

    application_deadline = db.Column(
            db.DateTime, nullable=True)

    employee_id = db.Column(
            db.Integer, db.ForeignKey('employee.id', ondelete='SET NULL'), nullable=True)

    employee = db.relationship(
            'Employee', backref='jobs')

    manager_id = db.Column(
            db.Integer, db.ForeignKey('manager.id', ondelete='SET NULL'),
            nullable=True)

    manager = db.relationship(
            'Manager', backref='listings')

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
            'Business', backref='positions')

    manager_id = db.Column(
            db.Integer, db.ForeignKey('manager.id'))

    manager = db.relationship(
            'Manager', backref='created_positions')
