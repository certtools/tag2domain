#!/usr/bin/env python3

import time
import logging

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.security.api_key import APIKeyHeader, APIKey

from enum import Enum

from typing import List
import datetime

# Starlette
# from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN


#from nicat_microservice import metadata
import psycopg2
import psycopg2.extras
# from psycopg2 import sql
from config import config
from misc import  send_email_api_key
# from admin import * # XXX FIXME
from models import *



###############################################################################
# Global vars
debug = config['debug']
version = config['version']
description = """
## A RESTful API for querying the tag2domain DB.

You can query the database of mappings of domains to tags.
See [docuwiki](https://docu.labs.nic.at/doku.php?id=cef5:tag2domain) (as a nic.at employee)
or [github](https://github.com/certtools/tag2domain) (the public repository)

Author: Aaron Kaplan <[kaplan@nic.at](kaplan@nic.at)>

**Copyright** 2020 (C) nic.at GmbH, all rights reserved.

**License**: GNU Affero General Public License v3.0. See the LICENSE file for details

"""
baseurl = config['baseurl']
db_conn = None
app = FastAPI(title="tag2domain API", version=version, description=description)
security = HTTPBasic()


###############################################################################
# API key stuff
API_KEYLEN = 32
API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)



HELPSTR = """
# About

This app provides a simple RESTful API for the tag2domain DB.
Please see %s

Example:
```
  GET /api/v1/tags/all?limit=1000&offset=1000
```
Will return all results of the tags table starting at offset 1000 and only send back 1000 results.
The default value for limit is 1000.


  Error codes:
      HTTP 200        --> OK
      HTTP 204        --> OK but no results
      HTTP 401        --> not authorized
      HTTP 408        --> timeout
      HTTP 404        --> invalid endpoint or request
      HTTP 500        --> internal server error
""" % (baseurl,)



