from app import app, db

from app.util import to_rfc3339

# The to_dict methods implemented on the models correspond to the objects
# specified in `json-schema/api.json`.

### Business structure and listing-related tables

class JobMatch(db.Model):
    """ Represents a match between an employee and a job.

    Rows in this table are considerably more volatile than in most other tables
    in the database.

    When a listing is created, a message is written into the Redis-backed
    message queue and picked up by the matcher. The matcher runs the listing
    through each employee row and finds matches. It writes rows to this
    table as a record of its work, which also allows it to pick up where it
    left off in case of failures.

    As it writes rows to this table, the matcher also enqueues messages to the
    dispatcher. The dispatcher uses GCM to send batches of listings to the
    phones.

    Each phone decides whether the listing is a true match based on the
    employee's current location. The phone's decisions are relayed back to the
    webapp using the REST API and are also recorded in this table.

    In sum, each row represents a match as well as the following information:
    * whether the match has been dispatched
    * whether the match was a true match

    Of course, the match can't be a true match unless the match has been
    dispatched, so until `dispatched` becomes `true`, `true match` can't have a
    value other than NULL. CHECK constraints will enforce this.
    """
    __tablename__ = 'jobmatch'

    __table_args__ = (
            db.PrimaryKeyConstraint(
                'employee_id',
                'job_id',
            ),
    )

    id = db.Column(
            db.Integer,
            unique=True,
            nullable=False,
    )

    create_date = db.Column(
            db.DateTime,
            server_default=db.func.now(),
            nullable=False,
    )

    is_dispatched = db.Column(
            db.Boolean,
            nullable=False,
            server_default='f',
            index=True,
    )

    is_true_match = db.Column(
            db.Boolean,
            nullable=True,
    )

    employee_id = db.Column(
            db.Integer,
            db.ForeignKey('employee.id'),
    )

    job_id = db.Column(
            db.Integer,
            db.ForeignKey('job.id'),
    )

    employee = db.relationship(
            'Employee',
            backref='employee_matches',
    )

    job = db.relationship(
            'Job',
            backref='job_matches',
    )

class Rating(db.Model):
    __tablename__ = 'rating'

    id = db.Column(
            db.Integer,
            unique=True,
            primary_key=True,
    )

    employee_rating = db.Column(
            db.Float,
            nullable=False,
    )

    employee_comment = db.Column(
            db.String,
            nullable=True,
    )

    job_rating = db.Column(
            db.Float,
            nullable=False,
    )

    job_comment = db.Column(
            db.String,
            nullable=True,
    )

    def to_dict(self):
        return dict(
                ofEmployee=dict(
                    value=self.employee_rating,
                    comment=self.employee_comment,
                ),
                ofEmployer=dict(
                    value=self.job_rating,
                    comment=self.job_comment,
                )
        )

class JobStatus(db.Model):
    __tablename__ = 'jobstatus'

    id = db.Column(
            db.Integer,
            nullable=False,
            unique=True,
            primary_key=True,
    )

    name = db.Column(
            db.String,
            nullable=False, unique=True,
    )

    friendly_name = db.Column(
            db.String,
            nullable=False,
    )

    def to_dict(self):
        return dict(
                id=self.id,
                name=self.name,
                friendly_name=self.friendly_name,
        )

class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(
            db.Integer,
            primary_key=True,
    )

    name = db.Column(
            db.String,
            nullable=False,
    )

    businesses = db.relationship(
            'Business', backref='company')

    def to_dict(self):
        return dict(
                id=self.id,
                name=self.name,
        )

class Business(db.Model):
    __tablename__ = 'business'

    id = db.Column(
            db.Integer,
            primary_key=True,
    )

    name = db.Column(
            db.String,
            nullable=False,
    )

    description = db.Column(
            db.String,
            nullable=False,
    )

    is_verified = db.Column(
            db.Boolean,
            nullable=False,
    )

    location_id = db.Column(
            db.Integer,
            db.ForeignKey('location.id'),
            nullable=False,
    )

    industry_id = db.Column(
            db.Integer,
            db.ForeignKey('industry.id'),
            nullable=False,
    )

    company_id = db.Column(
            db.Integer,
            db.ForeignKey('company.id'),
            nullable=True,
    )

    contact_info_id = db.Column(
            db.Integer,
            db.ForeignKey('contactinfo.id'),
            nullable=False,
    )

    managers = db.relationship(
            'Manager',
            secondary='managerset',
    )

    industry = db.relationship(
            'Industry',
            backref='businesses',
    )

    location = db.relationship(
            'Location',
            backref='business',
            uselist=False,
    )

    contact_info = db.relationship(
            'ContactInfo',
            backref='business',
            uselist=False,
            lazy='joined',
    )

    def to_dict(self):
        result = dict(
                id=self.id,
                name=self.name,
                description=self.description,
                location=self.location.to_dict(),
                is_verified=self.is_verified,
                contact_info=self.contact_info.to_dict(),
        )

        if self.company is not None:
            result['company'] = self.company.to_dict()

        return result

