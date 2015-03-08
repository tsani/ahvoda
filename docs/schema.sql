--===========================================================================--

--===================--
-- Schema for Ahvoda --
--===================--

-- Conventions --
-----------------

-- Identifiers
-------------------------------------------------
-- All identifiers are unquoted.
-- Table names are written in TitleCase.
-- Column names are written in camelCase.
-- SQL keywords are written in CAPS.

-- Indentation
-------------------------------------------------
-- After a CREATE TABLE, indent 4 spaces.
-- After the name of a column, indent 4 spaces.
-- Column declarations should be aligned.

-- Dates
-------------------------------------------------
-- Dates are always stored as UTC.

--===========================================================================--

START TRANSACTION;

DROP TABLE IF EXISTS Job;
DROP TABLE IF EXISTS ShiftSet;
DROP TABLE IF EXISTS Shift;
DROP TABLE IF EXISTS Position;
DROP TABLE IF EXISTS Employee;
DROP TABLE IF EXISTS ManagerSet;
DROP TABLE IF EXISTS Manager;
DROP TABLE IF EXISTS Login;
DROP TABLE IF EXISTS Gender;
DROP TABLE IF EXISTS Business;
DROP TABLE IF EXISTS Company;

-- A Company is an entity used to tie together multiple Businesses, which we
-- consider to be instances of that Company.
-- e.g. Tim Horton's
CREATE TABLE Company (
    companyId
        SERIAL
        PRIMARY KEY,
    companyName
        VARCHAR --120
        NOT NULL
    );

-- A Business is a type of account in Ahvoda
CREATE TABLE Business (
	businessId
        SERIAL
        PRIMARY KEY,
    -- The name of this Business
    -- e.g. Starbucks Fairview
    -- as opposed to just 'Starbucks', which would be the name of the company.
    businessName
        VARCHAR --120
        NOT NULL,
    -- A component of the Business's position, namely it's latitude.
    businessLocationLat
        FLOAT
        NOT NULL,
    -- A component of the Business's position, namely it's longitude.
    businessLocationLon
        FLOAT
        NOT NULL,
    -- An arbitrary textual description of this Business.
    businessDescription
        VARCHAR
        NOT NULL,
    -- Whether or not the Business has submitted documents proving its
    -- legitimacy.
    businessVerified
        BOOLEAN
        NOT NULL,
    -- Identifies the Company to which this Business is associated.
    -- Independent Businesses have this value set to NULL.
    companyId
        INTEGER
        REFERENCES Company
	);

CREATE TABLE Gender (
    genderId
        SERIAL
        PRIMARY KEY,
    genderName
        VARCHAR --35
        NOT NULL
    );

INSERT INTO Gender ( genderName ) VALUES ( 'male' );
INSERT INTO Gender ( genderName ) VALUES ( 'female' );
INSERT INTO Gender ( genderName ) VALUES ( 'other' );

