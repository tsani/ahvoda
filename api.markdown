Authentication
==============

There are currently two schemes for authentication, which allows for a
versatile use of the API according to the user-agent of the client.


Cookies
-------

Using the `/login` page, the client can authenticate to the server, and is
provided with an encrypted cookie that uniquely identifies the client with a
server-side session.

This authentication scheme is for use mainly in a browser environment.


HTTP Basic Authentication
-------------------------

By providing credentials in the HTTP headers, the client can elevate the
privilege level of an individual request.

This authentication scheme is for use mainly in environments where managing
cookies is a pain, or where the number of requests made to the server is
limited.


Validation
==========

JSON schemas are used to validate both incoming requests and outgoing
responses, to ensure end-to-end correctness of the data.

See `json-schemas/README.markdown` for more information.


Dates
=====

All dates emitted by the API are UTC.

All dates consumed by the API must be UTC.


API
===

This sections gives an overview of each API endpoint. In should be consulted in
tandem with the associated JSON schemas.

Common
------

The following API endpoints do not require authentication as a specific type of
account. Both employee and manager accounts can access the following endpoints.

### `GET /api/business/:businessId/details`

Get information about a business.

#### Responses

* 200 (OK)
* 403 (Forbidden)
    * The account is not authorized to use that businessId.
* 404 (Not Found)
    * No such business.

### `GET /api/business/:businessId/listing/:listingId`

Get the details of a listing.

#### Responses

* 200 (OK)
* 403 (Forbidden)
    * The account is not authorized to use that businessId. (Manager only)
    * The listing was not dispatched to the employee. (Employee only)
* 404 (Not Found)
    * No such listing.

### `GET /api/business/:businessId/listing/:listingId/employee/departure`

Get the departure time of the employee.

#### Responses

* 200 (OK)
* 403 (Forbidden)
    * The account is not associated with that listing. (Employee only)
    * The account is not authorized to use that businessId. (Manager only)
* 404 (Not Found)
    * No such listing.
    * No employee is associated with the listing.
    * No departure time has been indicated yet.

### `GET /api/business/:businessId/listing/:listingId/employee/arrival`

Get the arrival time of the employee.

#### Responses

* 200 (OK)
* 403 (Forbidden)
    * The account is not associated with that listing. (Employee only)
    * The account is not authorized to use that businessId. (Manager only)
* 404 (Not Found)
    * No such listing.
    * No employee is associated with the listing.
    * The employee has not arrived yet.

### `GET /api/business/:businessId/listing/:listingId/employee/rating`

Get the rating of the employee associated with the given listing.

#### Responses

* 200 (OK)
* 403 (Forbidden)
    * The account is not associated with that listing. (Employee only)
    * The account is not authorized to use that businessId. (Manager only)
* 404 (Not Found)
    * No such listing.
    * No employee is associated with the listing.
    * No rating has been given yet.

### `GET /api/listings`

List all listings with the given status.

#### Parameters

* status (type: string)
    * List all listings with the given status.
* statusGroup (type: string)
    * A status group is an identifier that matches multiple statuses. The
        implemented status groups are the following:
        * open: "pending", "submitted".
        * active: "inProgress".
        * closed: "cancelled", "completed", "rated", "stale", "aborted"
* since (type: datetime)
    * List all listings created after the given date and time.
* before (type: datetime)
    * List all listings created before the given date and time.
* max (type: integer)
    * List no more than the given number of listings.
* createdBy (type: integer)
    * List only listings created by this business, identified by their
      businessId.
* dispatchedTo (type: integer)
    * List only listings that have been dispatched to this employee, identified
      by their employeeId.
* workedBy (type: integer)
    * List only listings associated with this employee, identified by their
      employeeId.

#### Responses

* 200 (OK)
* 400 (Bad Request)
    * The query string does not conform to the schema.
    * No such status.
* 403 (Forbidden)
    * The result set contains entries that the account is not allowed to see.

Manager
-------

All the following API endpoints must be used from a manager account.

### `PATCH /api/business/:businessId/details`

Update information about a business.

#### Responses

* 204 (No Content)
* 403 (Forbidden)
    * The account is not authorized to use that businessId.
* 404 (Not Found)
    * No such business.

### `POST /api/business/:businessId/listing/new`

Create a new listing.

#### Responses

* 202 (Accepted)
    * The request is submitted, but will be dispatched to employees in
    the near future. This is to allow time for cancellation.
* 400 (Bad Request)
    * The enclosed entity does not conform to the schema.
* 403 (Forbidden)
    * The account is not authorized to use that businessId.

### `PATCH /api/business/:businessId/listing/:listingId/details`

Update the details of a listing.

#### Responses

* 204 (No Content)
* 400 (Bad Request)
    * The enclosed entity does not conform to the schema.
