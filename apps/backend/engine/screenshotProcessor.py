import cv2
import numpy as np


class ScreenshotProcessor:
    def __init__(
        self,
        fixed_width=1024,
        clahe_clip=2.0,
        clahe_grid=(8, 8),
        sharpen_strength=1.0,
        crop_margin=0.02
    ):
        self.fixed_width = fixed_width
        self.clahe_clip = clahe_clip
        self.clahe_grid = clahe_grid
        self.sharpen_strength = sharpen_strength
        self.crop_margin = crop_margin

        self.clahe = cv2.createCLAHE(
            clipLimit=self.clahe_clip,
            tileGridSize=self.clahe_grid
        )

    def resize_fixed_width(self, img):
        h, w = img.shape[:2]
        scale = self.fixed_width / w
        new_h = int(h * scale)
        return cv2.resize(img, (self.fixed_width, new_h), interpolation=cv2.INTER_AREA)

    def apply_clahe(self, img):
        if len(img.shape) == 3:
            # Convert to LAB color space to separate lightness from color
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            # Apply CLAHE to the L-channel
            l2 = self.clahe.apply(l)
            # Merge and convert back to BGR
            lab = cv2.merge((l2, a, b))
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            # If already grayscale
            return self.clahe.apply(img)

    def mild_sharpen(self, img):
        kernel = np.array([
            [0, -1, 0],
            [-1, 5 + self.sharpen_strength, -1],
            [0, -1, 0]
        ])
        return cv2.filter2D(img, -1, kernel)

    def crop_outer_background(self, img):
        h, w = img.shape[:2]
        dx = int(w * self.crop_margin)
        dy = int(h * self.crop_margin)
        return img[dy:h - dy, dx:w - dx]

    def preprocess(self, img):
        """
        Full preprocessing pipeline:
        Resize → CLAHE → Sharpen → Crop
        """
        img = self.resize_fixed_width(img)
        contrast = self.apply_clahe(img)
        sharpened = self.mild_sharpen(contrast)
        final = self.crop_outer_background(sharpened)
        return final
