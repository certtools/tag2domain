import logging

from fastapi import APIRouter

from tag2domain_api.app.util.config import config

logger = logging.getLogger(__name__)

router = APIRouter()

HELPSTR = """
# About

This app provides a simple RESTful API for the tag2domain DB.
Please see %s

Example:
```
  GET /api/v1/tags/all?limit=1000&offset=1000
```
Will return all results of the tags table starting at offset 1000 and only send
back 1000 results. The default value for limit is 1000.

  Error codes:
      HTTP 200        --> OK
      HTTP 204        --> OK but no results
      HTTP 401        --> not authorized
      HTTP 408        --> timeout
      HTTP 404        --> invalid endpoint or request
      HTTP 500        --> internal server error
""" % (config['baseurl'],)


@router.get('/')
async def help():
    return {'help': HELPSTR}
