from pydantic import BaseModel

class HealthCheckResponse(BaseModel):
    status: str
    project: str
    version: str
    debug: bool