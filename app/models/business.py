from app import db
from app.util import to_rfc3339

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
            nullable=False,
            unique=True,
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
    )

    is_true_match = db.Column(
            db.Boolean,
            nullable=True,
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

    employee = db.relationship(
            'Employee',
            backref=db.backref(
                'employee_matches',
                cascade='all, delete-orphan',
            ),
    )

    job = db.relationship(
            'Job',
            backref=db.backref(
                'job_matches',
                cascade='all, delete-orphan',
            )
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

    priority = db.Column(
            db.Integer,
            nullable=False,
            unique=True,
    )

    def to_dict(self):
        return dict(
                id=self.id,
                name=self.name,
                friendly_name=self.friendly_name,
                priority=self.priority,
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

    is_available = db.Column(
            db.Boolean,
            nullable=False,
            server_default="t",
    )

    businesses = db.relationship(
            'Business', backref='company')

    @classmethod
    def available(cls):
        return cls.query.filter_by(is_available=True)

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

    is_available = db.Column(
            db.Boolean,
            nullable=False,
            server_default='t',
    )

    fixed_location_id = db.Column(
            db.Integer,
            db.ForeignKey('fixedlocation.id'),
            nullable=False,
            unique=True,
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

    fixed_location = db.relationship(
            'FixedLocation',
            backref=db.backref(
                'business',
                uselist=False,
            ),
    )

    languages = db.relationship(
            'Language',
            backref='businesses',
            secondary='businesslanguageset',
    )

    contact_info = db.relationship(
            'ContactInfo',
            backref='business',
            uselist=False,
            lazy='joined',
    )

    @classmethod
    def available(cls):
        return cls.query.filter_by(is_available=True)

    def to_dict(self):
        result = dict(
                id=self.id,
                name=self.name,
                description=self.description,
                fixed_location=self.fixed_location.to_dict(),
                is_verified=self.is_verified,
                contact_info=self.contact_info.to_dict(),
                languages=[
                    lang.to_dict()
                    for lang
                    in self.languages
                ],
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

    default_pay = db.Column(
            db.Float,
    )

    default_details = db.Column(
            db.String,
    )

    default_languages = db.relationship(
            'Language',
            backref='positions',
            secondary='positionlanguageset',
    )

    create_date = db.Column(
            db.DateTime,
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

    @classmethod
    def available(cls):
        return cls.query.filter_by(is_available=True)

    def to_dict(self):
        return dict(
                id=self.id,
                name=self.name,
                create_date=to_rfc3339(self.create_date),
                default_languages=[
                    lang.to_dict()
                    for lang
                    in self.default_languages
                ],
                default_pay=self.default_pay,
                default_details=self.default_details,
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
            index=True,
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

    is_available = db.Column(
            db.Boolean,
            nullable=False,
            server_default="t",
    )

    position_id = db.Column(
            db.Integer,
            db.ForeignKey('position.id'),
            nullable=False,
            index=True,
    )

    employee_id = db.Column(
            db.Integer,
            db.ForeignKey('employee.id', ondelete='SET NULL'),
            nullable=True,
            index=True,
    )

    manager_id = db.Column(
            db.Integer,
            db.ForeignKey('manager.id', ondelete='SET NULL'),
            nullable=True,
            index=True,
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
            index=True,
    )

    status_id = db.Column(
            db.Integer,
            db.ForeignKey('jobstatus.id'),
            nullable=False,
            index=True,
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

    @classmethod
    def available(cls):
        return cls.query.filter_by(is_available=True)

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

        return result

