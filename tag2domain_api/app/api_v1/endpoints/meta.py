import logging

from fastapi import APIRouter, HTTPException
from typing import List, Optional

from tag2domain_api.app.util.models import (
    TaxonomiesResponse,
    TagsResponse,
    ValuesResponse,
    TagInfoResponse,
    ErrorMessage
)
from tag2domain_api.app.util.config import config
from tag2domain_api.app.util.db import execute_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/taxonomies",
    response_model=List[TaxonomiesResponse],
    name="Taxonomies",
    summary="Show all taxonomies"
)
def get_taxonomies(
    limit: int = config['default_limit'],
    offset: int = config['default_offset']
):
    """ Returns all known taxonomies.

    **GET Parameters:**
      * limit .... how many entries should we return?
      * offset.... starting at {offset}

    **Output (JSON):**
      * id... integer
      * name ... name of the tag
      * description ... long description
      * is_actionable ... value between 0 and 1 on how actionable this is on
            data (can we automatically do an action based on the tag?)
      * is_automatically_classifiable... bool. Can we automatically tag a
            domain based on this taxonomy?
      * is_stable... bool. Does this taxonomy change a lot?
      * allows_auto_tags... bool. If a new tag appears, may it be automatically
            added to the taxonomy?
      * allows_auto_values... bool. If a new tag appears, may it be
            automatically added to the taxonomy?
      * for_numbers... bool. Is this taxonomy meant for numbers (IP addresses)?
      * for_domains... bool. Same but is it meant for domains?
      * url ... string. URL to further documentation.
    """
    SQL = """SELECT
                id,
                name,
                description,
                is_actionable,
                is_automatically_classifiable,
                is_stable,allows_auto_tags,
                for_numbers,
                for_domains,
                url
             FROM taxonomy ORDER BY id asc LIMIT %s OFFSET %s"""
    rows = execute_db(SQL, (limit, offset), dict_=True)
    return rows


@router.get(
    "/tags",
    response_model=List[TagsResponse],
    summary="Show all tags"
)
def get_tags(
    taxonomy: str = None,
    category: str = None,
    limit: int = config['default_limit'],
    offset: int = config['default_offset']
):
    """ Returns all known tags.

    **GET Parameters:**
      * limit .... how many entries should we return?
      * offset.... starting at {offset}

    **Output (JSON):**
      * tag_id... integer
      * tag_name ... name of the tag
      * tag_description ... long description
      * taxonomy_id ... id of the linked taxonomy
      * extras... JSON dict of potential extra information
    """
    params = {
        'taxonomy': taxonomy,
        'category': category,
        'limit': limit,
        'offset': offset
    }

    if taxonomy is not None:
        taxonomy_where_clause = "(taxonomy.name = %(taxonomy)s)"
    else:
        taxonomy_where_clause = "True"

    if category is not None:
        if taxonomy is None:
            raise HTTPException(
                status_code=400,
                detail="querying category tags requires taxonomy to be set"
            )

        if category == "":
            category_where_clause = "(STRPOS(tag_name, '::') = 0)"
        else:
            category_where_clause = (
                "(STRPOS(tag_name, '::') != 0) "
                "AND ("
                "(REGEXP_REPLACE(tag_name,'^(.+)::.+$', '\\1')) = %(category)s"
                ")"
            )
    else:
        category_where_clause = "True"

    SQL = """
      SELECT tag_id,tag_name,tag_description,taxonomy_id,extras
      FROM tags
      JOIN taxonomy ON (tags.taxonomy_id = taxonomy.id)
      WHERE ( %s ) AND ( %s ) -- taxonomy_where_clause, category_where_clause
      ORDER BY tag_id ASC
      LIMIT %%(limit)s
      OFFSET %%(offset)s
    """ % (taxonomy_where_clause, category_where_clause)
    rows = execute_db(SQL, params, dict_=True)
    return rows


