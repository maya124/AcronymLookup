CREATE TABLE acronyms (
AID serial PRIMARY KEY,
acronym varchar(20) NOT NULL
);

CREATE TABLE definitions (
DID serial PRIMARY KEY,
definition varchar(300) NOT NULL,
context varchar(5000) NOT NULL,
url varchar(300) NOT NULL
);

CREATE TABLE acronyms_definitions (
ADID serial PRIMARY KEY,
AID int NOT NULL,
DID int NOT NULL
);

CREATE TABLE true_definitions (
TID serial PRIMARY KEY,
acronym varchar(20) NOT NULL, 
true_definition varchar(300) NOT NULL,
url varchar(300) NOT NULL
);

