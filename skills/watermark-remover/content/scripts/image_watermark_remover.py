#!/usr/bin/env python3
"""
Image Watermark Removal Script
Provides utilities for detecting and removing various types of watermarks from images.
"""

import cv2
import numpy as np
from PIL import Image
import io
from typing import Tuple, Optional, List, Dict


class ImageWatermarkRemover:
    """Handles watermark removal for images."""

    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']

    def load_image(self, image_path: str) -> np.ndarray:
        """Load image from file path."""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        return image

    def detect_text_watermark(self, image: np.ndarray) -> List[Dict]:
        """Detect text-based watermarks in image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Use MSER for text detection
        mser = cv2.MSER_create(_delta=5, _min_area=100, _max_area=500)
        regions, _ = mser.detectRegions(gray)

        text_regions = []
        for region in regions:
            x, y, w, h = cv2.boundingRect(region)
            # Filter for likely text regions
            aspect_ratio = w / h if h > 0 else 0
            if 0.1 < aspect_ratio < 10 and w > 20:
                text_regions.append({
                    'bbox': (x, y, x + w, y + h),
                    'type': 'text',
                    'confidence': 0.7
                })

        return text_regions

    def detect_logo_watermark(self, image: np.ndarray) -> List[Dict]:
        """Detect logo-based watermarks using feature matching."""
        # Edge detection for logo boundaries
        edges = cv2.Canny(image, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        logo_regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 50000:  # Typical logo size range
                x, y, w, h = cv2.boundingRect(contour)
                logo_regions.append({
                    'bbox': (x, y, x + w, y + h),
                    'type': 'logo',
                    'confidence': 0.6
                })

        return logo_regions

    def detect_semi_transparent_watermark(self, image: np.ndarray) -> List[Dict]:
        """Detect semi-transparent watermarks (like TV channel logos)."""
        # Analyze alpha channel or color distribution
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Semi-transparent watermarks often have distinct saturation
        _, saturation, _ = cv2.split(hsv)

        # Find regions with unique saturation patterns (corners often)
        height, width = saturation.shape
        corners = [
            (0, 0, width // 4, height // 4),  # Top-left
            (3 * width // 4, 0, width, height // 4),  # Top-right
            (0, 3 * height // 4, width // 4, height),  # Bottom-left
            (3 * width // 4, 3 * height // 4, width, height)  # Bottom-right
        ]

        detected = []
        for i, (x1, y1, x2, y2) in enumerate(corners):
            region = saturation[y1:y2, x1:x2]
            if region.size > 0 and np.std(region) > 10:
                detected.append({
                    'bbox': (x1, y1, x2, y2),
                    'type': 'semi_transparent',
                    'corner': ['top_left', 'top_right', 'bottom_left', 'bottom_right'][i],
                    'confidence': 0.5
                })

        return detected

    def create_mask(self, image: np.ndarray, regions: List[Dict]) -> np.ndarray:
        """Create binary mask from detected regions."""
        mask = np.zeros(image.shape[:2], dtype=np.uint8)

        for region in regions:
            x1, y1, x2, y2 = region['bbox']
            mask[y1:y2, x1:x2] = 255

        # Soft edges for better blending
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        return mask

    def inpaint_region(self, image: np.ndarray, mask: np.ndarray, method: str = 'telea') -> np.ndarray:
        """Remove watermarks using inpainting algorithms."""
        if method == 'telea':
            result = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA)
        else:
            result = cv2.inpaint(image, mask, 3, cv2.INPAINT_NS)

        return result

    def remove_pattern_watermark(self, image: np.ndarray) -> np.ndarray:
        """Remove repeating pattern watermarks using Fourier transform."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = np.float32(gray)

        # Fourier transform
        dft = cv2.dft(gray, flags=cv2.DFT_COMPLEX_OUTPUT)
        dft_shift = np.fft.fftshift(dft)

        # Create mask to remove periodic patterns
        rows, cols = gray.shape
        crow, ccol = rows // 2, cols // 2

        # Create circular mask
        mask = np.ones((rows, cols, 2), np.uint8)
        r = 30  # Remove central region (watermark artifacts)
        center = [crow, ccol]
        x, y = np.ogrid[:rows, :cols]
        mask_area = (x - center[0]) ** 2 + (y - center[1]) ** 2 <= r * r
        mask[mask_area] = 0

        # Apply mask and inverse DFT
        fshift = dft_shift * mask
        f_ishift = np.fft.ifftshift(fshift)
        img_back = cv2.idft(f_ishift, flags=cv2.DFT_SCALE | cv2.DFT_REAL_OUTPUT)

        # Convert back to BGR
        result = cv2.cvtColor(img_back.astype(np.uint8), cv2.COLOR_GRAY2BGR)

        return result

    def remove_watermark(self, image_path: str, regions: List[Dict] = None,
                        method: str = 'auto') -> Tuple[np.ndarray, List[Dict]]:
        """
        Main function to remove watermarks from an image.

        Args:
            image_path: Path to the input image
            regions: Optional pre-detected regions to remove
            method: 'auto', 'inpaint', or 'fourier'

        Returns:
            Tuple of (result_image, detected_regions)
        """
        image = self.load_image(image_path)

        # Auto-detect if regions not provided
        if regions is None:
            regions = []
            regions.extend(self.detect_text_watermark(image))
            regions.extend(self.detect_logo_watermark(image))
            regions.extend(self.detect_semi_transparent_watermark(image))

        if not regions:
            return image, []

        # Create mask from regions
        mask = self.create_mask(image, regions)

        # Select method based on watermark type
        if method == 'auto':
            # Check if it's a pattern watermark
            has_pattern = any(r['type'] == 'semi_transparent' for r in regions)
            method = 'fourier' if has_pattern else 'inpaint'

        # Apply removal
        if method == 'fourier':
            result = self.remove_pattern_watermark(image)
        else:
            result = self.inpaint_region(image, mask)

        return result, regions

    def save_image(self, image: np.ndarray, output_path: str) -> bool:
        """Save image to file."""
        return cv2.imwrite(output_path, image)


def main():
    """CLI interface for image watermark removal."""
    import argparse

    parser = argparse.ArgumentParser(description='Remove watermarks from images')
    parser.add_argument('input', help='Input image path')
    parser.add_argument('-o', '--output', help='Output image path', required=True)
    parser.add_argument('--method', choices=['auto', 'inpaint', 'fourier'],
                       default='auto', help='Removal method')

    args = parser.parse_args()

    remover = ImageWatermarkRemover()
    result, regions = remover.remove_watermark(args.input, method=args.method)

    remover.save_image(result, args.output)
    print(f"Removed {len(regions)} watermark regions")
    print(f"Output saved to: {args.output}")


if __name__ == '__main__':
    main()