@router.get(
    "/categories",
    response_model=List[str],
    summary="Show all categories, optionally filtered by taxonomy"
)
def get_categories(
    taxonomy: Optional[str] = None,
    limit: int = config['default_limit'],
    offset: int = config['default_offset']
):
    """ Returns all categories optionally filtered by taxonomy.

    **GET Parameters:**
      * limit ....... how many entries should we return?
      * offset....... starting at {offset}
      * taxonomy_id.. ID of the taxonomy to be looked up

    **Output (JSON List):**
      * category_name (string)
    """
    params = {
        'limit': limit,
        'offset': offset,
        'taxonomy': taxonomy
    }
    if taxonomy is None:
        taxonomy_clause = "TRUE"
    else:
        taxonomy_clause = "(taxonomy.name = %(taxonomy)s)"

    SQL = """
      SELECT DISTINCT ON (category)
        (REGEXP_REPLACE(tag_name, '^(.+)::.+$', '\\1')) AS category
      FROM tags
      JOIN taxonomy ON (tags.taxonomy_id = taxonomy.id)
      WHERE STRPOS(tag_name, '::') != 0 AND {0}
      UNION ALL
      SELECT
        category
      FROM (
        SELECT
          '' AS category
          FROM tags
          JOIN taxonomy ON (tags.taxonomy_id = taxonomy.id)
          WHERE
            STRPOS(tag_name, '::') = 0 AND {0}
          LIMIT 1
      ) AS t
      LIMIT %(limit)s
      OFFSET %(offset)s
    """.format(taxonomy_clause)
    rows = execute_db(SQL, params, dict_=False)
    return [_elem[0] for _elem in rows]


@router.get(
    "/values",
    response_model=List[ValuesResponse],
    summary="Show all values filtered by taxonomy and tag"
)
def get_values(
    taxonomy: str,
    tag: str,
    limit: int = config['default_limit'],
    offset: int = config['default_offset']
):
    """ Returns all categories optionally filtered by taxonomy.

    **GET Parameters:**
      * limit ....... how many entries should we return?
      * offset....... starting at {offset}
      * taxonomy_id.. ID of the taxonomy to be looked up

    **Output (JSON List):**
      * category_name (string)
    """
    params = {
        'tag': tag,
        'taxonomy': taxonomy,
        'limit': limit,
        'offset': offset
    }

    SQL = """
      SELECT DISTINCT
        taxonomy_tag_val.id AS value_id, taxonomy_tag_val.value AS value
      FROM taxonomy_tag_val
      JOIN tags USING (tag_id)
      JOIN taxonomy ON (tags.taxonomy_id = taxonomy.id)
      WHERE (taxonomy.name = %(taxonomy)s) AND (tags.tag_name = %(tag)s)
      LIMIT %(limit)s
      OFFSET %(offset)s
    """
    rows = execute_db(SQL, params, dict_=True)
    return rows


