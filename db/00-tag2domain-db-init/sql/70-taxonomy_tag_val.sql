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

CREATE TABLE taxonomy_tag_val (
    id integer NOT NULL,
    value text,
    tag_id integer NOT NULL
);

CREATE SEQUENCE taxonomy_tag_val_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE taxonomy_tag_val_id_seq OWNED BY taxonomy_tag_val.id;
ALTER TABLE ONLY taxonomy_tag_val ALTER COLUMN id SET DEFAULT nextval('taxonomy_tag_val_id_seq'::regclass);
ALTER TABLE ONLY taxonomy_tag_val ADD CONSTRAINT taxonomy_tag_val_pkey PRIMARY KEY (id);
ALTER TABLE ONLY taxonomy_tag_val ADD CONSTRAINT taxonomy_tag_val_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES tags(tag_id);

COMMENT ON TABLE taxonomy_tag_val IS 'Table of tag2domain-tag values';
COMMENT ON COLUMN taxonomy_tag_val.id IS 'Primary Key';
COMMENT ON COLUMN taxonomy_tag_val.value IS 'Value for this Tag';
COMMENT ON COLUMN taxonomy_tag_val.tag_id IS 'ID of tag the value is associated with (foreign key in "tags")';
