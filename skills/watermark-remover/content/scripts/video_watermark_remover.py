#!/usr/bin/env python3
"""
Video Watermark Removal Script
Provides utilities for removing watermarks from videos frame-by-frame.
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import json
from pathlib import Path


class VideoWatermarkRemover:
    """Handles watermark removal for videos."""

    def __init__(self):
        self.frame_processor = FrameProcessor()

    def load_video(self, video_path: str) -> Tuple[cv2.VideoCapture, Dict]:
        """Load video and get metadata."""
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        metadata = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'codec': int(cap.get(cv2.CAP_PROP_FOURCC))
        }

        return cap, metadata

    def detect_static_watermark(self, cap: cv2.VideoCapture, metadata: Dict) -> List[Dict]:
        """Detect static watermarks that appear in the same position across frames."""
        regions = []
        sample_frames = [0, metadata['frame_count'] // 4,
                        metadata['frame_count'] // 2,
                        3 * metadata['frame_count'] // 4]

        frame_diffs = []

        # Sample frames to find consistent watermark regions
        for frame_idx in sample_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame_diffs.append(gray)

        # Compare frames to find consistent elements
        if len(frame_diffs) >= 2:
            # Find common bright/dark regions (potential watermarks)
            combined = np.mean(frame_diffs, axis=0)

            # Detect corners (common watermark positions)
            h, w = combined.shape
            corners = {
                'top_left': combined[0:h//4, 0:w//4],
                'top_right': combined[0:h//4, 3*w//4:w],
                'bottom_left': combined[3*h//4:h, 0:w//4],
                'bottom_right': combined[3*h//4:h, 3*w//4:w]
            }

            for corner_name, corner_region in corners.items():
                if np.std(corner_region) > 15:  # Has distinct pattern
                    if corner_name == 'top_left':
                        bbox = (0, 0, w//4, h//4)
                    elif corner_name == 'top_right':
                        bbox = (3*w//4, 0, w, h//4)
                    elif corner_name == 'bottom_left':
                        bbox = (0, 3*h//4, w//4, h)
                    else:
                        bbox = (3*w//4, 3*h//4, w, h)

                    regions.append({
                        'bbox': bbox,
                        'type': 'static',
                        'corner': corner_name,
                        'position': 'fixed'
                    })

        # Reset to beginning
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        return regions

    def detect_moving_watermark(self, cap: cv2.VideoCapture, metadata: Dict,
                                max_frames: int = 100) -> List[Dict]:
        """Detect moving watermarks by tracking positions across frames."""
        regions = []

        prev_gray = None
        positions = []

        frame_count = min(metadata['frame_count'], max_frames)
        for i in range(frame_count):
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_gray is not None:
                # Detect differences between consecutive frames
                diff = cv2.absdiff(gray, prev_gray)
                _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

                # Find contours in the difference
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    if cv2.contourArea(contour) > 100:
                        x, y, w, h = cv2.boundingRect(contour)
                        positions.append((x, y, w, h))

            prev_gray = gray.copy()

        # Reset to beginning
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        if positions:
            # Analyze position patterns
            x_positions = [p[0] for p in positions]
            y_positions = [p[1] for p in positions]

            regions.append({
                'bbox': (min(x_positions), min(y_positions),
                        max(x_positions) + 20, max(y_positions) + 20),
                'type': 'moving',
                'pattern': 'tracked',
                'position_count': len(positions)
            })

        return regions

    def remove_video_watermark(self, video_path: str,
                              watermark_regions: List[Dict] = None,
                              output_path: str = None) -> Tuple[bool, List[Dict]]:
        """
        Remove watermarks from video.

        Args:
            video_path: Input video path
            watermark_regions: Optional pre-detected regions
            output_path: Output video path

        Returns:
            Tuple of (success, detected_regions)
        """
        cap, metadata = self.load_video(video_path)

        # Auto-detect if regions not provided
        if watermark_regions is None:
            watermark_regions = self.detect_static_watermark(cap, metadata)
            if not watermark_regions:
                watermark_regions = self.detect_moving_watermark(cap, metadata)

        if not watermark_regions:
            cap.release()
            return False, []

        # Prepare output video writer
        if output_path is None:
            output_path = str(Path(video_path).with_suffix('.no_watermark.mp4'))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, metadata['fps'],
                           (metadata['width'], metadata['height']))

        # Process frames
        frame_count = metadata['frame_count']
        for i in range(frame_count):
            ret, frame = cap.read()
            if not ret:
                break

            # Apply inpainting for each watermark region
            for region in watermark_regions:
                x1, y1, x2, y2 = region['bbox']
                # Ensure bounds are within frame
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

                if x2 > x1 and y2 > y1:
                    # Extract region and mask
                    roi = frame[y1:y2, x1:x2].copy()
                    mask = np.ones((y2 - y1, x2 - x1), dtype=np.uint8) * 255

                    # Inpaint the region
                    try:
                        inpainted = cv2.inpaint(roi, mask, 3, cv2.INPAINT_TELEA)
                        frame[y1:y2, x1:x2] = inpainted
                    except Exception:
                        pass

            out.write(frame)

            # Progress indicator
            if i % 100 == 0:
                print(f"Processing frame {i}/{frame_count}")

        cap.release()
        out.release()

        return True, watermark_regions


class FrameProcessor:
    """Helper class for frame-level processing."""

    @staticmethod
    def apply_temporal_smoothing(frames: List[np.ndarray], window_size: int = 3) -> List[np.ndarray]:
        """Apply temporal smoothing to reduce flickering."""
        if len(frames) < window_size:
            return frames

        smoothed = []
        half_window = window_size // 2

        for i in range(len(frames)):
            start = max(0, i - half_window)
            end = min(len(frames), i + half_window + 1)

            # Average frames in window
            window_frames = frames[start:end]
            avg_frame = np.mean(window_frames, axis=0).astype(np.uint8)
            smoothed.append(avg_frame)

        return smoothed

    @staticmethod
    def detect_timestamp(frame: np.ndarray) -> Optional[Dict]:
        """Detect timestamp-like regions in a frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Timestamps often appear in corners with high contrast
        h, w = gray.shape

        # Check bottom-right corner (common timestamp position)
        roi = gray[7*h//8:h, 7*w//8:w]
        if np.mean(roi) > 128:  # Bright region
            return {
                'bbox': (7*w//8, 7*h//8, w, h),
                'type': 'timestamp'
            }

        return None


def main():
    """CLI interface for video watermark removal."""
    import argparse

    parser = argparse.ArgumentParser(description='Remove watermarks from videos')
    parser.add_argument('input', help='Input video path')
    parser.add_argument('-o', '--output', help='Output video path', required=True)

    args = parser.parse_args()

    remover = VideoWatermarkRemover()
    success, regions = remover.remove_video_watermark(args.input, output_path=args.output)

    if success:
        print(f"Removed watermarks from {len(regions)} regions")
        print(f"Output saved to: {args.output}")
    else:
        print("No watermarks detected")


if __name__ == '__main__':
    main()