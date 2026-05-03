from PIL import Image, ImageDraw, ImageFont
import os

STORE_DIR = "static/store"
os.makedirs(STORE_DIR, exist_ok=True)

products = [
    ("degree_it.jpg", "Bachelor of IT\nWeekend Degree", "#2563eb", "#ffffff"),
    ("ielts_course.jpg", "IELTS Prep\n90% Success Rate", "#dc2626", "#ffffff"),
    ("japan_visa.jpg", "Japan Work Visa\nComplete Assistance", "#7c3aed", "#ffffff"),
    ("laptop_deal.jpg", "Dell Inspiron 15\nGovernment Deal", "#059669", "#ffffff"),
    ("batik_saree.jpg", "Handlo Batik\nTraditional Design", "#ea580c", "#ffffff"),
    ("ol_tuition.jpg", "O/L Tuition\nExpert Teachers", "#ca8a04", "#1f2937"),
    ("slas_training.jpg", "SLAS Exam Prep\nWeekend Classes", "#1f2937", "#ffffff"),
    ("data_entry.jpg", "Part-Time Jobs\nWork From Home", "#0891b2", "#ffffff"),
    ("kids_coding.jpg", "Kids Coding Camp\nAges 8-14", "#c026d3", "#ffffff"),
    ("leadership.jpg", "Leadership\nProfessional Dev", "#4f46e5", "#ffffff")
]

def create_product_image(filename, title, bg_color, text_color):
    # Create image with better dimensions for product cards
    img = Image.new('RGB', (600, 400), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font, fallback to default
    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
        subtitle_font = ImageFont.truetype("arial.ttf", 28)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Split title into lines
    lines = title.split('\n')
    
    # Draw text centered
    y_offset = 150 if len(lines) == 2 else 180
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=title_font if i == 0 else subtitle_font)
        text_width = bbox[2] - bbox[0]
        text_x = (600 - text_width) // 2
        text_y = y_offset + (i * 60)
        draw.text((text_x, text_y), line, fill=text_color, font=title_font if i == 0 else subtitle_font)
    
    # Add decorative element (simple banner)
    draw.rectangle([(0, 0), (600, 30)], fill=text_color)
    draw.text((20, 5), "🛒 Public Store", fill=bg_color, font=subtitle_font)
    
    # Save
    path = os.path.join(STORE_DIR, filename)
    img.save(path, 'JPEG', quality=90)
    print(f"Created {filename}")

for p in products:
    create_product_image(p[0], p[1], p[2], p[3])

print("\n✓ All product images created successfully!")
