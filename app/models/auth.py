from app import db
from app.util import to_rfc3339

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

    is_available = db.Column(
            db.Boolean,
            nullable=False,
            server_default="t",
    )

    @classmethod
    def available(cls):
        return cls.query.filter_by(is_available=True)

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
                android_devices=[
                    d.to_dict()
                    for d
                    in self.android_devices
                ],
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
