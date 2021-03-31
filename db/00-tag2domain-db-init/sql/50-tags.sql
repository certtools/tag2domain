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

CREATE TABLE tags (
    tag_id integer NOT NULL,
    tag_name character varying(200),
    tag_description character varying NOT NULL,
    taxonomy_id integer,
    extras jsonb
);


CREATE SEQUENCE tags_tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE tags_tag_id_seq OWNED BY tags.tag_id;
ALTER TABLE ONLY tags ALTER COLUMN tag_id SET DEFAULT nextval('tags_tag_id_seq'::regclass);
ALTER TABLE ONLY tags ADD CONSTRAINT pk_tags_tag_id PRIMARY KEY (tag_id);
ALTER TABLE ONLY tags ADD CONSTRAINT tags_tag_name_taxonomy_id_key UNIQUE (tag_name, taxonomy_id);
ALTER TABLE ONLY tags ADD CONSTRAINT taxonomy_predicates_taxonomy_id_fkey FOREIGN KEY (taxonomy_id) REFERENCES taxonomy(id);

COMMENT ON COLUMN tags.tag_id IS 'Primary Key';
COMMENT ON COLUMN tags.tag_name IS 'Tag Name';
COMMENT ON COLUMN tags.tag_description IS 'Short description of the tag';
COMMENT ON COLUMN tags.taxonomy_id IS 'Foreign key in "taxonomy"';
COMMENT ON COLUMN tags.extras IS 'Additional descriptions of the tag';
