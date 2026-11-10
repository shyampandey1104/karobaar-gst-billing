"""Unit tests for GSTBillingCalculator and AIVoiceBillParser."""

from backend.services.gst_calculator import GSTBillingCalculator
from backend.services.ai_voice_parser import AIVoiceBillParser


def test_intra_state_gst_split():
    # 18% GST intra-state (Maharashtra to Maharashtra) -> 9% CGST + 9% SGST
    line = GSTBillingCalculator.calculate_line_item(
        item_id="ITM-01",
        name="Basmati Rice",
        hsn="1006",
        unit="KG",
        qty=10.0,
        price=100.0,
        gst_rate=18.0,
        is_inter_state=False,
    )
    assert line.taxable_value == 1000.0
    assert line.cgst_amount == 90.0
    assert line.sgst_amount == 90.0
    assert line.igst_amount == 0.0
    assert line.line_total == 1180.0


def test_inter_state_igst():
    # 18% GST inter-state (Maharashtra to Delhi) -> 18% IGST
    line = GSTBillingCalculator.calculate_line_item(
        item_id="ITM-01",
        name="Basmati Rice",
        hsn="1006",
        unit="KG",
        qty=10.0,
        price=100.0,
        gst_rate=18.0,
        is_inter_state=True,
    )
    assert line.taxable_value == 1000.0
    assert line.cgst_amount == 0.0
    assert line.sgst_amount == 0.0
    assert line.igst_amount == 180.0
    assert line.line_total == 1180.0


def test_upi_intent_link():
    link = GSTBillingCalculator.generate_upi_payment_link(
        vpa="shop@upi",
        payee_name="Karobaar Kirana",
        amount=1180.0,
        invoice_no="INV-101",
    )
    assert link.startswith("upi://pay?")
    assert "pa=shop@upi" in link
    assert "am=1180.00" in link


def test_ai_voice_dictation():
    text = "5 packet biscuit 20 rs, 2 kilo rice 120 rupaye"
    parsed = AIVoiceBillParser.parse_dictation(text)
    assert len(parsed) == 2
    assert parsed[0]["quantity"] == 5.0
    assert parsed[0]["unit_price"] == 20.0
    assert parsed[1]["quantity"] == 2.0
    assert parsed[1]["unit"] == "KG"
    assert parsed[1]["unit_price"] == 120.0
