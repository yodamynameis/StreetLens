from utils import logger
from ocr_module import OCRProcessor
from extractor import InformationExtractor
from classifier import ShopClassifier
import os
from dotenv import load_dotenv

load_dotenv()

ocr_processor = OCRProcessor()
extractor = InformationExtractor()
classifier = ShopClassifier()

def process_image(image_path):
    logger.info(f"Processing: {os.path.basename(image_path)}")
    
    # Extract text from image
    text_lines = ocr_processor.extract_text(image_path)
    logger.info(f"Extracted text: {text_lines}")

    if not text_lines:
        logger.error("OCR returned no text; skipping extraction and classification")
        return {
            "image_name": os.path.basename(image_path),
            "error": "OCR failed. Gemini could not process the image or returned no text.",
            "shop_name": "",
            "phone_number": [],
            "category": "",
            "address": "",
            "gst_number": "",
        }

    # Extract structured fields
    extracted_data = extractor.extract_fields(text_lines)

    # Classify shop category
    category = classifier.classify(text_lines)
    logger.info(f"Shop category: {category}")

    # Build response - no duplicates
    final_data = {
        "image_name": os.path.basename(image_path),
        "shop_name": extracted_data["shop_name"],
        "phone_number": extracted_data["phone_number"],
        "category": category,
        "address": extracted_data["address"],
        "gst_number": extracted_data["gst_number"],
    }
    
    # Build miscellaneous with non-primary fields
    miscellaneous = {}
    
    if extracted_data["email"] != "NA":
        miscellaneous["email"] = extracted_data["email"]
    if extracted_data["website"] != "NA":
        miscellaneous["website"] = extracted_data["website"]
    
    # Add miscellaneous only if it has data
    if miscellaneous:
        final_data["miscellaneous"] = miscellaneous

    return final_data
