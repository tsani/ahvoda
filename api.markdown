General object formats
======================


Position
--------

    {
        "id": <unique identifier of the position>
        "name": <position name>,
        "pay": <amount as a float>,
        "startTime": <time the shift starts at>
        "duration":  <employment duration>,
        "languages": [ 
            <language name>,
            ...
        ]
    }


Business
--------

    {
        "id": <unique identifer of the business>,
        "name": <business name>,
        "description": <business description>,
        "location": [
            <longitude>,
            <latitude>
        ],
        "address": {
            "streetNumber": <integer>,
            "street": <name of the street>,
            "city": <city name>,
            "country": <country name
        },
        "company": <null if no company, otherwise a company object>,
        "rating": <real in the closed interval [0, 1]>
    }


Company
-------

    {
        "name": <company name>
    }


Rating
------

    {
        "rating": <real in the interval [0, 1]>,
        "comments": <(possibly empty) string accompanying the rating>
    }


API
===


Business
--------

All the following API endpoints must be used from a business account. The HTTP
header should include a session token associated with the user's account.


 * `POST /api/listings/create`

Create a job listing. A position object is required as the POST body.

    <position object>


 * `GET /api/listings/list/open`

List all open listings, i.e. listings that are not in the past.

This request must be made from an authentiated business account.

Response: 200.

    [
        <position object>,
        ...
    ]


 * `GET /api/listings/detail/:id`

Get detailed information about a listing, which includes the list of all
applicants.

    {
        "position": <position object>,
        "applicants": [
            <employee object>,
            ...
        ]
    }

 * `DELETE /api/listings/delete/:id`

Delete the listing identified by the given ID.

Response: 204.

Note the request body is empty.


 * `POST /api/listings/approve`

Approve an employee to work a job. This request includes an object identifying
an employee by an ID and a position by an ID.

    {
        "employeeId": <identifier for the employee to approve>
        "positionId": <identifier for the position / job that employee is
            filling>
    }

Response: 204.


 * `POST /api/rate/employee/:id`

Rate the employee identified by the given ID.

    <rating object>

Response: 204.


Employee
--------

All the following API endpoints must be made from a logged in employee account.
The HTTP headers should include a session token associated with the user's
account.


 * `GET /api/notifications/:userid`

Get the list of all the notifications that have been dispatched to a given
user. Each notification is in fact a job object.

    [
        {
            "id": <unique identifier for each notification>,
            "business": <business object>,
            "position": <position object>
        },
        ...
    ]


 * `POST /api/listings/apply/:id`

Apply to the listing identified by the given ID.

    {
    }

Note that the request body is empty / ignored.


 * `POST /api/rate/job/:id`

Rate the job identified by the given ID.

    <rating object>
