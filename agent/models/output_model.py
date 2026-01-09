from pydantic import BaseModel, Field

class BillItem(BaseModel):
    product_name: str = Field(..., description="Name of the product")   
    quantity: int = Field(..., description="Quantity of the product purchased")
    unit_price: float = Field(..., description="Unit price of the product")
    total_price: float = Field(..., description="Total price for the quantity of the product")

class BillingOutputModel(BaseModel):
    total_amount: float = Field(..., description="The total amount billed in the document.")
    due_date: str = Field(..., description="The due date for the payment.")
    vendor_name: str = Field(..., description="The name of the vendor or service provider.")
    items: list[BillItem] = Field(
        ..., description="A list of billed items with details such as product name, quantity, and price and total price."
    )