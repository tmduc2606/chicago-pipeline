from pydantic import BaseModel


class DistrictArrest(BaseModel):
    district: int
    arrest_rate: float
    total: int