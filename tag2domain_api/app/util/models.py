from pydantic import BaseModel
from typing import List, Union
from enum import Enum
from datetime import datetime


class ErrorMessage(BaseModel):
    detail: str


class VersionComparisonOperatorParameter(str, Enum):
    equal = "="
    lessthan = "<"
    lessthanequal = "<="
    greaterthan = ">"
    greaterthanequal = ">="


class TagsResponse(BaseModel):
    tag_id: int
    tag_name: str
    tag_description: str = None
    taxonomy_id: int = None
    extras: dict = None


class ValuesResponse(BaseModel):
    value_id: int
    value: str


class DomainsResponse(BaseModel):
    domain_id: int
    domain_name: str
    tag_type: str
    value: Union[str, None]
    start_time: datetime
    measured_at: Union[datetime, None]
    end_time: datetime = None


class DomainsResponseWithVersion(BaseModel):
    domain_id: int
    domain_name: str
    version: Union[str, None]
    start_time: datetime
    measured_at: Union[datetime, None]
    end_time: datetime = None


class DomainTagResponse(BaseModel):
    tag_id: int
    tag_name: str
    start_time: datetime
    measured_at: Union[datetime, None]
    end_time: datetime = None


class DomainsWithTagsResponse(BaseModel):
    domain_id: int
    domain_name: str
    tags: List[DomainTagResponse]


class TaxonomiesResponse(BaseModel):
    id: int
    name: str
    description: str = None
    is_actionable: float = None
    is_automatically_classifiable: float = None
    is_stable: float = None
    for_numbers: bool = None
    for_domains: bool = None
    url: str = None


class TagsOfDomainsResponse(BaseModel):
    tag_id: int
    tag_name: str
    value_id: Union[int, None]
    value: Union[str, None]
    taxonomy_id: int
    taxonomy_name: str
    start_time: datetime
    measured_at: Union[datetime, None]
    end_time: datetime = None


class StatsTaxonomiesResponse(BaseModel):
    taxonomy_name: str
    count: int


class StatsTagsResponse(BaseModel):
    tag_name: str
    count: int


class StatsCategoriesResponse(BaseModel):
    category: str
    count: int


class StatsValuesResponse(BaseModel):
    value: Union[str, None]
    count: int


class TagDetailsResponse(BaseModel):
    name: str
    description: str
    category: Union[str, None]
    extras: Union[dict, None]


class TaxonomyFlagsResponse(BaseModel):
    is_actionable: Union[float, None]
    is_automatically_classifiable: Union[bool, None]
    is_stable: Union[bool, None]
    for_numbers: bool
    for_domains: bool
    allows_auto_tags: bool
    allows_auto_values: bool


class TaxonomyDetailsResponse(BaseModel):
    name: str
    description: str
    url: Union[str, None]
    flags: TaxonomyFlagsResponse


class ValuesAggregateResponse(BaseModel):
    count: int


class TagInfoResponse(BaseModel):
    tag: TagDetailsResponse
    taxonomy: TaxonomyDetailsResponse
    values: ValuesAggregateResponse
