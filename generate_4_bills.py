"""
generate_4_bills.py
-------------------
Generates 4 perfectly filled Medical Invoice bills by drawing text
directly onto the canonical blank template image. No structural
changes are made — the template stays absolutely intact.
All 4 bills are saved to app/golden_templates/.
"""

import os
from PIL import Image, ImageDraw, ImageFont

TEMPLATE_PATH = "app/golden_templates/bajaj_medical_invoice_canonical.png"
OUTPUT_DIR    = "app/golden_templates"

# ── Font helpers ───────────────────────────────────────────────────────────────
def try_font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\verdanab.ttf" if bold else r"C:\Windows\Fonts\verdana.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


DARK    = (10, 10, 10)
DGREY   = (60, 60, 60)
WHITE   = (255, 255, 255)
BLUE_BG = (168, 196, 232)   # matches the template header blue


# ── 4 Patient Datasets ────────────────────────────────────────────────────────
BILLS = [
    # ── BILL 1 ────────────────────────────────────────────────────────────────
    {
        "out":        "bill_1_priya_sharma.png",
        "invoice_no": "INV-2026-40021",
        "date":       "01-Aug-2026",
        "company":    "APOLLO HOSPITALS",
        "address":    "Plot 1A, Jubilee Hills, Hyderabad - 500033",
        "contact":    "+91-40-23607777",
        "email":      "billing@apollohyd.in",
        "gstin":      "36AABCA4099B1ZK",
        "pan":        "AABCA4099B",
        "party": {
            "name":     "Mrs. Priya Sharma",
            "id":       "PID-10023  |  DOB: 18-Mar-1990  (Age: 36)",
            "address":  "H.No. 45, Banjara Hills, Hyderabad, TS - 500034",
            "phone":    "+91-9912345678  |  Insurance Ref: APL-CL-2026-30012",
            "doctor":   "Dr. Meena Reddy, MD (Gynaecology)",
            "ward":     "Maternity Ward — Room 202",
        },
        "items": [
            ("Gynaecology Consultation (Dr. Meena Reddy)",  "998311", "1", "1,500.00", "1,500.00"),
            ("Ultrasound Pelvis (TVS)",                     "998312", "1", "2,200.00", "2,200.00"),
            ("Complete Blood Count (CBC)",                  "998312", "1",   "650.00",   "650.00"),
            ("Vitamin D3 Test",                             "998312", "1",   "900.00",   "900.00"),
            ("Tab: Folic Acid 5mg x 30 tabs",               "300490", "1",   "120.00",   "120.00"),
        ],
        "subtotal":    "5,370.00",
        "cgst":        "9", "cgst_amt": "483.30",
        "sgst":        "9", "sgst_amt": "483.30",
        "grand":       "6,336.60",
        "words":       "Six Thousand Three Hundred Thirty Six Rupees Sixty Paise Only",
        "terms": [
            "Medicines once dispensed will not be returned.",
            "Retain this invoice for insurance claims.",
            "Payment: Cash, UPI, Card, NEFT/RTGS accepted.",
            "Queries: billing@apollohyd.in | Helpline: 1800-200-0200",
        ],
        "license":     "Reg. No.: MCI/TS/2018/00345  |  NABH Accredited  |  Lic. No.: CPCB-TS-MED-2019-1122",
    },

    # ── BILL 2 ────────────────────────────────────────────────────────────────
    {
        "out":        "bill_2_arjun_patel.png",
        "invoice_no": "INV-2026-40022",
        "date":       "03-Aug-2026",
        "company":    "FORTIS HOSPITALS",
        "address":    "Mulund Goregaon Link Road, Mumbai - 400078",
        "contact":    "+91-22-67125000",
        "email":      "billing@fortismumbai.in",
        "gstin":      "27AABCF1122H1ZP",
        "pan":        "AABCF1122H",
        "party": {
            "name":     "Mr. Arjun Patel",
            "id":       "PID-20145  |  DOB: 22-Jul-1982  (Age: 44)",
            "address":  "Block C, Powai, Mumbai, MH - 400076",
            "phone":    "+91-9823456789  |  Insurance Ref: FRT-CL-2026-41221",
            "doctor":   "Dr. Rakesh Joshi, MD (Gastroenterology)",
            "ward":     "General Ward — Room 310",
        },
        "items": [
            ("Gastroenterology Consultation (Dr. Rakesh Joshi)", "998311", "1", "2,000.00", "2,000.00"),
            ("Upper GI Endoscopy (OGD Scopy)",                   "998312", "1", "4,500.00", "4,500.00"),
            ("Liver Function Test (LFT Panel)",                   "998312", "1",   "950.00",   "950.00"),
            ("H. Pylori Antigen Stool Test",                      "998312", "1",   "700.00",   "700.00"),
            ("Cap: Omeprazole 20mg x 14 caps",                    "300490", "1",   "180.00",   "180.00"),
        ],
        "subtotal":    "8,330.00",
        "cgst":        "9", "cgst_amt": "749.70",
        "sgst":        "9", "sgst_amt": "749.70",
        "grand":       "9,829.40",
        "words":       "Nine Thousand Eight Hundred Twenty Nine Rupees Forty Paise Only",
        "terms": [
            "Medicines once dispensed will not be returned.",
            "Retain this invoice for insurance claims.",
            "Payment: Cash, UPI, Card, NEFT/RTGS accepted.",
            "Queries: billing@fortismumbai.in | Helpline: 1800-111-4567",
        ],
        "license":     "Reg. No.: MCI/MH/2015/07821  |  NABH Accredited  |  Lic. No.: CPCB-MH-MED-2016-8891",
    },

    # ── BILL 3 ────────────────────────────────────────────────────────────────
    {
        "out":        "bill_3_sunita_verma.png",
        "invoice_no": "INV-2026-40023",
        "date":       "05-Aug-2026",
        "company":    "MAX SUPER SPECIALITY HOSPITAL",
        "address":    "108A, IP Extension, Patparganj, Delhi - 110092",
        "contact":    "+91-11-26515050",
        "email":      "billing@maxdelhiip.in",
        "gstin":      "07AABCM7734K1ZQ",
        "pan":        "AABCM7734K",
        "party": {
            "name":     "Mrs. Sunita Verma",
            "id":       "PID-30389  |  DOB: 09-Nov-1978  (Age: 47)",
            "address":  "Flat 501, Sector 9, Rohini, Delhi - 110085",
            "phone":    "+91-9811223344  |  Insurance Ref: MAX-CL-2026-55310",
            "doctor":   "Dr. Anil Kumar, MD (Endocrinology)",
            "ward":     "OPD — Cabin 5",
        },
        "items": [
            ("Endocrinology Consultation (Dr. Anil Kumar)",  "998311", "1", "1,800.00", "1,800.00"),
            ("Thyroid Profile — T3, T4, TSH",                "998312", "1",   "750.00",   "750.00"),
            ("HbA1c — Glycated Haemoglobin",                  "998312", "1",   "700.00",   "700.00"),
            ("Fasting Blood Glucose (FBG)",                   "998312", "1",   "200.00",   "200.00"),
            ("Tab: Levothyroxine 50mcg x 30 tabs",            "300490", "1",   "140.00",   "140.00"),
        ],
        "subtotal":    "3,590.00",
        "cgst":        "9", "cgst_amt": "323.10",
        "sgst":        "9", "sgst_amt": "323.10",
        "grand":       "4,236.20",
        "words":       "Four Thousand Two Hundred Thirty Six Rupees Twenty Paise Only",
        "terms": [
            "Medicines once dispensed will not be returned.",
            "Retain this invoice for insurance claims.",
            "Payment: Cash, UPI, Card, NEFT/RTGS accepted.",
            "Queries: billing@maxdelhiip.in | Helpline: 1800-300-0900",
        ],
        "license":     "Reg. No.: MCI/DL/2017/03311  |  NABH Accredited  |  Lic. No.: CPCB-DL-MED-2018-4412",
    },

    # ── BILL 4 ────────────────────────────────────────────────────────────────
    {
        "out":        "bill_4_kiran_nair.png",
        "invoice_no": "INV-2026-40024",
        "date":       "07-Aug-2026",
        "company":    "MANIPAL HOSPITALS",
        "address":    "98, HAL Airport Road, Bengaluru, KA - 560017",
        "contact":    "+91-80-25023000",
        "email":      "billing@manipalbng.in",
        "gstin":      "29AABCM5521R1ZB",
        "pan":        "AABCM5521R",
        "party": {
            "name":     "Mr. Kiran Nair",
            "id":       "PID-40512  |  DOB: 14-Feb-1995  (Age: 31)",
            "address":  "No. 22, Indiranagar, 100 Ft Road, Bengaluru, KA - 560038",
            "phone":    "+91-9886554433  |  Insurance Ref: MNP-CL-2026-66781",
            "doctor":   "Dr. Suresh Menon, MS (Orthopaedics)",
            "ward":     "Ortho Ward — Bed 7",
        },
        "items": [
            ("Orthopaedic Consultation (Dr. Suresh Menon)",  "998311", "1", "1,200.00", "1,200.00"),
            ("X-Ray Right Knee AP & Lateral",                "998312", "1",   "500.00",   "500.00"),
            ("MRI Right Knee Joint without Contrast",        "998312", "1", "6,000.00", "6,000.00"),
            ("Physiotherapy Session (60 mins)",              "998312", "2",   "900.00", "1,800.00"),
            ("Tab: Diclofenac 50mg x 10 tabs",               "300490", "1",   "110.00",   "110.00"),
        ],
        "subtotal":    "9,610.00",
        "cgst":        "9", "cgst_amt": "864.90",
        "sgst":        "9", "sgst_amt": "864.90",
        "grand":       "11,339.80",
        "words":       "Eleven Thousand Three Hundred Thirty Nine Rupees Eighty Paise Only",
        "terms": [
            "Medicines once dispensed will not be returned.",
            "Retain this invoice for insurance claims.",
            "Payment: Cash, UPI, Card, NEFT/RTGS accepted.",
            "Queries: billing@manipalbng.in | Helpline: 1800-102-8484",
        ],
        "license":     "Reg. No.: MCI/KA/2016/09923  |  NABH Accredited  |  Lic. No.: CPCB-KA-MED-2017-6634",
    },
]


