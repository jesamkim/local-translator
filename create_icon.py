#!/usr/bin/env python3
"""
Create a simple translator app icon
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_gradient_circle(size=512):
    """Create a gradient circle icon"""
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Colors matching the app theme
    color1 = (102, 126, 234)  # #667eea
    color2 = (118, 75, 162)   # #764ba2

    # Draw gradient circle
    center = size // 2
    radius = size // 2 - 20

    for i in range(radius, 0, -1):
        # Calculate gradient
        ratio = (radius - i) / radius
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)

        # Draw circle
        draw.ellipse(
            [center - i, center - i, center + i, center + i],
            fill=(r, g, b, 255)
        )

    # Draw white "KO ⇄ EN" text
    try:
        font_size = size // 6
        # Try to use a nice font, fall back to default
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()

        text = "KO\n⇄\nEN"

        # Get text bbox for centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2 - font_size // 4

        draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font, align='center')
    except Exception as e:
        print(f"Warning: Could not add text: {e}")

    return image

def main():
    print("Creating translator app icon...")

    # Create icon directory
    os.makedirs('icons', exist_ok=True)

    # Create main icon (512x512)
    icon = create_gradient_circle(512)
    icon.save('icons/icon.png')
    print("✓ Created icons/icon.png (512x512)")

    # Create smaller sizes for different uses
    sizes = [16, 32, 64, 128, 256]
    for size in sizes:
        resized = icon.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(f'icons/icon_{size}.png')
        print(f"✓ Created icons/icon_{size}.png")

    print("\n✓ All icon files created successfully!")
    print("Icon location: icons/icon.png")

if __name__ == '__main__':
    main()
