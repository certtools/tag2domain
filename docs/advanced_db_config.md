# Advanced DB configuration

## Glue tables
tag2domain-api uses SQL function in the glue section of the tag2domain schema
to gather the tags that are active at any time. This allows one to combine 
information from multiple tables and provide them through the tag2domain API.

The functions required are:
+ _tag2domain_get_open_tags_() - provides a table with all tags that are open,
i.e. whose end_time is NULL
+ _tag2domain_get_tags_at_time_(at_time) - provides a table with all tags that
were active at time _at_time_
+ _tag2domain_get_open_tags_domain_(domain_name)_ - provides a table with all
tags that are open (end_time is NULL) and that are associated with domain name
_domain_name_
+ _tag2domain_get_tags_at_time_domain_(at_time, domain_name) - provides a table
with all tags that are associated with _domain_name_ and that were open at time
_at_time_
+ _tag2domain_get_all_tags_domain(domain_name)_ - get all tags that were ever
associated with the domain name _domain_name_

In addition there are also filtered versions of the first two functions:
+ _tag2domain_get_open_tags_filtered(filter_type, filter_value)_
+ _tag2domain_get_tags_at_time_filtered(at_time, filter_type, filter_value)_

These functions only return domains that have a certain property. See the
[Filters](#filters) section for more details on how filters can be implemented.

As an illustration consider the tables that are set up for the all-in-one demo
setup (`docker/all-in-one-demo/db/all-in-one-demo-sql/tag2domain_glue_tables.sql`).
First a view is defined:
``` sql
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
```
In this case this view simply combines the domain ID and name with the tags
in the intersections table. The required functions are then based on this view:
``` sql
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
$$ LANGUAGE SQL STABLE;
```

The simplest way to extend this setup to one with two intersection tables is
to replace the v_unified_tags with a version where multiple intersection tables
are combined through a `UNION ALL`:
``` sql
CREATE OR REPLACE VIEW v_unified_tags
AS SELECT
  domains.domain_id,
  domains.domain_name,
  'A' AS tag_type,
  intersections_A.tag_id,
  intersections_A.value_id,
  intersections_A.start_ts,
  intersections_A.measured_at,
  intersections_A.end_ts
FROM public.domains AS domains
JOIN intersections_A ON (domains.domain_id = intersections_A.entity_id)
UNION ALL SELECT
  domains.domain_id,
  domains.domain_name,
  'B' AS tag_type,
  intersections_B.tag_id,
  intersections_B.value_id,
  intersections_B.start_ts,
  intersections_B.measured_at,
  intersections_B.end_ts
FROM public.domains AS domains
JOIN intersections_B ON (domains.domain_id = intersections_B.entity_id);
```
This allows you to combine information from different tables into a single
view. However, care has to be taken that the _tag_id_s and _value_id_s that
result from these views are consistent with the content of the taxonomy, tags,
and the taxonomy_tag_val tables.

You may wonder, why the views are wrapped into the additional layer of
functions. The reason is, that the PostgreSQL planner (as of 2021-01-08) does
not optimize over the UNION ALL statements, resulting in large memory
consumption and long run times for the queries required by the API. This
becomes especially noticeable when filters are used. The functions can be
defined in such a way, that the number of domains is reduced before the tables
are appended so that the number of records that have to be loaded is
considerably smaller.

Which brings us to the topic of filters.

## Filters
Filters can be implemented in the *_filtered functions. The simplest way is to
define an additional table as done in the all-in.one demo:
``` sql
CREATE OR REPLACE VIEW v_tag2domain_domain_filter
 AS
  -- registrars
  SELECT
    domains.domain_id AS domain_id,
    'temperature' AS tag_name,
    temperatures.start_ts AS start_ts,
    temperatures.end_ts AS end_ts,
    temperatures.temperature::text AS value
  FROM public.temperatures AS temperatures
  JOIN public.domains AS domains USING(domain_id)
;
```
Here a v_tag2domain_domain_filter view is defined that contains rows like the
following:

| domain_id | tag_name      | start_ts            | end_ts              | value       |
|-----------|---------------|---------------------|---------------------|-------------|
| 1         | 'temperature' | 2020-12-13T12:56:00 | NULL                | 'hot'       |
| 2         | 'temperature' | 2020-06-01T06:13:00 | 2020-10-12T18:23:00 | 'cold'      |
| ...       | ...           | ...                 | ...                 | ...         |

The aim is that domains can be filtered using criteria like
_tag_name = value_. This must be implemented in the *_filtered functions. In
the all-in-one demo this is done like so:
``` sql
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
```



## Schema
![EER Diagram](../static/schema.svg)
