from PIL import Image
import numpy as np

extracted_dir = r"c:\RIYOMA\Internship\WallfitAI\scratch\extracted_media"

for name in ["image1.png", "image7.png"]:
    p = os.path.join(extracted_dir, name)
    if os.path.exists(p):
        img = Image.open(p)
        arr = np.array(img)
        # Get average color
        avg_color = arr.mean(axis=(0, 1))
        # Get color variance to see if it's colorful
        var_color = arr.var(axis=(0, 1))
        print(f"{name}: Avg color={avg_color}, Var color={var_color}")
        # Count unique colors in a small downsampled version
        small = img.resize((100, 100))
        unique_colors = len(set(small.getdata()))
        print(f"  Unique colors in 100x100 version: {unique_colors}")
    else:
        print(f"{name} does not exist!")
import os