class Position(db.Model):
    __tablename__ = 'position'

    id = db.Column(
            db.Integer,
            primary_key=True,
    )

    name = db.Column(
            db.String,
            nullable=False,
    )

    create_date = db.Column(
            db.Date,
            nullable=False,
            server_default=db.func.now(),
    )

    is_available = db.Column(
            db.Boolean,
            nullable=False,
            server_default="t",
    )

    business_id = db.Column(
            db.Integer,
            db.ForeignKey('business.id'),
            nullable=False,
    )

    business = db.relationship(
            'Business',
            backref='positions',
            lazy='joined',
    )

    manager_id = db.Column(
            db.Integer,
            db.ForeignKey('manager.id', ondelete='SET NULL'),
    )

    manager = db.relationship(
            'Manager',
            backref='created_positions',
    )

    def to_dict(self):
        return dict(
                id=self.id,
                name=self.name,
                create_date=to_rfc3339(self.create_date),
        )

class Job(db.Model):
    __tablename__ = 'job'

    id = db.Column(
            db.Integer,
            primary_key=True,
    )

    pay = db.Column(
            db.Float,
            nullable=False,
    )

    details = db.Column(
            db.String,
            nullable=True,
    )

    create_date = db.Column(
            db.DateTime,
            nullable=False,
            server_default=db.func.now(),
    )

    arrival_date = db.Column(
            db.DateTime,
            nullable=True,
    )

    departure_date = db.Column(
            db.DateTime,
            nullable=True,
    )

    duration = db.Column(
            db.Float,
            nullable=False,
    )

    position_id = db.Column(
            db.Integer,
            db.ForeignKey('position.id'),
            nullable=False,
    )

    employee_id = db.Column(
            db.Integer,
            db.ForeignKey('employee.id', ondelete='SET NULL'),
            nullable=True,
    )

    manager_id = db.Column(
            db.Integer,
            db.ForeignKey('manager.id', ondelete='SET NULL'),
            nullable=True,
    )

    rating_id = db.Column(
            db.Integer,
            db.ForeignKey('rating.id'),
            nullable=True,
    )

    business_id = db.Column(
            db.Integer,
            db.ForeignKey('business.id'),
            nullable=False,
    )

    status_id = db.Column(
            db.Integer,
            db.ForeignKey('jobstatus.id'),
            nullable=False,
    )

    position = db.relationship(
            'Position',
            backref='jobs',
            lazy='joined',
    )

    employee = db.relationship(
            'Employee',
            backref='jobs',
            uselist=False,
    )

    manager = db.relationship(
            'Manager',
            backref='listings',
            uselist=False,
            lazy='joined',
    )

    business = db.relationship(
            'Business',
            backref='jobs',
            uselist=False,
    )

    languages = db.relationship(
            'Language',
            secondary='joblanguageset'
    )

    rating = db.relationship(
            'Rating',
            backref='job',
            uselist=False,
            lazy='joined',
    )

    status = db.relationship(
            'JobStatus',
            backref='jobs',
            uselist=False,
            lazy='joined',
    )

    applicants = db.relationship(
            'Employee',
            secondary='applicant',
    )

    def to_dict(self):
        result = dict(
                id=self.id,
                pay=self.pay,
                details=self.details,
                create_date=to_rfc3339(self.create_date),
                duration=self.duration,
                position=self.position.to_dict(),
                rating=dict(
                    ofEmployer=None,
                    ofEmployee=None,
                ),
                business=self.business.to_dict(),
                status=self.status.to_dict(),
                languages=[
                    lang.to_dict()
                    for lang
                    in self.languages
                ],
        )

        if self.manager is not None:
            result['manager'] = self.manager.to_dict()

        if self.rating is not None:
            result['rating']['ofEmployer'] = dict(
                    value=self.rating.job_rating,
                    comment=self.rating.job_comment,
            )
            result['rating']['ofEmployee'] = dict(
                    value=self.rating.employee_rating,
                    comment=self.rating.employee_comment,
            )

        if self.arrival_date is not None:
            result['arrival_date'] = to_rfc3339(self.arrival_date)

        if self.departure_date is not None:
            result['departure_date'] = to_rfc3339(self.departure_date)

        if self.employee is not None:
            result['employee'] = self.employee.to_dict()

        print(result.keys())

        return result

### Location-relation tables

