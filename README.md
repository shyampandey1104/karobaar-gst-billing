# 🛍️ Karobaar (कारोबार) — Best GST Billing, Khata & Inventory Software for Small Businesses in India

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![GST Ready](https://img.shields.io/badge/GST-India%20Compliant-orange.svg)](https://www.gst.gov.in)
[![UPI Enabled](https://img.shields.io/badge/UPI-Instant%20QR%20Pay-25D366.svg)](https://www.npci.org.in)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **"Aapka Apna Digital Munimji"** — Ek modern, fast aur user-friendly GST Invoicing, Customer Khata (Lena Hai / Dena Hai), Inventory Stock aur Barcode Billing Software jo Indian Vyapariyo aur MSMEs ke liye tailor-made banaya gaya hai.

In-depth alternative inspired by popular software like **Vyapar App**, with modern web architecture and cutting-edge additional features (AI Voice Dictation billing and instant dynamic UPI payment QR codes on bills).

---

## ✨ Key Features (Vyapar Core + Modern Innovations)

### 1. 🧾 GST Tax Invoicing (बिक्री बिल)
- Full B2B & B2C Tax Invoices with HSN/SAC codes.
- Automatic tax splits:
  - **Intra-State (Same state)**: CGST + SGST split (e.g. 9% + 9% = 18%).
  - **Inter-State (Different state)**: IGST (18%).
- Cash, UPI, Bank Transfer, and Cheque payment modes.
- Instant A4 Tax Invoice & Thermal Receipt format print layouts.

### 2. 📱 Dynamic UPI QR Codes on Every Invoice
- Automatically embeds standard NPCI UPI payment QR intent (`upi://pay?pa=...&am=...`) right on the customer's bill.
- Customers can scan directly with **Google Pay, PhonePe, Paytm, or BHIM UPI** to settle the exact invoice amount.

### 3. 👥 Customer & Supplier Khata (उधारी / जमा खाता)
- Real-time **"Lena Hai" (You'll Receive)** and **"Dena Hai" (You'll Pay)** indicators.
- 1-Click WhatsApp payment collection reminder links pre-drafted in courteous Hindi/English.

### 4. 📦 Inventory & Stock Management (सामान और स्टॉक)
- Item barcode tracking, sale price vs purchase price margins.
- **Low Stock Alerts** with automatic warning badges when items breach safety reorder limits.

### 5. 🎙️ AI Voice Dictation Quick Billing (बोलकर बिल बनाओ)
- Shopkeeper can dictate in natural Hindi / Hinglish:
  > *"5 packet parle-g 10 rupaye, 2 kilo basmati rice 120 rupaye"*
- The built-in NLP engine automatically parses quantities, units, item names, and rates into line items!

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────┐
│            Karobaar Responsive Web App (SPA)           │
│     (Tailwind CSS + Alpine.js + Printable Invoices)     │
└───────────────────────────┬────────────────────────────┘
                            │ REST JSON
                            ▼
┌────────────────────────────────────────────────────────┐
│              FastAPI Backend Engine (Python)           │
│  • GST Tax Calculator (CGST / SGST / IGST)             │
│  • Dynamic NPCI UPI QR Generator                       │
│  • Customer & Supplier Khata Ledger                    │
│  • AI Voice / Text Dictation Parser                    │
│  • Low-Stock Inventory Management                      │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/shyampandey1104/karobaar-gst-billing.git
cd karobaar-gst-billing
pip install -r requirements.txt
```

### 2. Run Application

```bash
uvicorn backend.main:app --reload --port 8080
```
- Open `http://localhost:8080` in your browser.
- Open `http://localhost:8080/docs` for interactive Swagger API documentation.

### 3. Docker Deployment

```bash
docker compose up -d --build
```

---

## 🧪 Running Unit Tests

```bash
pytest tests/ -v
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

Author: **Shyamkumar Bhupendra Pandey** ([@shyampandey1104](https://github.com/shyampandey1104))
