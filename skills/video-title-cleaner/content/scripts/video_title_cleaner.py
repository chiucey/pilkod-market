#!/usr/bin/env python3
"""
Video Title Cleaner Skill - Smart Version
------------------------------------------
A smarter tool for cleaning video file names with intelligent detection:

DETECTION MODES:
1. Standalone Topics (Part X/Y, Topic 1, Lesson 2) → "1 - Title" format
2. TV Series (Episode 1, S1E1) → "S1E1 - Title" format
3. Single Topic → Just "Title"
4. Common themes → Group into subfolder

Usage:
    python video_title_cleaner.py "/path/to/root/folder" [--preview]
"""

import os
import re
import shutil
import sys
from typing import List, Tuple, Dict, Optional
from collections import defaultdict


class VideoTitleCleaner:
    """Intelligently clean and organize video file names."""

    # Words to skip when extracting series name
    SKIP_WORDS = {
        'the', 'a', 'an', 'of', 'and', 'or', 'in', 'on', 'for', 'to',
        'part', 'episode', 'season', 'chapter', 'vol', 'volume', 'document',
    }

    # Words that indicate standalone topics (NOT TV series)
    STANDALONE_INDICATORS = {
        'part', 'lesson', 'topic', 'tip', 'way', 'method', 'step',
        'hack', 'technique', 'strategy', 'rule', 'secret', 'guide',
    }

    # Words that indicate TV-style series
    SERIES_INDICATORS = {
        'episode', 'season', 'ep', 'ep.', 'episode.', 's1', 's2',  # e.g., S1E1
        'series', 'chapter',  # when clearly TV-style
    }

    def is_standalone_numbering(self, filename: str) -> bool:
        """Check if filename uses standalone topic numbering (Part X/Y)."""
        name_lower = filename.lower()

        # Check for "Part X/Y" or "Part X" patterns
        if re.search(r'part\s*\d+\s*[/⁄]\s*\d+', name_lower):
            return True
        if re.search(r'\bpart\s+\d+\b', name_lower):
            return True

        # Check for "X/4" standalone patterns
        if re.search(r'\d+\s*[/⁄]\s*\d+\b', name_lower):
            return True

        # Check for common standalone indicators
        for indicator in self.STANDALONE_INDICATORS:
            if re.search(rf'\b{indicator}\s*\d+', name_lower):
                return True

        return False

    def is_series_numbering(self, filename: str) -> bool:
        """Check if filename uses TV-style series numbering."""
        name_lower = filename.lower()

        # Check for S1E1, S2E3 patterns
        if re.search(r's\d+e\d+', name_lower):
            return True

        # Check for explicit "Episode X" or "Ep. X" patterns
        if re.search(r'\b(episode|ep\.?|ep)\s*\d+', name_lower):
            return True

        # Check for "Season X Episode Y"
        if re.search(r'\bseason\s*\d+\b', name_lower):
            return True

        return False

    def extract_series_info(self, filename: str) -> Tuple[Optional[str], Optional[str], str, str]:
        """
        Extract series name, number, clean title, and numbering style from filename.

        Returns: (series_name, number, clean_title, numbering_style)
        numbering_style: 'standalone', 'series', or 'none'
        """
        name = filename

        # Remove extension
        for ext in ['.mp4', '.mkv', '.avi', '.mov']:
            if name.lower().endswith(ext):
                name = name[:-len(ext)]
                break

        original_name = name
        numbering_style = 'none'

        # Pattern 1a: "#N; Title" - already cleaned format with hash
        match = re.match(r'^#(\d+)\s*[,;]?\s*(.+)$', name, re.IGNORECASE)
        if match:
            number = match.group(1)
            title = match.group(2).strip()
            return None, number, title, 'standalone'

        # Pattern 1a2: "N - Title" or "N. Title" - already cleaned standalone format
        match = re.match(r'^(\d+)\s*[-.]\s*(.+)$', name)
        if match:
            number = match.group(1)
            title = match.group(2).strip()
            return None, number, title, 'standalone'

        # Pattern 1b: "Series Name #N; Title" - full format with explicit series
        match = re.match(r'^(.+?)\s*#(\d+)\s*[,;]?\s*(.+)$', name, re.IGNORECASE)
        if match:
            series = match.group(1).strip()
            number = match.group(2)
            title = match.group(3).strip()
            # Determine style from series name
            if self.is_series_numbering(series):
                return series, number, title, 'series'
            return series, number, title, 'standalone'

        # Pattern 1c: "Title Part X/4" or "Title - Part X/4" (supports fraction slash)
        match = re.match(r'^(.+?)\s*(?:Part\s*)?(\d+)\s*[/⁄]\s*4\s*[,;]?\s*(.*)$', name, re.IGNORECASE)
        if match:
            number = match.group(2)
            title = match.group(1).strip()
            subtitle = match.group(3).strip()
            if subtitle:
                title = f"{title}; {subtitle}"
            return None, number, title, 'standalone'

        # Pattern 1d: "Title Part X" - standalone topic
        match = re.match(r'^(.+?)\s*Part\s+(\d+)\s*[,;]?\s*(.*)$', name, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            number = match.group(2)
            subtitle = match.group(3).strip()
            if subtitle:
                title = f"{title}; {subtitle}"
            return None, number, title, 'standalone'

        # Pattern 2: "Speaker; Title (tech specs)" - use folder name as series
        match = re.match(r'^([^;]+?)\s*;\s*(.+?)\s*\([^)]+\)$', name, re.IGNORECASE)
        if match:
            series = None  # Will use folder name
            title = match.group(2).strip()
            return series, None, title, 'none'

        # Pattern 2b: "Title - Document Show Name _ Channel Date"
        match = re.match(r'^(.+?)\s*-\s*Document\s+(.+?)\s*_', name, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            show_name = match.group(2).strip()
            words = show_name.split()
            cleaned = ' '.join(w for w in words if w.lower() not in self.SKIP_WORDS or w.isdigit() or any(c.isdigit() for c in w))
            return cleaned, None, title, 'none'

        # Pattern 3: "Title - Show Name" (simple format)
        match = re.match(r'^(.+?)\s*-\s*(.+?)$', name)
        if match:
            part1 = match.group(1).strip()
            part2 = match.group(2).strip()
            # If part1 has hyphenated proper nouns (like US-Iran), keep as-is
            if '-' in part1 and any(c in part1 for c in ['Iran', 'US', 'UK', 'EU', 'UN']):
                return None, None, original_name, 'none'
            # If part2 looks like a show name
            if 5 <= len(part2) <= 60 and ' ' in part2 and not part2[0].isdigit() and not part2.startswith('('):
                return part2, None, part1, 'none'

        # No series detected
        return None, None, original_name, 'none'

    def clean_title(self, title: str) -> str:
        """Clean a title by removing technical terms."""
        name = title

        # Remove technical suffixes like (720p_60fps_H264-128kbit_AAC-English)
        name = re.sub(r'\s*\([^(]*\d+[^)]*\)', '', name)
        name = re.sub(r'\s*\(.*(?:fps|kbps|aac|h264|h265|mp4|english).*\)', '', name, flags=re.IGNORECASE)

        # Remove unusual characters
        name = name.replace('\u00bf', '')
        name = name.replace('\u00a1', '')
        name = name.replace('\u00a6', ' - ')
        name = name.replace('_', ' ')

        # Clean up
        name = re.sub(r'\s+', ' ', name)
        name = re.sub(r'^\s*[\-;,\s]+', '', name)
        name = re.sub(r'[\-;,\s]+$', '', name)
        name = name.strip()

        return name

    def normalize_series_name(self, name: str) -> str:
        """Normalize series name."""
        words = name.split()
        significant = []
        for w in words:
            if w.lower() not in self.SKIP_WORDS:
                significant.append(w)
            elif w.isdigit() or any(c.isdigit() for c in w):
                significant.append(w)
        return ' '.join(significant[:4]) if significant else name

    def scan_folder_tree(self, root_folder: str) -> Dict[str, List[Tuple]]:
        """Scan entire folder tree and group files by series."""
        series_files = defaultdict(list)

        for dirpath, dirnames, filenames in os.walk(root_folder):
            for filename in filenames:
                if not filename.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                    continue

                series, number, title, style = self.extract_series_info(filename)

                if title and title != filename:
                    clean_title = self.clean_title(title) or title
                    series_key = self.normalize_series_name(series) if series else os.path.basename(dirpath)
                    sort_key = number if number else filename
                    full_path = os.path.join(dirpath, filename)
                    series_files[series_key].append((sort_key, clean_title, full_path, style))

        for key in series_files:
            series_files[key].sort(key=lambda x: str(x[0]))

        return series_files

    def get_output_filename(self, number: Optional[str], title: str, numbering_style: str) -> str:
        """Generate clean output filename based on numbering style."""
        if number:
            ep_num = int(number)
            if numbering_style == 'series':
                return f"S1E{ep_num} - {title}.mp4"
            else:
                return f"{ep_num} - {title}.mp4"
        else:
            return f"{title}.mp4"

    def clean_folder(self, root_folder: str, dry_run: bool = False) -> List[Tuple[str, str]]:
        """Clean and reorganize files in folder tree."""
        results = []

        series_files = self.scan_folder_tree(root_folder)

        if not series_files:
            print("No series detected in folder tree.")
            return results

        print(f"Detected {len(series_files)} groups:")
        for series, files in sorted(series_files.items()):
            print(f"  - {series}: {len(files)} files")
        print()

        for series_name, file_list in sorted(series_files.items()):
            folder_name = os.path.basename(root_folder)
            normalized_folder = self.normalize_series_name(folder_name)

            # Use current folder if series matches folder name, otherwise create subfolder
            if self.normalize_series_name(series_name) == normalized_folder:
                series_folder = root_folder
                series_display = "(current folder)"
            else:
                series_folder = os.path.join(root_folder, series_name)
                series_display = series_name

            if not dry_run and series_folder != root_folder:
                os.makedirs(series_folder, exist_ok=True)
            elif not dry_run:
                os.makedirs(series_folder, exist_ok=True)

            for sort_key, title, full_path, style in file_list:
                number = sort_key if isinstance(sort_key, str) and sort_key.isdigit() else None
                output_name = self.get_output_filename(number, title, style)
                output_path = os.path.join(series_folder, output_name)

                original_name = os.path.basename(full_path)

                if dry_run:
                    results.append((original_name, f"{series_display}/{output_name}"))
                    print(f"  {original_name}")
                    print(f"    -> {series_display}/{output_name}")
                else:
                    if full_path != output_path:
                        shutil.move(full_path, output_path)
                        results.append((original_name, output_name))
                        print(f"  {original_name}")
                        print(f"    -> {series_display}/{output_name}")

        return results

    def preview_changes(self, root_folder: str) -> List[Tuple[str, str]]:
        """Preview changes without applying them."""
        return self.clean_folder(root_folder, dry_run=True)


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: python video_title_cleaner.py <root_folder> [--preview]")
        print("\nVideo Title Cleaner - Smart Version:")
        print("  1. Detects standalone topics (Part X/Y) -> '1 - Title'")
        print("  2. Detects TV series (Episode/S1E1) -> 'S1E1 - Title'")
        print("  3. Simplifies titles")
        print("\nExamples:")
        print("  python video_title_cleaner.py /path/to/folder           # Organize and rename")
        print("  python video_title_cleaner.py /path/to/folder --preview  # Preview changes")
        sys.exit(1)

    root_folder = sys.argv[1]
    preview_only = '--preview' in sys.argv

    cleaner = VideoTitleCleaner()

    if preview_only:
        print(f"Preview mode - no files will be moved or renamed\n")
        results = cleaner.preview_changes(root_folder)
    else:
        print(f"Organizing folder: {root_folder}\n")
        results = cleaner.clean_folder(root_folder)

    if not results:
        print("No changes needed.")
    else:
        print(f"\n{'Would move' if preview_only else 'Moved'} {len(results)} files.")
        if preview_only:
            print("\nRun without --preview to apply changes.")


if __name__ == "__main__":
    main()
