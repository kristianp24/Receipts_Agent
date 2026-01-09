from typing import Literal
from pydantic import BaseModel, Field

class BillTypeModel(BaseModel):
    bill_type: Literal["electricity", "gas", "grocery", "other"] = Field(
        ..., 
        description="The type of the bill."
    )