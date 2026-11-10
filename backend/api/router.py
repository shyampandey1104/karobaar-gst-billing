"""Main API Router for Karobaar GST Billing."""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import date
from urllib.parse import quote

from backend.models.schemas import Party, Item, Invoice, InvoiceLineItem
from backend.services.gst_calculator import GSTBillingCalculator
from backend.services.ai_voice_parser import AIVoiceBillParser

router = APIRouter(prefix="/api/v1")

# In-memory storage seeded with realistic Indian MSME shop data
PARTIES: Dict[str, Party] = {
    "P-001": Party(id="P-001", name="Ramesh Kirana Stores", phone="9820123456", party_type="Customer", gstin="27AABCR1234F1Z5", state="Maharashtra", state_code="27", balance=14500.0, address="Shop 4, Station Road, Virar East"),
    "P-002": Party(id="P-002", name="Sharma Hardware & Electricals", phone="9821987654", party_type="Customer", gstin="27AAACS9988K1Z2", state="Maharashtra", state_code="27", balance=8200.0, address="Near Datta Mandir, Vasai West"),
    "P-003": Party(id="P-003", name="Gupta Wholesale Traders", phone="9811223344", party_type="Supplier", gstin="27AAACG4455P1Z9", state="Maharashtra", state_code="27", balance=-25000.0, address="APMC Market, Vashi, Navi Mumbai"),
}

ITEMS: Dict[str, Item] = {
    "ITM-01": Item(id="ITM-01", name="Premium Basmati Rice 5kg", hsn_code="1006", unit="BAG", sale_price=580.0, purchase_price=490.0, gst_rate=5.0, current_stock=45.0, min_stock_alert=10.0),
    "ITM-02": Item(id="ITM-02", name="Refined Sunflower Oil 1L", hsn_code="1512", unit="LTR", sale_price=165.0, purchase_price=138.0, gst_rate=5.0, current_stock=3.0, min_stock_alert=8.0),  # Low Stock!
    "ITM-03": Item(id="ITM-03", name="Tata Salt 1kg", hsn_code="2501", unit="PKT", sale_price=28.0, purchase_price=22.0, gst_rate=0.0, current_stock=120.0, min_stock_alert=20.0),
    "ITM-04": Item(id="ITM-04", name="Haldiram Bhujia 400g", hsn_code="2106", unit="PKT", sale_price=110.0, purchase_price=88.0, gst_rate=12.0, current_stock=25.0, min_stock_alert=5.0),
}

INVOICES: List[Invoice] = [
    Invoice(
        invoice_number="INV-2026-001",
        invoice_type="Sales Invoice",
        invoice_date="2026-11-09",
        party_id="P-001",
        party_name="Ramesh Kirana Stores",
        party_phone="9820123456",
        is_inter_state=False,
        items=[
            InvoiceLineItem(item_id="ITM-01", item_name="Premium Basmati Rice 5kg", hsn_code="1006", unit="BAG", quantity=2, unit_price=580.0, gst_rate=5.0, taxable_value=1160.0, cgst_amount=29.0, sgst_amount=29.0, igst_amount=0.0, line_total=1218.0)
        ],
        subtotal=1160.0,
        discount_amount=0.0,
        cgst_total=29.0,
        sgst_total=29.0,
        igst_total=0.0,
        grand_total=1218.0,
        paid_amount=1218.0,
        balance_due=0.0,
        payment_mode="UPI",
        upi_qr_string="upi://pay?pa=shop@upi&pn=Karobaar%20Store&am=1218.00&cu=INR&tn=Bill%20INV-2026-001",
        status="Paid",
    )
]


class CreateInvoiceRequest(BaseModel):
    party_id: str
    invoice_type: str = "Sales Invoice"
    items: List[Dict[str, Any]]
    discount_amount: float = 0.0
    paid_amount: float = 0.0
    payment_mode: str = "Cash"
    upi_vpa: str = "merchant@upi"


class VoiceParseRequest(BaseModel):
    dictation_text: str


@router.get("/dashboard/summary")
async def get_dashboard_summary():
    """Vyapar style financial metrics: Today's sales, To Collect (Lena Hai), To Pay (Dena Hai)."""
    today_str = date.today().strftime("%Y-%m-%d")
    today_sales = sum(inv.grand_total for inv in INVOICES if inv.invoice_date == today_str or inv.invoice_date == "2026-11-09")
    to_collect = sum(p.balance for p in PARTIES.values() if p.balance > 0)
    to_pay = abs(sum(p.balance for p in PARTIES.values() if p.balance < 0))
    low_stock = [itm for itm in ITEMS.values() if itm.current_stock <= itm.min_stock_alert]

    return {
        "today_sales": today_sales,
        "total_receivables_lena_hai": to_collect,
        "total_payables_dena_hai": to_pay,
        "low_stock_count": len(low_stock),
        "total_invoices_count": len(INVOICES),
    }


