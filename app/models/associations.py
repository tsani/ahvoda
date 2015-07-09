from app import db
from app.util import to_rfc3339

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

class BusinessLanguageSet(db.Model):
    __tablename__ = 'businesslanguageset'

    __table_args__ = (
            db.PrimaryKeyConstraint('language_id', 'business_id'),
    )

    language_id = db.Column(
            db.Integer,
            db.ForeignKey('language.id', ondelete='CASCADE'),
            nullable=False,
    )

    business_id = db.Column(
            db.Integer,
            db.ForeignKey('business.id', ondelete='CASCADE'),
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

class PositionLanguageSet(db.Model):
    __tablename__ = 'positionlanguageset'

    __table_args__ = (
            db.PrimaryKeyConstraint(
                'language_id',
                'position_id',
            ),
    )

    language_id = db.Column(
            db.Integer,
            db.ForeignKey('language.id', ondelete='CASCADE'),
            nullable=False,
    )

    position_id = db.Column(
            db.Integer,
            db.ForeignKey('position.id', ondelete='CASCADE'),
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
