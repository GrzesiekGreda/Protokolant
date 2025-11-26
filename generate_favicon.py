from PIL import Image, ImageDraw, ImageFont
import os

# Tworzymy ikonę 32x32 (favicon) i 64x64 (większa ikona)
sizes = [(32, 32), (64, 64)]

for size in sizes:
    width, height = size
    
    # Tworzenie obrazu z czarnym tłem
    image = Image.new('RGB', (width, height), color='#000000')
    draw = ImageDraw.Draw(image)
    
    # Czerwona ramka
    border_color = '#dc2626'
    border_width = 2 if width == 32 else 3
    corner_radius = 4 if width == 32 else 6
    
    # Rysowanie zaokrąglonego prostokąta (ramka)
    draw.rounded_rectangle(
        [(border_width//2, border_width//2), (width - border_width//2, height - border_width//2)],
        radius=corner_radius,
        outline=border_color,
        width=border_width
    )
    
    # Próba użycia czcionki Arial Black
    try:
        font_path = "C:/Windows/Fonts/ariblk.ttf"
        if not os.path.exists(font_path):
            font_path = "C:/Windows/Fonts/arialbd.ttf"
        font_size = 24 if width == 32 else 48
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()
    
    # Tekst do narysowania
    text = "G"
    
    # Pobieramy rozmiar tekstu
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Pozycja tekstu (wyśrodkowany)
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2 - (5 if width == 32 else 8)
    
    # Rysowanie tekstu z czerwoną obwódką
    outline_width = 1 if width == 32 else 2
    for adj_x in range(-outline_width, outline_width + 1):
        for adj_y in range(-outline_width, outline_width + 1):
            if adj_x != 0 or adj_y != 0:
                draw.text((text_x + adj_x, text_y + adj_y), text, font=font, fill=border_color)
    
    # Potem rysujemy czarne wypełnienie
    draw.text((text_x, text_y), text, font=font, fill='#000000')
    
    # Zapis obrazu
    if width == 32:
        output_path = os.path.join('static', 'favicon.ico')
        image.save(output_path, 'ICO', sizes=[(32, 32)])
        print(f"Favicon zapisane jako: {output_path}")
    else:
        output_path = os.path.join('static', 'images', 'icon-64.png')
        image.save(output_path, 'PNG')
        print(f"Ikona 64x64 zapisana jako: {output_path}")

print("Ikony wygenerowane pomyślnie!")
