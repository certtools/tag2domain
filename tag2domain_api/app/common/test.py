from fastapi import APIRouter, HTTPException
import logging

from tag2domain_api.app.util.db import execute_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/ping",
    name="Ping test",
    summary="Run a ping test, to check if the service is running"
)
async def ping():
    return {"message": "Pong!"}


@router.get(
    "/self-test",
    name="Self-test",
    summary="Run a self-test"
)
async def selftest():
    try:
        execute_db("SELECT 1", ())
    except Exception:
        raise HTTPException(status_code=503, detail="failed DB execute")
    return {"message": "OK"}
