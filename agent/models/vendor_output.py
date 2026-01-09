from pydantic import BaseModel, Field
class VendorOutput(BaseModel):
    vendor_name: str = Field(description="The name of the vendor identified in the document")