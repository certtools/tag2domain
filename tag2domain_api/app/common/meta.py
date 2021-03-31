from fastapi import APIRouter
import logging

from tag2domain_api.app.util.config import config

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/version",
    name="Service version",
    summary="Return the version of the service"
)
async def get_version():
    return {"version": config["version"]}


@router.get(
    "/api-versions",
    name="API versions",
    summary="Return the API versions available"
)
async def get_api_versions():
    return [{"version": "v1"}, ]
