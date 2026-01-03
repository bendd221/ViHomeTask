from pydantic import BaseModel, field_validator
from typing import List, Dict, Any

class GlueJobConfig(BaseModel):
    job_name: str
    script_name: str
    output_sub_folder: str
    glue_version: str = "5.0"

    @field_validator("output_sub_folder", mode="before")
    @classmethod
    def strip_slashes(cls, value: str) -> str:
        return value.strip("/")