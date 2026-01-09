from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# 1. Expand the types to include GROCERY
BillType = Literal["GAS", "ELECTRICITY", "WATER", "INTERNET", "GROCERY", "OTHER"]

class SubitemModel(BaseModel):
    name: str = Field(..., description="Name of the sub-component (e.g., 'di cui...' or 'Sconto')")
    total_price: float = Field(..., description="Partial amount")
    unit_price: Optional[float] = Field(None, description="Price per unit if listed")
    quantity: Optional[float] = Field(None, description="Quantity if listed")

class ItemModel(BaseModel):
    product_name: str = Field(..., description="Item name (e.g., 'Energia Attiva' or 'TRANCIO MARGHERITA')")
    
    # Generic quantity works for both (kWh for energy, Kg/Pcs for grocery)
    quantity: Optional[float] = Field(None, description="Amount (e.g., 214, 2.5, 1)")
    
    # Critical for distinguishing: 'kWh' vs 'Kg' vs 'Pz' (Pieces)
    unit_of_measure: Optional[str] = Field(None, description="Unit string (e.g., 'Smc', 'kWh', 'kg', 'pz')")
    
    unit_price: Optional[float] = Field(None, description="Price per unit")
    
    # Optional because some header rows in bills have no price
    total_price: Optional[float] = Field(None, description="Total line cost")
    
    # Useful for Grocery Discounts (e.g., a subitem 'Sconto 50%')
    subitems: Optional[List[SubitemModel]] = Field(None, description="Breakdown or discounts")

class UnifiedBillModel(BaseModel):
    vendor_name: str = Field(..., description="Vendor Name (e.g., 'IREN', 'PAM')")
    
    # 2. The Classifier Field
    type_of_bill: str = Field(..., description="Classify the document type based on content.")
    
    bill_date: str = Field(..., description="Date of issue or purchase")
    
    # 3. Strictly Optional for Groceries
    due_date: Optional[str] = Field(None, description="Payment deadline. LEAVE NULL for grocery receipts.")
    
    total_amount: float = Field(..., description="Final total paid/due")
    items: List[ItemModel] = Field(..., description="List of purchased items or services")
    