#############
# DB specific functions
@app.on_event('startup')
def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.  
    :rtype: psycopg2 connection"""
    global db_conn
    global valid_api_keys

    logging.info('starting up....')
    db_conn = connect_db()
    logging.debug("type(db) = %s . db = %s" % (type(db_conn), db_conn))

    valid_api_keys = fetch_valid_api_keys()

    return db_conn


@app.on_event('shutdown')
def close_db():
    """Closes the database again at the end of the request."""
    global db_conn

    logging.info('shutting down....')
    if db_conn:
        db_conn.close()
        db_conn = None


def connect_db():
    """Connects to the specific database.
    :rtype: psycopg2 connection"""
    try:
        conn = psycopg2.connect(dbname=config['DATABASE'], user=config['USERNAME'], password=config['PASSWORD'],
                                host=config['DBHOST'], port=config['DBPORT'])
    except Exception as ex:
        time.sleep(2)       # process would die and get respawned constantly otherwise
        raise HTTPException(status_code=500, detail="could not connect to the DB. Reason: %s" % (str(ex)))
    logging.info("connection to DB established")
    return conn


def fetch_valid_api_keys():
    global db_conn
    cur = None

    SQL = """SELECT api_key FROM api_keys WHERE (expires IS NULL or expires >= now())"""

    try:
        cur = db_conn.cursor()
    except (psycopg2.InterfaceError, psycopg2.errors.AdminShutdown) as ex:
        # need to re-connect to the DB
        logging.warning("need to re-establish the connection to the DB. Error message: %s" % str(ex))
        db_conn = connect_db()
        logging.debug("type(db) = %s . db = %s" % (type(db_conn), db_conn))
        cur = db_conn.cursor()
    except Exception as ex:
        raise HTTPException(status_code=503, detail="Connection to the DB lost. Please inform the site admins.")
        logging.error("ooops, this should not happen! Unknown exception during fetch_valid_api_keys(): %s." % str(ex))
    finally:
        cur.execute(SQL)
        rows = cur.fetchall()
        rows = list(sum(rows, ()))  # flatten list of tuples
        logging.debug("valid API key list: %r" % rows)
        return rows


def check_if_admin(credentials: HTTPBasicCredentials = Depends(security)):
    # XXX FIXME: maybe read a http basic auth file? IS there a better way?
    if not (credentials.username == "admin" and credentials.password == config.admin_pwd):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def is_valid_api_key(key: str):
    valid_api_keys = fetch_valid_api_keys()
    if key in valid_api_keys:
        return True
    return False


def validate_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN,
                            detail="need API key. Please get in contact with the admins of this site in order get your API key. In the meantime ask 'aaron@lo-res.org' for BETA testing.")
    if is_valid_api_key(api_key_header):
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Could not validate the provided credentials. Please get in contact with the admins of this site in order get your API key. In the meantime ask 'aaron@lo-res.org' for BETA testing."
        )



###############################################################################
# API endpoint functions
@app.get('/help')
@app.get('/api/v1')
async def help(api_key: APIKey = Depends(validate_api_key)):
    return {'help': HELPSTR}


@app.get("/test/ping")
async def ping():
    return {"message": "Pong!"}


@app.get("/test/self-test")
async def selftest():
    return {"message": "OK"}


@app.get("/api/v1/taxonomies/all",
         response_model=List[TaxonomiesResponse],
         name="Taxonomies",
         summary="Show all taxonomies",
         tags=["Supporting data"]
         )
def get_taxonomies(
        limit: int = config['default_limit'],
        offset: int = config['default_offset'],
        api_key: APIKey = Depends(validate_api_key)
    ):
    """ Returns all known taxonomies.

    **GET Parameters:**
      * limit .... how many entries should we return?
      * offset.... starting at {offset}

    **Output (JSON):**
      * id... integer
      * name ... name of the tag
      * description ... long description
      * is_actionable ... value between 0 and 1 on how actionable this is on data (can we automatically do an action based on the tag?)
      * is_automatically_classifiable... bool. Can we automatically tag a domain based on this taxonomy?
      * is_stable... bool. Does this taxonomy change a lot?
      * for_numbers... bool. Is this taxonomy meant for numbers (IP addresses)?
      * for_domains... bool. Same but is it meant for domains?
      * url ... string. URL to further documentation.
    """
    SQL = """SELECT id,name,description,is_actionable,is_automatically_classifiable,is_stable,for_numbers,for_domains,url
             FROM taxonomy ORDER BY id asc LIMIT %s OFFSET %s"""
    cur = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(SQL, (limit, offset))
    rows = cur.fetchall()
    return rows


@app.get("/api/v1/tags/all",
         response_model=List[TagsResponse],
         summary="Show all tags",
         tags=["Supporting data"]
         )
def get_tags(
        limit: int = config['default_limit'],
        offset: int = config['default_offset'],
        api_key: APIKey = Depends(validate_api_key)
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
    SQL = """SELECT tag_id,tag_name,tag_description,taxonomy_id,extras FROM tags ORDER BY tag_id asc LIMIT %s OFFSET %s"""
    cur = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(SQL, (limit, offset))
    rows = cur.fetchall()
    return rows


@app.get("/api/v1/taxonomies/bydomain/{domain}",
         response_model=List[TagsOfDomainsResponse],
         name="taxonomies_by_domain",
         summary="Show all taxonomies of a given domain",
         tags=["Main"]
         )
@app.get("/api/v1/tags/bydomain/{domain}",
         response_model=List[TagsOfDomainsResponse],
         name="tags_by_domain",
         summary="Show all tags of a given domain",
         tags=["Main"]
         )
def get_tags_by_domain(
        domain: str,
        limit: int = config['default_limit'],
        offset: int = config['default_offset'],
        api_key: APIKey = Depends(validate_api_key)
    ):
    """ Returns all taxonomies and tags of a given {domain}

    **GET Parameters:**
      * domain ... the domain name to query (required)
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
    SQL = """SELECT domain_name, domain_id, tag_id, tag_name, taxonomy_id, taxonomy_name 
             FROM v_taxonomies_domains 
             WHERE domain_name = %s 
             ORDER BY domain_id, tag_id asc LIMIT %s OFFSET %s"""
    cur = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(SQL, (domain, limit, offset))
    rows = cur.fetchall()
    return rows


@app.get("/api/v1/domains/bytag/{tag}",
         response_model=List[DomainsResponse],
         name="domains_by_tags",
         summary="Show all domains which are tagged by {tag}",
         tags=["Main"]
         )
