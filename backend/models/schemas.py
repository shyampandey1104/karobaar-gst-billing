"""Data models and schemas for Karobaar GST Billing."""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field


class Party(BaseModel):
    id: str
    name: str
    phone: str
    party_type: str = "Customer"  # Customer or Supplier
    gstin: Optional[str] = None
    state: str = "Maharashtra"
    state_code: str = "27"
    balance: float = 0.0  # Positive = Lena hai (Receivable), Negative = Dena hai (Payable)
    address: Optional[str] = None


class Item(BaseModel):
    id: str
    name: str
    hsn_code: str = "9999"
    unit: str = "PCS"  # PCS, KG, LTR, BOX, MTR
    sale_price: float
    purchase_price: float = 0.0
    gst_rate: float = 18.0  # 0, 5, 12, 18, 28
    current_stock: float = 0.0
    min_stock_alert: float = 5.0


class InvoiceLineItem(BaseModel):
    item_id: str
    item_name: str
    hsn_code: str
    unit: str
    quantity: float
    unit_price: float
    gst_rate: float
    taxable_value: float
    cgst_amount: float
    sgst_amount: float
    igst_amount: float
    line_total: float


class Invoice(BaseModel):
    invoice_number: str
    invoice_type: str = "Sales Invoice"  # Sales Invoice, Estimate/Quotation, Purchase Bill
    invoice_date: str
    party_id: str
    party_name: str
    party_phone: str
    is_inter_state: bool = False
    items: List[InvoiceLineItem]
    subtotal: float
    discount_amount: float = 0.0
    cgst_total: float = 0.0
    sgst_total: float = 0.0
    igst_total: float = 0.0
    grand_total: float
    paid_amount: float = 0.0
    balance_due: float = 0.0
    payment_mode: str = "Cash"  # Cash, UPI, Bank Transfer, Cheque
    upi_qr_string: Optional[str] = None
    status: str = "Paid"  # Paid, Unpaid, Partially Paid
