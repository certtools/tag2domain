CREATE SCHEMA IF NOT EXISTS :t2d_schema;
SET search_path TO :t2d_schema;

-- creates the view that is used to retrieve tags
CREATE OR REPLACE VIEW v_unified_tags
AS SELECT
  :t2d_entity_table.:t2d_entity_id_column AS domain_id,
  :t2d_entity_table.:t2d_entity_name_column AS domain_name,
  ':t2d_tag_type' AS tag_type,
  :t2d_intxn_table_name.tag_id,
  :t2d_intxn_table_name.value_id,
  :t2d_intxn_table_name.start_ts,
  :t2d_intxn_table_name.measured_at,
  :t2d_intxn_table_name.end_ts
FROM :t2d_entity_table
JOIN :t2d_intxn_table_name ON (:t2d_entity_table.:t2d_entity_id_column = :t2d_intxn_table_name.entity_id);

-- creates a filter table (this is an empty place holder only)
CREATE TABLE v_tag2domain_domain_filter (
    domain_id bigint NOT NULL,
    tag_name character varying(200) NOT NULL,
    start_ts timestamp with time zone NOT NULL,
    end_ts timestamp with time zone NOT NULL,
    value text
);

-- ----------------------------------------------------------------------------
-- SQL functions used to access the intersection tables
-- ----------------------------------------------------------------------------

DROP FUNCTION IF EXISTS tag2domain_get_open_tags;
-- function tag2domain_get_open_tags()
-- returns a table with all currently open tags
CREATE FUNCTION tag2domain_get_open_tags()
  RETURNS TABLE(
    domain_id bigint,
    domain_name character varying(100),
    tag_type text,
    tag_id int,
    value_id int,
    start_time timestamp with time zone,
    measured_at timestamp with time zone,
    end_time timestamp with time zone
  ) AS $$
 SELECT * FROM v_unified_tags
 WHERE (v_unified_tags.end_ts IS NULL)
$$ LANGUAGE SQL STABLE
    SET search_path TO :t2d_schema
;

DROP FUNCTION IF EXISTS tag2domain_get_open_tags_filtered;
-- function tag2domain_get_open_tags_filtered(filter_type, filter_value)
--
-- returns a table with all currently open tags for all domains that filtered
-- through the v_tag2domain_domain_filter filter tables.
--
-- filter_type references the tag_name column and filter_value the value column of the
-- v_tag2domain_domain_filter table. A domain passes if a row with
--   tag_name=filter_type AND value=filter_value
-- exists.
CREATE FUNCTION tag2domain_get_open_tags_filtered(filter_type text, filter_value text)
  RETURNS TABLE(
    domain_id bigint,
    domain_name character varying(100),
    tag_type text,
    tag_id int,
    value_id int,
    start_time timestamp with time zone,
    measured_at timestamp with time zone,
    end_time timestamp with time zone
  ) AS $$
 SELECT v_unified_tags.* FROM v_unified_tags
 JOIN v_tag2domain_domain_filter USING (domain_id)
 WHERE (
    (v_unified_tags.end_ts IS NULL)
    AND (v_tag2domain_domain_filter.end_ts IS NULL)
    AND (v_tag2domain_domain_filter.tag_name = $1)
    AND (v_tag2domain_domain_filter.value = $2)
  )
$$ LANGUAGE SQL STABLE
    SET search_path TO :t2d_schema
;

DROP FUNCTION IF EXISTS tag2domain_get_tags_at_time;
-- function tag2domain_get_tags_at_time(at_time)
-- Returns all tags that were open at time at_time.
CREATE FUNCTION tag2domain_get_tags_at_time(at_time timestamp)
  RETURNS TABLE(
    domain_id bigint,
    domain_name character varying(100),
    tag_type text,
    tag_id int,
    value_id int,
    start_time timestamp with time zone,
    measured_at timestamp with time zone,
    end_time timestamp with time zone
  ) AS $$
 SELECT v_unified_tags.* FROM v_unified_tags
 WHERE (
    (v_unified_tags.start_ts <= $1)
    AND ((v_unified_tags.end_ts > $1) OR (v_unified_tags.end_ts IS NULL))
  )
$$ LANGUAGE SQL STABLE
    SET search_path TO :t2d_schema
;

