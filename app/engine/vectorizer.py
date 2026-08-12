import numpy as np
import logging
from typing import List, Tuple
from app.engine.models import TemplateFingerprint

try:
    import torch
    import torchvision.transforms as transforms
    import torchvision.models as models
    from PIL import Image
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

logger = logging.getLogger(__name__)

# Lazy loaded model
_vision_model = None
_vision_transform = None

def get_vision_model():
    global _vision_model, _vision_transform
    if not HAS_TORCH:
        return None
        
    if _vision_model is None:
        logger.info("Initializing MobileNetV3 (CPU) for lightweight visual embedding...")
        # MobileNetV3 is highly optimized for CPU
        _vision_model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
        _vision_model.eval()
        
        # We only want the features, not the classification logits
        # However, keeping the 1000-d output is fine for a lightweight dense embedding.
        
        _vision_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
    return _vision_model

def vectorize_structural_fingerprint(fp: TemplateFingerprint) -> np.ndarray:
    """
    Flattens the deterministic structural TemplateFingerprint into a 140-d numpy array.
    100 (grid) + 20 (x_hist) + 20 (y_hist) = 140 dims.
    L2-Normalizes the array for FAISS Inner Product search.
    """
    # 1. Flatten the components
    grid = np.array(fp.spatial_grid, dtype=np.float32)
    x_hist = np.array(fp.x_alignment_hist, dtype=np.float32)
    y_hist = np.array(fp.y_alignment_hist, dtype=np.float32)
    
    # 2. Concatenate (length = 140)
    vector = np.concatenate([grid, x_hist, y_hist])
    
    # 3. L2 Normalize
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
        
    return vector

def generate_visual_embedding(image_path: str) -> np.ndarray:
    """
    Generates a dense visual embedding using MobileNetV3.
    L2-Normalizes the array for FAISS Inner Product search.
    Returns a 1000-d vector, or a zero vector if PyTorch isn't available.
    """
    if not HAS_TORCH:
        logger.warning("PyTorch not available. Returning zero visual embedding.")
        return np.zeros(1000, dtype=np.float32)
        
    try:
        model = get_vision_model()
        image = Image.open(image_path).convert('RGB')
        input_tensor = _vision_transform(image).unsqueeze(0) # Add batch dimension
        
        with torch.no_grad():
            output = model(input_tensor)
            
        vector = output.squeeze().numpy()
        
        # L2 Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector
        
    except Exception as e:
        logger.error(f"Failed to generate visual embedding for {image_path}: {e}")
        return np.zeros(1000, dtype=np.float32)
