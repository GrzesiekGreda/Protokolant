from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# Rozmiar obrazu
width, height = 400, 200

# Tworzenie obrazu z czarnym tłem
image = Image.new('RGB', (width, height), color='#000000')
draw = ImageDraw.Draw(image)

# Rysowanie czerwonej ramki
border_color = '#dc2626'
border_width = 6
corner_radius = 20

# Rysowanie zaokrąglonego prostokąta (ramka)
draw.rounded_rectangle(
    [(border_width//2, border_width//2), (width - border_width//2, height - border_width//2)],
    radius=corner_radius,
    outline=border_color,
    width=border_width
)

# Próba użycia czcionki Arial Black
try:
    # Szukamy czcionki w systemie Windows
    font_path = "C:/Windows/Fonts/ariblk.ttf"
    if not os.path.exists(font_path):
        font_path = "C:/Windows/Fonts/arialbd.ttf"  # Arial Bold jako alternatywa
    font = ImageFont.truetype(font_path, 70)
except:
    # Użycie domyślnej czcionki jeśli nie ma Arial
    font = ImageFont.load_default()

# Tekst do narysowania
text = "GREDA"

# Pobieramy rozmiar tekstu
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Pozycja tekstu (wyśrodkowany)
text_x = (width - text_width) // 2
text_y = (height - text_height) // 2 - 25

# Rysowanie tekstu z czerwoną obwódką
# Najpierw rysujemy czerwoną obwódkę (grubą)
outline_width = 3
for adj_x in range(-outline_width, outline_width + 1):
    for adj_y in range(-outline_width, outline_width + 1):
        if adj_x != 0 or adj_y != 0:
            draw.text((text_x + adj_x, text_y + adj_y), text, font=font, fill=border_color)

# Potem rysujemy czarne wypełnienie
draw.text((text_x, text_y), text, font=font, fill='#000000')

# Zapis obrazu
output_path = os.path.join('static', 'images', 'logo.png')
image.save(output_path, 'PNG', quality=100)
print(f"Logo zapisane jako: {output_path}")
