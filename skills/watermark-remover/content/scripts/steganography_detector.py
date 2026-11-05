#!/usr/bin/env python3
"""
Steganography Detector
Detects hidden watermarks in images using various steganographic analysis techniques.
"""

import numpy as np
from PIL import Image
import cv2
from typing import Dict, List, Optional, Tuple
from collections import Counter


class SteganographyDetector:
    """Detects hidden watermarks and steganographic content in images."""

    def __init__(self):
        self.techniques = [
            'lsb_analysis',
            'dct_analysis',
            'frequency_analysis',
            'metadata_inspection'
        ]

    def load_image(self, image_path: str) -> Tuple[np.ndarray, Image.Image]:
        """Load image for analysis."""
        pil_image = Image.open(image_path)
        cv_image = cv2.imread(image_path)
        return cv_image, pil_image

    def detect_lsb_watermark(self, image_path: str) -> Dict:
        """
        Detect LSB (Least Significant Bit) steganography.
        LSB hides data in the least significant bits of pixel values.
        """
        image = Image.open(image_path)
        pixels = np.array(image)

        results = {
            'technique': 'LSB Analysis',
            'suspicious': False,
            'confidence': 0.0,
            'details': []
        }

        if len(pixels.shape) < 3:
            return results

        # Analyze LSB distribution for each channel
        channels = ['Red', 'Green', 'Blue'] if len(pixels.shape) == 3 else ['Gray']

        for i, channel in enumerate(channels):
            channel_data = pixels[:, :, i] if len(pixels.shape) == 3 else pixels

            # Extract LSBs
            lsb = channel_data & 1

            # Count LSB distribution
            ones_ratio = np.mean(lsb)

            # Check for anomalies in LSB distribution
            # Natural images tend to have balanced LSB distribution (~50%)
            # Hidden data may show deviation from this pattern
            deviation = abs(ones_ratio - 0.5)

            if deviation > 0.05:  # Significant deviation
                results['suspicious'] = True
                results['details'].append({
                    'channel': channel,
                    'ones_ratio': float(ones_ratio),
                    'deviation': float(deviation),
                    'note': 'Unusual LSB distribution detected'
                })

            results['confidence'] = max(results['confidence'], deviation * 2)

        # Check for hidden text patterns in LSBs
        hidden_text_score = self._analyze_lsb_patterns(lsb)
        if hidden_text_score > 0.5:
            results['suspicious'] = True
            results['details'].append({
                'type': 'hidden_text_pattern',
                'score': hidden_text_score
            })

        return results

    def _analyze_lsb_patterns(self, lsb_data: np.ndarray) -> float:
        """Analyze LSB data for hidden patterns (potential hidden text)."""
        # Flatten and group bits into bytes
        bits = lsb_data.flatten()
        if len(bits) < 8:
            return 0.0

        # Check for ASCII-like patterns
        byte_score = 0
        for i in range(0, min(len(bits) - 8, 10000), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]

            # Check if byte resembles printable ASCII
            if 32 <= byte <= 126 or byte in [0, 255]:
                byte_score += 1

        return byte_score / min(len(bits) // 8, 10000)

    def detect_dct_watermark(self, image_path: str) -> Dict:
        """
        Detect DCT-based steganography (common in JPEG images).
        DCT modifies frequency coefficients to hide data.
        """
        results = {
            'technique': 'DCT Analysis',
            'suspicious': False,
            'confidence': 0.0,
            'details': []
        }

        # DCT analysis works best with JPEG images
        if not image_path.lower().endswith(('.jpg', '.jpeg')):
            results['details'].append('DCT analysis primarily effective for JPEG images')
            return results

        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Convert to float for DCT
            float_image = np.float32(gray)

            # Apply DCT
            dct = cv2.dft(float_image, flags=cv2.DCT_ROWS)

            # Analyze coefficient distribution
            dct_coeffs = dct.flatten()

            # Check for anomalies in high-frequency coefficients
            # Hidden data often modifies these coefficients
            high_freq = dct_coeffs[len(dct_coeffs)//2:]

            coefficient_variance = np.var(high_freq)
            coefficient_std = np.std(high_freq)

            # Look for unusual patterns in coefficient histogram
            hist, _ = np.histogram(high_freq, bins=50)
            hist_normalized = hist / np.sum(hist)

            # Calculate entropy of coefficient distribution
            entropy = -np.sum(hist_normalized * np.log2(hist_normalized + 1e-10))

            if entropy > 4.5:  # High entropy may indicate hidden data
                results['suspicious'] = True
                results['details'].append({
                    'entropy': float(entropy),
                    'variance': float(coefficient_variance),
                    'note': 'Unusual coefficient distribution'
                })
                results['confidence'] = min(1.0, (entropy - 4.5) / 2)

        except Exception as e:
            results['details'].append(f'Analysis error: {str(e)}')

        return results

    def detect_frequency_watermark(self, image_path: str) -> Dict:
        """
        Detect watermarks using frequency domain analysis.
        Watermarks often leave traces in the frequency domain.
        """
        results = {
            'technique': 'Frequency Analysis',
            'suspicious': False,
            'confidence': 0.0,
            'details': []
        }

        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Fourier transform
            f = np.fft.fft2(gray)
            fshift = np.fft.fftshift(f)
            magnitude = np.log(np.abs(fshift) + 1)

            # Analyze magnitude spectrum
            center_h, center_w = magnitude.shape[0] // 2, magnitude.shape[1] // 2

            # Check for unusual patterns in frequency spectrum
            # Look at specific frequency bands
            radius = 50
            center_region = magnitude[
                center_h - radius:center_h + radius,
                center_w - radius:center_w + radius
            ]

            center_mean = np.mean(center_region)
            overall_mean = np.mean(magnitude)

            # Significant difference may indicate watermarking
            ratio = center_mean / (overall_mean + 1e-10)

            if ratio > 2.0 or ratio < 0.5:
                results['suspicious'] = True
                results['details'].append({
                    'center_mean': float(center_mean),
                    'overall_mean': float(overall_mean),
                    'ratio': float(ratio),
                    'note': 'Unusual frequency spectrum pattern'
                })
                results['confidence'] = min(1.0, abs(ratio - 1.0) / 2)

        except Exception as e:
            results['details'].append(f'Analysis error: {str(e)}')

        return results

    def inspect_metadata(self, image_path: str) -> Dict:
        """
        Inspect image metadata for hidden watermarks or steganography markers.
        """
        results = {
            'technique': 'Metadata Inspection',
            'suspicious': False,
            'confidence': 0.0,
            'details': []
        }

        try:
            image = Image.open(image_path)

            # Check EXIF data
            exif_data = image.getexif()
            if exif_data:
                suspicious_tags = [
                    'Software', 'Artist', 'Copyright', 'UserComment',
                    'ImageDescription', 'XPAuthor', 'XPComment'
                ]

                for tag_id, tag_value in exif_data.items():
                    if tag_value and len(str(tag_value)) > 100:
                        results['suspicious'] = True
                        results['details'].append({
                            'tag_id': tag_id,
                            'length': len(str(tag_value)),
                            'note': 'Unusually long metadata field'
                        })
                        results['confidence'] = max(results['confidence'], 0.5)

            # Check for embedded ICC profiles (may contain watermark data)
            if image.info.get('icc_profile'):
                results['details'].append({
                    'type': 'icc_profile',
                    'size': len(image.info['icc_profile']),
                    'note': 'ICC profile detected (potential carrier)'
                })

            # Check PNG-specific chunks
            if 'pnginfo' in image.info:
                results['details'].append({
                    'type': 'png_metadata',
                    'note': 'PNG metadata chunks detected'
                })

        except Exception as e:
            results['details'].append(f'Analysis error: {str(e)}')

        return results

    def analyze_image(self, image_path: str, techniques: List[str] = None) -> Dict:
        """
        Comprehensive steganography analysis.

        Args:
            image_path: Path to the image to analyze
            techniques: List of techniques to apply (default: all)

        Returns:
            Dictionary containing analysis results
        """
        if techniques is None:
            techniques = self.techniques

        results = {
            'image_path': image_path,
            'overall_suspicious': False,
            'max_confidence': 0.0,
            'techniques': {},
            'summary': ''
        }

        technique_handlers = {
            'lsb_analysis': self.detect_lsb_watermark,
            'dct_analysis': self.detect_dct_watermark,
            'frequency_analysis': self.detect_frequency_watermark,
            'metadata_inspection': self.inspect_metadata
        }

        for technique in techniques:
            if technique in technique_handlers:
                result = technique_handlers[technique](image_path)
                results['techniques'][technique] = result

                if result.get('suspicious'):
                    results['overall_suspicious'] = True

                results['max_confidence'] = max(
                    results['max_confidence'],
                    result.get('confidence', 0.0)
                )

        # Generate summary
        if results['overall_suspicious']:
            results['summary'] = f"Potential hidden watermark detected (confidence: {results['max_confidence']:.2%})"
        else:
            results['summary'] = "No obvious signs of steganography detected"

        return results


def main():
    """CLI interface for steganography detection."""
    import argparse

    parser = argparse.ArgumentParser(description='Detect hidden watermarks in images')
    parser.add_argument('input', help='Input image path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    detector = SteganographyDetector()
    results = detector.analyze_image(args.input)

    print("=" * 50)
    print("STEGANOGRAPHY DETECTION REPORT")
    print("=" * 50)
    print(f"Image: {results['image_path']}")
    print(f"Status: {results['summary']}")
    print()

    if args.verbose:
        for technique, data in results['techniques'].items():
            print(f"\n{technique.upper()}:")
            print(f"  Suspicious: {data.get('suspicious', False)}")
            print(f"  Confidence: {data.get('confidence', 0.0):.2%}")
            if data.get('details'):
                for detail in data['details']:
                    print(f"  - {detail}")

    print(f"\nOverall Confidence: {results['max_confidence']:.2%}")


if __name__ == '__main__':
    main()