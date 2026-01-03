import easyocr
import numpy as np
import os
from pdf2image import convert_from_path
from PIL import Image

class OCRService:
    _reader_cache = {}
    
    def __init__(self, languages=['en', 'fr']):
        """
        Initializes the OCR service with specified languages.
        """
        lang_key = tuple(sorted(languages))
        if lang_key not in OCRService._reader_cache:
            print(f"Loading EasyOCR model for languages: {languages}...")
            OCRService._reader_cache[lang_key] = easyocr.Reader(languages)
            print("EasyOCR model loaded.")
        
        self.reader = OCRService._reader_cache[lang_key]

    def extract_text(self, file_path):
        """
        Extracts text from a given file (PDF or Image).
        Route to specific handler based on file extension.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            return self._extract_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    def _extract_from_image(self, image_path):
        """
        Extracts text from an image file.
        """
        try:
            result = self.reader.readtext(image_path, detail=0)
            return " ".join(result)
        except Exception as e:
            print(f"Error during image extract: {e}")
            return ""

    def _extract_from_pdf(self, pdf_path):
        """
        Extracts text from PDF. 
        Strategy:
        1. Try native text extraction (fast, accurate for digital PDFs).
        2. If empty, fallback to OCR (slow, for scanned PDFs).
        """
        text_content = ""
        
        # 1. Try Native Extraction
        try:
            from pdfminer.high_level import extract_text
            text_content = extract_text(pdf_path)
            if text_content and len(text_content.strip()) > 50:
                print("Native PDF extraction successful.")
                return text_content
        except Exception as e:
            print(f"Native extraction failed: {e}")

        # 2. Fallback to OCR (Image-based)
        print("Falling back to OCR for PDF...")
        try:
            # Poppler needs to be installed on the system for pdf2image to work.
            # Assuming it is in the path or configured.
            images = convert_from_path(pdf_path)
            
            ocr_text = []
            for i, image in enumerate(images):
                print(f"Processing page {i+1}/{len(images)}...")
                # Convert PIL image to numpy array for EasyOCR
                image_np = np.array(image)
                result = self.reader.readtext(image_np, detail=0)
                ocr_text.append(" ".join(result))
                
            return "\n".join(ocr_text)
        except Exception as e:
            print(f"Error during PDF extract: {e}")
            return text_content # Return whatever we got from native if OCR also fails
