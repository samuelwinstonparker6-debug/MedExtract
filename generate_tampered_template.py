"""
generate_tampered_template.py
--------------------------------
Generates a tampered / modified version of the canonical Bajaj Finserv Medical Invoice.
It introduces minor structural irregularities (shifted column lines, modified header color, 
altered section heights) to demonstrate how MedExtract's Machine Analytical Intelligence
detects template manipulation and flags the document as FRAUD / FAKE.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image, ImageDraw, ImageFont
import numpy as np

OUTPUT_PATH = "app/golden_templates/fraud_tampered_invoice.png"


def try_font(size, bold=False):
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


def draw_tampered_invoice():
    W, H = 860, 1200
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK = (20, 20, 20)
    LIGHT_GREY = (210, 210, 210)
    MID_GREY = (100, 100, 100)

    # ── MINOR IRREGULARITY 1: Modified Header Color (Crimson-tinted Blue instead of Authentic Header Blue) ──
    TAMPERED_HEADER_COLOR = (215, 185, 200) # Altered color palette
    TAMPERED_GRAND_COLOR  = (215, 185, 200)
    BORDER = (120, 60, 80)

    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    # Margins
    L, R, T = 28, 832, 35
    CW = R - L

    f_tiny   = try_font(12)
    f_sm     = try_font(14)
    f_sm_b   = try_font(14, bold=True)
    f_md     = try_font(16)
    f_md_b   = try_font(16, bold=True)
    f_lg_b   = try_font(18, bold=True)
    f_xl_b   = try_font(24, bold=True)
    f_title  = try_font(26, bold=True)

    y = T

    # Outer border
    draw.rectangle([L-2, T-2, R+2, H-40], outline=BORDER, width=2)

    # ── MINOR IRREGULARITY 2: Shifted Header Box Height (+12px taller than canonical) ──
    hdr_bot = y + 52
    split_x = L + int(CW * 0.52) # Shifted column split ratio (52% instead of 62%)

    draw.rectangle([L, y, R, hdr_bot], fill=TAMPERED_HEADER_COLOR, outline=BLACK, width=1)
    label = "TAX INVOICE"
    draw.text((L + 20, y + 14), label, fill=BLACK, font=f_lg_b)

    draw.text((split_x + 12, y + 8),  "INVOICE NO: INV-2026-99104", fill=BLACK, font=f_sm_b)
    draw.text((split_x + 12, y + 26), "DATE: 15-Oct-2026",        fill=BLACK, font=f_sm_b)

    y = hdr_bot + 1

    # Provider Title
    pname_bot = y + 38
    draw.rectangle([L, y, R, pname_bot], outline=BLACK, width=1)
    pname = "BAJAJ FINSERV Medical Invoice"
    pname_w = text_w(draw, pname, f_title)
    draw.text(((W - pname_w) // 2, y + 6), pname, fill=BLACK, font=f_title)
    draw.text(((W - text_w(draw, "MEDICAL INVOICE", f_md_b)) // 2, y + 26),
              "MEDICAL INVOICE", fill=(80, 80, 80), font=f_md_b)

    y = pname_bot + 1

    # Address / Contact
    fields_bot = y + 54
    draw.rectangle([L, y, R, fields_bot], outline=BLACK, width=1)
    draw.text((L + 8, y + 5),  "Address : Plot No. 14, Sector 18, Gurugram, Haryana - 122001", fill=DARK, font=f_sm)
    draw.text((L + 8, y + 21), "Contact No. : +91-124-4567890   Email : billing@apollomedicare.in", fill=DARK, font=f_sm)
    draw.text((L + 8, y + 37), "GSTIN : 06AAACA1234F1ZX       PAN No. : AAACA1234F", fill=DARK, font=f_md_b)

    y = fields_bot + 1

    # ── MINOR IRREGULARITY 3: Shifted Party Details Box Height (140px instead of 110px) ──
    party_bot = y + 140
    draw.rectangle([L, y, R, party_bot], outline=BLACK, width=1)
    draw.text((L + 8, y + 5), "PARTY DETAILS  :", fill=BLACK, font=f_md_b)

    pd = [
        ("Patient Name",     "Mr. Vikram Malhotra"),
        ("Patient ID",       "PID-88412   |   DOB: 05-May-1985 (Age: 41)"),
        ("Address",          "H-102, Palm Heights, Sector 50, Gurgaon, HR - 122018"),
        ("Phone",            "+91-9811223344   |   Insurance Ref: BJFIN-CL-2026-77812"),
        ("Attending Doctor", "Dr. Rajesh Sharma, MD (Neurology)"),
        ("Ward / Bed",       "Special Room — 305"),
    ]
    py = y + 24
    for lbl, val in pd:
        draw.text((L + 12, py), f"{lbl} :", fill=MID_GREY, font=f_sm)
        draw.text((L + 145, py), val,         fill=DARK,     font=f_sm)
        py += 17

    y = party_bot + 1

    # ── MINOR IRREGULARITY 4: Shifted Table Columns (HSN/SAC column widened, Qty shifted right) ──
    cx_desc   = L
    cx_hsn    = L + int(CW * 0.50) # Shifted from 60% to 50%
    cx_qty    = cx_hsn + 120        # Shifted column width
    cx_rate   = cx_qty + 80
    cx_amt    = R

    th_bot = y + 34
    draw.rectangle([L, y, R, th_bot], fill=(250, 240, 245), outline=BLACK, width=1)

    draw.text((cx_desc + 6, y + 4),  "Particulars (Descriptions & Specifications)", fill=BLACK, font=f_md_b)
    draw.text((cx_hsn + 4,  y + 11), "HSN / SAC Code", fill=BLACK, font=f_sm)
    draw.text((cx_qty + 8,  y + 11), "Qty",            fill=BLACK, font=f_sm)
    draw.text((cx_rate + 6, y + 11), "Rate (INR)",   fill=BLACK, font=f_sm)
    draw.text((cx_amt - 82, y + 11), "Amount (INR)",  fill=BLACK, font=f_sm)

    items = [
        ("Neurology Consultation (Dr. Rajesh Sharma)",  "998311", "1", "3,000.00", "3,000.00"),
        ("Brain MRI Scan with Contrast",                 "998312", "1", "7,500.00", "7,500.00"),
        ("Electroencephalogram (EEG) Test",              "998312", "1", "2,200.00", "2,200.00"),
        ("Tablet: Levetiracetam 500mg × 30 tabs",       "300490", "1",   "650.00",   "650.00"),
    ]

    iy = th_bot
    ROW_H = 26
    for i, (desc, hsn, qty, rate, amt) in enumerate(items):
        row_bot = iy + ROW_H
        bg = WHITE if i % 2 == 0 else (252, 248, 250)
        draw.rectangle([L, iy, R, row_bot], fill=bg, outline=LIGHT_GREY, width=1)

        draw.text((cx_desc + 6, iy + 7), desc, fill=DARK, font=f_sm)
        draw.text((cx_hsn + 4,  iy + 7), hsn,  fill=DARK, font=f_sm)

        vw = text_w(draw, qty, f_sm_b)
        draw.text((cx_qty + 40 - vw, iy + 7), qty, fill=BLACK, font=f_sm_b)
        vw = text_w(draw, rate, f_sm_b)
        draw.text((cx_rate + 70 - vw, iy + 7), rate, fill=BLACK, font=f_sm_b)
        vw = text_w(draw, amt, f_sm_b)
        draw.text((cx_amt - 6 - vw, iy + 7), amt, fill=BLACK, font=f_sm_b)

        iy = row_bot

    # Totals
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
    tot_row("Sub Total",                    "INR 13,350.00")
    tot_row("CGST @ 9 %",                   "INR 1,201.50")
    tot_row("SGST @ 9 %",                   "INR 1,201.50")
    tot_row("GRAND TOTAL",                  "INR 15,753.00", fill_col=TAMPERED_GRAND_COLOR)
    wt_bot = iy

    draw.rectangle([totals_x, totals_start_y, R, wt_bot], outline=BLACK, width=1)
    draw.rectangle([L, wt_top, totals_x - 1, wt_bot], outline=BLACK, width=1)
    draw.text((L + 6, wt_top + 4), "Warranty related Terms & Conditions", fill=BLACK, font=f_md_b)
    draw.text((L + 8, wt_top + 22), "1. Medicines once dispensed will not be returned.", fill=DARK, font=f_tiny)
    draw.text((L + 8, wt_top + 36), "2. Retain invoice for insurance claims.", fill=DARK, font=f_tiny)

    y = iy + 4

    # Total in words
    words_bot = y + 42
    draw.rectangle([L, y, R, words_bot], outline=BLACK, width=1)
    draw.text((L + 8, y + 6), "Total Amount (INR — In Words) :", fill=MID_GREY, font=f_md_b)
    draw.line([(L + 8, y + 20), (R - 8, y + 20)], fill=BLACK, width=1)
    draw.text((L + 10, y + 23), "Fifteen Thousand Seven Hundred Fifty Three Rupees Only", fill=DARK, font=f_md_b)
    y = words_bot + 6

    # Signatory
    sig_split = L + int(CW * 0.55)
    draw.text((L + 8, y + 4), "For BAJAJ FINSERV MEDICAL INVOICE", fill=DARK, font=f_md_b)
    draw.text((sig_split, y + 4), "Authorized Signatory:", fill=MID_GREY, font=f_sm)
    y += 48

    # Column lines
    table_top_y = th_bot - 34
    for cx in [cx_hsn, cx_qty, cx_rate]:
        draw.line([(cx, table_top_y), (cx, wt_top)], fill=BLACK, width=1)
    draw.line([(totals_x, wt_top), (totals_x, wt_bot)], fill=BLACK, width=1)

    # Bottom License Bar
    lic_top = H - 45
    draw.rectangle([L, lic_top, R, H - 20], fill=(250, 240, 245), outline=BORDER, width=1)
    lic_text = "Reg. No.: MCI/HR/2021/04518  |  NABH Accredited  |  Lic. No.: CPCB-HR-MED-2021-7723"
    lw = text_w(draw, lic_text, f_md_b)
    draw.text(((W - lw) // 2, lic_top + 8), lic_text, fill=BLACK, font=f_md_b)

    return img


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    print("Generating tampered / modified sample invoice (Fraud Test Case)...")
    img = draw_tampered_invoice()
    img.save(OUTPUT_PATH, "PNG", dpi=(150, 150))
    print(f"Saved tampered template to: {OUTPUT_PATH}")
    print(f"Size: {img.size[0]}x{img.size[1]} px")


if __name__ == "__main__":
    main()
