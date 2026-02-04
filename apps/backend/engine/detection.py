import cv2
import numpy as np

class UIElementDetector:
    def __init__(self):
        pass

    def detect_elements(self, img):
        """
        Detects UI elements (buttons, inputs, containers) using contour detection.
        Returns a list of dictionaries: [{'type': 'block', 'box': [x, y, w, h]}]
        """
        # Convert to grayscale if not already
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # Adaptive thresholding to find edges/blocks
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        elements = []
        min_area = 100 # Filter out tiny noise
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(cnt)
                elements.append({
                    "type": "block", # Generic type for now, will refine in LayoutEngine
                    "box": [x, y, w, h]
                })

        # Sort elements by Y then X to roughly order them top-left to bottom-right
        elements.sort(key=lambda k: (k['box'][1], k['box'][0]))
        
        return elements
