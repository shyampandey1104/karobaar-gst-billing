"""GST Calculation and Indian UPI QR Code generator for Karobaar."""

from typing import Dict, Any, List
from urllib.parse import quote
from backend.models.schemas import InvoiceLineItem


class GSTBillingCalculator:
    """Calculates tax brackets, inter-state IGST vs intra-state CGST/SGST, and rounding."""

    MY_STATE_CODE = "27"  # Default Maharashtra

    @classmethod
    def calculate_line_item(
        cls,
        item_id: str,
        name: str,
        hsn: str,
        unit: str,
        qty: float,
        price: float,
        gst_rate: float,
        is_inter_state: bool = False,
    ) -> InvoiceLineItem:
        taxable_value = round(qty * price, 2)

        if is_inter_state:
            cgst = 0.0
            sgst = 0.0
            igst = round(taxable_value * (gst_rate / 100.0), 2)
        else:
            half_rate = gst_rate / 2.0
            cgst = round(taxable_value * (half_rate / 100.0), 2)
            sgst = round(taxable_value * (half_rate / 100.0), 2)
            igst = 0.0

        total = round(taxable_value + cgst + sgst + igst, 2)

        return InvoiceLineItem(
            item_id=item_id,
            item_name=name,
            hsn_code=hsn,
            unit=unit,
            quantity=qty,
            unit_price=price,
            gst_rate=gst_rate,
            taxable_value=taxable_value,
            cgst_amount=cgst,
            sgst_amount=sgst,
            igst_amount=igst,
            line_total=total,
        )

    @classmethod
    def generate_upi_payment_link(cls, vpa: str, payee_name: str, amount: float, invoice_no: str) -> str:
        """Generate standard NPCI UPI payment intent URI for GPay, PhonePe, Paytm."""
        clean_vpa = vpa.strip()
        encoded_name = quote(payee_name.strip())
        encoded_note = quote(f"Payment for Bill {invoice_no}")
        return f"upi://pay?pa={clean_vpa}&pn={encoded_name}&am={amount:.2f}&cu=INR&tn={encoded_note}"
