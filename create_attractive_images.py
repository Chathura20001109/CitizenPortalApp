from PIL import Image, ImageDraw, ImageFont
import os

STORE_DIR = "static/store"
os.makedirs(STORE_DIR, exist_ok=True)

def create_gradient(width, height, color1, color2):
    """Create a vertical gradient"""
    base = Image.new('RGB', (width, height), color1)
    top = Image.new('RGB', (width, height), color2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_modern_product_image(filename, emoji, title, subtitle, bg_start, bg_end, accent):
    """Create a modern, attractive product image"""
    width, height = 800, 600
    
    # Create gradient background
    img = create_gradient(width, height, hex_to_rgb(bg_start), hex_to_rgb(bg_end))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Try to load fonts
    try:
        emoji_font = ImageFont.truetype("seguiemj.ttf", 120)  # Windows emoji font
    except:
        emoji_font = None
    
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 64)
        subtitle_font = ImageFont.truetype("arial.ttf", 36)
        tag_font = ImageFont.truetype("arial.ttf", 24)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        tag_font = ImageFont.load_default()
    
    # Draw decorative shapes
    # Top accent bar
    draw.rectangle([(0, 0), (width, 8)], fill=hex_to_rgb(accent))
    
    # Draw emoji/icon at top
    if emoji_font:
        emoji_bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
        emoji_width = emoji_bbox[2] - emoji_bbox[0]
        draw.text(((width - emoji_width) // 2, 80), emoji, fill='white', font=emoji_font)
    else:
        # Fallback: draw large text emoji
        draw.text((width // 2 - 60, 80), emoji, fill='white', font=title_font)
    
    # Add semi-transparent overlay for text area
    overlay_y = 280
    draw.rectangle([(40, overlay_y), (width - 40, height - 40)], 
                   fill=(0, 0, 0, 120))
    
    # Draw title
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, overlay_y + 40), title, fill='white', font=title_font)
    
    # Draw subtitle
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    draw.text((subtitle_x, overlay_y + 120), subtitle, fill=hex_to_rgb(accent), font=subtitle_font)
    
    # Add decorative corner elements
    corner_color = hex_to_rgb(accent) + (100,)
    draw.ellipse([(width - 150, -50), (width + 50, 150)], fill=corner_color)
    draw.ellipse([(-50, height - 150), (150, height + 50)], fill=corner_color)
    
    # Add "Limited Offer" or similar tag
    tag_text = "🏷️ Available Now"
    tag_bbox = draw.textbbox((0, 0), tag_text, font=tag_font)
    tag_width = tag_bbox[2] - tag_bbox[0]
    tag_bg_x = (width - tag_width - 40) // 2
    draw.rectangle([(tag_bg_x, overlay_y + 200), (tag_bg_x + tag_width + 40, overlay_y + 240)],
                   fill=hex_to_rgb(accent), outline='white', width=2)
    draw.text((tag_bg_x + 20, overlay_y + 207), tag_text, fill='white', font=tag_font)
    
    # Save
    path = os.path.join(STORE_DIR, filename)
    img.save(path, 'JPEG', quality=95)
    print(f"[OK] Created {filename}")

# Product configurations with emojis and modern color schemes
products = [
    ("degree_it.jpg", "🎓", "Bachelor of IT", "Weekend Classes Available", "#1e3a8a", "#3b82f6", "#60a5fa"),
    ("ielts_course.jpg", "📚", "IELTS Prep", "90% Success Rate", "#7f1d1d", "#dc2626", "#f87171"),
    ("japan_visa.jpg", "✈️", "Japan Work Visa", "Complete Assistance", "#581c87", "#9333ea", "#c084fc"),
    ("laptop_deal.jpg", "💻", "Dell Inspiron 15", "Government Employee Deal", "#064e3b", "#059669", "#34d399"),
    ("batik_saree.jpg", "👗", "Batik Saree", "Traditional Handloom", "#9a3412", "#ea580c", "#fb923c"),
    ("ol_tuition.jpg", "📝", "O/L Tuition", "Expert Teachers", "#854d0e", "#ca8a04", "#facc15"),
    ("slas_training.jpg", "🏛️", "SLAS Training", "Weekend Classes", "#1f2937", "#4b5563", "#9ca3af"),
    ("data_entry.jpg", "💼", "Part-Time Jobs", "Work From Home", "#0e7490", "#0891b2", "#22d3ee"),
    ("kids_coding.jpg", "🎮", "Kids Coding", "Ages 8-14", "#86198f", "#c026d3", "#e879f9"),
    ("leadership.jpg", "🎯", "Leadership Workshop", "Professional Development", "#3730a3", "#4f46e5", "#818cf8"),
    ("advanced_ai.jpg", "🤖", "Advanced AI", "Machine Learning Course", "#1e40af", "#3b82f6", "#60a5fa"),
    ("teacher_training.jpg", "🏫", "Teacher Training", "Modern Pedagogy", "#0f766e", "#14b8a6", "#2dd4bf"),
    ("med_equip.jpg", "🩺", "Medical Kit", "Stethoscope & BP Monitor", "#9f1239", "#e11d48", "#fb7185"),
]

print("Creating modern, attractive product images...\n")

for config in products:
    create_modern_product_image(*config)

print(f"\n✅ All {len(products)} attractive product images created successfully!")
print(f"📁 Location: {STORE_DIR}/")
