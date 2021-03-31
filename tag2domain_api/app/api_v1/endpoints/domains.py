import time
import datetime
import logging

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from fastapi.responses import ORJSONResponse

from tag2domain_api.app.util.models import (
    DomainsResponse,
    DomainsWithTagsResponse,
    VersionComparisonOperatorParameter,
    DomainsResponseWithVersion
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
    "/bytag",
    response_model=List[DomainsResponse],
    name="domains_by_tags",
    summary="Show all domains which are tagged by {tag}"
)
def get_domains_by_tag(
    tag: str,
    at_time: datetime.datetime = None,
    filter_by_value: Optional[bool] = False,
    value: Optional[str] = None,
    filter: str = Query(None, regex=RE_FILTER),
    limit: int = config['default_limit'],
    offset: int = config['default_offset']
):
    """ Returns all domains of a given {tag}

    A filter is a string of the form Tag=Value. The available tags and values
    can be fetched using the /api/v1/filters/types and /api/v1/filters/values
    endpoints, respectively.

    **GET Parameters:**
      * tag ... the tag name to query (required)
      * at_time .. reference time to look at. If empty, open tags are returned.
            (YYYY-MM-DDTHH:mm:ss)
      * limit .... how many entries should we return?
      * offset.... starting at {offset}

    **Output (JSON):**
      * domain name... string
      * domain_id ... ID of the domain
      * tag_id... int
      * tag_name ... name of the tag
      :type tag: str
    """
    base_table, base_table_params = get_sql_base_table(at_time, filter)
    parameters = {
        "tag_name": tag,
        "limit": limit,
        "offset": offset,
        "at_time": at_time,
        "value": value
    }
    parameters.update(base_table_params)

    whereclause_list = ["(tag_name = %(tag_name)s)", ]
    if filter_by_value:
        if value is None:
            whereclause_list.append("(value IS NULL)")
        elif isinstance(value, str):
            whereclause_list.append("(value = %(value)s)")
        else:
            raise ValueError(
                "expected value to be str, got '%s'" % str(type(value))
            )

    whereclause = ' AND '.join(whereclause_list)

    SQL = (
        """
        SELECT
            domain_id,
            domain_name,
            tag_type,
            value,
            start_time,
            measured_at,
            end_time
        FROM %s AS tag_table -- base_table
        JOIN tags USING (tag_id)
        LEFT JOIN taxonomy_tag_val ON (tag_table.value_id = taxonomy_tag_val.id)
        WHERE (%s) -- whereclause
        ORDER BY domain_id, tag_table.tag_id ASC
        LIMIT %%(limit)s OFFSET %%(offset)s""" % (
            base_table,
            whereclause
        )
    )
    rows = execute_db(SQL, parameters, dict_=True)
    return rows


@router.get(
    "/bytaxonomy",
    response_model=List[DomainsWithTagsResponse],
    name="domains_by_taxonomy",
    summary="Show all domains which are classified by {taxonomy} and their tags"
)
def get_domains_by_taxonomy(
    taxonomy: str,
    at_time: datetime.datetime = None,
    filter: str = Query(None, regex=RE_FILTER),
    limit: int = config['default_limit'],
    offset: int = config['default_offset']
):
    """ Returns all domains of a given {taxonomy}

    A filter is a string of the form Tag=Value. The available tags and values
    can be fetched using the /api/v1/filters/types and /api/v1/filters/values
    endpoints, respectively.

    **GET Parameters:**
      * taxonomy ... the taxonomy name to query (required)
      * at_time .. reference time to look at. If empty, open tags are returned.
            (YYYY-MM-DDTHH:mm:ss)
      * limit .... how many entries should we return?
      * offset.... starting at {offset}

    **Output (JSON):**
      * domain name... string
      * domain_id ... ID of the domain
      * taxonomy_id... int
      * taxonomy_name ... name of the taxonomy
      :type taxonomy: str
    """
    parameters = {
        "taxonomy_name": taxonomy,
        "limit": limit,
        "offset": offset,
        "at_time": at_time
    }
    base_table, base_table_params = get_sql_base_table(at_time, filter)
    parameters.update(base_table_params)

    whereclause = "(taxonomy.name = %(taxonomy_name)s)"
    SQL = (
        """
        SELECT
            domain_id,
            domain_name,
            tag_id,
            tag_name,
            start_time,
            measured_at,
            end_time
        FROM %s AS tag_table -- base_table
        JOIN tags USING(tag_id)
        JOIN taxonomy ON (tags.taxonomy_id = taxonomy.id)
        WHERE (%s) -- whereclause
        ORDER BY domain_id, tag_id asc, tag_type
        LIMIT %%(limit)s OFFSET %%(offset)s""" % (
            base_table,
            whereclause
        )
    )
    start = time.time()
    rows = execute_db(SQL, parameters, dict_=True)

    start = time.time()
    ret = []
    cur_domain = None
    for row in rows:
        if cur_domain is None or row["domain_id"] != cur_domain["domain_id"]:
            if cur_domain is not None:
                ret.append(cur_domain)
            cur_domain = {
                "domain_id": row["domain_id"],
                "domain_name": row["domain_name"],
                "tags": []
            }
        cur_domain["tags"].append({
            "tag_id": row["tag_id"],
            "tag_name": row["tag_name"],
            "start_time": row["start_time"],
            "measured_at": row["measured_at"],
            "end_time": row["end_time"]
        })
    if cur_domain is not None:
        ret.append(cur_domain)
    logger.debug("reshuffled results in %f s", time.time() - start)

    logger.debug("preparing response...")
    start = time.time()
    response = ORJSONResponse(content=ret)
    logger.debug("response prepared in %f s", time.time() - start)
    return response