def get_domains_by_tag(
        tag: str,
        limit: int = config['default_limit'],
        offset: int = config['default_offset'],
        api_key: APIKey = Depends(validate_api_key)
    ):
    """ Returns all domains of a given {tag}

    **GET Parameters:**
      * tag ... the tag name to query (required)
      * limit .... how many entries should we return?
      * offset.... starting at {offset}

    **Output (JSON):**
      * domain name... string
      * domain_id ... ID of the domain
      * tag_id... int
      * tag_name ... name of the tag
      :type tag: str
    """
    SQL = """SELECT domain_id, domain_name, tag_id, tag_name
             FROM v_taxonomies_domains 
             WHERE tag_name = %s 
             ORDER BY domain_id, tag_id asc LIMIT %s OFFSET %s"""
    cur = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(SQL, (tag, limit, offset))
    rows = cur.fetchall()
    return rows

@app.get("/api/v1/domains/bytaxonomy/{taxonomy}",
         response_model=List[TagsOfDomainsResponse],
         name="domains_by_taxonomy",
         summary="Show all domains which are classified by {taxonomy}",
         tags=["Main"]
         )
def get_domains_by_taxonomy(
        taxonomy: str,
        limit: int = config['default_limit'],
        offset: int = config['default_offset'],
        api_key: APIKey = Depends(validate_api_key)
    ):
    """ Returns all domains of a given {taxonomy}

    **GET Parameters:**
      * taxonomy ... the taxonomy name to query (required)
      * limit .... how many entries should we return?
      * offset.... starting at {offset}

    **Output (JSON):**
      * domain name... string
      * domain_id ... ID of the domain
      * taxonomy_id... int
      * taxonomy_name ... name of the taxonomy
      :type taxonomy: str
    """
    SQL = """SELECT domain_id, domain_name, tag_id, tag_name, taxonomy_id, taxonomy_name
             FROM v_taxonomies_domains 
             WHERE taxonomy_name = %s 
             ORDER BY domain_id, tag_id asc LIMIT %s OFFSET %s"""
    cur = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(SQL, (taxonomy, limit, offset))
    rows = cur.fetchall()
    return rows


@app.get("/api/v1/stats/taxonomies",
         response_model=List[StatsTaxResponse],
         name="Stats of taxonomies",
         summary="Show stats on all taxonomies",
         tags=["Stats"]
         )
def get_stats_taxonomies(
        limit: int = config['default_limit'],
        offset: int = config['default_offset'],
        api_key: APIKey = Depends(validate_api_key)
    ):
    """ Returns stats on all taxonomies

    **GET Parameters:**
      * limit .... how many entries should we return?
      * offset.... starting at {offset}

    **Output (JSON):**
      * taxonomy_id ... int
      * taxonomy_name ... name of the linked taxonomy
      * count.... how many domains are labeled by this taxonomy
    """
    SQL = """SELECT count(domain_id), taxonomy_id, taxonomy_name 
             FROM v_taxonomies_domains 
             GROUP by taxonomy_id,taxonomy_name
             ORDER BY count DESC LIMIT %s OFFSET %s"""
    cur = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(SQL, (limit, offset))
    rows = cur.fetchall()
    return rows


@app.get("/api/v1/stats/tags",
         response_model=List[StatsTagResponse],
         name="Stats of tags",
         summary="Show stats on all tags",
         tags=["Stats"]
         )
def get_stats_tags(
        limit: int = config['default_limit'],
        offset: int = config['default_offset'],
        api_key: APIKey = Depends(validate_api_key)
    ):
    """ Returns stats on all tags

    **GET Parameters:**
      * limit .... how many entries should we return?
      * offset.... starting at {offset}

    **Output (JSON):**
      * tag_id ... int
      * tag_name ... name of the linked taxonomy
      * count.... how many domains are labeled by this tag
    """
    SQL = """SELECT count(domain_id), tag_id, tag_name 
             FROM v_taxonomies_domains 
             GROUP by tag_id,tag_name
             ORDER BY count DESC LIMIT %s OFFSET %s"""
    cur = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(SQL, (limit, offset))
    rows = cur.fetchall()
    return rows


if __name__ == "__main__":
    logging.basicConfig(level=config['loglevel'])
    conn = get_db()

