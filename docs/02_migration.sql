START TRANSACTION;

DROP TABLE IF EXISTS LanguageTestLoginAssociation;
DROP TABLE IF EXISTS TestLogin;
DROP TABLE IF EXISTS Industry;
DROP TABLE IF EXISTS Language;
DROP TABLE IF EXISTS SchoolFaculty;
DROP TABLE IF EXISTS Availability;

CREATE TABLE Availability (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

INSERT INTO Availability ( name ) VALUES ( 'asap' );
INSERT INTO Availability ( name ) VALUES ( 'emay' );
INSERT INTO Availability ( name ) VALUES ( 'mmay' );
INSERT INTO Availability ( name ) VALUES ( 'ejun' );
INSERT INTO Availability ( name ) VALUES ( 'mjun' );
INSERT INTO Availability ( name ) VALUES ( 'ejul' );
INSERT INTO Availability ( name ) VALUES ( 'mjul' );
INSERT INTO Availability ( name ) VALUES ( 'eaug' );
INSERT INTO Availability ( name ) VALUES ( 'maug' );
INSERT INTO Availability ( name ) VALUES ( 'sep' );

CREATE TABLE SchoolFaculty (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

INSERT INTO SchoolFaculty ( name ) VALUES ( '' );
INSERT INTO SchoolFaculty ( name ) VALUES ( 'science' );
INSERT INTO SchoolFaculty ( name ) VALUES ( 'commerce' );
INSERT INTO SchoolFaculty ( name ) VALUES ( 'arts' );
INSERT INTO SchoolFaculty ( name ) VALUES ( 'medecine' );
INSERT INTO SchoolFaculty ( name ) VALUES ( 'engineering' );
INSERT INTO SchoolFaculty ( name ) VALUES ( 'education' );
INSERT INTO SchoolFaculty ( name ) VALUES ( 'religion' );
INSERT INTO SchoolFaculty ( name ) VALUES ( 'environment' );
INSERT INTO SchoolFaculty ( name ) VALUES ( 'dentistry' );
INSERT INTO SchoolFaculty ( name ) VALUES ( 'law' );
INSERT INTO SchoolFaculty ( name ) VALUES ( 'music' );
INSERT INTO SchoolFaculty ( name ) VALUES ( 'continuing' );
INSERT INTO SchoolFaculty ( name ) VALUES ( 'other' );

CREATE TABLE Language (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

INSERT INTO Language ( name ) VALUES ( 'english' );
INSERT INTO Language ( name ) VALUES ( 'french' );

CREATE TABLE Industry (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

INSERT INTO Industry ( name ) VALUES ( 'fooddrink' );
INSERT INTO Industry ( name ) VALUES ( 'nightlife' );
INSERT INTO Industry ( name ) VALUES ( 'sales' );

CREATE TABLE TestLogin (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email_address VARCHAR UNIQUE NOT NULL,
    password VARCHAR,
    password_salt VARCHAR,
    gender_id INTEGER REFERENCES Gender ( id ) NOT NULL,
    date_of_birth DATE NOT NULL,
    address_line_1 VARCHAR NOT NULL,
    address_line_2 VARCHAR NOT NULL,
    postal_code VARCHAR NOT NULL,
    phone_number VARCHAR NOT NULL,
    cv_original_name VARCHAR NOT NULL,
    cv_name VARCHAR NOT NULL,
    is_student BOOLEAN NOT NULL,
    faculty_id INTEGER REFERENCES SchoolFaculty ( id ),
    year VARCHAR,
    canadian_citizen BOOLEAN NOT NULL,
    canadian_work BOOLEAN NOT NULL,
    availability_id INTEGER REFERENCES Availability ( id ),
    industry_1_id INTEGER REFERENCES Industry ( id ),
    industry_2_id INTEGER REFERENCES Industry ( id ),
    industry_3_id INTEGER REFERENCES Industry ( id )
);

CREATE TABLE LanguageTestLoginAssociation (
    language_id INTEGER REFERENCES Language ( id ) NOT NULL,
    login_id INTEGER REFERENCES TestLogin ( id ) NOT NULL
);

COMMIT;
