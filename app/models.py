from app import app, db

class Rating(db.Model):
    __tablename__ = 'rating'

    id = db.Column(
            db.Integer, unique=True, primary_key=True)

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
            db.String, nullable=False, unique=True)

    employees = db.relationship(
            'Employee', secondary='employeelanguageset')

    jobs = db.relationship(
            'Job', secondary='joblanguageset')

class JobStatus(db.Model):
    __tablename__ = 'jobstatus'

    id = db.Column(
            db.Integer, nullable=False, unique=True, primary_key=True)

    name = db.Column(
            db.String, nullable=False, unique=True)

    friendly_name = db.Column(
            db.String, nullable=False)

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

class Business(db.Model):
    __tablename__ = 'business'

    id = db.Column(
            db.Integer, primary_key=True)

    name = db.Column(
            db.String, nullable=False)

    description = db.Column(
            db.String, nullable=False)

    location_id = db.Column(
            db.Integer, db.ForeignKey('location.id'), nullable=False)

    location = db.relationship(
            'Location')

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
            db.String, nullable=False, unique=True)

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

    administrator_account = db.relationship(
            'Administrator', uselist=False, backref='login', lazy='joined')

    def is_employee(self):
        return bool(self.employee_account)

    def is_manager(self):
        return bool(self.manager_account)

    def is_administrator(self):
        return bool(self.administrator_account)

    def get_account(self):
        """ Get the account associated with this Login.

        Returns:
            Either a Manager or Employee instance.
        """

        account_possibilities = (
                (self.is_employee, lambda: self.employee_account),
                (self.is_manager, lambda: self.manager_account),
                (self.is_administrator, lambda: self.administrator_account),
        )

        for predicate, thunk in account_possibilities:
            if predicate():
                return thunk()

        app.logger.warning('Login %d (%s) has no associated account.',
                (self.id, self.first_name, self.username))

        return None
        return self.employee_account or self.manager_account

class Manager(db.Model):
    __tablename__ = 'manager'

    id = db.Column(
            db.Integer, primary_key=True)

    human_id = db.Column(
            db.Integer, db.ForeignKey('human.id'), nullable=False, unique=True)

    login_id = db.Column(
            db.Integer, db.ForeignKey('login.id', ondelete='CASCADE'),
            nullable=False, unique=True)

    businesses = db.relationship(
            'Business', secondary='managerset')

    human = db.relationship(
            'Human', backref='manager', uselist=False)

class Human(db.Model):
    __tablename__ = 'human'

    id = db.Column(
            db.Integer, primary_key=True, nullable=False, unique=True)

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

    def is_employee():
        """ Whether the account associated with this human is an employee. """
        # The employee attribute comes from a backref given by the Employee
        # class.
        return self.employee is not None

    def is_manager():
        """ Whether the account associated with this human is a manager. """
        # The manager attribute comes from a backref given by the Manager
        # class.
        return self.manager is not None

    def get_account():
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

class ManagerSet(db.Model):
    __tablename__ = 'managerset'

    __table_args__ = (
            db.PrimaryKeyConstraint('manager_id', 'business_id'),
    )

    manager_id = db.Column(
            db.Integer, db.ForeignKey('manager.id', ondelete='CASCADE'))

    business_id = db.Column(
            db.Integer, db.ForeignKey('business.id', ondelete='CASCADE'))

    name = db.Column(
            db.String, nullable=False)

    level = db.Column(
            db.Integer, nullable=False)

class Administrator(db.Model):
    __tablename__ = 'administrator'

    id = db.Column(
            db.Integer, primary_key=True)

    login_id = db.Column(
            db.Integer, db.ForeignKey('login.id', ondelete='CASCADE'),
            nullable=False, unique=True)

class Employee(db.Model):
    __tablename__ = 'employee'

    id = db.Column(
            db.Integer, primary_key=True)

    login_id = db.Column(
            db.Integer, db.ForeignKey('login.id', ondelete='CASCADE'),
            nullable=False, unique=True)

    is_verified = db.Column(
            db.Boolean, nullable=False)

    human_id = db.Column(
            db.Integer, db.ForeignKey('human.id'), nullable=False, unique=True)

    human = db.relationship(
            'Human', backref='employee', uselist=False, lazy='joined')

    home_location_id = db.Column(
            db.Integer, db.ForeignKey('location.id'), nullable=False)

    home_location = db.relationship(
            'Location')

    languages = db.relationship(
            'Language', secondary='employeelanguageset')

class Job(db.Model):
    __tablename__ = 'job'

    id = db.Column(
            db.Integer, primary_key=True)

    pay = db.Column(
            db.Float, nullable=False)

    details = db.Column(
            db.String, nullable=True)

    create_date = db.Column(
            db.DateTime, nullable=False, server_default=db.func.now())

    start_date = db.Column(
            db.DateTime, nullable=True)

    end_date = db.Column(
            db.DateTime, nullable=True)

    position_id = db.Column(
            db.Integer, db.ForeignKey('position.id'), nullable=False)

    employee_id = db.Column(
            db.Integer, db.ForeignKey('employee.id', ondelete='SET NULL'),
            nullable=True)

    manager_id = db.Column(
            db.Integer, db.ForeignKey('manager.id', ondelete='SET NULL'),
            nullable=True)

    rating_id = db.Column(
            db.Integer, db.ForeignKey('rating.id'), nullable=False)

    status_id = db.Column(
            db.Integer, db.ForeignKey('jobstatus.id'), nullable=False)

    position = db.relationship(
            'Position', lazy='joined')

    employee = db.relationship(
            'Employee', backref='jobs', uselist=False)

    manager = db.relationship(
            'Manager', backref='listings', uselist=False, lazy='joined')

    languages = db.relationship(
            'Language', secondary='joblanguageset')

    rating = db.relationship(
            'Rating', backref='job', uselist=False, lazy='joined')

    status = db.relationship(
            'JobStatus', backref='jobs', lazy='joined')

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
