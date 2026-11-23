#!/usr/bin/env python3
"""
Prepare the portrait image for clean ASCII conversion:
  1. Remove background by detecting the uniform background color and thresholding
  2. Enhance contrast, sharpness, and edge details so facial contours and glasses stay sharp
  3. Ensure background is pure white (255) so it maps to blank spaces in ASCII output
  4. Save as source-prepped.png
"""
import os
import sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

def prep():
    img = Image.open(INP).convert("RGB")
    arr = np.array(img).astype(np.float32)

    # Detect background color from outer border samples
    border = np.concatenate([arr[0:5, :], arr[-5:, :], arr[:, 0:5], arr[:, -5:]], axis=None).reshape(-1, 3)
    bg_color = np.median(border, axis=0)
    print(f"Detected background color: {bg_color}")

    # Color distance from background
    dist = np.linalg.norm(arr - bg_color, axis=-1)
    
    # Smooth mask slightly to prevent harsh stepped artifacts
    raw_mask = (dist > 18.0).astype(np.float32)
    mask_im = Image.fromarray((raw_mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=1.0))
    mask = np.array(mask_im).astype(np.float32) / 255.0

    # Grayscale image
    gray_im = img.convert("L")
    # Enhance local contrast and sharpness
    gray_im = ImageOps.autocontrast(gray_im, cutoff=2)
    gray_im = gray_im.filter(ImageFilter.UnsharpMask(radius=2, percent=130, threshold=3))
    gray = np.array(gray_im).astype(np.float32)

    # Tone stretch: push lighter face areas slightly brighter so sparser ASCII chars are chosen
    p_low, p_high = np.percentile(gray[mask > 0.5], (2, 95))
    tone = np.clip((gray - p_low) / (p_high - p_low + 1e-5), 0, 1) * 255.0

    # Subject onto pure white background
    prepped = tone * mask + 255.0 * (1.0 - mask)
    out_im = Image.fromarray(np.clip(prepped, 0, 255).astype(np.uint8))
    
    out_im.save(OUT)
    print(f"Wrote prepped image: {OUT} ({out_im.size[0]}x{out_im.size[1]})")

if __name__ == "__main__":
    prep()
