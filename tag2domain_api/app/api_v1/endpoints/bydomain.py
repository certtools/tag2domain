import datetime
import logging

from fastapi import APIRouter
from typing import List

from tag2domain_api.app.util.models import TagsOfDomainsResponse
from tag2domain_api.app.util.config import config
from tag2domain_api.app.util.db import execute_db, get_sql_base_table

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{domain}",
    response_model=List[TagsOfDomainsResponse],
    name="taxonomies_by_domain",
    summary="Show all open tags of a given domain at a single point in time"
)
def get_tags_by_domain(
    domain: str,
    at_time: datetime.datetime = None,
    limit: int = config['default_limit'],
    offset: int = config['default_offset']
):
    """ Returns all taxonomies and tags of a given {domain}

    **GET Parameters:**
      * domain ... the domain name to query (required)
      * at_time .. reference time to look at. If empty, open tags are returned.
            (YYYY-MM-DDTHH:mm:ss)
      * limit .... how many entries should we return?
      * offset.... starting at {offset}

    **Output (JSON):**
      * domain name... string
      * domain_id ... ID of the domain
      * tag_id... int
      * tag_name ... name of the tag
      * taxonomy_id ... int
      * taxonomy_name ... name of the linked taxonomy
    """
    parameters = {
        "domain": domain,
        "limit": limit,
        "offset": offset,
        "at_time": at_time
    }
    base_table, base_table_params = get_sql_base_table(at_time, domain=domain)
    parameters.update(base_table_params)

    SQL = """
            SELECT
              taxonomy_id,
              taxonomy.name AS taxonomy_name,
              tag_table.tag_id,
              tag_name,
              value_id,
              value,
              start_time,
              measured_at,
            end_time
            FROM %s AS tag_table -- base_table
            JOIN tags USING (tag_id)
            JOIN taxonomy ON (tags.taxonomy_id = taxonomy.id)
            LEFT JOIN taxonomy_tag_val ON (tag_table.value_id = taxonomy_tag_val.id)
            ORDER BY domain_id, tag_table.tag_id asc
            LIMIT %%(limit)s OFFSET %%(offset)s""" % (base_table)
    rows = execute_db(SQL, parameters, dict_=True)
    return rows


@router.get(
    "/{domain}/history",
    response_model=List[TagsOfDomainsResponse],
    name="taxonomies_by_domain",
    summary="Return the tag history of a domain"
)
def get_tag_history_by_domain(
    domain: str,
    limit: int = config['default_limit'],
    offset: int = config['default_offset']
):
    """ Returns the tag history of a single domain.

    **GET Parameters:**
      * domain ... the domain name to query (required)
      * limit .... how many entries should we return?
      * offset.... starting at {offset}

    **Output (JSON):**
      * domain name... string
      * domain_id ... ID of the domain
      * tag_id... int
      * tag_name ... name of the tag
      * value_id ... ID of the value associated with the tag
      * value ... value associated with the tag
      * taxonomy_id ... int
      * taxonomy_name ... name of the linked taxonomy
    """
    parameters = {
        "domain": domain,
        "limit": limit,
        "offset": offset
    }

    SQL = """
      SELECT
         taxonomy_id,
         taxonomy.name AS taxonomy_name,
         tag_table.tag_id,
         tag_name,
         value_id,
         value,
         start_time,
         measured_at,
         end_time
      FROM tag2domain_get_all_tags_domain(%(domain)s) AS tag_table
      JOIN tags USING (tag_id)
      JOIN taxonomy ON (tags.taxonomy_id = taxonomy.id)
      LEFT JOIN taxonomy_tag_val ON (tag_table.value_id = taxonomy_tag_val.id)
      ORDER BY domain_id, tag_id ASC
      LIMIT %(limit)s OFFSET %(offset)s
    """
    rows = execute_db(SQL, parameters, dict_=True)
    return rows
