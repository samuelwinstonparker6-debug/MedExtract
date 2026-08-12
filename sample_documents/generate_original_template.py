from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

out_path = Path(__file__).with_name('original_hospital_template.png')

width, height = 1400, 1800
img = Image.new('RGB', (width, height), 'white')
draw = ImageDraw.Draw(img)

# Header
header = (0, 0, width, 280)
draw.rectangle(header, fill='#0f4c81')
font_title = ImageFont.truetype('arial.ttf', 52)
font_sub = ImageFont.truetype('arial.ttf', 30)
font_body = ImageFont.truetype('arial.ttf', 28)
font_small = ImageFont.truetype('arial.ttf', 24)

draw.text((80, 80), 'Bajaj Finserv Health Pvt. Ltd', fill='white', font=font_title)
draw.text((80, 145), 'Original Provider Invoice / Medical Claim', fill='#dceeff', font=font_sub)
draw.text((80, 200), 'Document Type: Hospital Invoice', fill='white', font=font_body)

# Patient / Provider section
box = (80, 340, width-80, 620)
draw.rounded_rectangle(box, radius=18, outline='#c9d6e6', width=3)
draw.text((120, 380), 'Provider Details', fill='#0f4c81', font=font_body)
draw.text((120, 430), 'Provider Name: Bajaj Finserv Health Pvt. Ltd', fill='black', font=font_body)
draw.text((120, 480), 'Address: 12, Medical Plaza, Sector 15, Gurgaon', fill='black', font=font_body)
draw.text((120, 530), 'Contact: +91 98765 43210', fill='black', font=font_body)
draw.text((120, 580), 'Invoice No: HOSP-2026-001', fill='black', font=font_body)

draw.text((820, 380), 'Patient Details', fill='#0f4c81', font=font_body)
draw.text((820, 430), 'Patient Name: Asha Verma', fill='black', font=font_body)
draw.text((820, 480), 'Date of Service: 10-Aug-2026', fill='black', font=font_body)
draw.text((820, 530), 'Member ID: HLM-44501', fill='black', font=font_body)
draw.text((820, 580), 'Policy No: POL-88211', fill='black', font=font_body)

# Service table
box2 = (80, 700, width-80, 1220)
draw.rounded_rectangle(box2, radius=18, outline='#c9d6e6', width=3)
draw.text((120, 740), 'Service Breakdown', fill='#0f4c81', font=font_body)
# Table header line
for y in [800, 860, 920]:
    draw.line((120, y, width-120, y), fill='#b9c7d2', width=2)
draw.text((120, 780), 'Service', fill='black', font=font_body)
draw.text((540, 780), 'Qty', fill='black', font=font_body)
draw.text((760, 780), 'Rate', fill='black', font=font_body)
draw.text((1020, 780), 'Amount', fill='black', font=font_body)

services = [
    ('Consultation', '1', '₹ 800', '₹ 800'),
    ('Pathology Lab Test', '1', '₹ 1800', '₹ 1800'),
    ('Radiology Scan', '1', '₹ 3200', '₹ 3200'),
]
for i, (name, qty, rate, amount) in enumerate(services):
    y = 860 + i * 90
    draw.text((120, y), name, fill='black', font=font_body)
    draw.text((540, y), qty, fill='black', font=font_body)
    draw.text((760, y), rate, fill='black', font=font_body)
    draw.text((1020, y), amount, fill='black', font=font_body)
    draw.line((120, y + 50, width-120, y + 50), fill='#e3e8ee', width=2)

# Summary
summary_y = 1240
draw.text((900, summary_y), 'Subtotal', fill='black', font=font_body)
draw.text((1120, summary_y), '₹ 5800', fill='black', font=font_body)
draw.text((900, summary_y + 70), 'GST (5%)', fill='black', font=font_body)
draw.text((1120, summary_y + 70), '₹ 290', fill='black', font=font_body)
draw.line((900, summary_y + 120, width-120, summary_y + 120), fill='black', width=2)
draw.text((900, summary_y + 150), 'Total Payable', fill='#0f4c81', font=font_body)
draw.text((1120, summary_y + 150), '₹ 6090', fill='#0f4c81', font=font_body)

# Footer
footer = (80, 1520, width-80, 1700)
draw.rounded_rectangle(footer, radius=16, outline='#c9d6e6', width=3)
draw.text((120, 1560), 'This is a clean, original provider document intended for structural template verification.', fill='black', font=font_small)
draw.text((120, 1610), 'Status: Genuine / Original Template Candidate', fill='#0f4c81', font=font_small)

img.save(out_path)
print(f'Saved original template image to {out_path}')
