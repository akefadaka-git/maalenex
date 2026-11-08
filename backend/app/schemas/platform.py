from pydantic import BaseModel, ConfigDict


class ServiceAreaAvailabilityResponse(BaseModel):
    area_code: str
    area_name: str
    availability_status: str
    is_enabled: bool
    is_available: bool
    synthetic_test_available: bool


class PlatformServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    description: str
    rollout_status: str
    is_enabled: bool
    availability: list[ServiceAreaAvailabilityResponse]
