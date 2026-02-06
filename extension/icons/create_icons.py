# create_icons.py (run in extension/icons/ folder)
from PIL import Image, ImageDraw, ImageFont
import os

# Create 16x16 icon
img16 = Image.new('RGBA', (16, 16), (139, 92, 246, 255))
draw = ImageDraw.Draw(img16)
draw.rectangle([4, 4, 12, 12], fill=(255, 255, 255, 255))
img16.save('icon16.png')

# Create 48x48 icon  
img48 = Image.new('RGBA', (48, 48), (139, 92, 246, 255))
draw = ImageDraw.Draw(img48)
draw.rectangle([12, 12, 36, 36], fill=(255, 255, 255, 255))
img48.save('icon48.png')

# Create 128x128 icon
img128 = Image.new('RGBA', (128, 128), (139, 92, 246, 255))
draw = ImageDraw.Draw(img128)
draw.rectangle([32, 32, 96, 96], fill=(255, 255, 255, 255))
img128.save('icon128.png')