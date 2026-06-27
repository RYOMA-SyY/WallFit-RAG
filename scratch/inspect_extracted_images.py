from PIL import Image
import os

extracted_dir = r"c:\RIYOMA\Internship\WallfitAI\scratch\extracted_media"

for name in ["image1.png", "image7.png"]:
    p = os.path.join(extracted_dir, name)
    if os.path.exists(p):
        img = Image.open(p)
        print(f"Image {name}: Format={img.format}, Size={img.size}, Mode={img.mode}")
    else:
        print(f"Image {name} does not exist!")
