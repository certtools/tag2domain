import datetime
import logging

from fastapi import APIRouter, Query
from typing import List, Optional

from tag2domain_api.app.util.models import (
    StatsTaxonomiesResponse,
    StatsTagsResponse,
    StatsCategoriesResponse,
    StatsValuesResponse
)
from tag2domain_api.app.util.config import config
from tag2domain_api.app.util.db import (
    execute_db,
    get_sql_base_table,
    RE_FILTER
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/taxonomies",
    response_model=List[StatsTaxonomiesResponse],
    name="Stats on taxonomies",
    summary="Show stats on all taxonomies"
)
def get_stats_taxonomies(
    at_time: datetime.datetime = None,
    filter: str = Query(None, regex=RE_FILTER),
    limit: int = config['default_limit'],
    offset: int = config['default_offset']
):
    """ Returns all taxonomies with the number of domains that
    are associated with at least one tag from this taxonomy.

    A filter is a string of the form Tag=Value. The available tags and values
    can be fetched using the /api/v1/filters/types and /api/v1/filters/values
    endpoints, respectively.

    **GET Parameters:**
      | parameter                   | description                                                                     |
      | --------------------------- | ------------------------------------------------------------------------------- |
      | at_time                     | point in time to query                                                          |
      | filter                      | filter domains by entries in the filter table before counting                   |
      | limit                       | limit answer to {limit} entries                                                 |
      | offset                      | start answer at the {offset}-th entry                                           |

    **Output (JSON):**
    JSON list of objects, ordered by count, descending. Each object has the following keys:
      | key                         | description                                                                     |
      | --------------------------- | ------------------------------------------------------------------------------- |
      | taxonomy_name               | name of the taxonomy                                                            |
      | count                       | number of domains labeled by at least one tag from this taxonomy                |
    """
    base_table, base_table_params = get_sql_base_table(at_time, filter)

    # Build the SQL statement
    SQL = """
      SELECT
        COUNT(DISTINCT domain_id), taxonomy.name AS taxonomy_name
        FROM %s AS tag_table -- base_table
        JOIN tags USING (tag_id)
        JOIN taxonomy ON (tags.taxonomy_id = taxonomy.id)
        GROUP by taxonomy.id, taxonomy.name
        ORDER BY count DESC LIMIT %%(limit)s OFFSET %%(offset)s
      """ % (base_table)

    params = {
        'at_time': at_time,
        'limit': limit,
        'offset': offset
    }
    params.update(base_table_params)
    rows = execute_db(SQL, params, dict_=True)
    return rows


@router.get(
    "/categories",
    response_model=List[StatsCategoriesResponse],
    name="Stats on categories",
    summary="Show stats on categories within a taxonomy"
)
def get_stats_categories(
    taxonomy: str,
    at_time: datetime.datetime = None,
    filter: str = Query(None, regex=RE_FILTER),
    limit: int = config['default_limit'],
    offset: int = config['default_offset']
):
    """Returns the categories within a taxonomy with the number of
    domains that are associated with at least one tag from the
    category.

    A filter is a string of the form Tag=Value. The available tags and values can be fetched using
    the /api/v1/filters/types and /api/v1/filters/values endpoints, respectively.

    **GET Parameters:**
    | parameter                   | description                                                                     |
    | --------------------------- | ------------------------------------------------------------------------------- |
    | taxonomy                    | name of taxonomy to be looked up                                                |
    | at_time                     | point in time to query                                                          |
    | filter                      | filter domains by entries in the filter table before counting                   |
    | limit                       | limit answer to {limit} entries                                                 |
    | offset                      | start answer at the {offset}-th entry                                           |

    **Output (JSON):**
    JSON list of objects, ordered by count, descending. Each object has the following keys:
    | key                         | description                                                                     |
    | --------------------------- | ------------------------------------------------------------------------------- |
    | category                    | name of the category                                                            |
    | count                       | number of domains  labeled by at least one tag from this category               |
    """
    base_table, base_table_params = get_sql_base_table(at_time, filter)

    SQL = """
      WITH t AS (
        SELECT
          domain_id,
          REGEXP_REPLACE(tag_name, '^(.+)::.+$', '\\1') AS category
        FROM %s AS tag_table -- base_table
        JOIN tags USING (tag_id)
        JOIN taxonomy ON (tags.taxonomy_id = taxonomy.id)
        WHERE
          (taxonomy.name = %%(taxonomy)s)
          AND (STRPOS(tag_name, '::') != 0)
        UNION ALL
        SELECT
          domain_id,
          '' AS category
        FROM %s AS tag_table -- base_table
        JOIN tags USING (tag_id)
        JOIN taxonomy ON (tags.taxonomy_id = taxonomy.id)
        WHERE
          (taxonomy.name = %%(taxonomy)s)
          AND (STRPOS(tag_name, '::') = 0)
      )
      SELECT
        category,
        COUNT(*) AS count
      FROM (
        SELECT DISTINCT ON (domain_id, category) category FROM t
      ) AS subquery
      GROUP BY category
      ORDER BY count DESC
      LIMIT %%(limit)s
        OFFSET %%(offset)s""" % (base_table, base_table)
    params = {
        'taxonomy': taxonomy,
        'at_time': at_time,
        'limit': limit,
        'offset': offset
    }
    params.update(base_table_params)
    rows = execute_db(SQL, params, dict_=True)
    return rows


