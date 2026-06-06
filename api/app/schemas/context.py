from pydantic import BaseModel


class BooleanSplit(BaseModel):
    true_count: int
    false_count: int


class LocationCount(BaseModel):
    location_description: str
    count: int