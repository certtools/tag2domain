from fastapi import APIRouter

from tag2domain_api.app.api_v1.endpoints import (
    util,
    domains,
    stats,
    meta,
    bydomain,
    filters,
    msm2tag
)

router = APIRouter()
router.include_router(
    util.router,
    tags=["Util"]
)
router.include_router(
    meta.router,
    prefix="/meta",
    tags=["List Taxonomy Information"]
)
router.include_router(
    filters.router,
    prefix="/filters",
    tags=["List Filter Information"]
)
router.include_router(
    bydomain.router,
    prefix="/bydomain",
    tags=["List Domain Tags"]
)
router.include_router(
    domains.router,
    prefix="/domains",
    tags=["List Domains"]
)
router.include_router(
    msm2tag.router,
    prefix="/msm2tag",
    tags=["Add Tags"]
)
router.include_router(
    stats.router,
    prefix="/stats",
    tags=["Statistics"]
)
