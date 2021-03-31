SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

CREATE SCHEMA IF NOT EXISTS :t2d_schema;
SET search_path TO :t2d_schema;

CREATE TABLE taxonomy (
    id integer NOT NULL,
    name character varying(300) NOT NULL,
    description text,
    is_actionable double precision,
    is_automatically_classifiable boolean,
    is_stable boolean,
    for_numbers boolean,
    for_domains boolean,
    url character varying(500),
    allows_auto_tags boolean DEFAULT false,
    allows_auto_values boolean DEFAULT false
);

CREATE SEQUENCE taxonomy_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE taxonomy_id_seq OWNED BY taxonomy.id;
ALTER TABLE ONLY taxonomy ALTER COLUMN id SET DEFAULT nextval('taxonomy_id_seq'::regclass);
ALTER TABLE ONLY taxonomy ADD CONSTRAINT taxonomy_name_key UNIQUE (name);
ALTER TABLE ONLY taxonomy ADD CONSTRAINT taxonomy_pkey PRIMARY KEY (id);

COMMENT ON COLUMN taxonomy.id IS 'Primary Key';
COMMENT ON COLUMN taxonomy.name IS 'Name of the taxonomy';
COMMENT ON COLUMN taxonomy.description IS 'Short description of the taxonomy';
COMMENT ON COLUMN taxonomy.is_actionable IS '1 is taxonomy is actionable, 0 if not';
COMMENT ON COLUMN taxonomy.is_automatically_classifiable IS '1 if tags can be automatically detected, 0 if not';
COMMENT ON COLUMN taxonomy.is_stable IS 'rue if taxonomy is stable';
COMMENT ON COLUMN taxonomy.for_numbers IS 'true if taxonomy can be applied to IP adresses';
COMMENT ON COLUMN taxonomy.for_domains IS 'true if taxonomy can be applied to domains';
COMMENT ON COLUMN taxonomy.url IS 'Link to a description or the source of the taxonomy';
COMMENT ON COLUMN taxonomy.allows_auto_tags IS 'true if the taxonomy allows the automatic generation of tags';
COMMENT ON COLUMN taxonomy.allows_auto_values IS 'true if the taxonomy allows the automatic generation of values';
