"""
create_canonical_template.py
-----------------------------
Creates a pixel-accurate Python-drawn version of the Bajaj Finserv
Medical Invoice template shown in the problem statement.

This produces a proper structural template image that generate_fingerprint()
can detect boxes and layout regions from, which is then registered permanently.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image, ImageDraw, ImageFont
import numpy as np

OUTPUT_PATH = "app/golden_templates/bajaj_medical_invoice_canonical.png"


def create_medical_invoice_template(width=794, height=1123):
    """
    Draws the Medical Invoice template at A4 proportions.
    Matches the exact layout from the Bajaj Finserv problem statement image:
    - Blue TAX INVOICE header bar
    - MEDICAL INVOICE title
    - Address / Contact / GSTIN fields
    - PARTY DETAILS bordered box
    - Items table with HSN/SAC, Qty, Rate, Amount columns
    - Caduceus watermark area
    - GST totals (Total, CGST, SGST, Grand Total)
    - Warranty Terms section
    - Total Amount in Words box
    - Company name footer
    """
    # Colors
    BLUE_HEADER = (173, 196, 230)      # Light blue header
    BLUE_GRAND_TOTAL = (173, 196, 230) # Same blue for grand total row
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    DARK_GREY = (30, 30, 30)
    LIGHT_GREY = (200, 200, 200)
    BORDER_BLUE = (91, 133, 188)

    img = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(img)

    # Margins
    LEFT = 30
    RIGHT = width - 30
    TOP = 15

    # ─────────────────────────────────────────────────────────
    # ROW 1: Blue header bar — "TAX INVOICE" + INVOICE NO / DATE
    # ─────────────────────────────────────────────────────────
    header_top = TOP
    header_bottom = TOP + 38
    draw.rectangle([LEFT, header_top, RIGHT, header_bottom], fill=BLUE_HEADER, outline=BLACK, width=1)

    # "TAX INVOICE" centered (left 2/3)
    draw.rectangle([LEFT, header_top, LEFT + (RIGHT - LEFT) * 2 // 3, header_bottom],
                   fill=BLUE_HEADER, outline=BLACK, width=1)
    draw.text((LEFT + (RIGHT - LEFT) // 3, header_top + 10), "TAX INVOICE",
              fill=BLACK, anchor="mm" if hasattr(draw, 'textbbox') else None)

    # INVOICE NO: / DATE: (right 1/3)
    inv_x = LEFT + (RIGHT - LEFT) * 2 // 3 + 5
    draw.text((inv_x, header_top + 6), "INVOICE NO:", fill=BLACK)
    draw.text((inv_x, header_top + 20), "DATE:", fill=BLACK)

    # ─────────────────────────────────────────────────────────
    # ROW 2: MEDICAL INVOICE title (large, centered)
    # ─────────────────────────────────────────────────────────
    title_y = header_bottom + 18
    draw.text((width // 2, title_y), "MEDICAL INVOICE", fill=BLACK, anchor="mt" if hasattr(draw, 'textbbox') else None)

    # ─────────────────────────────────────────────────────────
    # ROW 3: Address / Contact / GSTIN fields
    # ─────────────────────────────────────────────────────────
    fields_y = title_y + 28
    draw.text((LEFT + 10, fields_y), "Address:", fill=DARK_GREY)
    draw.text((LEFT + 10, fields_y + 16), "Contact No.:", fill=DARK_GREY)
    draw.text((LEFT + 200, fields_y + 16), "Email:", fill=DARK_GREY)
    draw.text((LEFT + 10, fields_y + 32), "GSTIN:", fill=DARK_GREY)
    draw.text((LEFT + 200, fields_y + 32), "PAN No.:", fill=DARK_GREY)

    # Underlines for field values
    for fy in [fields_y + 12, fields_y + 28, fields_y + 44]:
        draw.line([(LEFT + 70, fy), (LEFT + 180, fy)], fill=LIGHT_GREY, width=1)
    draw.line([(LEFT + 240, fields_y + 28), (RIGHT - 30, fields_y + 28)], fill=LIGHT_GREY, width=1)
    draw.line([(LEFT + 240, fields_y + 44), (RIGHT - 30, fields_y + 44)], fill=LIGHT_GREY, width=1)

    # ─────────────────────────────────────────────────────────
    # ROW 4: PARTY DETAILS box (large bordered box)
    # ─────────────────────────────────────────────────────────
    party_top = fields_y + 60
    party_bottom = party_top + 100
    draw.rectangle([LEFT, party_top, RIGHT, party_bottom], outline=BLACK, width=1)
    draw.text((LEFT + 8, party_top + 6), "PARTY DETAILS:>", fill=BLACK)

    # ─────────────────────────────────────────────────────────
    # ROW 5: Items Table Header
    # ─────────────────────────────────────────────────────────
    # Increase fonts significantly to match generate_filled_invoice.py
    f_tiny   = try_font(18)
    f_sm     = try_font(20)
    f_md     = try_font(22)
    f_md_b   = try_font(22, bold=True)
    f_lg_b   = try_font(26, bold=True)
    f_xl_b   = try_font(32, bold=True)
    f_title  = try_font(36, bold=True)
    table_top = party_bottom + 2
    table_bottom = table_top + 280
    col_hsn = RIGHT - 280
    col_qty = RIGHT - 180
    col_rate = RIGHT - 100
    col_amount = RIGHT

    # Table outer border
    draw.rectangle([LEFT, table_top, RIGHT, table_bottom], outline=BLACK, width=1)

    # Column header row
    header_row_bottom = table_top + 36
    draw.rectangle([LEFT, table_top, RIGHT, header_row_bottom], outline=BLACK, width=1)

    # Column separator lines
    draw.line([(col_hsn, table_top), (col_hsn, table_bottom)], fill=BLACK, width=1)
    draw.line([(col_qty, table_top), (col_qty, table_bottom)], fill=BLACK, width=1)
    draw.line([(col_rate, table_top), (col_rate, table_bottom)], fill=BLACK, width=1)

    # Header texts
    draw.text((LEFT + 8, table_top + 8), "Particulars (Descriptions & Specifications)", fill=BLACK)
    draw.text((col_hsn + 4, table_top + 4), "HSN /", fill=BLACK)
    draw.text((col_hsn + 4, table_top + 18), "SAC Code", fill=BLACK)
    draw.text((col_qty + 8, table_top + 12), "Qty", fill=BLACK)
    draw.text((col_rate + 4, table_top + 12), "Rate", fill=BLACK)
    draw.text((col_amount - 55, table_top + 12), "Amount", fill=BLACK)

    # Horizontal lines for rows in table (5 item rows)
    for i in range(1, 6):
        row_y = header_row_bottom + i * 40
        if row_y < table_bottom:
            draw.line([(LEFT, row_y), (RIGHT, row_y)], fill=LIGHT_GREY, width=1)

    # ─────────────────────────────────────────────────────────
    # TOTALS section (bottom-right of table)
    # ─────────────────────────────────────────────────────────
    totals_x = col_qty  # Start of totals columns
    total_row_y = table_bottom - 72
    cgst_row_y = table_bottom - 48
    sgst_row_y = table_bottom - 24

    # Total row
    draw.line([(LEFT, total_row_y), (RIGHT, total_row_y)], fill=BLACK, width=1)
    draw.line([(totals_x, total_row_y), (totals_x, table_bottom)], fill=BLACK, width=1)
    draw.text((totals_x + 4, total_row_y + 4), "Total", fill=BLACK)

    draw.text((totals_x + 4, cgst_row_y + 4), "CGST @         %", fill=BLACK)
    draw.text((totals_x + 4, sgst_row_y + 4), "SGST @         %", fill=BLACK)

    # Grand Total row (blue fill)
    draw.rectangle([totals_x, table_bottom - 1, RIGHT, table_bottom + 23],
                   fill=BLUE_GRAND_TOTAL, outline=BLACK, width=1)
    draw.text((totals_x + 4, table_bottom + 4), "Grand Total", fill=BLACK)

    # ─────────────────────────────────────────────────────────
    # Warranty Terms (left side below table)
    # ─────────────────────────────────────────────────────────
    warranty_y = table_bottom + 8
    draw.text((LEFT, warranty_y), "Warranty related Terms & Conditions", fill=BLACK)
    for i, num in enumerate(["1.", "2.", "3.", "4."]):
        draw.text((LEFT + 4, warranty_y + 16 + i * 14), num, fill=DARK_GREY)

    # ─────────────────────────────────────────────────────────
    # Total Amount (INR - In Words) — bordered box at bottom
    # ─────────────────────────────────────────────────────────
    words_top = table_bottom + 90
    words_bottom = words_top + 38
    draw.rectangle([LEFT, words_top, RIGHT, words_bottom], outline=BLACK, width=1)
    draw.text((LEFT + 8, words_top + 6), "Total Amount (INR - In Words):", fill=BLACK)
    # Underline
    draw.line([(LEFT + 8, words_top + 22), (RIGHT - 8, words_top + 22)], fill=BLACK, width=1)

    # ─────────────────────────────────────────────────────────
    # Company Name footer
    # ─────────────────────────────────────────────────────────
    draw.text((LEFT, words_bottom + 12), "For YOUR COMPANY NAME", fill=BLACK)

    # Draw outer border around entire document
    draw.rectangle([LEFT - 2, TOP - 2, RIGHT + 2, words_bottom + 40], outline=BLACK, width=2)

    return img


def main():
    os.makedirs("app/golden_templates", exist_ok=True)

    print("Creating canonical Bajaj Medical Invoice template...")
    img = create_medical_invoice_template()
    img.save(OUTPUT_PATH, "PNG", dpi=(150, 150))
    print(f"Saved: {OUTPUT_PATH}")

    # Verify fingerprint
    from app.services.template_extractor import generate_fingerprint
    fp = generate_fingerprint(OUTPUT_PATH)
    print(f"phash:      {fp.get('phash', 'NONE')}")
    print(f"Boxes:      {len(fp.get('boxes', []))} structural regions")
    print(f"Color bins: {len(fp.get('color_hist', []))}")

    if len(fp.get('boxes', [])) < 3:
        print("WARNING: Fewer than 3 boxes detected. Template may need adjustment.")
    else:
        print("SUCCESS: Template has rich structural fingerprint for fraud detection.")

    return fp


if __name__ == "__main__":
    fp = main()

    # Auto-register in database
    import sys
    sys.path.insert(0, '.')
    from app.core.database import SessionLocal
    from app.models.domain import ProviderReference, Document, GoldenTemplate

    try:
        from app.models.fraud import TemplateMatch
        has_tm = True
    except:
        has_tm = False

    db = SessionLocal()
    try:
        # Wipe existing
        if has_tm:
            db.query(TemplateMatch).delete()
        db.query(Document).delete()
        db.query(ProviderReference).delete()
        db.query(GoldenTemplate).delete()
        db.commit()
        print("Database wiped clean.")

        # Register for all 4 source types
        CATEGORIES = ["hospital", "doctor", "lab", "customer"]
        LABEL = "Bajaj Finserv Medical Invoice (Official)"
        for cat in CATEGORIES:
            ref = ProviderReference(
                category=cat,
                label=f"{LABEL} - {cat.capitalize()}",
                fingerprint_data={
                    "phash": fp.get("phash", ""),
                    "boxes": fp.get("boxes", []),
                    "color_hist": fp.get("color_hist", []),
                }
            )
            db.add(ref)
            db.flush()
            print(f"Registered: category={cat}, id={ref.id}")

        # GoldenTemplate
        golden = GoldenTemplate(
            provider_name="Bajaj Finserv Medical Invoice",
            document_type="invoice",
            file_path=os.path.abspath(OUTPUT_PATH)
        )
        db.add(golden)
        db.flush()
        print(f"GoldenTemplate: id={golden.id}")

        db.commit()
        print("REGISTRATION COMPLETE!")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback; traceback.print_exc()
    finally:
        db.close()
