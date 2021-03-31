import logging

from fastapi import APIRouter
from typing import List

from tag2domain_api.app.util.db import execute_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/types",
    response_model=List[str],
    name="Filter types",
    summary="Show all available filter types"
)
def get_types():
    """ Returns filter categories defined in the filter table.

    **Output (JSON list):**
        str - name of filter
    """
    rows = execute_db("""
        SELECT DISTINCT ON (tag_name)
            tag_name
        FROM v_tag2domain_domain_filter
        ORDER BY tag_name
    """, ())
    return [name for name, in rows]


@router.get(
    "/values",
    response_model=List[str],
    name="Filter values",
    summary="Show all values found for a given filter"
)
def get_values(filter: str):
    """ Returns filter values found in the filter table.

    **Output (JSON list):**
        str - value
    """
    rows = execute_db(
        """
        SELECT DISTINCT ON (value)
            value
        FROM v_tag2domain_domain_filter
        WHERE (tag_name = %s) AND (value IS NOT NULL)
        ORDER BY value
        """,
        (filter, )
    )

    return [name for name, in rows]
