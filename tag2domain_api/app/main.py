#!/usr/bin/env python3
import logging

from fastapi import FastAPI, HTTPException

import tag2domain_api.app.util.logging
from tag2domain_api.app.util.config import config, description
from tag2domain_api.app.util.db import connect_db, disconnect_db

from tag2domain_api.app.api_v1.api import router as router_api_v1
from tag2domain_api.app.common.test import router as router_test
from tag2domain_api.app.common.meta import router as router_meta

tag2domain_api.app.util.logging.setup()
logger = logging.getLogger(__name__)

###############################################################################
# Setup fastAPI app
app = FastAPI(
    title="tag2domain API",
    version=config['version'],
    description=description
)

app.include_router(router_test, prefix="/test", tags=["Test"])
app.include_router(router_meta, prefix="/meta", tags=["Meta"])
app.include_router(router_api_v1, prefix="/api/v1")


@app.on_event('startup')
def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    :rtype: psycopg2 connection"""

    logger.info('starting up....')
    logger.debug(config)
    try:
        connect_db(config)
    except RuntimeError as e:
        logger.error("error connecting to DB", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event('shutdown')
def close_db():
    """Closes the database again at the end of the request."""
    logger.info('shutting down....')
    logger.info('disconnecting from DB...')
    disconnect_db()


if __name__ == "__main__":
    logger.basicConfig(level=config['loglevel'])
    conn = get_db()