* 403 (Forbidden)
    * The account is not authorized to use that businessId.
* 404 (Not Found)
    No such listing.
* 409 (Conflict)
    * An employee has already been accepted to the listing.

### `DELETE /api/business/:businessId/listing/:listingId`

Delete a listing.

#### Responses

* 204 (No Content)
* 402 (Payment Required)
    * A cancellation fee must be paid.
* 403 (Forbidden)
    * The account is not authorized to use that businessId.
* 404 (Not Found)
    * No such listing.

### `POST /api/business/:businessId/listing/:listingId/employee`

Approve an employee to work a job.

If such a request is made twice, then the second request will fail if a
different employee is approved; approving the same employee twice has no
effect.

#### Responses

* 204 (No Content)
* 400 (Bad Request)
    * The enclosed entity does not conform to the schema.
    * An employee has already been approved.
* 404 (Not Found)
    * No such listing.

### `GET /api/business/:businessId/listing/:listingId/employee`

Get the details of the employee associated with a given listing.

#### Responses

* 200 (OK)
* 404 (Not Found)
    * No such listing.
    * No employee is associated with the listing.

### `GET /api/business/:businessId/listing/:listingId/applicants`

Get a list of applicants for a listing.

#### Responses

* 200 (OK)
* 403 (Forbidden)
    * The account is not authorized to use that businessId.
* 404 (Not Found)
    * No such business.
    * No such listing.

### `POST /api/business/:businessId/listing/:listingId/employee/departure`

Indicate to the server at what time the employee has left. The indicated time
must be in the past, and by no more than 15 minutes.

#### Responses

* 204 (No Content)
* 400 (Bad Request)
    * The enclosed entity does not conform to the schema.
    * The indicated time is too far in the past.
* 403 (Forbidden)
    * The account is not authorized to use that businessId.
* 404 (Not Found)
    * No such listing.
    * There is no employee associated with the listing.
* 409 (Conflict)
    * The status of the listing is not `"inProgress"`.

### `POST /api/business/:businessId/listing/:listingId/employee/arrival`

Indicate to the server at what time the employee has arrived. The indicated
time must be in the past, and by no more than 15 minutes.

#### Responses

* 204 (No Content)
* 400 (Bad Request)
    * The indicated time is too far in the past.
* 404 (Not Found)
    * No such listing.
    * No employee is associated with the listing.

### `POST /api/business/:businessId/listing/:listingId/employee/rating`

Rate the employee associated with a given listing.

#### Responses

* 204 (No Content)
* 400 (Bad Request)
    * The enclosed entity does not conform to the schema.
    * The employee has already been rated.
* 404 (Not Found)
    * No such listing.
    * No employee is associated with the listing.
* 409 (Conflict)
    The status of the listing is not yet "completed".

Employee
--------

The following API endpoints require authentication as an employee.

### `PUT /api/employee/:userId/location`

Update the current location of the employee.

#### Responses

* 204 (No Content)
* 400 (Bad Request)
    * The enclosed entity does not conform to the schema.
* 403 (Forbidden)
    * The account is not authorized to use that userId.

### `GET /api/employee/:userId/location`

Get the current location of the employee.

#### Responses

* 200 (OK)
* 403 (Forbidden)
    * The account is not authorized ot use that userId.

### `PATCH /api/employee/:userId/details`

Update information regarding an employee.

#### Responses

* 204 (No Content)
* 400 (Bad Request)
    * The enclosed entity does not conform to the schema.
* 403 (Forbidden)
    * The account is not authorized to use that userId.

### `GET /api/employee/:userId/details`

Get information regarding an employee.

#### Responses

* 200 (OK)
* 403 (Forbidden)
    * The account is not authorized to use that userId.

### `POST /api/business/:businessId/listing/:listingId/applicants

Apply to a listing.

#### Responses

* 204 (No Content)
* 403 (Forbidden)
    * The listing was not dispatched to the user.
    * The user account is not authorized to use that userId.
* 404 (Not Found)
    * No such listing.
* 409 (Conflict)
    * The listing can no longer be applied to.

### `POST /api/business/:businessId/listing/:listingId/rating`

Rate a job.

#### Responses

* 204 (No Content)
* 403 (Forbidden)
    * The user is not approved for this job.
* 404 (Not Found)
    * No such business.
    * No such listing.
* 409 (Conflict)
    * The status of the listing is not yet `"completed"`.

### `GET /api/business/:businessId/listings/:listingId/rating`

Get the rating of a job given by its employee.

#### Responses

* 200 (OK)
* 403 (Forbidden)
    * The account is not authorized.
* 404 (Not Found)
    * No such business.
    * No such listing.
    * No rating has been given yet.
