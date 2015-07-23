from app import db
from app.util import to_rfc3339

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

class Geolocation(db.Model):
    """ Class of locations on the Earth, represented by a latitude and a
    longitude. Many objects that require storing ephemeral latitude/longitude
    pairs should use this class.
    """
    __tablename__ = 'geolocation'

    id = db.Column(
            db.Integer,
            primary_key=True,
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
                latitude=self.latitude,
                longitude=self.longitude,
        )

class FixedLocation(db.Model):
    """ Class of fixed locations on the Earth, tied to a legal address. """
    __tablename__ = 'fixedlocation'

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

    geolocation_id = db.Column(
            db.Integer,
            db.ForeignKey('geolocation.id'),
            nullable=False,
            unique=True,
    )

    geolocation = db.relationship(
            'Geolocation',
            uselist=False,
            backref='fixed_location'
    )

    def to_dict(self):
        return dict(
            id=self.id,
            address=self.address,
            city=self.city.to_dict(),
            postal_code=self.postal_code,
            geolocation=self.geolocation.to_dict(),
        )
