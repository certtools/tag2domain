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

CREATE TABLE :t2d_intxn_table_name (
    entity_id bigint,
    tag_id integer,
    start_date integer,
    end_date integer,
    taxonomy_id integer,
    value_id integer,
    measured_at timestamp with time zone,
    start_ts timestamp with time zone,
    end_ts timestamp with time zone,
    producer character varying(100) DEFAULT NULL::character varying,
    FOREIGN KEY (value_id) REFERENCES taxonomy_tag_val(id),
    FOREIGN KEY (taxonomy_id) REFERENCES taxonomy(id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id),
    FOREIGN KEY (entity_id) REFERENCES :t2d_entity_table(:t2d_entity_id_column)
);

COMMENT ON TABLE :t2d_intxn_table_name IS 'Intersection table that marks which tags and values where set on an entity in a given timespan';
COMMENT ON COLUMN :t2d_intxn_table_name.entity_id IS 'Foreign key in the table of entities';
COMMENT ON COLUMN :t2d_intxn_table_name.tag_id IS 'Foreign Key in table "tags"';
COMMENT ON COLUMN :t2d_intxn_table_name.start_date IS 'Startdate as int (YYYYMMDD)';
COMMENT ON COLUMN :t2d_intxn_table_name.end_date IS 'Enddate as int (YYYYMMDD)';
COMMENT ON COLUMN :t2d_intxn_table_name.taxonomy_id IS 'Foreign Key in table "taxonomy"';
COMMENT ON COLUMN :t2d_intxn_table_name.value_id IS 'Foreign Key in table "taxonomy_tag_val"';
COMMENT ON COLUMN :t2d_intxn_table_name.measured_at IS 'Last time the tag was measured';
COMMENT ON COLUMN :t2d_intxn_table_name.start_ts IS 'Start date/time of tag';
COMMENT ON COLUMN :t2d_intxn_table_name.end_ts IS 'End date/time of tag';
COMMENT ON COLUMN :t2d_intxn_table_name.producer IS 'Name of producer that measured the tag';

CREATE INDEX ON :t2d_intxn_table_name USING btree (entity_id);
CREATE INDEX ON :t2d_intxn_table_name USING btree (end_ts DESC);
CREATE INDEX ON :t2d_intxn_table_name USING btree (start_ts DESC);
CREATE INDEX ON :t2d_intxn_table_name USING btree (tag_id);