@router.get(
    "/tags",
    response_model=List[StatsTagsResponse],
    name="Stats of tags",
    summary="Show stats on tags in a taxonomy, optionally filtered by category"
)
def get_stats_bycategory(
    taxonomy: str,
    category: Optional[str] = None,
    at_time: datetime.datetime = None,
    filter: str = Query(None, regex=RE_FILTER),
    limit: int = config['default_limit'],
    offset: int = config['default_offset']
):
    """ Returns stats on all tags that are within a taxonomy, optionally
    filtered by categories.

    A filter is a string of the form Tag=Value. The available tags and values
    can be fetched using the /api/v1/filters/types and /api/v1/filters/values
    endpoints, respectively.

    **GET Parameters:**
    | parameter          | description                                                                                                          |
    | ------------------ | -------------------------------------------------------------------------------------------------------------------- |
    | taxonomy           | taxonomy to calculate stats for                                                                                      |
    | category           | filter for this category. If not given all tags in taxonomy are returned. Set empty string for tags in root category |
    | at_time            | point in time to query                                                                                               |
    | filter             | filter domains by entries in the filter table before counting                                                        |
    | limit              | limit answer to {limit} entries                                                                                      |
    | offset             | start answer at the {offset}-th entry                                                                                |

    **Output (JSON):**
    JSON list of objects, ordered by count, descending. Each object has the following keys:
    | key                | description                                                                     |
    | ------------------ | ------------------------------------------------------------------------------- |
    | tag_name           | name of the tag                                                                 |
    | count              | number of domains labeled by this tag in taxonomy {taxonomy}                    |
    """
    base_table, base_table_params = get_sql_base_table(at_time, filter)

    if category is not None:
        category_clause = """
          (
            ( -- tags with a category
              (STRPOS(tag_name, '::') != 0)
              AND (
                (REGEXP_REPLACE(tag_name, '^(.+)::.+$', '\\1')) = %(category)s
              )
            )
            OR
            ( -- tags without a category
              (STRPOS(tag_name, '::') = 0)
              AND (%(category)s = '')
            )
          )
        """
    else:
        category_clause = "TRUE"

    SQL = """
      SELECT
        tag_name,
          COUNT(DISTINCT domain_id) AS count
        FROM %s AS tag_table -- base_table
        JOIN tags USING (tag_id)
        JOIN taxonomy ON (tags.taxonomy_id = taxonomy.id)
      WHERE
        (taxonomy.name = %%(taxonomy)s)
        AND (%s) -- category clause
      GROUP BY tag_id, tag_name
      ORDER BY count DESC
      """ % (base_table, category_clause)
    params = {
        'taxonomy': taxonomy,
        'category': category,
        'at_time': at_time,
        'limit': limit,
        'offset': offset
    }
    params.update(base_table_params)
    rows = execute_db(SQL, params, dict_=True)
    return rows


@router.get(
    "/values",
    response_model=List[StatsValuesResponse],
    name="Stats on values",
    summary="Show stats on values associated with a tag"
)
def get_stats_values(
    taxonomy: str,
    tag: str,
    at_time: datetime.datetime = None,
    filter: str = Query(None, regex=RE_FILTER),
    limit: int = config['default_limit'],
    offset: int = config['default_offset']
):
    """ Returns stats on the values associated with a tag in a taxonomy.

    A filter is a string of the form Tag=Value. The available tags and values
    can be fetched using the /api/v1/filters/types and /api/v1/filters/values
    endpoints, respectively.

    **GET Parameters:**
      | parameter                   | description                                                                     |
      | --------------------------- | ------------------------------------------------------------------------------- |
      | taxonomy                    | name of taxonomy the tag to be looked up belongs to                             |
      | tag                         | name of the tag to be looked up                                                 |
      | at_time                     | point in time to query                                                          |
      | filter                      | filter domains by entries in the filter table before counting                   |
      | limit                       | limit answer to {limit} entries                                                 |
      | offset                      | start answer at the {offset}-th entry                                           |

    **Output (JSON):**
    JSON list of objects, ordered by count, descending. Each object has the following keys:
      | key                         | description                                                                     |
      | --------------------------- | ------------------------------------------------------------------------------- |
      | value                       | value                                                                           |
      | count                       | number of domains labeled by value and tag {tag}                                |
    """
    base_table, base_table_params = get_sql_base_table(at_time, filter)

    SQL = """
      SELECT
        value,
        COUNT(domain_id) AS count
      FROM (
        SELECT DISTINCT
          domain_id, value
        FROM %s AS tag_table -- base_table
        JOIN tags USING (tag_id)
        JOIN taxonomy ON (tags.taxonomy_id = taxonomy.id)
        JOIN taxonomy_tag_val ON (tag_table.value_id = taxonomy_tag_val.id)
        WHERE
          (taxonomy.name = %%(taxonomy)s)
          AND (tag_name = %%(tag)s)
      ) AS t
      GROUP BY value
      ORDER BY count DESC
    """ % base_table
    params = {
        'taxonomy': taxonomy,
        'tag': tag,
        'at_time': at_time,
        'limit': limit,
        'offset': offset
    }
    params.update(base_table_params)
    rows = execute_db(SQL, params, dict_=True)
    return rows
