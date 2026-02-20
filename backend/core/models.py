from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import uuid
from decimal import Decimal


class InvoiceItem(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the item")
    quantity: float = Field(..., gt=0, description="Quantity of the item")
    unit_price: float = Field(..., ge=0, description="Unit price of the item")

    @property
    def line_total(self) -> float:
        return round(self.quantity * self.unit_price, 2)


class InvoiceSchema(BaseModel):
    invoice_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: Optional[str] = Field(None, description="Invoice number")
    customer_name: str = Field(..., min_length=1, description="Customer name")
    customer_email: EmailStr = Field(..., description="Customer email address")
    customer_gst: Optional[str] = Field(
        None, description="Customer GST number")
    invoice_date: Optional[str] = Field(None, description="Invoice date")
    due_date: Optional[str] = Field(None, description="Due date for payment")
    currency: str = Field(default="INR", description="Currency code")
    tax_percent: float = Field(
        default=18.0, ge=0, le=100, description="Tax percentage")
    shipping_fee: float = Field(
        default=0.0, ge=0, description="Shipping fee amount")
    discount: float = Field(default=0.0, ge=0, description="Discount amount")
    discount_code: Optional[str] = Field(
        None, description="Discount code applied")
    items: List[InvoiceItem] = Field(
        default=[], description="List of invoice items")

    @property
    def subtotal(self) -> float:
        return round(sum(item.line_total for item in self.items), 2)

    @property
    def tax_amount(self) -> float:
        return round(self.subtotal * (self.tax_percent / 100), 2)

    @property
    def grand_total(self) -> float:
        return round(self.subtotal + self.tax_amount + self.shipping_fee - self.discount, 2)

    def to_dict(self):
        """Convert to dictionary format compatible with existing system"""
        d = self.model_dump()  # Updated for Pydantic v2
        d['subtotal'] = self.subtotal
        d['tax_amount'] = self.tax_amount
        d['grand_total'] = self.grand_total
        return d

    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v:
            raise ValueError('At least one item is required')
        return v


class ConversationMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    sender: str  # 'user' or 'bot'
    timestamp: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    type: Optional[str] = "info"


class ConversationHistory(BaseModel):
    session_id: str
    messages: List[ConversationMessage] = []
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = Field(
        default_factory=lambda: datetime.now().isoformat())
    active: bool = True

    def add_message(self, message: ConversationMessage):
        self.messages.append(message)
        self.last_updated = datetime.now().isoformat()

    def to_dict(self):
        d = self.dict()
        d['messages'] = [msg.dict() for msg in self.messages]
        return d
