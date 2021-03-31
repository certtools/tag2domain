import logging
import traceback

from fastapi import APIRouter, HTTPException, Body

from tag2domain_api.app.util.config import config
from tag2domain_api.app.util.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

if "ENABLE_MSM2TAG" in config and config["ENABLE_MSM2TAG"] is True:
    logger.info("enabling msm2tag endpoints")
    from py_tag2domain.db import Psycopg2Adapter
    from py_tag2domain.msm2tags import MeasurementToTags
    from py_tag2domain.schema.measurement import MeasurementModel
    from py_tag2domain.exceptions import (
        InvalidMeasurementException,
        StaleMeasurementException
    )
    from py_tag2domain.util import parse_config

    if config["MSM2TAG_DB_CONFIG"] is None:
        logger.error("using msm2tag requires MSM2TAG_DB_CONFIG option "
                     "to point to a config file")
        raise RuntimeError("no msm2tag db config found")
    else:
        _, intxn_table_mappings = parse_config(config["MSM2TAG_DB_CONFIG"])
    max_measurement_age = config["MSM2TAG_MAX_MEASUREMENT_AGE"]

    @router.post("/")
    async def msm2tag(
        msm: MeasurementModel = Body(
            ...,
            example={
                "version": "1",
                "tag_type": "intersection",
                "tagged_id": 3,
                "taxonomy": "colors",
                "producer": "test",
                "measured_at": "2020-12-22T12:35:32",
                "measurement_id": "test/12345",
                "tags": [
                    {
                        "tag": "rgb::blue"
                    },
                    {
                        "tag": "cmyk::black"
                    },
                ]
            }
        )
    ):
        _db_adapter = Psycopg2Adapter(
            get_db(),
            intxn_table_mappings,
            logger=logger
        )

        _msm2tags = MeasurementToTags(
            _db_adapter,
            logger=logger,
            max_measurement_age=max_measurement_age
        )
        try:
            logger.debug(msm.dict(exclude_unset=True))
            _msm2tags.handle_measurement(
                msm.dict(exclude_unset=True),
                skip_validation=True
            )
        except (InvalidMeasurementException, StaleMeasurementException) as e:
            logger.info("error 400: " + str(e))
            logger.debug(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))

        return {"message": "OK"}