@router.get(
    "/tag",
    response_model=TagInfoResponse,
    summary="Return information about a tag",
    responses={
        404: {
            "model": ErrorMessage,
            "description": "The tag was not found"
        }
    }
)
def get_tag_info(
    taxonomy: str,
    tag: str,
):
    """ Returns information about a single tag.

    **GET Parameters:**
    + taxonomy - name of the taxonomy the tag is in
    + tag - name of the tag to be fetched

    **Output (JSON Object):**
    + tag
      + name
      + description
      + category
      + extras
    + taxonomy
      + name
      + description
      + url
      + flags
        + is_actionable
        + is_automatically_classifiable
        + is_stable
        + for_numbers
        + for_domains
        + allows_auto_tags
        + allows_auto_values
    + values
      + count - number of distinct values that are associated with the tag

    See the [tag2domain docs](https://docu.labs.nic.at/doku.php?id=rd:topics:tag2domain:konzept)
    for further information about the fields.

    """
    params = {
        'tag': tag,
        'taxonomy': taxonomy
    }

    SQL = """
      SELECT
        tags.tag_name AS tag_name,
        tags.tag_description AS tag_description,
        REGEXP_REPLACE(tags.tag_name, '^(.+)::.+$', '\\1') AS tag_category,
        tags.extras AS tag_extras,
        taxonomy.name AS taxonomy_name,
        taxonomy.description AS taxonomy_description,
        taxonomy.url AS taxonomy_url,
        taxonomy.is_actionable AS taxonomy_flags_is_actionable,
        taxonomy.is_automatically_classifiable AS taxonomy_flags_is_automatically_classifiable,
        taxonomy.is_stable AS taxonomy_flags_is_stable,
        taxonomy.for_numbers AS taxonomy_flags_for_numbers,
        taxonomy.for_domains AS taxonomy_flags_for_domains,
        taxonomy.allows_auto_tags AS taxonomy_flags_allows_auto_tags,
        taxonomy.allows_auto_values AS taxonomy_flags_allows_auto_values,
        COUNT(DISTINCT taxonomy_tag_val.id) AS values_count
      FROM tags
      JOIN taxonomy ON (taxonomy.id = tags.taxonomy_id)
      LEFT JOIN taxonomy_tag_val ON (taxonomy_tag_val.tag_id = tags.tag_id)
      WHERE
        tags.tag_name = %(tag)s
        AND taxonomy.name = %(taxonomy)s
        AND (STRPOS(tag_name, '::') != 0)
      GROUP BY
      tags.tag_name, tags.tag_description, tags.extras,
      taxonomy.name, taxonomy.description, taxonomy.description,
      taxonomy.url, taxonomy.is_actionable, taxonomy.is_automatically_classifiable,
      taxonomy.is_stable, taxonomy.for_numbers, taxonomy.for_domains,
      taxonomy.allows_auto_tags, taxonomy.allows_auto_values
      UNION ALL
      SELECT
        tags.tag_name AS tag_name,
        tags.tag_description AS tag_description,
        NULL AS tag_category,
        tags.extras AS tag_extras,
        taxonomy.name AS taxonomy_name,
        taxonomy.description AS taxonomy_description,
        taxonomy.url AS taxonomy_url,
        taxonomy.is_actionable AS taxonomy_flags_is_actionable,
        taxonomy.is_automatically_classifiable AS taxonomy_flags_is_automatically_classifiable,
        taxonomy.is_stable AS taxonomy_flags_is_stable,
        taxonomy.for_numbers AS taxonomy_flags_for_numbers,
        taxonomy.for_domains AS taxonomy_flags_for_domains,
        taxonomy.allows_auto_tags AS taxonomy_flags_allows_auto_tags,
        taxonomy.allows_auto_values AS taxonomy_flags_allows_auto_values,
        COUNT(DISTINCT taxonomy_tag_val.id) AS values_count
      FROM tags
      JOIN taxonomy ON (taxonomy.id = tags.taxonomy_id)
      LEFT JOIN taxonomy_tag_val ON (taxonomy_tag_val.tag_id = tags.tag_id)
      WHERE
        tags.tag_name = %(tag)s
        AND taxonomy.name = %(taxonomy)s
        AND (STRPOS(tag_name, '::') = 0)
      GROUP BY
      tags.tag_name, tags.tag_description, tags.extras,
      taxonomy.name, taxonomy.description, taxonomy.description,
      taxonomy.url, taxonomy.is_actionable, taxonomy.is_automatically_classifiable,
      taxonomy.is_stable, taxonomy.for_numbers, taxonomy.for_domains,
      taxonomy.allows_auto_tags, taxonomy.allows_auto_values
    ;
    """
    rows = execute_db(SQL, params, dict_=True)

    if len(rows) == 0:
        raise HTTPException(
            status_code=404,
            detail="no tag '%s' in taxonomy '%s' found" % (tag, taxonomy)
        )
    elif len(rows) > 1:
        raise HTTPException(status_code=500, detail="more than 1 tag found")

    row, = rows

    ret = {
        'tag': {
            'name': row['tag_name'],
            'description': row['tag_description'],
            'category': row['tag_category'],
            'extras': row['tag_extras'],
        },
        'taxonomy': {
            'name': row['taxonomy_name'],
            'description': row['taxonomy_description'],
            'url': row['taxonomy_url'],
            'flags': {
                'is_actionable': row['taxonomy_flags_is_actionable'],
                'is_automatically_classifiable': row['taxonomy_flags_is_automatically_classifiable'],
                'is_stable': row['taxonomy_flags_is_actionable'],
                'for_numbers': row['taxonomy_flags_for_numbers'],
                'for_domains': row['taxonomy_flags_for_domains'],
                'allows_auto_tags': row['taxonomy_flags_allows_auto_tags'],
                'allows_auto_values': row['taxonomy_flags_allows_auto_values']
            }
        },
        'values': {
            'count': row["values_count"]
        }
    }

    return ret
