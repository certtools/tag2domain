CREATE SCHEMA IF NOT EXISTS :t2d_schema;
SET search_path TO :t2d_schema;

CREATE OR REPLACE VIEW v_unified_tags
AS SELECT
  domains.domain_id,
  domains.domain_name,
  'domain' AS tag_type,
  intersections.tag_id,
  intersections.value_id,
  intersections.start_ts,
  intersections.measured_at,
  intersections.end_ts
FROM public.domains AS domains
JOIN intersections ON (domains.domain_id = intersections.entity_id);

CREATE OR REPLACE VIEW v_tag2domain_domain_filter
 AS
  -- registrars
  SELECT
    domains.domain_id AS domain_id,
    'registrar-id' AS tag_name,
    delegations.start_ts AS start_ts,
    delegations.end_ts AS  end_ts,
    registrars.registrar_id::text AS value
  FROM public.registrars AS registrars
  JOIN public.delegations AS delegations USING(registrar_id)
  JOIN public.domains AS domains USING(domain_id)
;

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
CREATE FUNCTION tag2domain_get_open_tags_domain(domain_name character varying (100))
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