from pydantic import BaseModel

class TagsResponse(BaseModel):
    tag_id: int
    tag_name: str
    tag_description: str = None
    taxonomy_id: int = None
    extras: dict = None

class DomainsResponse(BaseModel):
    domain_id: int
    domain_name: str
    tag_id: int = None
    tag_name: str = None

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
    domain_name: str
    domain_id: int
    tag_id: int = None
    tag_name: str = None
    taxonomy_id: int = None
    taxonomy_name: str = None

class StatsTaxResponse(BaseModel):
    count: int
    taxonomy_id: int
    taxonomy_name: str

class StatsTagResponse(BaseModel):
    count: int
    tag_id: int
    tag_name: str