@router.get("/invoices")
async def list_invoices():
    return INVOICES


@router.post("/invoices")
async def create_invoice(req: CreateInvoiceRequest):
    party = PARTIES.get(req.party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")

    line_items: List[InvoiceLineItem] = []
    subtotal = 0.0
    cgst_tot = 0.0
    sgst_tot = 0.0
    igst_tot = 0.0

    is_inter_state = party.state_code != "27"

    for itm_req in req.items:
        item_obj = ITEMS.get(itm_req.get("item_id", ""))
        name = item_obj.name if item_obj else itm_req.get("item_name", "Item")
        hsn = item_obj.hsn_code if item_obj else "9999"
        unit = item_obj.unit if item_obj else "PCS"
        rate = float(itm_req.get("unit_price", 0.0))
        qty = float(itm_req.get("quantity", 1.0))
        gst = float(item_obj.gst_rate if item_obj else itm_req.get("gst_rate", 18.0))

        line = GSTBillingCalculator.calculate_line_item(
            item_id=itm_req.get("item_id", "GEN"),
            name=name,
            hsn=hsn,
            unit=unit,
            qty=qty,
            price=rate,
            gst_rate=gst,
            is_inter_state=is_inter_state,
        )
        line_items.append(line)
        subtotal += line.taxable_value
        cgst_tot += line.cgst_amount
        sgst_tot += line.sgst_amount
        igst_tot += line.igst_amount

        # Deduct stock if sales invoice
        if item_obj and req.invoice_type == "Sales Invoice":
            item_obj.current_stock = max(0.0, item_obj.current_stock - qty)

    grand_total = round((subtotal - req.discount_amount) + cgst_tot + sgst_tot + igst_tot, 2)
    bal_due = max(0.0, grand_total - req.paid_amount)
    inv_num = f"INV-2026-{len(INVOICES) + 1:03d}"

    upi_string = GSTBillingCalculator.generate_upi_payment_link(
        vpa=req.upi_vpa,
        payee_name="Karobaar Merchant",
        amount=grand_total,
        invoice_no=inv_num,
    )

    inv = Invoice(
        invoice_number=inv_num,
        invoice_type=req.invoice_type,
        invoice_date=date.today().strftime("%Y-%m-%d"),
        party_id=party.id,
        party_name=party.name,
        party_phone=party.phone,
        is_inter_state=is_inter_state,
        items=line_items,
        subtotal=subtotal,
        discount_amount=req.discount_amount,
        cgst_total=cgst_tot,
        sgst_total=sgst_tot,
        igst_total=igst_tot,
        grand_total=grand_total,
        paid_amount=req.paid_amount,
        balance_due=bal_due,
        payment_mode=req.payment_mode,
        upi_qr_string=upi_string,
        status="Paid" if bal_due == 0 else ("Partially Paid" if req.paid_amount > 0 else "Unpaid"),
    )

    # Update party khata balance
    if bal_due > 0 and req.invoice_type == "Sales Invoice":
        party.balance += bal_due

    INVOICES.insert(0, inv)
    return inv


@router.get("/parties")
async def list_parties():
    return list(PARTIES.values())


@router.get("/parties/{party_id}/whatsapp-reminder")
async def get_whatsapp_reminder(party_id: str):
    party = PARTIES.get(party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")

    text = f"Namaste {party.name}! 🙏\nThis is a friendly reminder that an outstanding payment of ₹{party.balance:,.2f} is pending with Karobaar Store. Kindly process payment at your earliest convenience. Thank you!"
    wa_url = f"https://wa.me/91{party.phone}?text={quote(text)}"
    return {"party_name": party.name, "phone": party.phone, "whatsapp_link": wa_url, "message": text}


@router.get("/inventory")
async def list_inventory():
    return list(ITEMS.values())


@router.post("/ai/parse-voice-bill")
async def parse_voice_bill(req: VoiceParseRequest):
    """AI Voice parser converts voice dictation into invoice line items."""
    parsed = AIVoiceBillParser.parse_dictation(req.dictation_text)
    return {"raw_text": req.dictation_text, "parsed_items": parsed}