class City(db.Model):
    __tablename__ = 'city'

    id = db.Column(
            db.Integer,
            primary_key=True,
    )

    name = db.Column(
            db.String,
            nullable=False,
    )

    state_id = db.Column(
            db.Integer,
            db.ForeignKey('state.id'),
            nullable=False,
    )

    state = db.relationship(
            'State',
            backref='cities',
    )

    def to_dict(self):
        return dict(
                id=self.id,
                name=self.name,
                state=self.state.to_dict(),
        )

class State(db.Model):
    __tablename__ = 'state'

    id = db.Column(
            db.Integer,
            primary_key=True,
    )

    name = db.Column(
            db.String,
            nullable=False,
    )

    country_id = db.Column(
            db.Integer,
            db.ForeignKey('country.id'),
            nullable=False,
    )

    country = db.relationship(
            'Country',
            backref='states',
    )

    def to_dict(self):
        return dict(
                id=self.id,
                name=self.name,
                country=self.country.to_dict(),
        )

class Country(db.Model):
    __tablename__ = 'country'

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

class Location(db.Model):
    __tablename__ = 'location'

    id = db.Column(
            db.Integer,
            primary_key=True,
    )

    address = db.Column(
            db.String,
            nullable=False,
    )

    postal_code = db.Column(
            db.String,
            nullable=False,
    )

    city_id = db.Column(
            db.Integer,
            db.ForeignKey('city.id'),
            nullable=False,
    )

    city = db.relationship(
            'City',
    )

    latitude = db.Column(
            db.Float,
            db.CheckConstraint(
                'latitude > -90.0 AND latitude < 90.0',
                name='latitude',
            ),
            nullable=False,
    )

    longitude = db.Column(
            db.Float,
            db.CheckConstraint(
                'longitude > -180.0 AND longitude < 180.0',
                name='longitude',
            ),
            nullable=False,
    )

    def to_dict(self):
        return dict(
            id=self.id,
            address=self.address,
            city=self.city.to_dict(),
            postal_code=self.postal_code,
            location=dict(
                latitude=self.latitude,
                longitude=self.longitude,
            ),
        )

### Additional data tables

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

### Account types

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

### Association tables

class Applicant(db.Model):
    __tablename__ = 'applicant'

    __table_args__ = (
            db.PrimaryKeyConstraint(
                'employee_id',
                'job_id',
            ),
    )

    employee_id = db.Column(
            db.Integer,
            db.ForeignKey('employee.id', ondelete='CASCADE'),
            nullable=False,
    )

    job_id = db.Column(
            db.Integer,
            db.ForeignKey('job.id', ondelete='CASCADE'),
            nullable=False,
    )

class EmployeeLanguageSet(db.Model):
    __tablename__ = 'employeelanguageset'

    __table_args__ = (
            db.PrimaryKeyConstraint('language_id', 'employee_id'),
    )

    language_id = db.Column(
            db.Integer,
            db.ForeignKey('language.id', ondelete='CASCADE'),
            nullable=False,
    )

    employee_id = db.Column(
            db.Integer,
            db.ForeignKey('employee.id', ondelete='CASCADE'),
            nullable=False,
    )

class JobLanguageSet(db.Model):
    __tablename__ = 'joblanguageset'

    __table_args__ = (
            db.PrimaryKeyConstraint('language_id', 'job_id'),
    )

    language_id = db.Column(
            db.Integer,
            db.ForeignKey('language.id', ondelete='CASCADE'),
            nullable=False,
    )

    job_id = db.Column(
            db.Integer,
            db.ForeignKey('job.id', ondelete='CASCADE'),
            nullable=False,
    )

class ManagerSet(db.Model):
    __tablename__ = 'managerset'

    __table_args__ = (
            db.PrimaryKeyConstraint('manager_id', 'business_id'),
    )

    manager_id = db.Column(
            db.Integer,
            db.ForeignKey('manager.id', ondelete='CASCADE'),
    )

    business_id = db.Column(
            db.Integer,
            db.ForeignKey('business.id', ondelete='CASCADE'),
    )

### Authentication-related

class Login(db.Model):
    __tablename__ = 'login'

    id = db.Column(
            db.Integer,
            primary_key=True
    )

    username = db.Column(
            db.String,
            nullable=False,
            unique=True,
    )

    password = db.Column(
            db.String,
            nullable=True,
    )

    password_salt = db.Column(
            db.String,
            nullable=True,
    )

    create_date = db.Column(
            db.DateTime,
            nullable=False,
            server_default=db.func.now(),
    )

    def is_employee(self):
        return bool(self.employee_account)

    def is_manager(self):
        return bool(self.manager_account)

    def is_administrator(self):
        return bool(self.administrator_account)

    def to_dict(self):
        return dict(
                id=self.id,
                username=self.username,
        )

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
