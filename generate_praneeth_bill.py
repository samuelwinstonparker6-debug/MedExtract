"""
generate_praneeth_bill.py
---------------------------
Generates a filled hospital medical invoice matching the exact template format requested.
Patient Name: praneeth
License Key at bottom: WIsN68
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

ARTIFACT_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\8c056a35-8b83-42c0-9e91-8f046cb74b15"
OUTPUT_PATH_1 = os.path.join(ARTIFACT_DIR, "hospital_bill_praneeth.png")
OUTPUT_PATH_2 = r"c:\Users\DELL\Desktop\Baja Finserv Health Pvt. Ltd\MedExtract\hospital_bill_praneeth.png"

# Colors
BLUE_HEADER    = (168, 196, 232)
BLUE_GRAND     = (168, 196, 232)
BLACK          = (0, 0, 0)
DARK           = (20, 20, 20)
WHITE          = (255, 255, 255)
LIGHT_GREY     = (210, 210, 210)
MID_GREY       = (100, 100, 100)
BORDER         = (0, 0, 0)

DATA = {
    "invoice_no":     "INV-2026-08492",
    "date":           "07-Aug-2026",
    "provider_name":  "CARE & CURE HOSPITALS & HEALTHCARE",
    "address":        "Plot No. 45, Healthcare Boulevard, Sector 12, Hyderabad - 500081",
    "contact":        "+91-40-67890123",
    "email":          "billing@careandcurehospitals.com",
    "gstin":          "36AAACC1234F1Z5",
    "pan":            "AAACC1234F",
    "license_key":    "WIsN68",
    # Patient Details
    "patient_name":   "praneeth",
    "patient_id":     "PID-88492",
    "patient_age_sex":"29 Yrs / Male",
    "patient_addr":   "Plot 42, Jubilee Hills, Hyderabad, Telangana - 500033",
    "patient_phone":  "+91-9876543210",
    "attending_dr":   "Dr. A. K. Sharma (MD, Internal Medicine)",
    "ward_bed":       "OPD — Room 104",
    "insurance_id":   "BJFIN-CL-2026-98312",
    # Table Items
    "items": [
        ("Emergency Consultation & Clinical Triage (Dr. A.K. Sharma)", "998311", "1", "1,500.00", "1,500.00"),
        ("Complete Blood Count (CBC) with Differential",               "998312", "1",   "850.00",   "850.00"),
        ("Lipid Profile & Comprehensive Metabolic Panel",              "998312", "1", "1,200.00", "1,200.00"),
        ("Electrocardiogram (ECG - 12 Lead)",                          "998312", "1",   "650.00",   "650.00"),
        ("Chest X-Ray PA View (Digital Radiography)",                  "998312", "1",   "850.00",   "850.00"),
        ("IV Infusion & Medication Supplies",                          "300490", "1",   "580.00",   580.00),
    ],
    "subtotal":   "5,630.00",
    "cgst_rate":  "9",
    "cgst_amt":   "506.70",
    "sgst_rate":  "9",
    "sgst_amt":   "506.70",
    "grand_total": "6,643.40",
    "total_words": "Six Thousand Six Hundred Forty-Three Rupees and Forty Paise Only",
    "terms": [
        "Medicines once dispensed will not be accepted for return or exchange.",
        "Please retain this invoice for insurance reimbursement claims.",
        "Payment accepted: Cash, UPI, Credit/Debit Card, NEFT/RTGS.",
        "For billing queries contact: billing@careandcurehospitals.com | Helpline: 1800-123-4567",
    ],
}

def try_font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\Arial Bold.ttf" if bold else r"C:\Windows\Fonts\Arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

def text_w(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]

def draw_invoice():
    W, H = 860, 1220
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    L, R, T = 28, 832, 14
    CW = R - L

    f_tiny   = try_font(12)
    f_sm     = try_font(13)
    f_md     = try_font(15)
    f_md_b   = try_font(15, bold=True)
    f_lg_b   = try_font(17, bold=True)
    f_xl_b   = try_font(22, bold=True)
    f_title  = try_font(24, bold=True)

    y = T

    # Outer border
    draw.rectangle([L, T, R, H - 20], outline=BLACK, width=2)

    # ── ROW 1: Blue TAX INVOICE header bar ──────────────────────────────────
    hdr_bot = y + 42
    split_x = L + int(CW * 0.64)

    draw.rectangle([L, y, R, hdr_bot], fill=BLUE_HEADER, outline=BLACK, width=1)
    draw.line([(split_x, y), (split_x, hdr_bot)], fill=BLACK, width=1)

    # "TAX INVOICE"
    label = "TAX INVOICE"
    lw = text_w(draw, label, f_lg_b)
    draw.text(((L + split_x - lw) // 2, y + 12), label, fill=BLACK, font=f_lg_b)

    # INVOICE NO / DATE
    draw.text((split_x + 10, y + 6),  f"INVOICE NO:  {DATA['invoice_no']}", fill=BLACK, font=f_sm)
    draw.text((split_x + 10, y + 23), f"DATE:              {DATA['date']}",  fill=BLACK, font=f_sm)

    y = hdr_bot

    # ── ROW 2: MEDICAL INVOICE title ─────────────────────────────────────────
    pname_bot = y + 55
    draw.rectangle([L, y, R, pname_bot], outline=BLACK, width=1)
    draw.text(((W - text_w(draw, DATA["provider_name"], f_lg_b)) // 2, y + 6),
              DATA["provider_name"], fill=BLACK, font=f_lg_b)
    draw.text(((W - text_w(draw, "MEDICAL INVOICE", f_md_b)) // 2, y + 28),
              "MEDICAL INVOICE", fill=(80, 80, 80), font=f_md_b)

    y = pname_bot

    # ── ROW 3: Address / Contact / GSTIN fields ──────────────────────────────
    fields_bot = y + 60
    draw.rectangle([L, y, R, fields_bot], outline=BLACK, width=1)

    draw.text((L + 10, y + 6),   "Address:",     fill=BLACK, font=f_sm)
    draw.text((L + 75, y + 6),  DATA["address"], fill=DARK,  font=f_sm)
    draw.line([(L + 72, y + 18), (L + 340, y + 18)], fill=LIGHT_GREY, width=1)

    draw.text((L + 10,  y + 24), "Contact No.:", fill=BLACK, font=f_sm)
    draw.text((L + 88,  y + 24), DATA["contact"], fill=DARK,  font=f_sm)
    draw.line([(L + 85, y + 36), (L + 240, y + 36)], fill=LIGHT_GREY, width=1)

    draw.text((L + 270, y + 24), "Email:",       fill=BLACK, font=f_sm)
    draw.text((L + 315, y + 24), DATA["email"],   fill=DARK,  font=f_sm)
    draw.line([(L + 312, y + 36), (R - 15, y + 36)], fill=LIGHT_GREY, width=1)

    draw.text((L + 10,  y + 42), "GSTIN:",       fill=BLACK, font=f_sm)
    draw.text((L + 60,  y + 42), DATA["gstin"],   fill=DARK,  font=f_md_b)
    draw.line([(L + 58, y + 54), (L + 240, y + 54)], fill=LIGHT_GREY, width=1)

    draw.text((L + 270, y + 42), "PAN No.:",     fill=BLACK, font=f_sm)
    draw.text((L + 330, y + 42), DATA["pan"],     fill=DARK,  font=f_md_b)
    draw.line([(L + 328, y + 54), (R - 15, y + 54)], fill=LIGHT_GREY, width=1)

    y = fields_bot

    # ── ROW 4: PARTY DETAILS box ─────────────────────────────────────────────
    party_bot = y + 125
    draw.rectangle([L, y, R, party_bot], outline=BLACK, width=1)
    draw.text((L + 10, y + 6), "PARTY DETAILS >", fill=BLACK, font=f_md_b)

    pd = [
        ("Patient Name",     DATA["patient_name"]),
        ("Patient ID",       DATA["patient_id"] + "   |   Age/Sex: " + DATA["patient_age_sex"]),
        ("Address",          DATA["patient_addr"]),
        ("Contact Phone",    DATA["patient_phone"] + "   |   Insurance ID: " + DATA["insurance_id"]),
        ("Attending Doctor", DATA["attending_dr"]),
        ("Ward / Bed",       DATA["ward_bed"]),
    ]
    py = y + 26
    for lbl, val in pd:
        draw.text((L + 16, py), f"{lbl} :", fill=MID_GREY, font=f_sm)
        # Emphasize praneeth name clearly
        if lbl == "Patient Name":
            draw.text((L + 150, py), val, fill=BLACK, font=f_md_b)
        else:
            draw.text((L + 150, py), val, fill=DARK, font=f_sm)
        py += 16

    y = party_bot

    # ── ROW 5: Items Table ───────────────────────────────────────────────────
    cx_desc   = L
    cx_hsn    = L + int(CW * 0.58)
    cx_qty    = cx_hsn + 95
    cx_rate   = cx_qty + 55
    cx_amt    = R

    th_bot = y + 36
    draw.rectangle([L, y, R, th_bot], outline=BLACK, width=1)

    draw.text((cx_desc + 8, y + 8),  "Particulars (Descriptions & Specifications)", fill=BLACK, font=f_md_b)
    draw.text((cx_hsn + 4,  y + 4),  "HSN /",    fill=BLACK, font=f_sm)
    draw.text((cx_hsn + 4,  y + 18), "SAC Code", fill=BLACK, font=f_sm)
    draw.text((cx_qty + 10, y + 10), "Qty",       fill=BLACK, font=f_sm)
    draw.text((cx_rate + 8, y + 10), "Rate",      fill=BLACK, font=f_sm)
    draw.text((cx_amt - 60, y + 10), "Amount",    fill=BLACK, font=f_sm)

    iy = th_bot
    ROW_H = 28
    for i, (desc, hsn, qty, rate, amt) in enumerate(DATA["items"]):
        row_bot = iy + ROW_H
        draw.rectangle([L, iy, R, row_bot], fill=WHITE, outline=LIGHT_GREY, width=1)

        draw.text((cx_desc + 8, iy + 7), desc, fill=DARK, font=f_sm)
        draw.text((cx_hsn + 4,  iy + 7), hsn,  fill=DARK, font=f_sm)

        for val_str, col_r in [(qty, cx_qty + 35), (str(rate), cx_rate + 50), (str(amt), cx_amt - 10)]:
            vw = text_w(draw, val_str, f_sm)
            draw.text((col_r - vw, iy + 7), val_str, fill=DARK, font=f_sm)

        iy = row_bot

    # Pad remaining empty rows to fill visual height
    for i in range(3):
        row_bot = iy + ROW_H
        draw.rectangle([L, iy, R, row_bot], fill=WHITE, outline=LIGHT_GREY, width=1)
        iy = row_bot

    # ── ROW 6: Totals & Terms ────────────────────────────────────────────────
    totals_x = cx_qty
    wt_top = iy

    def tot_row(label, val, fill_col=None):
        nonlocal iy
        bot = iy + 24
        if fill_col:
            draw.rectangle([totals_x, iy, R, bot], fill=fill_col, outline=BLACK, width=1)
        else:
            draw.rectangle([totals_x, iy, R, bot], fill=WHITE, outline=BLACK, width=1)

        draw.text((totals_x + 6, iy + 4), label, fill=BLACK, font=f_md_b if fill_col else f_sm)
        if val:
            vw = text_w(draw, val, f_md_b if fill_col else f_sm)
            draw.text((R - vw - 8, iy + 4), val, fill=BLACK, font=f_md_b if fill_col else f_sm)
        iy = bot

    tot_row("Total",                    DATA['subtotal'])
    tot_row(f"CGST @ {DATA['cgst_rate']} %", DATA['cgst_amt'])
    tot_row(f"SGST @ {DATA['sgst_rate']} %", DATA['sgst_amt'])
    tot_row("Grand Total",               DATA['grand_total'], fill_col=BLUE_GRAND)
    wt_bot = iy

    # Terms & Conditions box on left side of totals
    draw.rectangle([L, wt_top, totals_x, wt_bot], outline=BLACK, width=1)
    draw.text((L + 8, wt_top + 4), "Warranty related Terms & Conditions", fill=BLACK, font=f_sm)
    for ti, num in enumerate(["1.", "2.", "3.", "4."]):
        term_txt = DATA["terms"][ti] if ti < len(DATA["terms"]) else ""
        draw.text((L + 8, wt_top + 22 + ti * 16), f"{num} {term_txt[:55]}", fill=DARK, font=f_tiny)

    y = wt_bot

    # Vertical column dividers for main table
    for cx in [cx_hsn, cx_qty, cx_rate]:
        draw.line([(cx, th_bot - 36), (cx, wt_top)], fill=BLACK, width=1)
    draw.line([(totals_x, wt_top), (totals_x, wt_bot)], fill=BLACK, width=1)

    # ── ROW 7: Total Amount (INR - In Words) ─────────────────────────────────
    words_bot = y + 45
    draw.rectangle([L, y, R, words_bot], outline=BLACK, width=1)
    draw.text((L + 8, y + 6), "Total Amount (INR - In Words):", fill=BLACK, font=f_sm)
    draw.line([(L + 8, y + 22), (R - 8, y + 22)], fill=BLACK, width=1)
    draw.text((L + 12, y + 25), DATA["total_words"], fill=BLACK, font=f_md_b)

    y = words_bot

    # ── ROW 8: Company Name / Footer ─────────────────────────────────────────
    footer_bot = y + 45
    draw.rectangle([L, y, R, footer_bot], outline=BLACK, width=1)
    draw.text((L + 10, y + 12), f"For {DATA['provider_name']}", fill=BLACK, font=f_md_b)
    draw.text((R - 180, y + 12), "Authorized Signatory", fill=MID_GREY, font=f_sm)

    # ── License Key Footer ───────────────────────────────────────────────────
    lic_top = footer_bot + 6
    lic_bot = H - 24
    draw.rectangle([L, lic_top, R, lic_bot], fill=(245, 247, 250), outline=BLACK, width=1)
    lic_text = f"License key : {DATA['license_key']}"
    lw = text_w(draw, lic_text, f_lg_b)
    draw.text(((W - lw) // 2, lic_top + 6), lic_text, fill=BLACK, font=f_lg_b)

    # Outer border final stroke
    draw.rectangle([L, T, R, H - 20], outline=BLACK, width=2)

    return img

def main():
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_PATH_2), exist_ok=True)
    print("Generating exact template hospital bill for praneeth...")
    img = draw_invoice()
    img.save(OUTPUT_PATH_1, "PNG", dpi=(150, 150))
    img.save(OUTPUT_PATH_2, "PNG", dpi=(150, 150))
    print(f"Saved artifact 1: {OUTPUT_PATH_1}")
    print(f"Saved artifact 2: {OUTPUT_PATH_2}")

if __name__ == "__main__":
    main()
