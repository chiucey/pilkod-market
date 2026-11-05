"""
Character Management Module
Manages comic character images with realistic features
"""

from typing import Dict, Tuple, Optional, List
from PIL import Image, ImageDraw, ImageFilter
import math
import random

from .parser import Character


class CharacterManager:
    """Character Manager with realistic features"""

    # Emotion mapping
    EMOTIONS = {
        "normal": "neutral",
        "happy": "smile",
        "sad": "frown",
        "angry": "angry",
        "surprised": "surprised"
    }

    def __init__(self, base_size: int = 300):
        """
        Initialize character manager

        Args:
            base_size: Character base size
        """
        self.base_size = base_size
        self.character_images: Dict[str, Dict[str, Image.Image]] = {}

    def register_character(self, character: Character) -> None:
        """Register character and generate images"""
        self.character_images[character.name] = {}

        # Generate images for each emotion
        for emotion in ["normal", "happy", "sad", "angry", "surprised"]:
            img = self._generate_realistic_character(character, emotion)
            self.character_images[character.name][emotion] = img

    def get_character_image(self, name: str, emotion: str = "normal") -> Optional[Image.Image]:
        """Get character image by name and emotion"""
        if name not in self.character_images:
            return None

        emotion_key = self.EMOTIONS.get(emotion, "normal")
        return self.character_images[name].get(emotion_key)

    def _generate_realistic_character(self, character: Character, emotion: str) -> Image.Image:
        """
        Generate realistic character image

        Args:
            character: Character info
            emotion: Emotion type

        Returns:
            PIL Image object
        """
        size = self.base_size
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Get character colors
        skin_color = self._get_skin_color(character)
        hair_color = self._get_hair_color(character)
        cloth_color = self._get_cloth_color(character)

        # Draw body (upper body)
        self._draw_body(draw, size, cloth_color, skin_color, character)

        # Draw head
        self._draw_realistic_head(draw, size, skin_color, hair_color, character)

        # Draw face features
        self._draw_face_features(draw, size, skin_color, emotion, character)

        # Draw accessories
        self._draw_accessories(draw, size, character)

        # Apply subtle shadow
        img = self._apply_shadow(img)

        return img

    def _draw_body(self, draw: ImageDraw.ImageDraw, size: int,
                   cloth_color: Tuple[int, int, int],
                   skin_color: Tuple[int, int, int],
                   character: Character) -> None:
        """Draw upper body with realistic proportions"""
        center_x = size // 2
        body_top = size // 2 + 30
        body_bottom = size - 20

        # Draw shoulders and torso
        shoulder_width = size // 3
        torso_points = [
            (center_x - shoulder_width, body_top),
            (center_x + shoulder_width, body_top),
            (center_x + shoulder_width - 10, body_bottom),
            (center_x - shoulder_width + 10, body_bottom)
        ]
        draw.polygon(torso_points, fill=cloth_color)

        # Draw neck
        neck_width = size // 8
        neck_height = size // 10
        neck_top = size // 2 - 10
        draw.rectangle(
            [center_x - neck_width, neck_top, center_x + neck_width, neck_top + neck_height],
            fill=skin_color
        )

        # Draw collar details
        collar_y = body_top + 5
        draw.polygon([
            (center_x - neck_width - 10, collar_y),
            (center_x, collar_y + 20),
            (center_x + neck_width + 10, collar_y),
            (center_x, collar_y)
        ], fill=cloth_color)

        # Draw sleeves
        sleeve_length = size // 4
        # Left sleeve
        draw.polygon([
            (center_x - shoulder_width, body_top),
            (center_x - shoulder_width - 20, body_top + sleeve_length),
            (center_x - shoulder_width - 10, body_top + sleeve_length + 20),
            (center_x - shoulder_width + 15, body_top + 10)
        ], fill=cloth_color)

        # Right sleeve
        draw.polygon([
            (center_x + shoulder_width, body_top),
            (center_x + shoulder_width + 20, body_top + sleeve_length),
            (center_x + shoulder_width + 10, body_top + sleeve_length + 20),
            (center_x + shoulder_width - 15, body_top + 10)
        ], fill=cloth_color)

        # Draw hands
        hand_size = size // 12
        # Left hand
        draw.ellipse([
            center_x - shoulder_width - 25, body_top + sleeve_length + 10,
            center_x - shoulder_width - 25 + hand_size, body_top + sleeve_length + 10 + hand_size
        ], fill=skin_color)
        # Right hand
        draw.ellipse([
            center_x + shoulder_width + 25 - hand_size, body_top + sleeve_length + 10,
            center_x + shoulder_width + 25, body_top + sleeve_length + 10 + hand_size
        ], fill=skin_color)

    def _draw_realistic_head(self, draw: ImageDraw.ImageDraw, size: int,
                            skin_color: Tuple[int, int, int],
                            hair_color: Tuple[int, int, int],
                            character: Character) -> None:
        """Draw realistic head shape"""
        center_x = size // 2
        head_center_y = size // 3 + 20
        head_width = size // 4
        head_height = size // 3

        # Draw hair back layer
        hair_back_y = head_center_y - head_height // 2 - 10
        draw.ellipse([
            center_x - head_width - 5, hair_back_y,
            center_x + head_width + 5, hair_back_y + head_height + 20
        ], fill=hair_color)

        # Draw face shape (oval)
        draw.ellipse([
            center_x - head_width, head_center_y - head_height // 2,
            center_x + head_width, head_center_y + head_height
        ], fill=skin_color)

        # Draw ears
        ear_size = head_width // 4
        # Left ear
        draw.ellipse([
            center_x - head_width - ear_size // 2, head_center_y - ear_size,
            center_x - head_width + ear_size // 2, head_center_y + ear_size
        ], fill=skin_color)
        # Right ear
        draw.ellipse([
            center_x + head_width - ear_size // 2, head_center_y - ear_size,
            center_x + head_width + ear_size // 2, head_center_y + ear_size
        ], fill=skin_color)

        # Draw hair front layer based on gender
        if "男" in character.gender:
            # Male short hair
            self._draw_male_hair(draw, center_x, head_center_y, head_width, head_height, hair_color)
        else:
            # Female longer hair
            self._draw_female_hair(draw, center_x, head_center_y, head_width, head_height, hair_color)

        # Add highlights to hair
        highlight_color = tuple(min(255, c + 30) for c in hair_color)
        draw.arc([
            center_x - head_width // 3, head_center_y - head_height // 2 + 5,
            center_x + head_width // 3, head_center_y - head_height // 2 + 20
        ], start=0, end=180, fill=highlight_color, width=3)

    def _draw_male_hair(self, draw: ImageDraw.ImageDraw, cx: int, cy: int,
                       hw: int, hh: int, color: Tuple[int, int, int]) -> None:
        """Draw male short hair style"""
        # Top hair
        draw.polygon([
            (cx - hw + 5, cy - hh // 2 + 10),
            (cx + hw - 5, cy - hh // 2 + 10),
            (cx + hw - 10, cy - hh // 2 - 10),
            (cx - hw + 10, cy - hh // 2 - 10)
        ], fill=color)

        # Side hair
        draw.rectangle([cx - hw, cy - hh // 2 + 5, cx - hw + 15, cy + hh // 3], fill=color)
        draw.rectangle([cx + hw - 15, cy - hh // 2 + 5, cx + hw, cy + hh // 3], fill=color)

    def _draw_female_hair(self, draw: ImageDraw.ImageDraw, cx: int, cy: int,
                         hw: int, hh: int, color: Tuple[int, int, int]) -> None:
        """Draw female long hair style"""
        # Top hair
        draw.polygon([
            (cx - hw - 5, cy - hh // 2),
            (cx + hw + 5, cy - hh // 2),
            (cx + hw, cy - hh // 2 - 15),
            (cx - hw, cy - hh // 2 - 15)
        ], fill=color)

        # Side hair flowing down
        hair_length = hh + 30
        # Left side
        draw.polygon([
            (cx - hw - 5, cy - hh // 2),
            (cx - hw - 15, cy - hh // 2 + hair_length // 2),
            (cx - hw + 10, cy - hh // 2 + hair_length // 2 + 10),
            (cx - hw + 5, cy - hh // 2)
        ], fill=color)

        # Right side
        draw.polygon([
            (cx + hw + 5, cy - hh // 2),
            (cx + hw + 15, cy - hh // 2 + hair_length // 2),
            (cx + hw - 10, cy - hh // 2 + hair_length // 2 + 10),
            (cx + hw - 5, cy - hh // 2)
        ], fill=color)

        # Back hair hint
        draw.ellipse([
            cx - hw + 10, cy + hh // 4,
            cx + hw - 10, cy + hh // 4 + 20
        ], fill=color)

    def _draw_face_features(self, draw: ImageDraw.ImageDraw, size: int,
                           skin_color: Tuple[int, int, int],
                           emotion: str,
                           character: Character) -> None:
        """Draw eyes, nose, mouth with emotion"""
        center_x = size // 2
        head_center_y = size // 3 + 20
        head_width = size // 4
        head_height = size // 3

        eye_y = head_center_y - head_height // 6
        eye_spacing = head_width // 3

        # Draw eyebrows
        brow_y = eye_y - 15
        brow_width = head_width // 5
        brow_thickness = 4

        # Eyebrow angles based on emotion
        if emotion == "angry":
            brow_angle = -10
        elif emotion == "sad":
            brow_angle = 10
        else:
            brow_angle = 0

        # Left eyebrow
        draw.line([
            (center_x - eye_spacing - brow_width, brow_y + brow_angle),
            (center_x - eye_spacing + brow_width, brow_y - brow_angle)
        ], fill=(60, 40, 20), width=brow_thickness)

        # Right eyebrow
        draw.line([
            (center_x + eye_spacing - brow_width, brow_y - brow_angle),
            (center_x + eye_spacing + brow_width, brow_y + brow_angle)
        ], fill=(60, 40, 20), width=brow_thickness)

        # Draw eyes
        eye_width = head_width // 5
        eye_height = head_width // 7

        if emotion == "happy":
            # Happy eyes (curved, smiling)
            draw.arc([
                center_x - eye_spacing - eye_width, eye_y - eye_height,
                center_x - eye_spacing + eye_width, eye_y + eye_height * 2
            ], start=0, end=180, fill=(50, 50, 50), width=3)
            draw.arc([
                center_x + eye_spacing - eye_width, eye_y - eye_height,
                center_x + eye_spacing + eye_width, eye_y + eye_height * 2
            ], start=0, end=180, fill=(50, 50, 50), width=3)
            # Add highlights
            draw.ellipse([
                center_x - eye_spacing - 5, eye_y,
                center_x - eye_spacing + 5, eye_y + 5
            ], fill=(255, 255, 255))
            draw.ellipse([
                center_x + eye_spacing - 5, eye_y,
                center_x + eye_spacing + 5, eye_y + 5
            ], fill=(255, 255, 255))

        elif emotion == "surprised":
            # Surprised eyes (wide open)
            draw.ellipse([
                center_x - eye_spacing - eye_width, eye_y - eye_height,
                center_x - eye_spacing + eye_width, eye_y + eye_height
            ], fill=(255, 255, 255), outline=(50, 50, 50), width=2)
            draw.ellipse([
                center_x + eye_spacing - eye_width, eye_y - eye_height,
                center_x + eye_spacing + eye_width, eye_y + eye_height
            ], fill=(255, 255, 255), outline=(50, 50, 50), width=2)
            # Large pupils
            pupil_size = eye_width // 2
            draw.ellipse([
                center_x - eye_spacing - pupil_size, eye_y - pupil_size,
                center_x - eye_spacing + pupil_size, eye_y + pupil_size
            ], fill=(30, 30, 30))
            draw.ellipse([
                center_x + eye_spacing - pupil_size, eye_y - pupil_size,
                center_x + eye_spacing + pupil_size, eye_y + pupil_size
            ], fill=(30, 30, 30))

        else:
            # Normal eyes with eyelids
            # Left eye
            draw.ellipse([
                center_x - eye_spacing - eye_width, eye_y - eye_height,
                center_x - eye_spacing + eye_width, eye_y + eye_height
            ], fill=(255, 255, 255))
            draw.ellipse([
                center_x - eye_spacing - eye_width // 2, eye_y - eye_height // 2,
                center_x - eye_spacing + eye_width // 2, eye_y + eye_height // 2
            ], fill=(80, 60, 40))
            draw.ellipse([
                center_x - eye_spacing - eye_width // 4, eye_y - eye_height // 3,
                center_x - eye_spacing + eye_width // 4, eye_y + eye_height // 3
            ], fill=(30, 30, 30))

            # Right eye
            draw.ellipse([
                center_x + eye_spacing - eye_width, eye_y - eye_height,
                center_x + eye_spacing + eye_width, eye_y + eye_height
            ], fill=(255, 255, 255))
            draw.ellipse([
                center_x + eye_spacing - eye_width // 2, eye_y - eye_height // 2,
                center_x + eye_spacing + eye_width // 2, eye_y + eye_height // 2
            ], fill=(80, 60, 40))
            draw.ellipse([
                center_x + eye_spacing - eye_width // 4, eye_y - eye_height // 3,
                center_x + eye_spacing + eye_width // 4, eye_y + eye_height // 3
            ], fill=(30, 30, 30))

            # Eye highlights
            draw.ellipse([
                center_x - eye_spacing - 3, eye_y - 3,
                center_x - eye_spacing + 3, eye_y + 3
            ], fill=(255, 255, 255))
            draw.ellipse([
                center_x + eye_spacing - 3, eye_y - 3,
                center_x + eye_spacing + 3, eye_y + 3
            ], fill=(255, 255, 255))

        # Draw nose
        nose_y = head_center_y + head_height // 8
        nose_width = head_width // 8
        draw.line([
            (center_x, nose_y - 5),
            (center_x - nose_width // 2, nose_y + 10)
        ], fill=self._darken_color(skin_color, 0.8), width=2)
        draw.line([
            (center_x, nose_y - 5),
            (center_x + nose_width // 2, nose_y + 10)
        ], fill=self._darken_color(skin_color, 0.8), width=2)

        # Draw mouth based on emotion
        mouth_y = head_center_y + head_height // 3
        mouth_width = head_width // 3

        if emotion == "happy":
            # Big smile
            draw.arc([
                center_x - mouth_width, mouth_y - 5,
                center_x + mouth_width, mouth_y + 20
            ], start=0, end=180, fill=(180, 80, 80), width=3)
        elif emotion == "sad":
            # Sad frown
            draw.arc([
                center_x - mouth_width, mouth_y + 5,
                center_x + mouth_width, mouth_y + 25
            ], start=180, end=360, fill=(150, 50, 50), width=3)
        elif emotion == "angry":
            # Angry straight line
            draw.line([
                (center_x - mouth_width // 2, mouth_y + 5),
                (center_x + mouth_width // 2, mouth_y + 10)
            ], fill=(150, 50, 50), width=3)
        elif emotion == "surprised":
            # O-shaped mouth
            draw.ellipse([
                center_x - mouth_width // 3, mouth_y - 3,
                center_x + mouth_width // 3, mouth_y + 12
            ], fill=(150, 50, 50))
        else:
            # Neutral slight smile
            draw.arc([
                center_x - mouth_width // 2, mouth_y,
                center_x + mouth_width // 2, mouth_y + 12
            ], start=0, end=180, fill=(150, 50, 50), width=2)

    def _draw_accessories(self, draw: ImageDraw.ImageDraw, size: int,
                         character: Character) -> None:
        """Draw glasses and other accessories"""
        appearance = character.appearance + character.description

        if "眼镜" in appearance or "glasses" in appearance.lower():
            center_x = size // 2
            head_center_y = size // 3 + 20
            head_width = size // 4
            head_height = size // 3

            eye_y = head_center_y - head_height // 6
            eye_spacing = head_width // 3
            eye_width = head_width // 4

            # Draw glasses frames
            glass_color = (80, 80, 80)
            frame_width = 3

            # Left lens
            draw.ellipse([
                center_x - eye_spacing - eye_width - 5, eye_y - eye_width // 2 - 5,
                center_x - eye_spacing + eye_width + 5, eye_y + eye_width // 2 + 5
            ], outline=glass_color, width=frame_width)

            # Right lens
            draw.ellipse([
                center_x + eye_spacing - eye_width - 5, eye_y - eye_width // 2 - 5,
                center_x + eye_spacing + eye_width + 5, eye_y + eye_width // 2 + 5
            ], outline=glass_color, width=frame_width)

            # Bridge
            draw.line([
                (center_x - eye_spacing + eye_width + 5, eye_y),
                (center_x + eye_spacing - eye_width - 5, eye_y)
            ], fill=glass_color, width=frame_width)

            # Temple arms
            draw.line([
                (center_x - eye_spacing - eye_width - 5, eye_y),
                (center_x - eye_spacing - eye_width - 25, eye_y + 10)
            ], fill=glass_color, width=frame_width)
            draw.line([
                (center_x + eye_spacing + eye_width + 5, eye_y),
                (center_x + eye_spacing + eye_width + 25, eye_y + 10)
            ], fill=glass_color, width=frame_width)

    def _apply_shadow(self, img: Image.Image) -> Image.Image:
        """Apply subtle shadow effect to character"""
        # Create shadow
        shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)

        # Draw shadow on right side
        w, h = img.size
        for x in range(w // 2, w):
            for y in range(h // 4, h * 3 // 4):
                shadow_draw.point((x, y), fill=(0, 0, 0, 15))

        # Blend shadow
        return Image.alpha_composite(img, shadow)

    def _get_skin_color(self, character: Character) -> Tuple[int, int, int]:
        """Get skin color based on character description"""
        appearance = character.appearance.lower()
        description = character.description.lower()

        if any(word in appearance + description for word in ["fair", "pale", "白皙", "白"]):
            return (255, 230, 220)
        elif any(word in appearance + description for word in ["dark", "deep", "黑", "深"]):
            return (180, 140, 110)
        elif any(word in appearance + description for word in ["yellow", "asian", "黄"]):
            return (255, 220, 180)
        elif any(word in appearance + description for word in ["tan", "sun", "小麦"]):
            return (240, 190, 150)
        else:
            return (255, 210, 180)

    def _get_hair_color(self, character: Character) -> Tuple[int, int, int]:
        """Get hair color based on character description"""
        appearance = character.appearance.lower()
        description = character.description.lower()
        text = appearance + description

        if any(word in text for word in ["black", "黑发", "黑色", "黑"]):
            return (30, 25, 20)
        elif any(word in text for word in ["blonde", "golden", "yellow", "金发", "金色", "黄"]):
            return (220, 195, 100)
        elif any(word in text for word in ["brown", "brunette", "棕", "褐色", "棕褐"]):
            return (100, 70, 50)
        elif any(word in text for word in ["red", "ginger", "红", "赤"]):
            return (150, 60, 40)
        elif any(word in text for word in ["white", "gray", "silver", "白发", "灰", "银"]):
            return (180, 180, 180)
        elif any(word in text for word in ["blue", "蓝"]):
            return (50, 100, 180)
        elif any(word in text for word in ["purple", "紫"]):
            return (100, 50, 150)
        else:
            # Default dark brown
            return (60, 40, 25)

    def _get_cloth_color(self, character: Character) -> Tuple[int, int, int]:
        """Get clothing color based on character description"""
        appearance = character.appearance.lower()
        description = character.description.lower()
        text = appearance + description

        if "blue" in text or "蓝" in text:
            return (70, 130, 180)
        elif "red" in text or "红" in text:
            return (180, 70, 70)
        elif "green" in text or "绿" in text:
            return (70, 140, 70)
        elif "yellow" in text or "黄" in text:
            return (220, 200, 100)
        elif "purple" in text or "紫" in text:
            return (140, 90, 160)
        elif "black" in text or "黑" in text:
            return (50, 50, 50)
        elif "white" in text or "白" in text:
            return (240, 240, 240)
        else:
            # Default school uniform colors
            if "男" in character.gender:
                return (70, 90, 140)  # Blue school uniform
            else:
                return (180, 100, 120)  # Pink or red school uniform

    def _darken_color(self, color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Darken a color by a factor"""
        return tuple(int(c * factor) for c in color)

    def create_character_icon(self, name: str, color: Tuple[int, int, int],
                               size: int = 100) -> Image.Image:
        """Create simple character icon with initials"""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw circular background
        margin = size // 10
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=color
        )

        # Draw initials
        from PIL import ImageFont
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size // 2)
        except:
            font = ImageFont.load_default()

        initial = name[0] if name else "?"
        bbox = draw.textbbox((0, 0), initial, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2
        draw.text((text_x, text_y), initial, fill=(255, 255, 255), font=font)

        return img


def generate_character_thumbnail(character: Character, size: int = 200) -> Image.Image:
    """Generate character thumbnail"""
    manager = CharacterManager(base_size=size)
    manager.register_character(character)
    return manager.get_character_image(character.name, "normal")
