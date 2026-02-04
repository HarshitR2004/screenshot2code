import easyocr
import numpy as np
import logging

logger = logging.getLogger("ScreenshotConverter")

class OCRProcessor:
    def __init__(self, lang_list=['en']):
        logger.info("Initializing EasyOCR Reader...")
        # gpu=True requires CUDA. If no CUDA, set gpu=False or catch exception.
        try:
            self.reader = easyocr.Reader(lang_list, gpu=True)
        except Exception as e:
            logger.warning(f"EasyOCR GPU initialization failed: {e}. Falling back to CPU.")
            self.reader = easyocr.Reader(lang_list, gpu=False)
        logger.info("EasyOCR initialized.")

    def extract_text(self, img, elements=None):
        """
        Extracts text from the image.
        If elements are provided, we could map text to elements.
        For now, we'll return a dictionary mapping box tuples to text.
        """
        # EasyOCR expects RGB or Grayscale
        # If OpenCV image (BGR), convert to RGB
        import cv2
        if len(img.shape) == 3:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = img

        # Run OCR on the full image for now to catch everything contextually
        # detail=1 returns [box, text, confidence]
        results = self.reader.readtext(img_rgb, detail=1)

        extracted_data = []
        for res in results:
            box, text, conf = res
            # box is [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
            # convert to [x, y, w, h] roughly
            x_min = min(p[0] for p in box)
            y_min = min(p[1] for p in box)
            x_max = max(p[0] for p in box)
            y_max = max(p[1] for p in box)
            w = x_max - x_min
            h = y_max - y_min
            
            extracted_data.append({
                "text": text,
                "confidence": float(conf),
                "box": [int(x_min), int(y_min), int(w), int(h)]
            })

        return extracted_data
