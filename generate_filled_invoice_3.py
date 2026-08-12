"""
generate_filled_invoice_3.py
---------------------------
Generates a filled Medical Invoice using the template design.
Custom credentials and matter as requested.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image, ImageDraw, ImageFont

OUTPUT_PATH = "app/golden_templates/filled_sample_invoice_3.png"

# ── Colors ─────────────────────────────────────────────────────────────────────
HEADER_COLOR   = (216, 192, 203)
GRAND_COLOR    = (202, 169, 182)
BLACK          = (0, 0, 0)
DARK           = (20, 20, 20)
WHITE          = (255, 255, 255)
LIGHT_GREY     = (210, 210, 210)
MID_GREY       = (100, 100, 100) 
BORDER         = (60, 80, 120)
WATERMARK      = (245, 247, 252)

# ── Different Patient / Provider Data ──────────────────────────────────────────
DATA = {
    "invoice_no":     "INV-2026-10293",
    "date":           "20-Oct-2026",
    "provider_name":  "MAXCARE HEALTH CLINIC",
    "address":        "55, Jubilee Hills, Hyderabad, Telangana - 500033",
    "contact":        "+91-40-23456789",
    "email":          "contact@maxcareclinic.in",
    "gstin":          "36AABCM9988L1ZY",
    "pan":            "AABCM9988L",
    "license":        "Reg. No.: MCI/TG/2020/99812  |  NABH Accredited  |  Lic. No.: CPCB-TG-MED-2022-4455",
    # Party (Patient)
    "patient_name":   "Mr. Ramesh K",
    "patient_id":     "PID-33291",
    "patient_dob":    "05-Jan-1975  (Age: 51)",
    "patient_addr":   "Plot 11, Banjara Hills, Hyderabad, TS - 500034",
    "patient_phone":  "+91-9888123456",
    "attending_dr":   "Dr. Suresh Babu, MD (Orthopedics)",
    "ward_bed":       "Private Ward — Room 101",
    "insurance_id":   "MAX-HLTH-2026-11223",
    # Items: (description, hsn_sac, qty, rate, amount)
    "items": [
        ("Orthopedic Consultation (Dr. Suresh Babu)",  "998311", "1",   "1,200.00",  "1,200.00"),
        ("X-Ray Right Knee Joint AP/LAT",             "998312", "1",     "600.00",    "600.00"),
        ("MRI Lumbar Spine without Contrast",         "998312", "1",   "5,500.00",  "5,500.00"),
        ("Physiotherapy Session (45 mins)",           "998312", "1",     "800.00",    "800.00"),
        ("Tablet: Etoricoxib 90mg × 10 tabs",         "300490", "1",     "150.00",    "150.00"),
    ],
    "subtotal":   "8,250.00",
    "cgst_rate":  "9",
    "cgst_amt":   "742.50",
    "sgst_rate":  "9",
    "sgst_amt":   "742.50",
    "grand_total": "9,735.00",
    "total_words": "Nine Thousand Seven Hundred Thirty Five Rupees Only",
    # Warranty/Terms
    "terms": [
        "Medicines once dispensed will not be returned.",
        "Retain invoice for insurance claims.",
        "Payment accepted: Cash, UPI, Card.",
    ],
}


def try_font(size, bold=False):
    """Try to load a real font, fall back gracefully."""
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\Arial Bold.ttf" if bold else r"C:\Windows\Fonts\Arial.ttf",
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


def text_w(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]


def draw_invoice():
    W, H = 860, 1200
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    L, R, T = 28, 832, 35
    CW = R - L

    # ── Fonts ─────────────────────────────────────────────────────────────────
    f_tiny   = try_font(12)
    f_sm     = try_font(14)
    f_sm_b   = try_font(14, bold=True)
    f_md     = try_font(16)
    f_md_b   = try_font(16, bold=True)
    f_lg_b   = try_font(18, bold=True)
    f_xl_b   = try_font(24, bold=True)
    f_title  = try_font(26, bold=True)

    y = T

    # ── Outer border ──────────────────────────────────────────────────────────
    def outer_rect():
        draw.rectangle([L-2, T-2, R+2, H-40], outline=BORDER, width=2)
    outer_rect()

    # ── ROW 1: HEADER ───────────────────────────────────────
    hdr_bot = y + 40
    split_x = L + int(CW * 0.62)

    draw.rectangle([L, y, R, hdr_bot], fill=HEADER_COLOR, outline=BLACK, width=1)

    label = "TAX INVOICE"
    lw = text_w(draw, label, f_lg_b)
    draw.text(((L + split_x - lw) // 2 + lw//8, y + 11), label, fill=BLACK, font=f_lg_b)

    draw.text((split_x + 24, y + 6),  f"INVOICE NO: {DATA['invoice_no']}", fill=BLACK, font=f_sm_b)
    draw.text((split_x + 24, y + 22), f"DATE: {DATA['date']}",  fill=BLACK, font=f_sm_b)

    y = hdr_bot + 1

    # ── ROW 2: Provider name ──────────────────────────────────────────────────
    pname_bot = y + 38
    draw.rectangle([L, y, R, pname_bot], outline=BLACK, width=1)
    pname_w = text_w(draw, DATA["provider_name"], f_title)
    draw.text(((W - pname_w) // 2, y + 6), DATA["provider_name"], fill=BLACK, font=f_title)
    draw.text(((W - text_w(draw, "MEDICAL INVOICE", f_md_b)) // 2, y + 26),
              "MEDICAL INVOICE", fill=(80, 80, 80), font=f_md_b)

    y = pname_bot + 1

    # ── ROW 3: Address / Contact / GSTIN fields ───────────────────────────────
    fields_bot = y + 54
    draw.rectangle([L, y, R, fields_bot], outline=BLACK, width=1)

    draw.text((L + 8, y + 5),  "Address :",    fill=MID_GREY, font=f_sm)
    draw.text((L + 75, y + 5), DATA["address"], fill=DARK,     font=f_sm)

    draw.text((L + 8,  y + 21), "Contact No. :", fill=MID_GREY, font=f_sm)
    draw.text((L + 88, y + 21), DATA["contact"], fill=DARK,     font=f_sm)
    draw.text((L + 300, y + 21), "Email :",       fill=MID_GREY, font=f_sm)
    draw.text((L + 344, y + 21), DATA["email"],   fill=DARK,     font=f_sm)

    draw.text((L + 8,  y + 37), "GSTIN :",       fill=MID_GREY, font=f_sm)
    draw.text((L + 58, y + 37), DATA["gstin"],    fill=DARK,     font=f_md_b)
    draw.text((L + 300, y + 37), "PAN No. :",     fill=MID_GREY, font=f_sm)
    draw.text((L + 356, y + 37), DATA["pan"],     fill=DARK,     font=f_md_b)

    y = fields_bot + 1

    # ── ROW 4: PARTY DETAILS box ──────────────────────────────────────────────
    party_bot = y + 110
    draw.rectangle([L, y, R, party_bot], outline=BLACK, width=1)
    draw.text((L + 8, y + 5), "PARTY DETAILS  :", fill=BLACK, font=f_md_b)

    pd = [
        ("Patient Name",     DATA["patient_name"]),
        ("Patient ID",       DATA["patient_id"] + "   |   DOB: " + DATA["patient_dob"]),
        ("Address",          DATA["patient_addr"]),
        ("Phone",            DATA["patient_phone"] + "   |   Insurance Ref: " + DATA["insurance_id"]),
        ("Attending Doctor", DATA["attending_dr"]),
        ("Ward / Bed",       DATA["ward_bed"]),
    ]
    py = y + 20
    for lbl, val in pd:
        draw.text((L + 12, py), f"{lbl} :", fill=MID_GREY, font=f_sm)
        draw.text((L + 145, py), val,         fill=DARK,     font=f_sm)
        py += 15

    y = party_bot + 1

    # ── ROW 5: Items Table ────────────────────────────────────────────────────
    cx_desc   = L
    cx_hsn    = L + int(CW * 0.60)
    cx_qty    = cx_hsn + 90
    cx_rate   = cx_qty + 60
    cx_amt    = R

    th_bot = y + 34
    draw.rectangle([L, y, R, th_bot], fill=(240, 244, 252), outline=BLACK, width=1)

    draw.text((cx_desc + 6, y + 4),  "Particulars (Descriptions & Specifications)", fill=BLACK, font=f_md_b)
    draw.text((cx_hsn + 4,  y + 4),  "HSN /",    fill=BLACK, font=f_sm)
    draw.text((cx_hsn + 4,  y + 16), "SAC Code", fill=BLACK, font=f_sm)
    draw.text((cx_qty + 8,  y + 11), "Qty",       fill=BLACK, font=f_sm)
    draw.text((cx_rate + 6, y + 11), "Rate (INR)",  fill=BLACK, font=f_sm)
    draw.text((cx_amt - 82, y + 11), "Amount (INR)", fill=BLACK, font=f_sm)

    iy = th_bot
    ROW_H = 26
    for i, (desc, hsn, qty, rate, amt) in enumerate(DATA["items"]):
        row_bot = iy + ROW_H
        bg = WHITE if i % 2 == 0 else (248, 250, 255)
        draw.rectangle([L, iy, R, row_bot], fill=bg, outline=LIGHT_GREY, width=1)

        max_chars = 60
        desc_display = desc if len(desc) <= max_chars else desc[:max_chars - 1] + "…"
        draw.text((cx_desc + 6, iy + 7), desc_display, fill=DARK, font=f_sm)
        draw.text((cx_hsn + 4,  iy + 7), hsn,           fill=DARK, font=f_sm)

        for val, col_r in [(qty, cx_qty + 52), (rate, cx_rate + 62), (amt, cx_amt - 6)]:
            vw = text_w(draw, val, f_sm_b)
            draw.text((col_r - vw, iy + 7), val, fill=BLACK, font=f_sm_b)

        iy = row_bot

    # ── Totals section ────────────────────────────────────────────────────────
    totals_x = cx_qty
    totals_start_y = iy

    def tot_row(label, val, fill_col=None):
        nonlocal iy
        bot = iy + 22
        if fill_col:
            draw.rectangle([totals_x, iy, R, bot], fill=fill_col, outline=None)

        draw.text((totals_x + 6, iy + 4), label, fill=BLACK, font=f_sm_b)
        if val:
            vw = text_w(draw, val, f_md_b if fill_col else f_sm_b)
            draw.text((R - vw - 6, iy + 4), val, fill=BLACK, font=f_md_b if fill_col else f_sm_b)
        iy = bot

    wt_top = iy
    tot_row(f"Sub Total",                    f"INR {DATA['subtotal']}")
    tot_row(f"CGST @ {DATA['cgst_rate']} %", f"INR {DATA['cgst_amt']}")
    tot_row(f"SGST @ {DATA['sgst_rate']} %", f"INR {DATA['sgst_amt']}")
    tot_row(f"GRAND TOTAL",                  f"INR {DATA['grand_total']}", fill_col=GRAND_COLOR)
    wt_bot = iy

    draw.rectangle([totals_x, totals_start_y, R, wt_bot], outline=BLACK, width=1)

    draw.rectangle([L, wt_top, totals_x - 1, wt_bot], outline=BLACK, width=1)
    draw.text((L + 6, wt_top + 4), "Warranty related Terms & Conditions", fill=BLACK, font=f_md_b)
    for ti, term in enumerate(DATA["terms"]):
        tw = text_w(draw, f"{ti+1}. {term}", f_tiny)
        max_w = totals_x - L - 16
        if tw > max_w:
            words = term.split()
            line = f"{ti+1}. "
            ty_off = wt_top + 20 + ti * 15
            for word in words:
                test = line + word + " "
                if text_w(draw, test, f_tiny) < max_w:
                    line = test
                else:
                    draw.text((L + 8, ty_off), line.rstrip(), fill=DARK, font=f_tiny)
                    ty_off += 11
                    line = "   " + word + " "
            draw.text((L + 8, ty_off), line.rstrip(), fill=DARK, font=f_tiny)
        else:
            draw.text((L + 8, wt_top + 20 + ti * 15), f"{ti+1}. {term}", fill=DARK, font=f_tiny)

    y = iy + 4

    # ── Total in Words box ────────────────────────────────────────────────────
    words_bot = y + 42
    draw.rectangle([L, y, R, words_bot], outline=BLACK, width=1)
    draw.text((L + 8, y + 6), "Total Amount (INR — In Words) :", fill=MID_GREY, font=f_md_b)
    draw.line([(L + 8, y + 20), (R - 8, y + 20)], fill=BLACK, width=1)
    draw.text((L + 10, y + 23), DATA["total_words"], fill=DARK, font=f_md_b)
    y = words_bot + 6

    # ── Authorized Signatory ──────────────────────────────────────────────────
    sig_split = L + int(CW * 0.55)
    draw.text((L + 8, y + 4), f"For {DATA['provider_name']}", fill=DARK, font=f_md_b)
    draw.text((sig_split, y + 4), "Authorized Signatory:", fill=MID_GREY, font=f_sm)
    draw.line([(sig_split, y + 30), (R - 10, y + 30)], fill=LIGHT_GREY, width=1)
    draw.text((sig_split, y + 33), "(Signature & Stamp)", fill=LIGHT_GREY, font=f_tiny)
    y += 48

    # ── Column dividers for table (draw on top of rows) ──────────────────────
    table_top_y = th_bot - 34 
    for cx in [cx_hsn, cx_qty, cx_rate]:
        draw.line([(cx, table_top_y), (cx, wt_top)], fill=BLACK, width=1)
    draw.line([(totals_x, wt_top), (totals_x, wt_bot)], fill=BLACK, width=1)

    # ── License / Registration bar at very bottom ─────────────────────────────
    lic_top = H - 45
    draw.rectangle([L, lic_top, R, H - 20], fill=(240, 244, 252), outline=BORDER, width=1)
    lic_text = DATA["license"]
    lw = text_w(draw, lic_text, f_md_b)
    draw.text(((W - lw) // 2, lic_top + 8), lic_text, fill=BLACK, font=f_md_b)

    # ── Caduceus watermark ───────────────────────────────────────────────────
    wm_font = try_font(72, bold=True)
    wm = "⚕"
    try:
        wm_w = text_w(draw, wm, wm_font)
        wm_h = wm_font.size
        wm_x = (W - wm_w) // 2
        wm_y = table_top_y + (wt_top - table_top_y) // 2 - wm_h // 2
        draw.text((wm_x, wm_y), wm, fill=WATERMARK, font=wm_font)
    except Exception:
        pass

    outer_rect()

    return img


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    print("Generating filled medical invoice 3...")
    img = draw_invoice()
    img.save(OUTPUT_PATH, "PNG", dpi=(150, 150))
    print(f"Saved to: {OUTPUT_PATH}")
    print(f"Size: {img.size[0]}x{img.size[1]} px")


if __name__ == "__main__":
    main()
