#!/usr/bin/env python

from app import db, models

priority_settings = {
        'pending': 40,
        'submitted': 30,
        'inProgress': 20,
        'cancelled': 100,
        'completed': 150,
        'stale': 200,
        'aborted': 70,
}

if __name__ == '__main__':
    db.session.autoflush = False

    for status_name, priority in priority_settings.items():
        status = models.business.JobStatus.query.filter_by(
                name=status_name,
        ).one()
        status.priority = priority
        db.session.add(status)
    db.session.commit()