@router.get(
    "/bycategory",
    response_model=List[DomainsWithTagsResponse],
    name="domains_by_taxonomy",
    summary="Show all domains which are classified by {taxonomy} and their tags"
)
def get_domains_by_category(
    taxonomy: str,
    category: Optional[str] = '',
    at_time: datetime.datetime = None,
    filter: str = Query(None, regex=RE_FILTER),
    limit: int = config['default_limit'],
    offset: int = config['default_offset']
):
    """ Returns all domains of a given {taxonomy}

    A filter is a string of the form Tag=Value. The available tags and values
    can be fetched using the /api/v1/filters/types and /api/v1/filters/values
    endpoints, respectively.

    **GET Parameters:**
      * taxonomy ... the taxonomy name to query (required)
      * at_time .. reference time to look at. If empty, open tags are returned.
            (YYYY-MM-DDTHH:mm:ss)
      * limit .... how many entries should we return?
      * offset.... starting at {offset}

    **Output (JSON):**
      * domain name... string
      * domain_id ... ID of the domain
      * taxonomy_id... int
      * taxonomy_name ... name of the taxonomy
      :type taxonomy: str
    """
    parameters = {
        "taxonomy_name": taxonomy,
        "category": category,
        "limit": limit,
        "offset": offset,
        "at_time": at_time
    }
    base_table, base_table_params = get_sql_base_table(at_time, filter)
    parameters.update(base_table_params)

    SQL = """SELECT
                domain_id,
                domain_name,
                tag_id,
                tag_name,
                start_time,
                measured_at,
                end_time
             FROM %s AS tag_table -- base_table
             JOIN tags USING (tag_id)
             JOIN taxonomy ON (tags.taxonomy_id = taxonomy.id)
             WHERE
              (taxonomy.name = %%(taxonomy_name)s)
              AND
              (
                ( -- tags with a category
                  (STRPOS(tag_name, '::') != 0)
                  AND (
                  (REGEXP_REPLACE(tag_name, '^(.+)::.+$', '\\1')) = %%(category)s)
                )
                OR
                ( -- tags without a category
                  (STRPOS(tag_name, '::') = 0)
                  AND (%%(category)s = '')
                )
              )
             ORDER BY domain_id, tag_id asc
             LIMIT %%(limit)s OFFSET %%(offset)s""" % base_table

    rows = execute_db(SQL, parameters, dict_=True)

    start = time.time()
    ret = []
    cur_domain = None
    for row in rows:
        if cur_domain is None or row["domain_id"] != cur_domain["domain_id"]:
            if cur_domain is not None:
                ret.append(cur_domain)
            cur_domain = {
                "domain_id": row["domain_id"],
                "domain_name": row["domain_name"],
                "tags": []
            }
        cur_domain["tags"].append({
            "tag_id": row["tag_id"],
            "tag_name": row["tag_name"],
            "start_time": row["start_time"],
            "measured_at": row["measured_at"],
            "end_time": row["end_time"]
        })
    if cur_domain is not None:
        ret.append(cur_domain)
    logger.debug("reshuffled results in %f s", time.time() - start)

    logger.debug("preparing response...")
    start = time.time()
    response = ORJSONResponse(content=ret)
    logger.debug("response prepared in %f s", time.time() - start)

    return response


