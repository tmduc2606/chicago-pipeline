from pydantic import BaseModel


class FilterOptions(BaseModel):
    date_min: str
    date_max: str
    primary_types: list[str]
    districts: list[int]
    community_areas: list[int]