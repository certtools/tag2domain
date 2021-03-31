_d = {}
db_statements = _d

_d["get_taxonomy_intersections"] = (
  "SELECT %(__all_fields__)s FROM %(table_name)s WHERE (%(taxonomy_id)s = %%s)"
)

_d["get_open_tags"] = (
    """
    SELECT
        %(tag_id)s AS tag_id,
        %(value_id)s AS value_id,
        %(measured_at)s AS measured_at,
        %(producer)s AS producer
    FROM %(table_name)s
    WHERE
        (%(id)s = %%s)
        AND (%(taxonomy_id)s = %%s)
        AND (%(end_date)s IS NULL)
        AND (%(end_ts)s IS NULL)
    """
)

_d["get_all_tags"] = (
    """
    SELECT
        %(tag_id)s AS tag_id,
        %(value_id)s AS value_id,
        %(start_ts)s AS start_ts,
        %(measured_at)s AS measured_at,
        %(end_ts)s AS end_ts,
        %(producer)s AS producer
    FROM %(table_name)s
    WHERE
        (%(id)s = %%s)
        AND (%(taxonomy_id)s = %%s)
    """
)

_d["insert_intersections"] = (
    """
    INSERT INTO %(table_name)s
        (%(id)s, %(tag_id)s, %(start_date)s, %(end_date)s, %(taxonomy_id)s,
         %(value_id)s, %(measured_at)s, %(start_ts)s, %(end_ts)s, %(producer)s)
    VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s)
    """
)

_d["prolong_intersections_no_value"] = (
    """
    UPDATE %(table_name)s
    SET
        %(measured_at)s = %%s,
        %(producer)s = %%s
    WHERE
        (%(id)s = %%s)
        AND (%(taxonomy_id)s = %%s)
        AND (%(tag_id)s = %%s)
        AND (%(value_id)s IS NULL)
        AND (%(end_date)s IS NULL)
        AND (%(end_ts)s IS NULL)
    """
)

_d["prolong_intersections_w_value"] = (
    """
    UPDATE %(table_name)s
    SET
        %(measured_at)s = %%s,
        %(producer)s = %%s
    WHERE
        (%(id)s = %%s)
        AND (%(taxonomy_id)s = %%s)
        AND (%(tag_id)s = %%s)
        AND (%(value_id)s = %%s)
        AND (%(end_date)s IS NULL)
        AND (%(end_ts)s IS NULL)
    """
)

_d["end_intersection_no_value"] = (
    """
    UPDATE %(table_name)s
    SET
        %(measured_at)s = %%s,
        %(end_date)s = %%s,
        %(end_ts)s = %%s,
        %(producer)s = %%s
    WHERE
        (%(id)s = %%s)
        AND (%(taxonomy_id)s = %%s)
        AND (%(tag_id)s = %%s)
        AND (%(value_id)s IS NULL)
        AND (%(end_date)s IS NULL)
        AND (%(end_ts)s IS NULL)
    """
)

_d["end_intersection_w_value"] = (
    """
    UPDATE %(table_name)s
    SET
        %(measured_at)s = %%s,
        %(end_date)s = %%s,
        %(end_ts)s = %%s,
        %(producer)s = %%s
    WHERE
        (%(id)s = %%s)
        AND (%(taxonomy_id)s = %%s)
        AND (%(tag_id)s = %%s)
        AND (%(value_id)s = %%s)
        AND (%(end_date)s IS NULL)
        AND (%(end_ts)s IS NULL)
    """
)