CREATE TABLE Login (
	loginId
        INTEGER
        PRIMARY KEY,
    -- The username, to log in with.
	loginName
        VARCHAR --100
        UNIQUE
        NOT NULL,
    -- The email address to which notifications are sent.
    loginEmail
        VARCHAR --256
        UNIQUE -- TODO decide whether to allow duplicate emails
        NOT NULL,
    -- The password, or rather a 512-bit SHA hash thereof.
    loginPassword
        VARCHAR --64 -- SHA-512 hash
        NOT NULL,
    -- The salt added to the password prior to hashing.
    -- Our salts are added to the end.
    -- Salts should be completely random, and as unique as possible (although
    -- we don't enforce this in the database.)
    loginSalt
        VARCHAR --16
        NOT NULL,
    -- The time the account was created.
    loginCreateTimestamp
        TIMESTAMP WITHOUT TIME ZONE
        NOT NULL
        DEFAULT ( now() AT TIME ZONE 'utc' )
    );

-- A Manager is a type of account in Ahvoda. Accounts are tied to physical
-- persons, and so have birth dates, genders, and first-last names.
CREATE TABLE Manager (
    managerId
        SERIAL
        PRIMARY KEY,
    managerFirstName
        VARCHAR --100
        NOT NULL,
    managerLastName
        VARCHAR --100
        NOT NULL,
    managerBirthDate
        DATE
        NOT NULL,
    genderId
        INTEGER
        REFERENCES Gender,
    loginId
        INTEGER
        NOT NULL
        REFERENCES Login
    );

-- Links Managers with Businesses by providing an extra string which is the
-- "title" of this manager and an integer which is their access level.
-- For now these simply default to 'manager' and 1.
-- In the future this allows for assistant managers and other management
-- personnel to have access to the Ahvoda management interface.
CREATE TABLE ManagerSet (
    managerId
        INTEGER
        NOT NULL
        REFERENCES Manager,
    businessId
        INTEGER
        NOT NULL
        REFERENCES Business,
    managerSetName
        VARCHAR --50
        NOT NULL,
    managerSetLevel
        INTEGER
        NOT NULL
        CHECK ( managerSetLevel > 0 )
    );

-- An Employee is a type of account in Ahvoda. Accounts are tied to physical
-- persons, and so have birth dates, genders, and first-last names.
CREATE TABLE Employee (
    employeeId
        SERIAL
        PRIMARY KEY,
    -- The first name of this Employee.
    employeeFirstName
        VARCHAR --100
        NOT NULL,
    -- The last name of this Employee.
    employeeLastName
        VARCHAR --100
        NOT NULL,
    -- The date of birth of this Employee.
    employeeBirthDate
        DATE
        NOT NULL,
    -- The home address of this Employee.
    -- e.g. 404 rue de l'Introuvable
    employeeHomeAddress
        VARCHAR --200
        NOT NULL,
    -- The city where that address is valid.
    -- e.g. Montreal
    employeeHomeCity
        VARCHAR --100
        NOT NULL,
    educationLevel
        VARCHAR --100
        NOT NULL,
    -- A NULL gender indicates that the gender is simply unspecified.
    genderId
        INTEGER
        REFERENCES Gender
        ON DELETE SET NULL,
    -- The information used to authenticate as this Employee.
    loginId
        INTEGER
        UNIQUE -- no two Employees can use the same login
        NOT NULL
        REFERENCES Login
    );

CREATE TABLE Position (
    positionId
        SERIAL
        PRIMARY KEY,
    -- The name of this Position.
    positionName
        VARCHAR --50
        NOT NULL,
    -- When this Position was created.
    positionCreateDate
        TIMESTAMP WITHOUT TIME ZONE
        NOT NULL
        DEFAULT ( now() AT TIME ZONE 'utc' ),
    -- The Business at which this Position exists.
    businessId
        INTEGER
        NOT NULL
        REFERENCES Business
        ON DELETE CASCADE,
    -- The Manager that created this Position.
    -- This reference is set to NULL if the Manager is deleted.
    managerId
        INTEGER
        REFERENCES Manager
        ON DELETE SET NULL,
    UNIQUE (positionName, businessId)
    );

-- Describes a shift, which is tied to a particular Position in a particular
-- Business, and has some finite length. This table does not include the notion
-- of shifts repeating.
CREATE TABLE Shift (
    shiftId
        SERIAL
        PRIMARY KEY,
    shiftStartTime
        TIMESTAMP WITHOUT TIME ZONE
        NOT NULL
        DEFAULT ( now() AT TIME ZONE 'utc' )
        CHECK ( shiftStartTime < shiftEndTime ),
    shiftEndTime
        TIMESTAMP WITHOUT TIME ZONE
        NOT NULL
        DEFAULT ( now() AT TIME ZONE 'utc' )
        CHECK ( shiftEndTime > shiftStartTime ),
    -- The position (type of work) of this shift.
    positionId
        INTEGER
        NOT NULL
        REFERENCES Position
        ON DELETE CASCADE,
    -- The business for which the work is being performed.
    businessId
        INTEGER
        NOT NULL
        REFERENCES Business
        ON DELETE CASCADE
    );

-- Describes the connection between workers and shifts.
CREATE TABLE ShiftSet (
    employeeId
        INTEGER
        NOT NULL
        REFERENCES Employee,
    shiftId
        INTEGER
        NOT NULL
        REFERENCES Shift,
    -- This pair of values is unique and both components are not null, so it
    -- forms the primary key for this table.
    PRIMARY KEY ( employeeId, shiftId )
    );

CREATE TABLE Job (
    jobId
        SERIAL
        PRIMARY KEY,
    -- The start date is either decided a priori by the employer or is set
    -- automatically by Ahvoda when the employee is added to the workforce.
	jobStartDate
        DATE,
    -- The end date either decided a priori by the employer or is set
    -- automatically by Ahvoda when the employee is removed from the workforce.
    jobEndDate
        DATE,
    -- A job is available iff applications can be submitted to it.
    jobIsAvailable
        BOOLEAN
        NOT NULL,
    -- A salary is an hourly rate. A NULL hourly rate means that the employer
    -- is not specifying the salary for this job.
    jobSalary
        FLOAT,
    -- An arbitrary text written by the employer explaining the job.
    jobPositionDetails
        VARCHAR
        NOT NULL,
    -- When was this record created. A date used primarily internally.
    jobCreateDate
        DATE
        NOT NULL,
    -- A job is for a particular position.
    positionId
        INTEGER
        NOT NULL
        REFERENCES Position
        ON DELETE CASCADE,
    -- Until when can applications be submitted for this Job. At this deadline,
    -- the jobIsAvailable field will be set to FALSE automatically by Ahvoda.
    jobApplicationDeadline
        DATE,
    -- Identifies the employee that has this Job. Starts off NULL before
    -- someone has been hired.
    employeeId
        INTEGER
        REFERENCES Employee,
    -- Identifies the Manager that created this Job.
    managerId
        INTEGER
        REFERENCES Manager
        ON DELETE SET NULL
    );

-- NOTE an index should be made on employeeId within Job.

-- NOTE a lot of inconsistencies can arise in the Job table due to the
-- interactions between jobApplicationDeadline, jobIsAvailable, and employeeId.

COMMIT;
