from pydantic import BaseModel


class GeoCluster(BaseModel):
    h3: str
    lat: float
    lng: float
    count: int


class ChoroplethBucket(BaseModel):
    key: str
    label: str
    value: float
    lat: float = 0.0
    lng: float = 0.0