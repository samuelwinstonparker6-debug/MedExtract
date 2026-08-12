import cv2
import numpy as np
import os
import glob

def analyze(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None: return
    laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
    total_pixels = img.shape[0] * img.shape[1]
    pure_white = np.sum(img >= 250)
    pure_black = np.sum(img <= 10)
    clean_ratio = (pure_white + pure_black) / total_pixels
    print(f"{os.path.basename(img_path)}:")
    print(f"  Laplacian Variance: {laplacian_var:.2f}")
    print(f"  Clean Pixel Ratio: {clean_ratio:.2f}")

if __name__ == "__main__":
    analyze("sunrise.png")
    for f in glob.glob("app/uploads/*.jpg")[:3]:
        analyze(f)