@router.get(
    "/byversion",
    response_model=List[DomainsResponseWithVersion],
    name="domains_by_tags",
    summary="Show all domains which are tagged by {tag}"
)
def get_domains_by_version(
    taxonomy: str,
    tag: str,
    version: Optional[str] = Query(
        None,
        regex="^(?:[0-9]+)(?:\.[0-9]+)*$"  # noqa: W605
    ),
    operator: VersionComparisonOperatorParameter = "=",
    at_time: datetime.datetime = None,
    filter: str = Query(None, regex=RE_FILTER),
    limit: int = config['default_limit'],
    offset: int = config['default_offset']
):
    """ Return domains by the version of the tag {tag} in taxonomy {taxonomy}.

    Only tags with a value that looks like a version number (e.g. 1.2.3.4) will
    be returned. Versioning schemes with letters are not considered.

    A filter is a string of the form Tag=Value. The available tags and values
    can be fetched using the /api/v1/filters/types and /api/v1/filters/values
    endpoints, respectively.

    **GET Parameters:**
      | parameter         | description                                                                      |
      | ----------------- | -------------------------------------------------------------------------------- |
      | taxonomy          | taxonomy to query from                                                           |
      | tag               | tag to query from                                                                |
      | version           | version to compare to. Must be in format 1.2.3.4 ... or null                     |
      | operator          | operator used to compare version strings. One of =, <, <=, >, >=                 |
      | at_time           | point in time to query                                                           |
      | filter            | filter domains by entries in the filter table before counting                    |
      | limit             | limit answer to {limit} entries                                                  |
      | offset            | start answer at the {offset}-th entry                                            |

    **Output (JSON):**
    JSON list of objects, ordered by count, descending. Each object has the following keys:
      | key             | description                                                                     |
      | ----------------| ------------------------------------------------------------------------------- |
      | domain_id       | ID of the found domain                                                          |
      | domain_name     | name of the found domain                                                        |
      | version         | version found in the value field                                                |
      | start_time      | start time of the tag                                                           |
      | measured_at     | time of last measurement of the tag                                             |
      | end_time        | end time of the tag                                                             |

    """
    if version is None and operator != VersionComparisonOperatorParameter.equal:
        raise HTTPException(
            status_code=400,
            detail="null tags can only be searched with operator '='"
        )

    parameters = {
        "taxonomy": taxonomy,
        "tag_name": tag,
        "version": version,
        "limit": limit,
        "offset": offset,
        "at_time": at_time
    }
    base_table, base_table_params = get_sql_base_table(at_time, filter)
    parameters.update(base_table_params)

    if version is None:
        value_clause = "(value IS NULL)"
    else:
        if operator == VersionComparisonOperatorParameter.equal:
            op = "="
        elif operator == VersionComparisonOperatorParameter.lessthan:
            op = "<"
        elif operator == VersionComparisonOperatorParameter.lessthanequal:
            op = "<="
        elif operator == VersionComparisonOperatorParameter.greaterthan:
            op = ">"
        elif operator == VersionComparisonOperatorParameter.greaterthanequal:
            op = ">="
        else:
            raise HTTPException(status_code=400, detail="invalid operator")

        if op == "=":
            value_clause = "(value = %(version)s)"
        else:
            value_clause = (
                "(value ~ '^(?:[0-9]+)(?:\.[0-9]+)*$')"  # noqa: W605
                " AND (string_to_array(value, '.')::bigint[] %s "
                "string_to_array(%%(version)s, '.')::bigint[])" % op
            )

    SQL = """
      SELECT
          domain_id,
          domain_name,
          start_time,
          measured_at,
          end_time,
          value AS version
      FROM %s AS tag_table -- base_table
      JOIN tags USING (tag_id)
      JOIN taxonomy ON (tags.taxonomy_id = taxonomy.id)
      LEFT JOIN taxonomy_tag_val ON (tag_table.value_id = taxonomy_tag_val.id)
      WHERE
          (taxonomy.name = %%(taxonomy)s)
          AND (tag_name = %%(tag_name)s)
          AND (%s) -- value_clause
      ORDER BY domain_id, tag_table.tag_id ASC
      LIMIT %%(limit)s
      OFFSET %%(offset)s
    """ % (base_table, value_clause)
    rows = execute_db(SQL, parameters, dict_=True)
    return rows
