#!/usr/bin/env python3
"""
Prepare the portrait image for clean, high-contrast, bold ASCII conversion:
  1. Remove background cleanly
  2. Enhance contrast, sharpness, and edge details
  3. Apply tone curve to deepen midtones so the face is dark and solid
  4. Ensure background is pure white (255)
  5. Save as source-prepped.png
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
    
    # Smooth mask
    raw_mask = (dist > 15.0).astype(np.float32)
    mask_im = Image.fromarray((raw_mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=1.0))
    mask = np.array(mask_im).astype(np.float32) / 255.0

    # Grayscale image with enhanced local contrast & strong edge sharpening
    gray_im = img.convert("L")
    gray_im = ImageOps.autocontrast(gray_im, cutoff=1)
    gray_im = gray_im.filter(ImageFilter.UnsharpMask(radius=3, percent=200, threshold=2))
    gray = np.array(gray_im).astype(np.float32)

    # Tone stretch: deepen midtones and shadows
    p_low = np.percentile(gray[mask > 0.5], 1)
    p_high = np.percentile(gray[mask > 0.5], 98)
    tone = np.clip((gray - p_low) / (p_high - p_low + 1e-5), 0, 1)

    # Apply power curve to give rich density to face and skin
    darkened_tone = np.power(tone, 1.25) * 255.0

    # Subject onto pure white background
    prepped = darkened_tone * mask + 255.0 * (1.0 - mask)
    out_im = Image.fromarray(np.clip(prepped, 0, 255).astype(np.uint8))
    
    out_im.save(OUT)
    print(f"Wrote prepped image: {OUT} ({out_im.size[0]}x{out_im.size[1]})")

if __name__ == "__main__":
    prep()
