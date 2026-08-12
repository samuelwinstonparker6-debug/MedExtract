import os
import cv2
import fitz  # PyMuPDF
import numpy as np
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Constants for validation
SUPPORTED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}

def validate_file(file_path: str) -> None:
    """
    Validates if the file exists and has a supported extension.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {ext}. Supported: {SUPPORTED_EXTENSIONS}")

def render_document(file_path: str, output_dir: str, dpi: int = 300) -> List[str]:
    """
    Renders a document into a list of image paths.
    Supports PDF (rendering each page) and images (returning the path itself, or copying).
    """
    ext = os.path.splitext(file_path)[1].lower()
    rendered_images = []
    
    if ext == '.pdf':
        try:
            doc = fitz.open(file_path)
            zoom = dpi / 72.0
            matrix = fitz.Matrix(zoom, zoom)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                out_path = os.path.join(output_dir, f"page_{page_num}.png")
                pix.save(out_path)
                rendered_images.append(out_path)
        except Exception as e:
            logger.error(f"Failed to render PDF: {e}")
            raise
    else:
        # It's an image. Just copy or use as is. We'll read and rewrite to ensure PNG format
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError(f"Could not read image: {file_path}")
        out_path = os.path.join(output_dir, "page_0.png")
        cv2.imwrite(out_path, img)
        rendered_images.append(out_path)
        
    return rendered_images


def normalize_resolution(img: np.ndarray, target_height: int = 1500) -> np.ndarray:
    """
    Normalizes the image resolution for optimal OCR and Layout processing.
    """
    h, w = img.shape[:2]
    if h == 0 or w == 0:
        return img
    
    scale = target_height / h
    # Only upscale if it's too small, or downscale if it's massive
    if 0.5 < scale < 1.5:
        return img  # Close enough, don't resample
        
    new_w = int(w * scale)
    new_h = target_height
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)


def deskew_image(img: np.ndarray) -> np.ndarray:
    """
    Detects skew angle and rotates the image to correct it.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) == 0:
        return img
        
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
        
    if abs(angle) < 0.5 or abs(angle) > 45:
        return img # Ignore tiny skews or extreme ones which might not be text skew
        
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Pad to avoid cutting off corners
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    M[0, 2] += (nW / 2) - center[0]
    M[1, 2] += (nH / 2) - center[1]
    
    rotated = cv2.warpAffine(img, M, (nW, nH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


def reduce_noise_and_normalize_contrast(img: np.ndarray) -> np.ndarray:
    """
    Applies lightweight noise reduction and contrast normalization (CLAHE).
    Optimized for CPU-first rapid execution.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img.copy()
    
    # Lightweight noise reduction
    denoised = cv2.medianBlur(gray, 3)
    
    # Contrast normalization using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrasted = clahe.apply(denoised)
    
    # Convert back to BGR for consistency
    return cv2.cvtColor(contrasted, cv2.COLOR_GRAY2BGR)


def preprocess_for_pipeline(file_path: str, output_dir: str) -> List[str]:
    """
    Main preprocessing entry point.
    Returns a list of paths to the fully preprocessed page images.
    """
    validate_file(file_path)
    os.makedirs(output_dir, exist_ok=True)
    
    raw_images = render_document(file_path, output_dir)
    processed_images = []
    
    for idx, img_path in enumerate(raw_images):
        img = cv2.imread(img_path)
        if img is None:
            continue
            
        img = normalize_resolution(img)
        img = deskew_image(img)
        img = reduce_noise_and_normalize_contrast(img)
        
        # Overwrite or save as new
        final_path = os.path.join(output_dir, f"processed_page_{idx}.png")
        cv2.imwrite(final_path, img)
        processed_images.append(final_path)
        
    return processed_images

# Keep a stub for compatibility if older things imported it before full refactor
def preprocess_for_embedding(image_path: str) -> str:
    return image_path
