import logging
import base64
import cv2
import numpy as np
import json
from io import BytesIO
from PIL import Image

# Import steps
# Import steps
from engine.screenshotProcessor import ScreenshotProcessor
from engine.detection import UIElementDetector
from engine.ocrProcessing import OCRProcessor
from engine.layout_engine import LayoutEngine
from engine.generator import CodeGenerator

logger = logging.getLogger("ScreenshotConverter")

class ScreenshotPipeline:
    def __init__(self):
        logger.info("Loading Pipeline Components...")
        self.preprocessor = ScreenshotProcessor()
        self.detector = UIElementDetector()
        self.ocr = OCRProcessor()
        self.layout_engine = LayoutEngine()
        self.generator = CodeGenerator()
        logger.info("All components loaded.")

    def decode_image(self, base64_string: str):
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        image_data = base64.b64decode(base64_string)
        # Convert to numpy array for OpenCV
        nparr = np.frombuffer(image_data, np.uint8)
        img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img_cv2

    async def process(self, base64_image: str, framework: str = "react"):
        """
        Runs the 7-step pipeline and yields status updates.
        """
        try:
            # Step 0: Decode
            yield {"type": "status", "step": "decoding", "message": "Decoding image..."}
            original_image = self.decode_image(base64_image)
            height, width = original_image.shape[:2]
            
            # Step 1: Preprocessing
            yield {"type": "status", "step": "preprocessing", "message": "Preprocessing image..."}
            processed_image = self.preprocessor.preprocess(original_image)
            
            # Step 2: Detection
            yield {"type": "status", "step": "detection", "message": "Detecting UI elements..."}
            elements = self.detector.detect_elements(processed_image)
            yield {"type": "status", "step": "detection_complete", "count": len(elements)}

            # Step 3: OCR
            yield {"type": "status", "step": "ocr", "message": "Extracting text..."}
            element_texts = self.ocr.extract_text(original_image, elements)
            
            # Step 4-6: Layout & Style
            yield {"type": "status", "step": "layout", "message": "Analyzing layout & style..."}
            layout_tree = self.layout_engine.build_layout(elements, element_texts, width, height)
            
            # Step 7: Code Generation
            yield {"type": "status", "step": "generation", "message": f"Generating {framework} code..."}
            async for chunk in self.generator.generate_code_stream(layout_tree, framework):
                yield {"type": "code_chunk", "chunk": chunk}
            
            yield {"type": "status", "step": "complete", "message": "Conversion complete"}

        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}")
            yield {"type": "error", "message": str(e)}
