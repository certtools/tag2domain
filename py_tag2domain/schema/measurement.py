from __future__ import annotations  # noqa: F407
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, constr


class Tag(BaseModel):
    tag: Union[int, str]
    value: Optional[Union[int, str]]
    description: Optional[str]
    extras: Optional[Dict[str, Any]]


class MeasurementModel(BaseModel):
    version: str
    tag_type: str
    tagged_id: int
    taxonomy: Union[int, str]
    producer: constr(min_length=1)
    measured_at: constr(
        regex='^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?$'  # noqa: W605, F722
    )
    tags: List[Tag]
    measurement_id: Optional[str]
    autogenerate_tags: Optional[bool]
    autogenerate_values: Optional[bool]
