import cv2
import base64
import google.genai as genai
from utils import logger
import os
from dotenv import load_dotenv

load_dotenv()

class OCRProcessor:
    def __init__(self):
        logger.info("Initializing Google Gemini Vision API...")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.5-flash'

    def preprocess_image(self, image_path):
        """Optional: basic preprocessing (resizing for API limits)"""
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                raise ValueError(f"Could not load image at {image_path}")
            
            # Resize if image is too large (Gemini has size limits)
            height, width = img.shape[:2]
            if max(height, width) > 4096:
                scale = 4096 / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            logger.info(f"Image preprocessed: {img.shape}")
            return img
        except Exception as e:
            logger.error(f"Preprocessing failed for {image_path}: {e}")
            return None

    def extract_text(self, image_path):
        """Extract text using Google Gemini Vision API"""
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image_path)
            if processed_img is None:
                return []

            # Read image and encode to base64
            with open(image_path, 'rb') as f:
                image_data = base64.standard_b64encode(f.read()).decode('utf-8')
            
            # Determine image type
            image_extension = image_path.split('.')[-1].lower()
            mime_types = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp'
            }
            mime_type = mime_types.get(image_extension, 'image/jpeg')

            # Call Gemini API with new syntax (using self.client)
            message = "Extract all text visible in this shop/storefront image. Return ONLY the text lines found, one per line. Do not include any analysis, just the raw text."
            
            # ✅ Use client.models.generate_content instead of model.generate_content
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": image_data
                                }
                            },
                            {
                                "text": message
                            }
                        ]
                    }
                ]
            )

            # Parse response
            if response and response.text:
                text_lines = [line.strip() for line in response.text.split('\n') if line.strip()]
                logger.info(f"Extracted {len(text_lines)} lines using Gemini API")
                return text_lines
            else:
                logger.warning("No text extracted from Gemini API")
                return []

        except Exception as e:
            logger.error(f"Gemini OCR failed for {image_path}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []