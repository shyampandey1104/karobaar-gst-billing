"""AI Voice & Text Line Item Parser for Quick Billing (Hinglish/English)."""

import re
from typing import List, Dict, Any


class AIVoiceBillParser:
    """Parses natural language billing voice/text input into structured invoice items.
    
    Example:
    '5 packet parle-g 10 rupaye, 2 kilo basmati rice 120 rupaye'
    """

    @classmethod
    def parse_dictation(cls, text: str) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        # Split by comma or 'aur' / 'and'
        clauses = re.split(r",|\s+aur\s+|\s+and\s+", text.strip(), flags=re.IGNORECASE)

        for clause in clauses:
            clause = clause.strip()
            if not clause:
                continue

            # Regex matching: <qty> <unit/optional> <item name> <price> <currency/rupaye/rs>
            # e.g.: 5 packet britannia biscuit 20 rs
            match = re.search(
                r"^(\d+(?:\.\d+)?)\s*(packet|piece|pcs|kg|kilo|litre|ltr|box|meter|mtr)?\s*(.+?)\s*(\d+(?:\.\d+)?)\s*(?:rs|rupaye|inr|/-)?$",
                clause,
                re.IGNORECASE,
            )

            if match:
                qty = float(match.group(1))
                unit = (match.group(2) or "PCS").upper()
                if unit == "KILO":
                    unit = "KG"
                elif unit == "LITRE":
                    unit = "LTR"

                name = match.group(3).strip().title()
                rate = float(match.group(4))

                items.append({
                    "item_name": name,
                    "quantity": qty,
                    "unit": unit,
                    "unit_price": rate,
                    "gst_rate": 18.0,
                })
            else:
                # Fallback simple split if price is at end
                words = clause.split()
                if len(words) >= 3 and words[0].isdigit() and words[-1].replace("rs", "").isdigit():
                    qty = float(words[0])
                    rate = float(words[-1].replace("rs", ""))
                    name = " ".join(words[1:-1]).title()
                    items.append({
                        "item_name": name,
                        "quantity": qty,
                        "unit": "PCS",
                        "unit_price": rate,
                        "gst_rate": 18.0,
                    })

        return items
