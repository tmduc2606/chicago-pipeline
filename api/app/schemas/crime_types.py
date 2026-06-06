from pydantic import BaseModel


class CrimeTypeCount(BaseModel):
    primary_type: str
    count: int


class CrimeTypeArrest(BaseModel):
    primary_type: str
    arrest_rate: float