DROP FUNCTION IF EXISTS tag2domain_get_tags_at_time_filtered;
-- function tag2domain_get_tags_at_time_filtered(at_time, filter_type, filter_value)
--
-- returns a table with all tags that were open at time at_time for all domains that
-- filtered through the v_tag2domain_domain_filter filter tables.
--
-- filter_type references the tag_name column and filter_value the value column of the
-- v_tag2domain_domain_filter table. A domain passes if a row with
--   tag_name=filter_type AND value=filter_value
-- exists.
CREATE FUNCTION tag2domain_get_tags_at_time_filtered(at_time timestamp, filter_type text, filter_value text)
  RETURNS TABLE(
    domain_id bigint,
    domain_name character varying(100),
    tag_type text,
    tag_id int,
    value_id int,
    start_time timestamp with time zone,
    measured_at timestamp with time zone,
    end_time timestamp with time zone
  ) AS $$
 SELECT v_unified_tags.* FROM v_unified_tags
 JOIN v_tag2domain_domain_filter USING (domain_id)
 WHERE (
    (v_unified_tags.start_ts <= $1)
    AND ((v_unified_tags.end_ts > $1) OR (v_unified_tags.end_ts IS NULL))
    AND (v_tag2domain_domain_filter.start_ts AT TIME ZONE 'UTC' <= $1)
    AND ((v_tag2domain_domain_filter.end_ts AT TIME ZONE 'UTC' > $1) OR (v_tag2domain_domain_filter.end_ts IS NULL))
    AND (v_tag2domain_domain_filter.tag_name = $2)
    AND (v_tag2domain_domain_filter.value = $3)
  )
$$ LANGUAGE SQL STABLE
    SET search_path TO :t2d_schema
;

DROP FUNCTION IF EXISTS tag2domain_get_open_tags_domain;
-- function tag2domain_get_open_tags_domain(domain_name)
--
-- returns a table with the open tags for a single domain with name domain_name
CREATE FUNCTION (domain_name character varying (100))
  RETURNS TABLE(
    domain_id bigint,
    domain_name character varying(100),
    tag_type text,
    tag_id int,
    value_id int,
    start_time timestamp with time zone,
    measured_at timestamp with time zone,
    end_time timestamp with time zone
  ) AS $$
 SELECT v_unified_tags.* FROM v_unified_tags
 WHERE
    (v_unified_tags.end_ts IS NULL)
    AND (v_unified_tags.domain_name = $1)
$$ LANGUAGE SQL STABLE
    SET search_path TO :t2d_schema
;

DROP FUNCTION IF EXISTS tag2domain_get_tags_at_time_domain;
-- function tag2domain_get_open_tags_domain(at_time, domain_name)
--
-- returns a table with the tags set at time at_time for a single domain with name domain_name
CREATE FUNCTION tag2domain_get_tags_at_time_domain(at_time timestamp, domain_name character varying (100))
  RETURNS TABLE(
    domain_id bigint,
    domain_name character varying(100),
    tag_type text,
    tag_id int,
    value_id int,
    start_time timestamp with time zone,
    measured_at timestamp with time zone,
    end_time timestamp with time zone
  ) AS $$
 SELECT * FROM v_unified_tags
 WHERE (
    (v_unified_tags.start_ts <= $1)
    AND ((v_unified_tags.end_ts > $1) OR (v_unified_tags.end_ts IS NULL))
    AND (v_unified_tags.domain_name = $2)
  )
$$ LANGUAGE SQL STABLE
    SET search_path TO :t2d_schema
;

DROP FUNCTION IF EXISTS tag2domain_get_all_tags_domain;
-- function tag2domain_get_all_tags_domain(domain_name)
--
-- returns a table with all tags that were ever set for a single domain with name domain_name
CREATE FUNCTION tag2domain_get_all_tags_domain(domain_name character varying (100))
  RETURNS TABLE(
    domain_id bigint,
    domain_name character varying(100),
    tag_type text,
    tag_id int,
    value_id int,
    start_time timestamp with time zone,
    measured_at timestamp with time zone,
    end_time timestamp with time zone
  ) AS $$
 SELECT v_unified_tags.* FROM v_unified_tags
 WHERE (
    (v_unified_tags.domain_name = $1)
  )
$$ LANGUAGE SQL
    SET search_path TO :t2d_schema
;