from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

out_path = Path(__file__).with_name('tampered_hospital_template.png')

width, height = 1400, 1800
img = Image.new('RGB', (width, height), 'white')
draw = ImageDraw.Draw(img)

# Header with different provider branding
header = (0, 0, width, 280)
draw.rectangle(header, fill='#8b1e2d')
font_title = ImageFont.truetype('arial.ttf', 52)
font_sub = ImageFont.truetype('arial.ttf', 30)
font_body = ImageFont.truetype('arial.ttf', 28)
font_small = ImageFont.truetype('arial.ttf', 24)

draw.text((80, 80), 'Metro Care Diagnostics', fill='white', font=font_title)
draw.text((80, 145), 'Claim Submission Copy', fill='#ffe8eb', font=font_sub)
draw.text((80, 200), 'Document Type: Hospital Invoice', fill='white', font=font_body)

# Patient / Provider section
box = (80, 340, width-80, 620)
draw.rounded_rectangle(box, radius=18, outline='#e5c2c7', width=3)
draw.text((120, 380), 'Provider Details', fill='#8b1e2d', font=font_body)
draw.text((120, 430), 'Provider Name: Metro Care Diagnostics', fill='black', font=font_body)
draw.text((120, 480), 'Address: 22, Wellness Avenue, Delhi', fill='black', font=font_body)
draw.text((120, 530), 'Contact: +91 99887 66554', fill='black', font=font_body)
draw.text((120, 580), 'Invoice No: MCD-2026-042', fill='black', font=font_body)

draw.text((820, 380), 'Patient Details', fill='#8b1e2d', font=font_body)
draw.text((820, 430), 'Patient Name: Rohan Mehta', fill='black', font=font_body)
draw.text((820, 480), 'Date of Service: 12-Aug-2026', fill='black', font=font_body)
draw.text((820, 530), 'Member ID: HLM-77890', fill='black', font=font_body)
draw.text((820, 580), 'Policy No: POL-99881', fill='black', font=font_body)

# Service table
box2 = (80, 700, width-80, 1220)
draw.rounded_rectangle(box2, radius=18, outline='#e5c2c7', width=3)
draw.text((120, 740), 'Service Breakdown', fill='#8b1e2d', font=font_body)
for y in [800, 860, 920]:
    draw.line((120, y, width-120, y), fill='#d8bfc2', width=2)
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
    draw.line((120, y + 50, width-120, y + 50), fill='#eee4e5', width=2)

summary_y = 1240
draw.text((900, summary_y), 'Subtotal', fill='black', font=font_body)
draw.text((1120, summary_y), '₹ 5800', fill='black', font=font_body)
draw.text((900, summary_y + 70), 'GST (5%)', fill='black', font=font_body)
draw.text((1120, summary_y + 70), '₹ 290', fill='black', font=font_body)
draw.line((900, summary_y + 120, width-120, summary_y + 120), fill='black', width=2)
draw.text((900, summary_y + 150), 'Total Payable', fill='#8b1e2d', font=font_body)
draw.text((1120, summary_y + 150), '₹ 6090', fill='#8b1e2d', font=font_body)

footer = (80, 1520, width-80, 1700)
draw.rounded_rectangle(footer, radius=16, outline='#e5c2c7', width=3)
draw.text((120, 1560), 'This sample is intentionally modified to represent a suspicious template reuse case.', fill='black', font=font_small)
draw.text((120, 1610), 'Status: Suspicious / Potential Clone', fill='#8b1e2d', font=font_small)

img.save(out_path)
print(f'Saved tampered template image to {out_path}')
