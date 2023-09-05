﻿CREATE USER meat_admin WITH ENCRYPTED PASSWORD 'myverystrongpass' createrole superuser;

CREATE DATABASE meatplants
    WITH 
    OWNER = meatplants_admin
    ENCODING = 'UTF8'
    LC_COLLATE = 'Russian_Russia.1251'
    LC_CTYPE = 'Russian_Russia.1251'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

GRANT ALL ON DATABASE meatplants TO meat_admin;
GRANT TEMPORARY, CONNECT ON DATABASE meatplants TO PUBLIC;
ALTER DEFAULT PRIVILEGES
GRANT ALL ON TABLES TO meat_admin;