from flask_sqlalchemy import (
        SQLAlchemy as BaseSQLAlchemy,
        Model,
        _BoundDeclarativeMeta,
        _QueryProperty,
        declarative_base,
)
from sqlalchemy import MetaData

class SQLAlchemy(BaseSQLAlchemy):
    def make_declarative_base(self):
        metadata = MetaData(
                naming_convention=dict(
                    pk='pk_%(table_name)s',
                    fk='fk_%(table_name)s_%(column_0_name)s'
                    '_%(referred_table_name)s',
                    ix='ix_%(table_name)s_%(column_0_name)s',
                    uq='uq_%(table_name)s_%(column_0_name)s',
                    ck='ck_%(table_name)s_%(constraint_name)s',
                )
        )
        base = declarative_base(
                metadata=metadata,
                cls=Model,
                name='Model',
                metaclass=_BoundDeclarativeMeta
        )
        base.query = _QueryProperty(self)
        return base
