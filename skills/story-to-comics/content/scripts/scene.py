"""
Scene Generation Module
Generate realistic comic backgrounds with physical characteristics
"""

from typing import Tuple, Dict, List, Optional
from PIL import Image, ImageDraw, ImageFilter
import random
import math

from .parser import Scene


class SceneGenerator:
    """Scene generator with realistic physical characteristics"""

    # Scene themes with realistic colors
    SCENE_THEMES = {
        "library": {
            "name": "Library",
            "colors": [(245, 222, 179), (210, 180, 140), (139, 90, 43)],
            "elements": ["bookshelf", "desk", "window", "lamp", "book"]
        },
        "classroom": {
            "name": "Classroom",
            "colors": [(240, 240, 235), (200, 200, 200), (100, 100, 100)],
            "elements": ["blackboard", "desk", "chair", "window", "projector"]
        },
        "outdoor": {
            "name": "Outdoor",
            "colors": [(135, 206, 235), (144, 238, 144), (255, 255, 224)],
            "elements": ["sky", "grass", "tree", "sun", "cloud"]
        },
        "street": {
            "name": "Street",
            "colors": [(169, 169, 169), (105, 105, 105), (245, 245, 220)],
            "elements": ["building", "road", "lamp", "tree", "sign"]
        },
        "room": {
            "name": "Room",
            "colors": [(255, 248, 220), (245, 245, 220), (210, 180, 140)],
            "elements": ["wall", "floor", "window", "furniture", "lamp"]
        },
        "fantasy": {
            "name": "Fantasy",
            "colors": [(147, 112, 219), (186, 85, 211), (138, 43, 226)],
            "elements": ["particle", "glow", "star", "magic", "light"]
        },
        "virtual": {
            "name": "Virtual",
            "colors": [(0, 191, 255), (30, 144, 255), (0, 0, 139)],
            "elements": ["grid", "data", "glow", "node", "line"]
        }
    }

    def __init__(self, width: int = 1200, height: int = 900):
        """Initialize scene generator"""
        self.width = width
        self.height = height
        self.cache: Dict[str, Image.Image] = {}

    def detect_scene_type(self, scene: Scene) -> str:
        """Detect scene type from scene description"""
        text = (scene.title + " " + scene.camera_desc + " " +
                " ".join([d.action for d in scene.dialogues])).lower()

        keywords_map = {
            "library": ["library", "book", "书架", "书", "借阅", "归还", "图书馆", "阅读"],
            "classroom": ["classroom", "教室", "课堂", "上课", "讲台", "黑板", "学生", "学校"],
            "outdoor": ["outdoor", "outside", "park", "户外", "外面", "街道", "校园", "天空"],
            "room": ["room", "bedroom", "office", "房间", "卧室", "宿舍", "办公室", "室内"],
            "fantasy": ["fantasy", "magic", "virtual", "dream", "奇幻", "虚拟", "空间", "幻想", "投影", "梦境"],
            "virtual": ["digital", "screen", "computer", "network", "网络", "屏幕", "电脑", "数据", "搜索"]
        }

        for scene_type, keywords in keywords_map.items():
            if any(kw in text for kw in keywords):
                return scene_type

        return "room"

    def generate_scene(self, scene: Scene, style: str = "realistic") -> Image.Image:
        """Generate scene image"""
        scene_type = self.detect_scene_type(scene)

        cache_key = f"{scene_type}_{style}_{self.width}_{self.height}"
        if cache_key in self.cache:
            return self.cache[cache_key].copy()

        if style == "realistic" or style == "traditional":
            img = self._generate_realistic_scene(scene_type)
        elif style == "cartoon":
            img = self._generate_cartoon_scene(scene_type)
        else:
            img = self._generate_realistic_scene(scene_type)

        img = self._add_scene_elements(img, scene_type, style)
        img = self._add_lighting_effect(img, scene_type)

        self.cache[cache_key] = img
        return img

    def _generate_realistic_scene(self, scene_type: str) -> Image.Image:
        """Generate realistic scene with gradients and shadows"""
        theme = self.SCENE_THEMES.get(scene_type, self.SCENE_THEMES["room"])
        colors = theme["colors"]

        img = Image.new('RGB', (self.width, self.height), colors[0])
        draw = ImageDraw.Draw(img)

        # Draw gradient background (sky effect - darker at top)
        for y in range(self.height):
            ratio = y / self.height
            # Invert ratio for sky-like gradient (lighter at bottom)
            adjusted_ratio = 1 - ratio
            r = int(colors[0][0] * adjusted_ratio + colors[1][0] * ratio * 0.5)
            g = int(colors[0][1] * adjusted_ratio + colors[1][1] * ratio * 0.5)
            b = int(colors[0][2] * adjusted_ratio + colors[1][2] * ratio * 0.5)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        # Add floor/wall division line for interior scenes
        if scene_type in ["library", "classroom", "room"]:
            floor_y = int(self.height * 0.7)
            floor_color = colors[2] if len(colors) > 2 else (150, 130, 100)
            draw.rectangle([0, floor_y, self.width, self.height], fill=floor_color)

            # Add perspective lines for floor
            horizon = floor_y
            for i in range(20):
                x = random.randint(0, self.width)
                draw.line([(x, horizon), (x + random.randint(-50, 50), self.height)],
                         fill=self._darken_color(floor_color, 0.9), width=1)

        return img

    def _generate_cartoon_scene(self, scene_type: str) -> Image.Image:
        """Generate cartoon style scene"""
        theme = self.SCENE_THEMES.get(scene_type, self.SCENE_THEMES["room"])
        base_color = theme["colors"][1]

        img = Image.new('RGB', (self.width, self.height), base_color)

        # Add decorative elements
        draw = ImageDraw.Draw(img)
        self._draw_cartoon_clouds(draw, count=3)

        return img

    def _add_scene_elements(self, img: Image.Image, scene_type: str,
                           style: str) -> Image.Image:
        """Add physical scene elements"""
        draw = ImageDraw.Draw(img)
        theme = self.SCENE_THEMES.get(scene_type, self.SCENE_THEMES["room"])

        if scene_type == "library":
            self._draw_library_scene(draw, style)
        elif scene_type == "classroom":
            self._draw_classroom_scene(draw, style)
        elif scene_type == "outdoor":
            self._draw_outdoor_scene(draw, style)
        elif scene_type == "virtual" or scene_type == "fantasy":
            self._draw_digital_scene(draw, style)
        elif scene_type == "room":
            self._draw_room_scene(draw, style)

        return img

    def _draw_library_scene(self, draw: ImageDraw.ImageDraw, style: str) -> None:
        """Draw realistic library scene"""
        shelf_color = (101, 67, 33)  # Wood brown
        book_colors = [
            (178, 34, 34), (0, 100, 0), (25, 25, 112), (139, 69, 19),
            (85, 107, 47), (72, 61, 139), (143, 188, 143), (165, 42, 42)
        ]

        # Draw bookshelf (right side)
        shelf_x = self.width - 250
        shelf_y = 50
        shelf_w = 220
        shelf_h = self.height - 100

        # Shelf back
        draw.rectangle([shelf_x, shelf_y, shelf_x + shelf_w, shelf_y + shelf_h],
                      fill=(245, 222, 179))

        # Shelf frame
        frame_width = 15
        draw.rectangle([shelf_x, shelf_y, shelf_x + frame_width, shelf_y + shelf_h],
                      fill=shelf_color)
        draw.rectangle([shelf_x + shelf_w - frame_width, shelf_y, shelf_x + shelf_w, shelf_y + shelf_h],
                      fill=shelf_color)

        # Draw shelves
        num_shelves = 5
        shelf_spacing = (shelf_h - 40) // num_shelves

        for i in range(num_shelves):
            shelf_level_y = shelf_y + 20 + i * shelf_spacing
            # Shelf board
            draw.rectangle([shelf_x + frame_width, shelf_level_y,
                          shelf_x + shelf_w - frame_width, shelf_level_y + 10],
                          fill=shelf_color)

            # Books on shelf
            book_x = shelf_x + frame_width + 10
            book_top = shelf_level_y + 10
            book_bottom = shelf_level_y + shelf_spacing - 10

            while book_x < shelf_x + shelf_w - frame_width - 20:
                book_width = random.randint(15, 30)
                book_height = book_bottom - book_top - random.randint(0, 10)
                book_color = random.choice(book_colors)

                draw.rectangle([book_x, book_bottom - book_height,
                              book_x + book_width, book_bottom],
                              fill=book_color)

                # Book spine highlight
                draw.line([(book_x, book_bottom - book_height),
                          (book_x, book_bottom)],
                         fill=self._lighten_color(book_color, 1.3), width=1)

                book_x += book_width + 2

        # Draw reading desk (left side)
        desk_x = 100
        desk_y = self.height - 200
        desk_w = 300
        desk_h = 100

        draw.rectangle([desk_x, desk_y, desk_x + desk_w, desk_y + desk_h],
                      fill=(139, 90, 43))
        # Desk top
        draw.rectangle([desk_x - 10, desk_y, desk_x + desk_w + 10, desk_y + 10],
                      fill=(165, 42, 42))

        # Draw book on desk
        book_x = desk_x + 50
        book_y = desk_y - 40
        draw.rectangle([book_x, book_y, book_x + 80, book_y + 50],
                      fill=(220, 220, 220))
        draw.rectangle([book_x + 5, book_y + 5, book_x + 75, book_y + 45],
                      fill=(245, 245, 240))

        # Draw lamp
        lamp_x = desk_x + desk_w - 60
        lamp_y = desk_y - 120
        # Lamp base
        draw.ellipse([lamp_x, lamp_y + 80, lamp_x + 40, lamp_y + 100],
                    fill=(50, 50, 50))
        # Lamp pole
        draw.rectangle([lamp_x + 15, lamp_y + 30, lamp_x + 25, lamp_y + 80],
                      fill=(80, 80, 80))
        # Lamp shade
        draw.polygon([
            (lamp_x - 10, lamp_y + 30),
            (lamp_x + 50, lamp_y + 30),
            (lamp_x + 35, lamp_y),
            (lamp_x + 5, lamp_y)
        ], fill=(255, 200, 100))

        # Lamp glow
        glow_color = (255, 220, 150)
        draw.ellipse([lamp_x - 30, lamp_y + 20, lamp_x + 70, lamp_y + 150],
                    fill=glow_color)

        # Window (back wall)
        window_x = self.width // 2 - 100
        window_y = 80
        window_w = 200
        window_h = 150

        draw.rectangle([window_x, window_y, window_x + window_w, window_y + window_h],
                      fill=(135, 206, 235))  # Sky blue
        # Window frame
        draw.rectangle([window_x, window_y, window_x + window_w, window_y + window_h],
                      outline=(200, 200, 200), width=8)
        # Window panes
        draw.line([(window_x + window_w // 2, window_y),
                  (window_x + window_w // 2, window_y + window_h)],
                 fill=(200, 200, 200), width=4)
        draw.line([(window_x, window_y + window_h // 2),
                  (window_x + window_w, window_y + window_h // 2)],
                 fill=(200, 200, 200), width=4)

        # Light from window
        light_points = [
            (window_x, window_y + window_h),
            (window_x + window_w, window_y + window_h),
            (window_x + window_w + 100, self.height),
            (window_x - 100, self.height)
        ]
        draw.polygon(light_points, fill=(255, 255, 200, 80))

    def _draw_classroom_scene(self, draw: ImageDraw.ImageDraw, style: str) -> None:
        """Draw realistic classroom scene"""
        # Black/whiteboard
        board_x = self.width // 2 - 200
        board_y = 100
        board_w = 400
        board_h = 150

        draw.rectangle([board_x, board_y, board_x + board_w, board_y + board_h],
                      fill=(240, 248, 255))  # Whiteboard
        draw.rectangle([board_x, board_y, board_x + board_w, board_y + board_h],
                      outline=(50, 50, 50), width=5)

        # Writing on board
        draw.line([(board_x + 30, board_y + 50), (board_x + 150, board_y + 50)],
                 fill=(30, 30, 30), width=3)
        draw.line([(board_x + 30, board_y + 80), (board_x + 100, board_y + 80)],
                 fill=(30, 30, 30), width=3)

        # Desks and chairs (perspective view)
        desk_color = (139, 90, 43)
        chair_color = (100, 70, 30)

        for i in range(4):
            offset = i * 80
            scale = 1 - i * 0.15

            desk_x = self.width // 2 - 100 * scale + offset * 0.5
            desk_y = self.height - 150 - offset
            desk_w = 200 * scale
            desk_h = 80 * scale

            # Desk
            draw.rectangle([desk_x, desk_y, desk_x + desk_w, desk_y + desk_h],
                          fill=desk_color)

            # Chair (behind desk)
            chair_x = desk_x + desk_w // 2 - 20 * scale
            chair_y = desk_y - 40 * scale
            draw.rectangle([chair_x, chair_y, chair_x + 40 * scale, chair_y + 30 * scale],
                          fill=chair_color)

        # Window
        window_x = 50
        window_y = 80
        draw.rectangle([window_x, window_y, window_x + 150, window_y + 120],
                      fill=(135, 206, 235))
        draw.rectangle([window_x, window_y, window_x + 150, window_y + 120],
                      outline=(255, 255, 255), width=6)

    def _draw_outdoor_scene(self, draw: ImageDraw.ImageDraw, style: str) -> None:
        """Draw realistic outdoor scene with sun, clouds, trees"""
        # Sun
        sun_x = self.width - 150
        sun_y = 100
        sun_r = 50

        # Sun glow
        for i in range(3):
            glow_r = sun_r + i * 20
            glow_alpha = 100 - i * 30
            draw.ellipse([sun_x - glow_r, sun_y - glow_r,
                         sun_x + glow_r, sun_y + glow_r],
                        fill=(255, 255, 200))

        # Sun core
        draw.ellipse([sun_x - sun_r, sun_y - sun_r,
                     sun_x + sun_r, sun_y + sun_r],
                    fill=(255, 220, 50))

        # Clouds
        self._draw_realistic_cloud(draw, 100, 60)
        self._draw_realistic_cloud(draw, 400, 40)
        self._draw_realistic_cloud(draw, 700, 80)

        # Trees
        self._draw_tree(draw, 100, self.height - 100, height=150)
        self._draw_tree(draw, 800, self.height - 100, height=120)

        # Ground
        ground_y = self.height - 100
        draw.rectangle([0, ground_y, self.width, self.height],
                      fill=(85, 139, 47))  # Grass green

        # Path/road
        path_x = self.width // 2 - 50
        draw.rectangle([path_x, ground_y, path_x + 100, self.height],
                      fill=(189, 183, 107))

    def _draw_room_scene(self, draw: ImageDraw.ImageDraw, style: str) -> None:
        """Draw realistic room scene"""
        # Wall
        draw.rectangle([0, 0, self.width, self.height - 150],
                      fill=(250, 248, 245))

        # Floor
        draw.rectangle([0, self.height - 150, self.width, self.height],
                      fill=(160, 120, 80))

        # Window with view
        window_x = self.width // 2 - 100
        window_y = 100
        draw.rectangle([window_x, window_y, window_x + 200, window_y + 180],
                      fill=(135, 206, 235))  # Sky
        draw.rectangle([window_x, window_y, window_x + 200, window_y + 180],
                      outline=(255, 255, 255), width=8)
        # Curtains
        draw.polygon([
            (window_x - 20, window_y - 10),
            (window_x + 40, window_y),
            (window_x + 40, window_y + 180),
            (window_x - 20, window_y + 190)
        ], fill=(200, 150, 150))
        draw.polygon([
            (window_x + 220, window_y - 10),
            (window_x + 160, window_y),
            (window_x + 160, window_y + 180),
            (window_x + 220, window_y + 190)
        ], fill=(200, 150, 150))

        # Desk
        desk_x = 100
        desk_y = self.height - 200
        draw.rectangle([desk_x, desk_y, desk_x + 200, desk_y + 100],
                      fill=(139, 90, 43))

        # Computer on desk
        monitor_x = desk_x + 50
        monitor_y = desk_y - 100
        draw.rectangle([monitor_x, monitor_y, monitor_x + 100, monitor_y + 80],
                      fill=(50, 50, 50))
        draw.rectangle([monitor_x + 5, monitor_y + 5, monitor_x + 95, monitor_y + 75],
                      fill=(200, 220, 255))  # Screen

    def _draw_digital_scene(self, draw: ImageDraw.ImageDraw, style: str) -> None:
        """Draw digital/virtual scene with grid and particles"""
        # Grid background
        grid_color = (0, 100, 200)
        grid_size = 50

        for x in range(0, self.width, grid_size):
            alpha = 50 + (x % 100)  # Varying alpha for depth
            draw.line([(x, 0), (x, self.height)], fill=grid_color, width=1)
        for y in range(0, self.height, grid_size):
            draw.line([(0, y), (self.width, y)], fill=grid_color, width=1)

        # Data nodes
        for _ in range(30):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(3, 10)
            draw.ellipse([x - size, y - size, x + size, y + size],
                        fill=(0, 200, 255))

        # Connection lines
        nodes = [(random.randint(0, self.width), random.randint(0, self.height))
                for _ in range(10)]
        for i in range(len(nodes) - 1):
            draw.line([nodes[i], nodes[i + 1]],
                     fill=(0, 150, 255), width=2)

    def _draw_realistic_cloud(self, draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
        """Draw realistic cloud with multiple ellipses"""
        cloud_color = (255, 255, 255)
        highlight_color = (255, 255, 200)

        # Main cloud body
        circles = [
            (x, y, 40), (x + 35, y - 10, 35), (x + 70, y, 40),
            (x + 35, y + 10, 30), (x + 20, y + 5, 25)
        ]

        for cx, cy, r in circles:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=cloud_color)

    def _draw_tree(self, draw: ImageDraw.ImageDraw, x: int, y: int, height: int) -> None:
        """Draw realistic tree with trunk and foliage"""
        trunk_width = height // 10
        trunk_height = height // 2

        # Trunk
        trunk_color = (101, 67, 33)
        draw.rectangle([x - trunk_width // 2, y - trunk_height,
                       x + trunk_width // 2, y],
                      fill=trunk_color)

        # Foliage (multiple circles)
        foliage_color = (34, 139, 34)
        foliage_colors = [(34, 139, 34), (50, 150, 50), (60, 160, 60)]

        for i, (fx, fy, fr, fc) in enumerate([
            (x, y - trunk_height - 50, 50, foliage_colors[0]),
            (x - 30, y - trunk_height - 30, 40, foliage_colors[1]),
            (x + 30, y - trunk_height - 30, 40, foliage_colors[1]),
            (x, y - trunk_height - 90, 45, foliage_colors[2])
        ]):
            draw.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], fill=fc)

    def _add_lighting_effect(self, img: Image.Image, scene_type: str) -> Image.Image:
        """Add realistic lighting effects"""
        draw = ImageDraw.Draw(img)

        # Add vignette effect
        center_x, center_y = self.width // 2, self.height // 2
        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)

        for i in range(10):
            ratio = i / 10
            radius = int(max_dist * (1 - ratio * 0.5))
            alpha = int(50 * ratio)
            color = (0, 0, 0, alpha)

            draw.ellipse([
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius
            ], outline=(0, 0, 0, alpha))

        return img

    def _darken_color(self, color: Tuple[int, int, int],
                     factor: float = 0.8) -> Tuple[int, int, int]:
        """Darken a color"""
        return tuple(int(c * factor) for c in color)

    def _lighten_color(self, color: Tuple[int, int, int],
                      factor: float = 1.2) -> Tuple[int, int, int]:
        """Lighten a color"""
        return tuple(min(255, int(c * factor)) for c in color)

    def create_gradient_background(self,
                                   color1: Tuple[int, int, int],
                                   color2: Tuple[int, int, int],
                                   direction: str = "vertical") -> Image.Image:
        """Create gradient background"""
        img = Image.new('RGB', (self.width, self.height), color1)
        draw = ImageDraw.Draw(img)

        if direction == "vertical":
            for y in range(self.height):
                ratio = y / self.height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        else:
            for x in range(self.width):
                ratio = x / self.width
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(x, 0), (x, self.height)], fill=(r, g, b))

        return img

    def apply_time_of_day(self, img: Image.Image, time: str) -> Image.Image:
        """Apply time of day effect"""
        overlay = Image.new('RGB', img.size, (0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        if "night" in time.lower() or "夜" in time:
            overlay = Image.new('RGB', img.size, (0, 0, 50))
            return Image.blend(img, overlay, 0.4)
        elif "morning" in time.lower() or "晨" in time or "早" in time:
            overlay = Image.new('RGB', img.size, (255, 200, 100))
            return Image.blend(img, overlay, 0.2)
        elif "dusk" in time.lower() or "黄昏" in time or "傍晚" in time:
            overlay = Image.new('RGB', img.size, (255, 100, 50))
            return Image.blend(img, overlay, 0.3)

        return img
