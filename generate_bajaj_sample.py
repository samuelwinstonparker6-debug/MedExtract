from PIL import Image, ImageDraw, ImageFont
import os

def create_invoice(filename, include_bajaj=False, license_text=None, title="Medical Invoice", patient_name="John Doe (ID: 12345)", is_fake=False):
    width, height = 800, 1000
    # Make background white, but if it's a fake, maybe slight tint or identical?
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to load a font, otherwise use default
    try:
        font_large = ImageFont.truetype("arial.ttf", 32)
        font_medium = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except IOError:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Hospital Name
    draw.text((50, 50), "Sunrise Health Medical Center", font=font_large, fill='black')
    draw.text((50, 90), title, font=font_medium, fill='gray')
    
    # Bajaj Finserv Watermark / Logo Area
    if include_bajaj:
        # Draw a little blue box for logo
        draw.rectangle([600, 40, 750, 90], outline="blue", width=2)
        draw.text((610, 50), "BAJAJ FINSERV", font=font_medium, fill='blue')
        
        if license_text:
            draw.text((610, 100), f"License: {license_text}", font=font_small, fill='black')

    # Invoice details
    draw.text((50, 150), "Invoice #: INV-4001", font=font_small, fill='black')
    draw.text((50, 180), f"Patient: {patient_name}", font=font_small, fill='black')
    draw.text((50, 210), "Date: 2026-09-15", font=font_small, fill='black')
    
    # Services
    draw.text((50, 270), "Services Provided:", font=font_medium, fill='black')
    draw.text((50, 310), "- General Consultation (Dr. Adams)", font=font_small, fill='black')
    draw.text((650, 310), "$150.00", font=font_small, fill='black')
    
    draw.text((50, 340), "- Comprehensive Blood Panel", font=font_small, fill='black')
    draw.text((650, 340), "$200.00", font=font_small, fill='black')
    
    draw.line([(50, 380), (750, 380)], fill="gray", width=1)
    
    # Total
    draw.text((50, 400), "Total Amount Due:", font=font_medium, fill='black')
    draw.text((650, 400), "$350.00", font=font_medium, fill='black')
    
    # Footer
    draw.text((50, 450), "Please remit payment within 30 days.", font=font_small, fill='gray')
    
    # Save the image
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    image.save(filename)
    print(f"Created {filename}")

if __name__ == "__main__":
    # Create the samples directory
    os.makedirs("samples", exist_ok=True)
    
    # 1. Authentic Bajaj Network Hospital Invoice
    create_invoice(
        "samples/bajaj_authentic.png", 
        include_bajaj=True, 
        license_text="BaB12", # Valid format: AaAANN
        patient_name="Alice Smith (ID: 55522)"
    )
    
    # 2. Fake Bajaj Network Invoice (Fraud)
    # The fraudster copied the logo but put a random license format, or misspelled something, 
    # but the regex won't match so it will trigger the RED flag.
    create_invoice(
        "samples/bajaj_fake.png", 
        include_bajaj=True, 
        license_text="12345", # Invalid format (not AaAANN)
        patient_name="Bob Jones (ID: 99911)",
        is_fake=True
    )
    
    print("Samples generated successfully.")
