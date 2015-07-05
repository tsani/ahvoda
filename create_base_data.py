from app import db, models

def make(cls, select, create):
    return cls.query.filter_by(**select).first() or cls(**create)

def make_easy(cls, **kwargs):
    return make(cls, kwargs, kwargs)

if __name__ == '__main__':
    db.session.autoflush = False

    [male, female, other_gender] = [
            make_easy(models.data.Gender, **d)
            for d
            in [
                dict(
                    name='male',
                ),
                dict(
                    name='female',
                ),
                dict(
                    name='other',
                )
            ]
    ]

    db.session.add(male)
    db.session.add(female)
    db.session.add(other_gender)

    db.session.commit()

    [canada] = [
            make_easy(models.location.Country, **d)
            for d
            in [
                dict(
                    name='Canada',
                ),
            ]
    ]

    db.session.add(canada)

    db.session.commit()

    [quebec, ontario] = [
            make_easy(models.location.State, **d)
            for d
            in [
                dict(
                    name='Quebec',
                    country=canada,
                ),
                dict(
                    name='Ontario',
                    country=canada,
                ),
            ]
    ]

    db.session.add(quebec)
    db.session.add(ontario)

    db.session.commit()

    [montreal] = [
            make_easy(models.location.City, **d)
            for d
            in [
                dict(
                    name='Montreal',
                    state=quebec,
                ),
            ]
    ]

    db.session.add(montreal)

    db.session.commit()

    [english, french] = [
            make_easy(models.data.Language, **d)
            for d
            in [
                dict(
                    name='English',
                    iso_name='en',
                ),
                dict(
                    name='French',
                    iso_name='fr',
                ),
            ]
    ]

    db.session.add(english)
    db.session.add(french)

    db.session.commit()

    [fooddrink, nightlife] = [
            make_easy(models.data.Industry, **d)
            for d
            in [
                dict(
                    name='fooddrink',
                ),
                dict(
                    name='nightlife',
                ),
            ]
    ]

    db.session.add(fooddrink)
    db.session.add(nightlife)

    db.session.commit()

    job_statuses = [
            make(models.business.JobStatus, *d)
            for d
            in [
                (
                    dict(
                        name='pending',
                    ),
                    dict(
                        name='pending',
                        friendly_name='pending',
                    ),
                ),
                (
                    dict(
                        name='submitted',
                    ),
                    dict(
                        name='submitted',
                        friendly_name='submitted',
                    ),
                ),
                (
                    dict(
                        name='inProgress',
                    ),
                    dict(
                        name='inProgress',
                        friendly_name='in progress',
                    ),
                ),
                (
                    dict(
                        name='cancelled',
                    ),
                    dict(
                        name='cancelled',
                        friendly_name='cancelled',
                    ),
                ),
                (
                    dict(
                        name='completed',
                    ),
                    dict(
                        name='completed',
                        friendly_name='completed',
                    ),
                ),
                (
                    dict(
                        name='stale',
                    ),
                    dict(
                        name='stale',
                        friendly_name='stale',
                    ),
                ),
                (
                    dict(
                        name='aborted',
                    ),
                    dict(
                        name='aborted',
                        friendly_name='aborted',
                    )
                )
            ]
    ]

    for job_status in job_statuses:
        db.session.add(job_status)

    db.session.commit()
