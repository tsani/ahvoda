from app import db
from app import models

ids = [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12]

if __name__ == '__main__':
    for i in ids:
        e = models.Employee.query.get(i)
        db.session.delete(e)
    db.session.commit()