# ── Core renderer ──────────────────────────────────────────────────────────────
def fill_bill(data: dict):
    """
    Opens the canonical blank template and draws all patient data
    precisely into each field without touching the template structure.
    """
    tmpl = Image.open(TEMPLATE_PATH).convert("RGB")
    W, H = tmpl.size
    draw = ImageDraw.Draw(tmpl)

    # Scale factor (template was drawn at ~800px wide)
    SX = W / 800.0
    SY = H / 1000.0

    def sx(px): return int(px * SX)
    def sy(py): return int(py * SY)

    # ── Fonts (scaled) ────────────────────────────────────────────────────────
    f_tiny = try_font(max(8,  int(9  * SX)))
    f_sm   = try_font(max(9,  int(10 * SX)))
    f_sm_b = try_font(max(9,  int(10 * SX)), bold=True)
    f_md   = try_font(max(10, int(11 * SX)))
    f_md_b = try_font(max(10, int(11 * SX)), bold=True)
    f_lg_b = try_font(max(11, int(12 * SX)), bold=True)

    def tw(text, font):
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0]

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 1  — Top header (blue bar): TAX INVOICE | INVOICE NO / DATE
    # The blue bar sits at y≈14..46 in the 800×1000 template
    # INVOICE NO and DATE go on the right side of the split (~x=510)
    # ─────────────────────────────────────────────────────────────────────────
    draw.text((sx(510), sy(16)), f"INV NO: {data['invoice_no']}", fill=DARK, font=f_sm_b)
    draw.text((sx(510), sy(30)), f"DATE: {data['date']}",         fill=DARK, font=f_sm_b)

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 2  — Company name (centered in the "MEDICAL INVOICE" row, y≈50..80)
    # ─────────────────────────────────────────────────────────────────────────
    name_w = tw(data["company"], f_lg_b)
    draw.text(((W - name_w) // 2, sy(55)), data["company"], fill=DARK, font=f_lg_b)

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 3  — Address / Contact / GSTIN  (y≈82..140)
    # ─────────────────────────────────────────────────────────────────────────
    draw.text((sx(95),  sy(90)),  data["address"],         fill=DARK, font=f_sm)
    draw.text((sx(118), sy(104)), data["contact"],         fill=DARK, font=f_sm)
    draw.text((sx(280), sy(104)), data["email"],           fill=DARK, font=f_sm)
    draw.text((sx(80),  sy(118)), data["gstin"],           fill=DARK, font=f_sm_b)
    draw.text((sx(290), sy(118)), data["pan"],             fill=DARK, font=f_sm_b)

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 4  — Party Details  (y≈142..230)
    # ─────────────────────────────────────────────────────────────────────────
    p = data["party"]
    py = sy(158)
    line_h = sy(16)
    rows = [
        ("Patient Name :",     p["name"]),
        ("Patient ID :",       p["id"]),
        ("Address :",          p["address"]),
        ("Phone :",            p["phone"]),
        ("Attending Doctor :", p["doctor"]),
        ("Ward / Bed :",       p["ward"]),
    ]
    for label, val in rows:
        draw.text((sx(38),  py), label, fill=(100,100,100), font=f_sm)
        draw.text((sx(165), py), val,   fill=DARK,          font=f_sm)
        py += line_h

    # ─────────────────────────────────────────────────────────────────────────
    # ROW 5  — Items table
    # Template columns (approx x positions in 800px space):
    #   Desc: 34..490   HSN: 490..580   Qty: 580..640   Rate: 640..710  Amt: 710..770
    # Table rows start at y≈260, row height ≈30
    # ─────────────────────────────────────────────────────────────────────────
    CX_DESC  = sx(36)
    CX_HSN   = sx(491)
    CX_QTY_R = sx(638)   # right-align qty here
    CX_RATE_R= sx(710)   # right-align rate here
    CX_AMT_R = sx(766)   # right-align amount here

    row_y = sy(261)
    ROW_H = sy(30)

    for desc, hsn, qty, rate, amt in data["items"]:
        draw.text((CX_DESC, row_y + sy(8)), desc, fill=DARK, font=f_sm)
        draw.text((CX_HSN,  row_y + sy(8)), hsn,  fill=DARK, font=f_sm)
        for val, rx in [(qty, CX_QTY_R), (rate, CX_RATE_R), (amt, CX_AMT_R)]:
            vw = tw(val, f_sm_b)
            draw.text((rx - vw, row_y + sy(8)), val, fill=DARK, font=f_sm_b)
        row_y += ROW_H

    # ─────────────────────────────────────────────────────────────────────────
    # Totals block — right side (y≈ after items rows)
    # Template has: Total | CGST @ % | SGST @ % | Grand Total
    # Approximate y positions in 800×1000: 444, 465, 490, 513
    # ─────────────────────────────────────────────────────────────────────────
    tot_label_x = sx(590)
    tot_val_x   = CX_AMT_R

    tot_rows_y = [sy(444), sy(464), sy(489)]
    labels = [
        f"INR {data['subtotal']}",
        f"INR {data['cgst_amt']}",
        f"INR {data['sgst_amt']}",
    ]
    for i, (yr, lbl) in enumerate(zip(tot_rows_y, labels)):
        vw = tw(lbl, f_sm_b)
        draw.text((tot_val_x - vw, yr + sy(4)), lbl, fill=DARK, font=f_sm_b)

    # CGST % and SGST % labels inline
    draw.text((sx(640), sy(464)), f"{data['cgst']} %", fill=DARK, font=f_sm_b)
    draw.text((sx(640), sy(489)), f"{data['sgst']} %", fill=DARK, font=f_sm_b)

    # Grand Total row (blue background already in template)
    grand_str = f"INR {data['grand']}"
    gw = tw(grand_str, f_md_b)
    draw.text((tot_val_x - gw, sy(510) + sy(4)), grand_str, fill=DARK, font=f_md_b)

    # ─────────────────────────────────────────────────────────────────────────
    # Warranty / Terms  (left side, y≈555..610)
    # ─────────────────────────────────────────────────────────────────────────
    ty = sy(563)
    for i, term in enumerate(data["terms"]):
        draw.text((sx(38), ty), f"{i+1}. {term}", fill=DGREY, font=f_tiny)
        ty += sy(13)

    # ─────────────────────────────────────────────────────────────────────────
    # Total in Words  (y≈620..640)
    # ─────────────────────────────────────────────────────────────────────────
    draw.text((sx(38), sy(632)), data["words"], fill=DARK, font=f_sm_b)

    # ─────────────────────────────────────────────────────────────────────────
    # Footer — "For YOUR COMPANY NAME"  (y≈658..678)
    # ─────────────────────────────────────────────────────────────────────────
    draw.text((sx(38), sy(660)), f"For {data['company']}", fill=DARK, font=f_md_b)

    # ─────────────────────────────────────────────────────────────────────────
    # License bar at very bottom (y≈690..710 in template)
    # ─────────────────────────────────────────────────────────────────────────
    lic_text = data["license"]
    lw2 = tw(lic_text, f_sm_b)
    draw.text(((W - lw2) // 2, sy(700)), lic_text, fill=DARK, font=f_sm_b)

    return tmpl


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for bill in BILLS:
        out_path = os.path.join(OUTPUT_DIR, bill["out"])
        print(f"Generating: {out_path} ...")
        img = fill_bill(bill)
        img.save(out_path, "PNG", dpi=(150, 150))
        print(f"  OK Saved ({img.size[0]}x{img.size[1]} px)")
    print("\nAll 4 bills generated successfully.")


if __name__ == "__main__":
    main()
