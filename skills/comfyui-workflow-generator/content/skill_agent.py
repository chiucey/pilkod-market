#!/usr/bin/env python3
"""
ComfyUI Workflow Generator - Main Agent Script
This script is the entry point for the ComfyUI workflow generator skill.
"""

import json
import random
from typing import Optional, Dict, Any, List, Tuple


class ComfyUIWorkflowGenerator:
    """Main workflow generator class"""

    # Comprehensive node library
    NODE_LIBRARY: Dict[str, Dict] = {
        # Core Nodes
        "CheckpointLoaderSimple": {
            "class_type": "CheckpointLoaderSimple",
            "description": "SD Model Loader",
            "inputs": {"ckpt_name": "str"},
            "outputs": ["MODEL", "CLIP", "VAE"],
            "default_params": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"},
            "required_plugin": "core"
        },
        "CLIPTextEncode": {
            "class_type": "CLIPTextEncode",
            "description": "Prompt CLIP Encoder",
            "inputs": {"text": "str", "clip": "CLIP"},
            "outputs": ["CONDITIONING"],
            "default_params": {"text": ""},
            "required_plugin": "core"
        },
        "EmptyLatentImage": {
            "class_type": "EmptyLatentImage",
            "description": "Empty Latent Space",
            "inputs": {"width": "int", "height": "int", "batch_size": "int"},
            "outputs": ["LATENT"],
            "default_params": {"width": 512, "height": 768, "batch_size": 1},
            "required_plugin": "core"
        },
        "KSampler": {
            "class_type": "KSampler",
            "description": "Core Sampler",
            "inputs": {
                "model": "MODEL", "positive": "CONDITIONING", "negative": "CONDITIONING",
                "latent_image": "LATENT", "seed": "int", "steps": "int", "cfg": "float",
                "sampler_name": "str", "scheduler": "str", "denoise": "float"
            },
            "outputs": ["LATENT"],
            "default_params": {
                "seed": 0, "steps": 20, "cfg": 8.0, "sampler_name": "euler",
                "scheduler": "normal", "denoise": 1.0
            },
            "required_plugin": "core"
        },
        "VAEDecode": {
            "class_type": "VAEDecode",
            "description": "VAE Latent Decoder",
            "inputs": {"samples": "LATENT", "vae": "VAE"},
            "outputs": ["IMAGE"],
            "default_params": {},
            "required_plugin": "core"
        },
        "VAEEncode": {
            "class_type": "VAEEncode",
            "description": "VAE Image Encoder",
            "inputs": {"pixels": "IMAGE", "vae": "VAE"},
            "outputs": ["LATENT"],
            "default_params": {},
            "required_plugin": "core"
        },
        "LoadImage": {
            "class_type": "LoadImage",
            "description": "Local Image Loader",
            "inputs": {"image": "str"},
            "outputs": ["IMAGE", "MASK"],
            "default_params": {"image": "input.png"},
            "required_plugin": "core"
        },
        "SaveImage": {
            "class_type": "SaveImage",
            "description": "Image Saver",
            "inputs": {"images": "IMAGE", "filename_prefix": "str"},
            "outputs": [],
            "default_params": {"filename_prefix": "ComfyUI_Output"},
            "required_plugin": "core"
        },

        # Video Nodes
        "VHS_LoadVideo": {
            "class_type": "VHS_LoadVideo",
            "description": "Video Loader & Frame Split",
            "inputs": {
                "video": "str", "frame_load_cap": "int", "skip_first_frames": "int",
                "select_every_nth": "int", "force_size": "str", "extract_audio": "bool"
            },
            "outputs": ["IMAGE", "AUDIO", "FRAME_RATE", "FRAME_COUNT", "DURATION"],
            "default_params": {
                "video": "input.mp4", "frame_load_cap": 48, "skip_first_frames": 0,
                "select_every_nth": 1, "force_size": "Disabled", "extract_audio": True
            },
            "required_plugin": "ComfyUI-VideoHelperSuite"
        },
        "VHS_VideoCombine": {
            "class_type": "VHS_VideoCombine",
            "description": "Frame Sequence to Video",
            "inputs": {
                "images": "IMAGE", "frame_rate": "int", "loop_count": "int",
                "filename_prefix": "str", "format": "str", "crf": "int",
                "save_output": "bool", "audio": "AUDIO"
            },
            "outputs": ["VIDEO"],
            "default_params": {
                "loop_count": 0, "filename_prefix": "ComfyUI_AI_Video",
                "format": "video/h264-mp4", "crf": 21, "save_output": True
            },
            "required_plugin": "ComfyUI-VideoHelperSuite"
        },
        "VHS_LoadAudio": {
            "class_type": "VHS_LoadAudio",
            "description": "Audio File Loader",
            "inputs": {"audio_file": "str"},
            "outputs": ["AUDIO"],
            "default_params": {"audio_file": "bgm.mp3"},
            "required_plugin": "ComfyUI-VideoHelperSuite"
        },

        # AnimateDiff Nodes
        "AnimateDiffLoaderV2": {
            "class_type": "AnimateDiffLoaderV2",
            "description": "AnimateDiff Motion Model Loader",
            "inputs": {"model_name": "str", "model": "MODEL", "context_length": "int", "context_overlap": "int"},
            "outputs": ["MODEL"],
            "default_params": {
                "model_name": "mm_sd_v15_v2.ckpt", "context_length": 16, "context_overlap": 4
            },
            "required_plugin": "ComfyUI-AnimateDiff-Evolved"
        },
        "AnimateDiffLoraLoader": {
            "class_type": "AnimateDiffLoraLoader",
            "description": "AnimateDiff Motion LoRA Loader",
            "inputs": {"lora_name": "str", "model": "MODEL", "strength": "float"},
            "outputs": ["MODEL"],
            "default_params": {"lora_name": "v2_lora_ZoomIn.ckpt", "strength": 1.0},
            "required_plugin": "ComfyUI-AnimateDiff-Evolved"
        },

        # ControlNet Nodes
        "ControlNetLoader": {
            "class_type": "ControlNetLoader",
            "description": "ControlNet Model Loader",
            "inputs": {"control_net_name": "str"},
            "outputs": ["CONTROL_NET"],
            "default_params": {"control_net_name": "control_v11p_sd15_canny.pth"},
            "required_plugin": "ComfyUI-Advanced-ControlNet"
        },
        "ControlNetApply": {
            "class_type": "ControlNetApply",
            "description": "ControlNet Apply",
            "inputs": {
                "positive": "CONDITIONING", "negative": "CONDITIONING",
                "control_net": "CONTROL_NET", "image": "IMAGE", "strength": "float",
                "start_percent": "float", "end_percent": "float"
            },
            "outputs": ["CONDITIONING", "CONDITIONING"],
            "default_params": {"strength": 0.9, "start_percent": 0.0, "end_percent": 1.0},
            "required_plugin": "ComfyUI-Advanced-ControlNet"
        },
        "Canny": {
            "class_type": "Canny",
            "description": "Canny Edge Detection",
            "inputs": {"image": "IMAGE", "low_threshold": "int", "high_threshold": "int"},
            "outputs": ["IMAGE"],
            "default_params": {"low_threshold": 100, "high_threshold": 200},
            "required_plugin": "ComfyUI-ControlNet"
        },
        "OpenPosePreprocessor": {
            "class_type": "OpenPosePreprocessor",
            "description": "OpenPose Human Pose",
            "inputs": {"image": "IMAGE", "detect_hand": "bool", "detect_body": "bool", "detect_face": "bool"},
            "outputs": ["IMAGE", "POSE_KEYPOINTS"],
            "default_params": {"detect_hand": True, "detect_body": True, "detect_face": True},
            "required_plugin": "ComfyUI-ControlNet"
        },
        "DepthMapPreprocessor": {
            "class_type": "DepthMapPreprocessor",
            "description": "Depth Map Preprocessor",
            "inputs": {"image": "IMAGE"},
            "outputs": ["IMAGE"],
            "default_params": {},
            "required_plugin": "ComfyUI-ControlNet"
        },
        "LineartPreprocessor": {
            "class_type": "LineartPreprocessor",
            "description": "Line Art Preprocessor",
            "inputs": {"image": "IMAGE", "coarse": "bool"},
            "outputs": ["IMAGE"],
            "default_params": {"coarse": False},
            "required_plugin": "ComfyUI-ControlNet"
        },

        # Enhancement Nodes
        "RIFE_VFI": {
            "class_type": "RIFE_VFI",
            "description": "RIFE Frame Interpolation",
            "inputs": {"images": "IMAGE", "multiplier": "int", "frame_rate": "int"},
            "outputs": ["IMAGE", "FRAME_RATE"],
            "default_params": {"multiplier": 2},
            "required_plugin": "ComfyUI-RIFE"
        },
        "UpscaleModelLoader": {
            "class_type": "UpscaleModelLoader",
            "description": "Upscale Model Loader",
            "inputs": {"model_name": "str"},
            "outputs": ["UPSCALE_MODEL"],
            "default_params": {"model_name": "RealESRGAN_x4plus.pth"},
            "required_plugin": "core"
        },
        "ImageUpscaleWithModel": {
            "class_type": "ImageUpscaleWithModel",
            "description": "AI Upscale",
            "inputs": {"upscale_model": "UPSCALE_MODEL", "image": "IMAGE"},
            "outputs": ["IMAGE"],
            "default_params": {},
            "required_plugin": "core"
        },

        # IP-Adapter Nodes
        "CLIPVisionLoader": {
            "class_type": "CLIPVisionLoader",
            "description": "CLIP Vision Model Loader",
            "inputs": {"clip_name": "str"},
            "outputs": ["CLIP_VISION"],
            "default_params": {"clip_name": "clip-vit-large-patch14.safetensors"},
            "required_plugin": "ComfyUI_IPAdapter_plus"
        },
        "IPAdapterLoader": {
            "class_type": "IPAdapterLoader",
            "description": "IP-Adapter Model Loader",
            "inputs": {"ipadapter_file": "str"},
            "outputs": ["IPADAPTER"],
            "default_params": {"ipadapter_file": "ip-adapter-plus_sd15.safetensors"},
            "required_plugin": "ComfyUI_IPAdapter_plus"
        },
        "IPAdapterApply": {
            "class_type": "IPAdapterApply",
            "description": "IP-Adapter Apply",
            "inputs": {
                "ipadapter": "IPADAPTER", "clip_vision": "CLIP_VISION", "model": "MODEL",
                "image": "IMAGE", "weight": "float", "weight_type": "str"
            },
            "outputs": ["MODEL"],
            "default_params": {"weight": 0.8, "weight_type": "original"},
            "required_plugin": "ComfyUI_IPAdapter_plus"
        },

        # LoRA Nodes
        "LoraLoaderModelOnly": {
            "class_type": "LoraLoaderModelOnly",
            "description": "LoRA Model Loader",
            "inputs": {"model": "MODEL", "lora_name": "str", "strength_model": "float", "strength_clip": "float"},
            "outputs": ["MODEL"],
            "default_params": {"lora_name": "example_lora.safetensors", "strength_model": 1.0, "strength_clip": 1.0},
            "required_plugin": "core"
        },
    }

    def __init__(self):
        self.node_id_counter = 1
        self.workflow: Dict[str, Any] = {}
        self.current_x = 0
        self.current_y = 0
        self.workflow_format = "ui"
        self.required_plugins: set = set()

    def reset_state(self):
        """Reset generator state"""
        self.node_id_counter = 1
        self.workflow = {}
        self.current_x = 0
        self.current_y = 0
        self.required_plugins = set()

    def add_node(self, node_key: str, custom_params: Dict[str, Any] = None) -> str:
        """Add a node to the workflow"""
        if node_key not in self.NODE_LIBRARY:
            raise ValueError(f"Node '{node_key}' not found in node library")

        node_meta = self.NODE_LIBRARY[node_key]
        node_id = str(self.node_id_counter)
        self.node_id_counter += 1

        inputs = node_meta["default_params"].copy()
        if custom_params:
            inputs.update(custom_params)

        self.workflow[node_id] = {
            "inputs": inputs,
            "class_type": node_meta["class_type"],
            "_meta": {"title": node_meta["description"]}
        }

        if self.workflow_format == "ui":
            self.workflow[node_id]["pos"] = [self.current_x, self.current_y]
            self.current_y += 120
            if self.current_y > 800:
                self.current_y = 0
                self.current_x += 320

        if node_meta["required_plugin"] != "core":
            self.required_plugins.add(node_meta["required_plugin"])

        return node_id

    def connect_node(self, target_node_id: str, input_key: str,
                     source_node_id: str, output_index: int = 0):
        """Connect two nodes"""
        self.workflow[target_node_id]["inputs"][input_key] = [source_node_id, output_index]

    def validate_workflow(self) -> Tuple[bool, str]:
        """Validate workflow structure"""
        errors = []

        if not self.workflow:
            return False, "Workflow is empty"

        for node_id, node_data in self.workflow.items():
            if "class_type" not in node_data:
                errors.append(f"Node {node_id} missing 'class_type'")

            for input_key, input_value in node_data.get("inputs", {}).items():
                if isinstance(input_value, list) and len(input_value) == 2:
                    if input_value[0] not in self.workflow:
                        errors.append(f"Node {node_id} input '{input_key}' references non-existent node")

        has_sampler = any(n["class_type"] == "KSampler" for n in self.workflow.values())
        has_vae_decode = any(n["class_type"] == "VAEDecode" for n in self.workflow.values())
        if has_sampler and not has_vae_decode:
            errors.append("KSampler found but no VAEDecode - image cannot be generated")

        if errors:
            return False, "; ".join(errors)

        return True, "Workflow validation passed"

    def generate_workflow_json(self) -> str:
        """Generate final workflow JSON"""
        return json.dumps(self.workflow, indent=2, ensure_ascii=False)

    # Template workflows
    def template_basic_txt2img(self, prompt: str, negative: str = "lowres, bad anatomy, blurry",
                                width: int = 512, height: int = 768) -> str:
        """Basic Text-to-Image workflow"""
        seed = random.randint(0, 999999999)

        ckpt = self.add_node("CheckpointLoaderSimple")
        pos_enc = self.add_node("CLIPTextEncode", {"text": prompt})
        neg_enc = self.add_node("CLIPTextEncode", {"text": negative})
        latent = self.add_node("EmptyLatentImage", {"width": width, "height": height, "batch_size": 1})
        sampler = self.add_node("KSampler", {"seed": seed, "steps": 20, "sampler_name": "euler", "cfg": 8.0})
        vae_decode = self.add_node("VAEDecode")
        save = self.add_node("SaveImage")

        self.connect_node(pos_enc, "clip", ckpt, 1)
        self.connect_node(neg_enc, "clip", ckpt, 1)
        self.connect_node(sampler, "model", ckpt, 0)
        self.connect_node(sampler, "positive", pos_enc, 0)
        self.connect_node(sampler, "negative", neg_enc, 0)
        self.connect_node(sampler, "latent_image", latent, 0)
        self.connect_node(vae_decode, "samples", sampler, 0)
        self.connect_node(vae_decode, "vae", ckpt, 2)
        self.connect_node(save, "images", vae_decode, 0)

        return "text_to_image"

    def template_animatediff_txt2vid(self, prompt: str, negative: str = "flicker, jitter, distorted",
                                      frames: int = 16, frame_rate: int = 12) -> str:
        """AnimateDiff Text-to-Video workflow"""
        ckpt = self.add_node("CheckpointLoaderSimple")
        ad_loader = self.add_node("AnimateDiffLoaderV2", {"context_length": min(frames, 16)})
        pos_enc = self.add_node("CLIPTextEncode", {"text": prompt})
        neg_enc = self.add_node("CLIPTextEncode", {"text": negative})
        latent = self.add_node("EmptyLatentImage", {"width": 512, "height": 512, "batch_size": frames})
        sampler = self.add_node("KSampler", {"steps": 20, "sampler_name": "euler", "cfg": 8.0})
        vae_decode = self.add_node("VAEDecode")
        video_combine = self.add_node("VHS_VideoCombine", {"frame_rate": frame_rate})

        self.connect_node(ad_loader, "model", ckpt, 0)
        self.connect_node(pos_enc, "clip", ckpt, 1)
        self.connect_node(neg_enc, "clip", ckpt, 1)
        self.connect_node(sampler, "model", ad_loader, 0)
        self.connect_node(sampler, "positive", pos_enc, 0)
        self.connect_node(sampler, "negative", neg_enc, 0)
        self.connect_node(sampler, "latent_image", latent, 0)
        self.connect_node(vae_decode, "samples", sampler, 0)
        self.connect_node(vae_decode, "vae", ckpt, 2)
        self.connect_node(video_combine, "images", vae_decode, 0)

        return "animatediff_text_to_video"

    def template_video_style_transfer(self, style: str = "anime, Studio Ghibli style",
                                      denoise: float = 0.5) -> str:
        """Video Style Transfer with ControlNet"""
        video_load = self.add_node("VHS_LoadVideo", {"frame_load_cap": 48})
        ckpt = self.add_node("CheckpointLoaderSimple")
        canny = self.add_node("Canny")
        cn_loader = self.add_node("ControlNetLoader")
        cn_apply = self.add_node("ControlNetApply", {"strength": 0.8})
        pos_enc = self.add_node("CLIPTextEncode", {"text": f"masterpiece, {style}, sharp lines, high detail"})
        neg_enc = self.add_node("CLIPTextEncode", {"text": "flicker, jitter, distorted, blurry, photo realistic"})
        vae_encode = self.add_node("VAEEncode")
        sampler = self.add_node("KSampler", {"denoise": denoise})
        vae_decode = self.add_node("VAEDecode")
        video_combine = self.add_node("VHS_VideoCombine")

        self.connect_node(canny, "image", video_load, 0)
        self.connect_node(pos_enc, "clip", ckpt, 1)
        self.connect_node(neg_enc, "clip", ckpt, 1)
        self.connect_node(cn_apply, "positive", pos_enc, 0)
        self.connect_node(cn_apply, "negative", neg_enc, 0)
        self.connect_node(cn_apply, "control_net", cn_loader, 0)
        self.connect_node(cn_apply, "image", canny, 0)
        self.connect_node(vae_encode, "pixels", video_load, 0)
        self.connect_node(vae_encode, "vae", ckpt, 2)
        self.connect_node(sampler, "model", ckpt, 0)
        self.connect_node(sampler, "positive", cn_apply, 0)
        self.connect_node(sampler, "negative", cn_apply, 1)
        self.connect_node(sampler, "latent_image", vae_encode, 0)
        self.connect_node(vae_decode, "samples", sampler, 0)
        self.connect_node(vae_decode, "vae", ckpt, 2)
        self.connect_node(video_combine, "images", vae_decode, 0)
        self.connect_node(video_combine, "frame_rate", video_load, 2)
        self.connect_node(video_combine, "audio", video_load, 1)

        return "video_style_transfer"

    def template_controlnet_img2img(self, prompt: str, controlnet_type: str = "canny") -> str:
        """ControlNet Image-to-Image"""
        load_img = self.add_node("LoadImage", {"image": "control_image.png"})
        ckpt = self.add_node("CheckpointLoaderSimple")

        if controlnet_type == "canny":
            preprocessor = self.add_node("Canny")
        elif controlnet_type == "openpose":
            preprocessor = self.add_node("OpenPosePreprocessor")
        elif controlnet_type == "depth":
            preprocessor = self.add_node("DepthMapPreprocessor")
        else:
            preprocessor = self.add_node("Canny")

        self.connect_node(preprocessor, "image", load_img, 0)

        cn_loader = self.add_node("ControlNetLoader")
        cn_apply = self.add_node("ControlNetApply", {"strength": 0.9})
        pos_enc = self.add_node("CLIPTextEncode", {"text": prompt})
        neg_enc = self.add_node("CLIPTextEncode", {"text": "lowres, bad anatomy, blurry"})
        vae_encode = self.add_node("VAEEncode")
        sampler = self.add_node("KSampler", {"denoise": 0.7})
        vae_decode = self.add_node("VAEDecode")
        save = self.add_node("SaveImage")

        self.connect_node(pos_enc, "clip", ckpt, 1)
        self.connect_node(neg_enc, "clip", ckpt, 1)
        self.connect_node(cn_apply, "positive", pos_enc, 0)
        self.connect_node(cn_apply, "negative", neg_enc, 0)
        self.connect_node(cn_apply, "control_net", cn_loader, 0)
        self.connect_node(cn_apply, "image", preprocessor, 0)
        self.connect_node(vae_encode, "pixels", load_img, 0)
        self.connect_node(vae_encode, "vae", ckpt, 2)
        self.connect_node(sampler, "model", ckpt, 0)
        self.connect_node(sampler, "positive", cn_apply, 0)
        self.connect_node(sampler, "negative", cn_apply, 1)
        self.connect_node(sampler, "latent_image", vae_encode, 0)
        self.connect_node(vae_decode, "samples", sampler, 0)
        self.connect_node(vae_decode, "vae", ckpt, 2)
        self.connect_node(save, "images", vae_decode, 0)

        return "controlnet_img2img"

    def template_lora_txt2img(self, prompt: str, lora_name: str, lora_strength: float = 1.0) -> str:
        """Text-to-Image with LoRA"""
        ckpt = self.add_node("CheckpointLoaderSimple")
        lora = self.add_node("LoraLoaderModelOnly", {
            "lora_name": lora_name,
            "strength_model": lora_strength,
            "strength_clip": lora_strength
        })
        pos_enc = self.add_node("CLIPTextEncode", {"text": prompt})
        neg_enc = self.add_node("CLIPTextEncode", {"text": "lowres, bad anatomy, blurry"})
        latent = self.add_node("EmptyLatentImage")
        sampler = self.add_node("KSampler")
        vae_decode = self.add_node("VAEDecode")
        save = self.add_node("SaveImage")

        self.connect_node(lora, "model", ckpt, 0)
        self.connect_node(pos_enc, "clip", ckpt, 1)
        self.connect_node(neg_enc, "clip", ckpt, 1)
        self.connect_node(sampler, "model", lora, 0)
        self.connect_node(sampler, "positive", pos_enc, 0)
        self.connect_node(sampler, "negative", neg_enc, 0)
        self.connect_node(sampler, "latent_image", latent, 0)
        self.connect_node(vae_decode, "samples", sampler, 0)
        self.connect_node(vae_decode, "vae", ckpt, 2)
        self.connect_node(save, "images", vae_decode, 0)

        return "lora_text_to_image"

    def template_img2img(self, prompt: str, denoise: float = 0.7) -> str:
        """Image-to-Image workflow"""
        load_img = self.add_node("LoadImage", {"image": "input.png"})
        ckpt = self.add_node("CheckpointLoaderSimple")
        pos_enc = self.add_node("CLIPTextEncode", {"text": prompt})
        neg_enc = self.add_node("CLIPTextEncode", {"text": "lowres, bad anatomy, blurry"})
        vae_encode = self.add_node("VAEEncode")
        sampler = self.add_node("KSampler", {"denoise": denoise})
        vae_decode = self.add_node("VAEDecode")
        save = self.add_node("SaveImage")

        self.connect_node(pos_enc, "clip", ckpt, 1)
        self.connect_node(neg_enc, "clip", ckpt, 1)
        self.connect_node(vae_encode, "pixels", load_img, 0)
        self.connect_node(vae_encode, "vae", ckpt, 2)
        self.connect_node(sampler, "model", ckpt, 0)
        self.connect_node(sampler, "positive", pos_enc, 0)
        self.connect_node(sampler, "negative", neg_enc, 0)
        self.connect_node(sampler, "latent_image", vae_encode, 0)
        self.connect_node(vae_decode, "samples", sampler, 0)
        self.connect_node(vae_decode, "vae", ckpt, 2)
        self.connect_node(save, "images", vae_decode, 0)

        return "image_to_image"

    def template_video_upscale_rife(self, multiplier: int = 2) -> str:
        """Video Upscale with RIFE"""
        video_load = self.add_node("VHS_LoadVideo", {"frame_load_cap": 48})
        upscale_loader = self.add_node("UpscaleModelLoader")
        upscale = self.add_node("ImageUpscaleWithModel")
        rife = self.add_node("RIFE_VFI", {"multiplier": multiplier})
        video_combine = self.add_node("VHS_VideoCombine")

        self.connect_node(upscale, "upscale_model", upscale_loader, 0)
        self.connect_node(upscale, "image", video_load, 0)
        self.connect_node(rife, "images", upscale, 0)
        self.connect_node(rife, "frame_rate", video_load, 2)
        self.connect_node(video_combine, "images", rife, 0)
        self.connect_node(video_combine, "frame_rate", rife, 1)
        self.connect_node(video_combine, "audio", video_load, 1)

        return "video_upscale_rife"

    def template_ipadapter_character_video(self, prompt: str, weight: float = 0.8) -> str:
        """IP-Adapter Character Consistent Video"""
        ref_image = self.add_node("LoadImage", {"image": "character_reference.png"})
        ckpt = self.add_node("CheckpointLoaderSimple")
        clip_vision = self.add_node("CLIPVisionLoader")
        ip_loader = self.add_node("IPAdapterLoader")
        ip_apply = self.add_node("IPAdapterApply", {"weight": weight})
        ad_loader = self.add_node("AnimateDiffLoaderV2")
        pos_enc = self.add_node("CLIPTextEncode", {"text": prompt})
        neg_enc = self.add_node("CLIPTextEncode", {"text": "flicker, jitter, distorted, inconsistent face"})
        latent = self.add_node("EmptyLatentImage", {"batch_size": 16})
        sampler = self.add_node("KSampler", {"steps": 20})
        vae_decode = self.add_node("VAEDecode")
        video_combine = self.add_node("VHS_VideoCombine", {"frame_rate": 12})

        self.connect_node(ip_apply, "ipadapter", ip_loader, 0)
        self.connect_node(ip_apply, "clip_vision", clip_vision, 0)
        self.connect_node(ip_apply, "model", ckpt, 0)
        self.connect_node(ip_apply, "image", ref_image, 0)
        self.connect_node(ad_loader, "model", ip_apply, 0)
        self.connect_node(pos_enc, "clip", ckpt, 1)
        self.connect_node(neg_enc, "clip", ckpt, 1)
        self.connect_node(sampler, "model", ad_loader, 0)
        self.connect_node(sampler, "positive", pos_enc, 0)
        self.connect_node(sampler, "negative", neg_enc, 0)
        self.connect_node(sampler, "latent_image", latent, 0)
        self.connect_node(vae_decode, "samples", sampler, 0)
        self.connect_node(vae_decode, "vae", ckpt, 2)
        self.connect_node(video_combine, "images", vae_decode, 0)

        return "ipadapter_character_video"

    # Intent matching
    def _extract_prompt(self, text: str) -> str:
        """Extract prompt from user text"""
        text_lower = text.lower()
        keywords = ["generate", "create", "build", "workflow", "for", "with", "using",
                    "生成", "创建", "构建", "工作流", "video", "视频", "image", "图片"]
        for kw in keywords:
            text_lower = text_lower.replace(kw, "")
        return text_lower.strip() if text_lower.strip() else "masterpiece, best quality, detailed, 8k"

    def _extract_style(self, text: str) -> str:
        """Extract style from text"""
        styles = ["anime", "cyberpunk", "realistic", "fantasy", "ghibli", "portrait",
                  "landscape", "impressionist", "oil painting", "watercolor"]
        text_lower = text.lower()
        for style in styles:
            if style in text_lower:
                return style
        return "anime, Studio Ghibli style"

    def _extract_lora_name(self, text: str) -> str:
        """Extract LoRA name from text"""
        return "example_lora.safetensors"

    def match_and_generate(self, user_requirement: str, workflow_format: str = "ui") -> Dict:
        """Match requirement to template and generate workflow"""
        self.reset_state()
        self.workflow_format = workflow_format

        req_lower = user_requirement.lower()
        workflow_type = "text_to_image"

        # Video detection
        is_video = any(kw in req_lower for kw in ["video", "视频", "animated", "animation"])

        if is_video:
            if "style" in req_lower or "风格" in req_lower or "重绘" in req_lower:
                workflow_type = self.template_video_style_transfer(
                    style=self._extract_style(user_requirement)
                )
            elif "upscale" in req_lower or "rife" in req_lower or "补帧" in req_lower:
                workflow_type = self.template_video_upscale_rife()
            elif "character" in req_lower or "ip-adapter" in req_lower or "人物" in req_lower:
                workflow_type = self.template_ipadapter_character_video(
                    prompt=self._extract_prompt(user_requirement)
                )
            else:
                workflow_type = self.template_animatediff_txt2vid(
                    prompt=self._extract_prompt(user_requirement)
                )
        else:
            # Image workflows
            if "controlnet" in req_lower or "control net" in req_lower:
                workflow_type = self.template_controlnet_img2img(
                    prompt=self._extract_prompt(user_requirement)
                )
            elif "lora" in req_lower:
                workflow_type = self.template_lora_txt2img(
                    prompt=self._extract_prompt(user_requirement),
                    lora_name=self._extract_lora_name(user_requirement)
                )
            elif "img2img" in req_lower or "image to image" in req_lower or "图生图" in req_lower:
                workflow_type = self.template_img2img(
                    prompt=self._extract_prompt(user_requirement)
                )
            else:
                workflow_type = self.template_basic_txt2img(
                    prompt=self._extract_prompt(user_requirement)
                )

        is_valid, validation_msg = self.validate_workflow()

        return {
            "success": is_valid,
            "workflow_json": self.generate_workflow_json(),
            "validation_message": validation_msg,
            "required_plugins": list(self.required_plugins),
            "node_count": len(self.workflow),
            "workflow_type": workflow_type
        }


def generate_comfyui_workflow(user_requirement: str,
                               workflow_format: str = "ui",
                               output_file: str = None) -> Dict:
    """
    Main entry point for generating ComfyUI workflows.
    """
    generator = ComfyUIWorkflowGenerator()
    result = generator.match_and_generate(user_requirement, workflow_format)

    if output_file and result["success"]:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result["workflow_json"])

    return result


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python skill_agent.py <requirement> [output_file]")
        sys.exit(1)

    requirement = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    result = generate_comfyui_workflow(requirement, output_file=output_file)

    print(f"\n{'='*60}")
    print(f"Workflow Type: {result['workflow_type']}")
    print(f"Node Count: {result['node_count']}")
    print(f"Validation: {result['validation_message']}")
    print(f"{'='*60}")

    if result["required_plugins"]:
        print(f"\nRequired Plugins:")
        for plugin in result["required_plugins"]:
            print(f"  - {plugin}")

    print(f"\n{'='*60}")
    print("Generated Workflow JSON:")
    print(f"{'='*60}\n")
    print(result["workflow_json"])
