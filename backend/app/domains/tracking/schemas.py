from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TelemetryPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    sequence: int = Field(ge=1, le=2_147_483_647)
    recorded_at: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    speed_kph: float = Field(ge=0, le=180)
    heading_degrees: float = Field(ge=0, lt=360)
    accuracy_meters: float = Field(gt=0, le=500)

    @field_validator("recorded_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("recorded_at must include a timezone")
        return value
