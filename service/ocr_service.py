from utils import logger
from ocr_module import OCRProcessor
import os
from dotenv import load_dotenv

load_dotenv()

ocr_processor = OCRProcessor()

def process_image(image_path):
    logger.info(f"Processing: {os.path.basename(image_path)}")
    
    text_lines = ocr_processor.extract_text(image_path)
    logger.info(f"The text identified is: {text_lines}")

    # Return only the extracted text for now
    final_data = {
        "image_name": os.path.basename(image_path),
        "extracted_text": text_lines
    }

    return final_data