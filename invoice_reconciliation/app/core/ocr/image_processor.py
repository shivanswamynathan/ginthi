import cv2
import numpy as np
import requests
import io
from PIL import Image, ImageEnhance, ImageFilter
import base64
import logging
from typing import Dict, Any
import tempfile
import os
import fitz  # PyMuPDF for PDF processing

logger = logging.getLogger(__name__)


def download_image_from_url(url: str) -> np.ndarray:
    """Download and convert image to OpenCV format"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        
        # Convert to OpenCV format
        image = Image.open(io.BytesIO(response.content))
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        return opencv_image
        
    except Exception as e:
        logger.error(f"Error downloading image from {url}: {str(e)}")
        raise


def download_pdf_from_url(url: str) -> bytes:
    """Download PDF content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        return response.content
        
    except Exception as e:
        logger.error(f"Error downloading PDF from {url}: {str(e)}")
        raise


def preprocess_image_advanced(pil_image: Image.Image) -> Image.Image:
    """Advanced image preprocessing using proven methods"""
    try:
        logger.info("Applying advanced image preprocessing...")
        
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert PIL Image to OpenCV format
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # Noise reduction using bilateral filter
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Morphological operations to clean up the image
        kernel = np.ones((1,1), np.uint8)
        gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        
        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        # Convert back to PIL Image
        processed_image = Image.fromarray(binary)
        
        # Additional PIL enhancements
        processed_image = processed_image.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Sharpness(processed_image)
        processed_image = enhancer.enhance(2.0)
        
        logger.info("Advanced preprocessing completed")
        return processed_image
        
    except Exception as e:
        logger.error(f"Error in advanced preprocessing: {e}")
        return pil_image


def image_to_base64(pil_image: Image.Image) -> str:
    """Convert PIL Image to base64 string"""
    try:
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Error converting image to base64: {str(e)}")
        return ""


def process_pdf_pages(pdf_content: bytes) -> list:
    """Process PDF pages and convert to PIL Images"""
    try:
        pages_data = []
        
        # Process PDF pages
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(pdf_content)
            tmp_file_path = tmp_file.name
        
        try:
            doc = fitz.open(tmp_file_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Convert page to high-resolution image
                mat = fitz.Matrix(2.0, 2.0)  # 2x resolution
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Convert to PIL Image
                pil_image = Image.open(io.BytesIO(img_data))
                
                pages_data.append({
                    'page_number': page_num + 1,
                    'pil_image': pil_image
                })
            
            return pages_data
            
        finally:
            try:
                doc.close()
            except:
                pass
            try:
                os.unlink(tmp_file_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Error processing PDF pages: {str(e)}")
        raise