from pydantic import BaseModel, Field
from typing import List, Optional

from typing import List, Optional
from pydantic import BaseModel, Field

class SubitemModel(BaseModel):
    name: str = Field(..., description="Name of the product breakdown (e.g., 'di cui spesa...')")
    quantity: Optional[float] = Field(None, description="Quantity, if different from parent") 
    unit_price: Optional[float] = Field(None, description="Price per unit")
    total_price: float = Field(..., description="Total price for this sub-component")

class ItemModel(BaseModel):
    product_name: str = Field(..., description="Name of the item (e.g., 'Quota per consumi')")
    quantity: Optional[float] = Field(None, description="Quantity (e.g., Smc or Months). Can be decimal.") 
    unit_price: Optional[float] = Field(None, description="Price per unit")
    total_price: float = Field(..., description="Total price for the item")
    subitems: Optional[List[SubitemModel]] = Field(None, description="Breakdown of costs if available")

class GeneralModel(BaseModel):
    vendor_name: str = Field(..., description="Name of the utility company")
    type_of_bill: str = Field(..., description="Type of the bill, e.g., 'Electricity Bill' , 'Grocery Bill', 'Gas Bill' , 'Water Bill'")
    bill_date: str = Field(..., description="Date of the bill")
    due_date: Optional[str] = Field(..., description="Due date for the payment") 
    total_amount: float = Field(..., description="Total amount due")
    items: List[ItemModel] = Field(..., description="List of billed items")
