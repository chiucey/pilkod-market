#!/usr/bin/env python3
"""
MIDI 多音轨长时间文件生成器
支持 Studio One 7 / Ableton Live 12 Suite 乐器库映射
"""

import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import os

# ============================================================
# 数据结构定义
# ============================================================

@dataclass
class TrackConfig:
    """音轨配置"""
    name: str
    program: int  # MIDI Program Number (0-127)
    channel: int = 0  # MIDI Channel (0-15)
    volume: int = 100  # 音量 (0-127)
    pan: int = 64  # 声像 (0-127, 64=居中)
    is_drum: bool = False  # 是否为鼓组轨道

@dataclass
class NoteEvent:
    """音符事件"""
    pitch: int  # MIDI音符号 (0-127)
    velocity: int  # 力度 (0-127)
    start_tick: int  # 开始时间 (ticks)
    duration: int  # 持续时间 (ticks)
    channel: int = 0  # MIDI Channel

@dataclass
class SongStructure:
    """歌曲结构"""
    name: str
    tempo: int  # BPM
    time_signature: Tuple[int, int] = (4, 4)
    duration_minutes: float = 3.0
    intro_bars: int = 4
    verse_bars: int = 8
    chorus_bars: int = 8
    bridge_bars: int = 4
    outro_bars: int = 4

# ============================================================
# GM 标准音色表
# ============================================================

GM_PROGRAMS = {
    # Piano (0-7)
    0: "Acoustic Grand Piano",
    1: "Bright Acoustic Piano",
    2: "Electric Grand Piano",
    3: "Honky-tonk Piano",
    4: "Electric Piano 1",
    5: "Electric Piano 2",
    6: "Harpsichord",
    7: "Clavinet",
    # Chromatic Percussion (8-15)
    8: "Celesta",
    9: "Glockenspiel",
    10: "Music Box",
    11: "Vibraphone",
    12: "Marimba",
    13: "Xylophone",
    14: "Tubular Bells",
    15: "Dulcimer",
    # Organ (16-23)
    16: "Drawbar Organ",
    17: "Percussive Organ",
    18: "Rock Organ",
    19: "Church Organ",
    20: "Reed Organ",
    21: "Accordion",
    22: "Harmonica",
    23: "Tango Accordion",
    # Guitar (24-31)
    24: "Nylon Guitar",
    25: "Steel Guitar",
    26: "Jazz Guitar",
    27: "Clean Guitar",
    28: "Muted Guitar",
    29: "Overdriven Guitar",
    30: "Distortion Guitar",
    31: "Guitar Harmonics",
    # Bass (32-39)
    32: "Acoustic Bass",
    33: "Electric Bass (Jazz)",
    34: "Electric Bass (Pick)",
    35: "Fretless Bass",
    36: "Slap Bass 1",
    37: "Slap Bass 2",
    38: "Synth Bass 1",
    39: "Synth Bass 2",
    # Strings (40-47)
    40: "Violin",
    41: "Viola",
    42: "Cello",
    43: "Contrabass",
    44: "Tremolo Strings",
    45: "Pizzicato Strings",
    46: "Orchestral Harp",
    47: "Timpani",
    # Ensemble (48-55)
    48: "String Ensemble 1",
    49: "String Ensemble 2",
    50: "Synth Strings 1",
    51: "Synth Strings 2",
    52: "Choir Aahs",
    53: "Voice Oohs",
    54: "Synth Choir",
    55: "Orchestra Hit",
    # Brass (56-63)
    56: "Trumpet",
    57: "Trombone",
    58: "Tuba",
    59: "Muted Trumpet",
    60: "French Horn",
    61: "Brass Section",
    62: "Synth Brass 1",
    63: "Synth Brass 2",
    # Reed (64-71)
    64: "Soprano Sax",
    65: "Alto Sax",
    66: "Tenor Sax",
    67: "Baritone Sax",
    68: "Oboe",
    69: "English Horn",
    70: "Bassoon",
    71: "Clarinet",
    # Pipe (72-79)
    72: "Piccolo",
    73: "Flute",
    74: "Recorder",
    75: "Pan Flute",
    76: "Blown Bottle",
    77: "Shakuhachi",
    78: "Whistle",
    79: "Ocarina",
    # Synth Lead (80-87)
    80: "Lead 1 (Square)",
    81: "Lead 2 (Sawtooth)",
    82: "Lead 3 (Calliope)",
    83: "Lead 4 (Chiff)",
    84: "Lead 5 (Charang)",
    85: "Lead 6 (Voice)",
    86: "Lead 7 (Fifths)",
    87: "Lead 8 (Bass+Lead)",
    # Synth Pad (88-95)
    88: "Pad 1 (New Age)",
    89: "Pad 2 (Warm)",
    90: "Pad 3 (Polysynth)",
    91: "Pad 4 (Choir)",
    92: "Pad 5 (Bowed)",
    93: "Pad 6 (Metallic)",
    94: "Pad 7 (Halo)",
    95: "Pad 8 (Sweep)",
    # Synth Effects (96-103)
    96: "FX 1 (Rain)",
    97: "FX 2 (Soundtrack)",
    98: "FX 3 (Crystal)",
    99: "FX 4 (Atmosphere)",
    100: "FX 5 (Brightness)",
    101: "FX 6 (Goblins)",
    102: "FX 7 (Echoes)",
    103: "FX 8 (Sci-Fi)",
    # Ethnic (104-111)
    104: "Sitar",
    105: "Banjo",
    106: "Shamisen",
    107: "Koto",
    108: "Kalimba",
    109: "Bagpipe",
    110: "Fiddle",
    111: "Shanai",
    # Percussive (112-119)
    112: "Tinkle Bell",
    113: "Agogo",
    114: "Steel Drums",
    115: "Woodblock",
    116: "Taiko Drum",
    117: "Melodic Tom",
    118: "Synth Drum",
    119: "Reverse Cymbal",
    # Sound Effects (120-127)
    120: "Guitar Fret Noise",
    121: "Breath Noise",
    122: "Seashore",
    123: "Bird Tweet",
    124: "Telephone Ring",
    125: "Helicopter",
    126: "Applause",
    127: "Gunshot"
}

# 鼓组音色映射 (Channel 9, Program = 0)
DRUM_KITS = {
    # Standard Drum Kit (GM Drum Map)
    35: "Acoustic Bass Drum",
    36: "Bass Drum 1",
    37: "Side Stick",
    38: "Acoustic Snare",
    39: "Hand Clap",
    40: "Electric Snare",
    41: "Low Floor Tom",
    42: "Closed Hi-Hat",
    43: "High Floor Tom",
    44: "Pedal Hi-Hat",
    45: "Low Tom",
    46: "Open Hi-Hat",
    47: "Low-Mid Tom",
    48: "Hi-Mid Tom",
    49: "Crash Cymbal 1",
    50: "High Tom",
    51: "Ride Cymbal 1",
    52: "Chinese Cymbal",
    53: "Ride Bell",
    54: "Tambourine",
    55: "Splash Cymbal",
    56: "Cowbell",
    57: "Crash Cymbal 2",
    58: "Vibraslap",
    59: "Ride Cymbal 2",
    60: "Hi Bongo",
    61: "Low Bongo",
    62: "Mute Hi Conga",
    63: "Open Hi Conga",
    64: "Low Conga",
    65: "High Timbale",
    66: "Low Timbale",
    67: "High Agogo",
    68: "Low Agogo",
    69: "Cabasa",
    70: "Maracas",
    71: "Short Whistle",
    72: "Long Whistle",
    73: "Short Guiro",
    74: "Long Guiro",
    75: "Claves",
    76: "Hi Wood Block",
    77: "Low Wood Block",
    78: "Mute Cuica",
    79: "Open Cuica",
    80: "Mute Triangle",
    81: "Open Triangle"
}

# ============================================================
# MIDI 生成器类
# ============================================================

class MidiGenerator:
    """MIDI 多音轨长时间文件生成器"""

    def __init__(self, ticks_per_beat: int = 480):
        """
        初始化 MIDI 生成器

        Args:
            ticks_per_beat: 每拍的 ticks 数（默认 480，高精度）
        """
        self.ticks_per_beat = ticks_per_beat
        self.mid = MidiFile(type=1, ticks_per_beat=ticks_per_beat)
        self.tracks: List[MidiTrack] = []
        self.track_configs: List[TrackConfig] = []

    def create_track(self, config: TrackConfig) -> MidiTrack:
        """
        创建单个音轨

        Args:
            config: 音轨配置

        Returns:
            MidiTrack 对象
        """
        track = MidiTrack()
        track.name = config.name

        # 设置音色 (Program Change)
        if config.is_drum:
            # 鼓组使用 Channel 9 (index=9)
            track.append(Message('program_change', program=0, channel=9, time=0))
        else:
            track.append(Message('program_change', program=config.program, channel=config.channel, time=0))

        # 设置音量 (Control Change 7)
        track.append(Message('control_change', controller=7, value=config.volume, channel=config.channel, time=0))

        # 设置声像 (Control Change 10)
        track.append(Message('control_change', controller=10, value=config.pan, channel=config.channel, time=0))

        # 表情控制器 (Control Change 11) - 用于力度动态
        track.append(Message('control_change', controller=11, value=100, channel=config.channel, time=0))

        self.tracks.append(track)
        self.track_configs.append(config)
        return track

    def add_tempo_track(self, tempo_bpm: int, time_signature: Tuple[int, int] = (4, 4)):
        """
        添加速度/节拍轨

        Args:
            tempo_bpm: 每分钟节拍数
            time_signature: 节拍号 (分子, 分母)
        """
        tempo_track = MidiTrack()
        tempo_track.name = "Tempo"

        # 设置速度
        tempo = mido.bpm2tempo(tempo_bpm)
        tempo_track.append(MetaMessage('set_tempo', tempo=tempo, time=0))

        # 设置拍号
        tempo_track.append(MetaMessage('time_signature',
                                       numerator=time_signature[0],
                                       denominator=time_signature[1],
                                       time=0))

        # 插入到开头
        self.mid.tracks.insert(0, tempo_track)

    def add_notes_to_track(self, track_index: int, notes: List[NoteEvent]):
        """
        向音轨添加音符事件

        Args:
            track_index: 音轨索引
            notes: 音符事件列表
        """
        if track_index >= len(self.tracks):
            raise ValueError(f"音轨索引 {track_index} 超出范围")

        track = self.tracks[track_index]
        config = self.track_configs[track_index]
        channel = 9 if config.is_drum else config.channel

        # 按开始时间排序
        notes_sorted = sorted(notes, key=lambda n: n.start_tick)

        for note in notes_sorted:
            # Note On
            track.append(Message('note_on',
                               note=note.pitch,
                               velocity=note.velocity,
                               channel=channel,
                               time=note.start_tick))

            # Note Off
            track.append(Message('note_off',
                               note=note.pitch,
                               velocity=0,
                               channel=channel,
                               time=note.start_tick + note.duration))

    def add_note(self, track_index: int, pitch: int, velocity: int,
                 start_tick: int, duration: int):
        """
        添加单个音符（便捷方法）

        Args:
            track_index: 音轨索引
            pitch: MIDI 音符号 (0-127)
            velocity: 力度 (0-127)
            start_tick: 开始时间
            duration: 持续时间
        """
        note = NoteEvent(pitch=pitch, velocity=velocity,
                        start_tick=start_tick, duration=duration,
                        channel=self.track_configs[track_index].channel)
        self.add_notes_to_track(track_index, [note])

    def save(self, filepath: str):
        """
        保存 MIDI 文件

        Args:
            filepath: 输出文件路径
        """
        # 确保所有音轨有 end_of_track
        for track in self.mid.tracks:
            if len(track) == 0 or track[-1].type != 'end_of_track':
                track.append(MetaMessage('end_of_track', time=0))

        self.mid.save(filepath)
        print(f"MIDI 文件已保存: {filepath}")

    def get_duration_ticks(self, duration_minutes: float, tempo_bpm: int) -> int:
        """
        将分钟转换为 ticks

        Args:
            duration_minutes: 时长（分钟）
            tempo_bpm: 速度 (BPM)

        Returns:
            总 ticks 数
        """
        beats_per_minute = tempo_bpm
        ticks_per_minute = beats_per_minute * self.ticks_per_beat
        return int(duration_minutes * ticks_per_minute)


# ============================================================
# 便捷生成函数
# ============================================================

def create_simple_melody(generator: MidiGenerator, track_index: int,
                         start_tick: int, length_ticks: int,
                         root_note: int = 60, scale_type: str = "major") -> List[int]:
    """
    创建简单旋律（基于音阶）

    Args:
        generator: MidiGenerator 实例
        track_index: 音轨索引
        start_tick: 开始时间
        length_ticks: 旋律长度
        root_note: 根音 (C4=60)
        scale_type: 音阶类型 ("major", "minor", "pentatonic")

    Returns:
        使用的音符列表
    """
    # 音阶间隔（半音）
    scales = {
        "major": [0, 2, 4, 5, 7, 9, 11, 12],
        "minor": [0, 2, 3, 5, 7, 8, 10, 12],
        "pentatonic": [0, 2, 4, 7, 9, 12],
        "blues": [0, 3, 5, 6, 7, 10, 12]
    }

    scale = scales.get(scale_type, scales["major"])
    note_length = self.ticks_per_beat // 2  # 八分音符
    used_notes = []

    current_tick = start_tick
    note_index = 0

    while current_tick < start_tick + length_ticks:
        # 选择音符（在音阶范围内循环）
        octave_shift = (note_index // len(scale)) * 12
        pitch = root_note + scale[note_index % len(scale)] + octave_shift

        # 限制在 127 以内
        if pitch > 127:
            break

        # 添加音符
        velocity = 80 + (note_index % 3) * 10  # 力度变化
        generator.add_note(track_index, pitch, velocity,
                          current_tick, note_length)
        used_notes.append(pitch)

        current_tick += note_length
        note_index += 1

    return used_notes


def create_chord_progression(generator: MidiGenerator, track_index: int,
                             start_tick: int, chord_root: int,
                             chord_progression: List[Tuple[int, str]],
                             note_length: int) -> List[List[int]]:
    """
    创建和弦进行

    Args:
        generator: MidiGenerator 实例
        track_index: 音轨索引
        start_tick: 开始时间
        chord_root: 和弦根音
        chord_progression: 和弦进行 [(根音偏移, 类型), ...]
        note_length: 和弦持续时间

    Returns:
        每个和弦的音符列表
    """
    # 和弦类型音程
    chord_intervals = {
        "maj": [0, 4, 7],
        "min": [0, 3, 7],
        "7": [0, 4, 7, 10],
        "maj7": [0, 4, 7, 11],
        "min7": [0, 3, 7, 10],
        "sus4": [0, 5, 7],
        "sus2": [0, 2, 7],
        "dim": [0, 3, 6],
        "aug": [0, 4, 8]
    }

    all_chords = []
    current_tick = start_tick

    for interval, chord_type in chord_progression:
        intervals = chord_intervals.get(chord_type, chord_intervals["maj"])
        chord_notes = []

        for i, interval_value in enumerate(intervals):
            pitch = chord_root + interval + interval_value
            if pitch <= 127:
                # 和弦音符错开几个 ticks 避免同时触发
                generator.add_note(track_index, pitch, 70,
                                  current_tick + i*2, note_length)
                chord_notes.append(pitch)

        all_chords.append(chord_notes)
        current_tick += note_length

    return all_chords


def create_drum_pattern(generator: MidiGenerator, track_index: int,
                        start_tick: int, pattern_length: int,
                        pattern_type: str = "basic") -> Dict[str, List[int]]:
    """
    创建鼓组节奏型

    Args:
        generator: MidiGenerator 实例
        track_index: 音轨索引
        start_tick: 开始时间
        pattern_length: 模式长度（ticks）
        pattern_type: 节奏型类型

    Returns:
        各鼓部件的音符列表
    """
    # GM 鼓组音符映射
    # Note: 鼓组在 Channel 9，program=0
    drum_notes = {
        "kick": 36,      # Bass Drum 1
        "snare": 38,     # Acoustic Snare
        "hihat_closed": 42,  # Closed Hi-Hat
        "hihat_open": 46,    # Open Hi-Hat
        "hihat_pedal": 44,  # Pedal Hi-Hat
        "tom_high": 50,     # High Tom
        "tom_mid": 47,      # Low-Mid Tom
        "tom_low": 45,      # Low Tom
        "cymbal_crash": 49, # Crash Cymbal 1
        "cymbal_ride": 51    # Ride Cymbal 1
    }

    patterns = {
        "basic": {
            # 4/4 基础节奏
            "kick": [0, 480, 960, 1440],
            "snare": [480, 1440],
            "hihat_closed": [0, 120, 240, 360, 480, 600, 720, 840, 960, 1080, 1200, 1320, 1440, 1560, 1680, 1800],
            "hihat_open": [960]
        },
        "rock": {
            "kick": [0, 480, 960, 1440],
            "snare": [480, 960, 1440, 1920],
            "hihat_closed": [0, 240, 480, 720, 960, 1200, 1440, 1680, 1920, 2160],
            "hihat_open": [1200, 2160]
        },
        "electronic": {
            "kick": [0, 240, 480, 720, 960, 1200, 1440, 1680],
            "snare": [480, 1440],
            "hihat_closed": [0, 120, 240, 360, 480, 600, 720, 840, 960, 1080, 1200, 1320, 1440, 1560, 1680, 1800],
        }
    }

    current_pattern = patterns.get(pattern_type, patterns["basic"])
    note_length = 120  # 短促的音符

    used_notes = {}
    for drum_part, times in current_pattern.items():
        if drum_part in drum_notes:
            used_notes[drum_part] = []
            for t in times:
                if start_tick + t < start_tick + pattern_length:
                    generator.add_note(track_index, drum_notes[drum_part], 100,
                                      start_tick + t, note_length)
                    used_notes[drum_part].append(drum_notes[drum_part])

    return used_notes


# ============================================================
# 主函数
# ============================================================

def generate_multitrack_midi(
    tracks_config: List[Dict],
    duration_minutes: float,
    tempo_bpm: int,
    output_path: str,
    song_structure: Optional[SongStructure] = None
) -> str:
    """
    生成多音轨 MIDI 文件

    Args:
        tracks_config: 音轨配置列表
            [{"name": str, "program": int, "channel": int, "volume": int, "is_drum": bool}, ...]
        duration_minutes: 时长（分钟）
        tempo_bpm: 速度 (BPM)
        output_path: 输出文件路径
        song_structure: 歌曲结构（可选）

    Returns:
        保存的文件路径
    """
    generator = MidiGenerator()

    # 添加速度轨
    time_sig = song_structure.time_signature if song_structure else (4, 4)
    generator.add_tempo_track(tempo_bpm, time_sig)

    # 创建音轨
    for config_dict in tracks_config:
        config = TrackConfig(**config_dict)
        generator.create_track(config)

    # 计算总 ticks
    total_ticks = generator.get_duration_ticks(duration_minutes, tempo_bpm)

    # 为每个音轨生成内容
    for i, config_dict in enumerate(tracks_config):
        if config_dict.get("is_drum", False):
            # 鼓组 - 重复节奏型
            pattern_ticks = generator.ticks_per_beat * 4  # 4拍的模式
            repeats = total_ticks // pattern_ticks + 1

            for rep in range(repeats):
                start_tick = rep * pattern_ticks
                create_drum_pattern(generator, i, start_tick, pattern_ticks, "rock")

    # 保存文件
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    generator.save(output_path)

    return output_path


# ============================================================
# 示例用法
# ============================================================

if __name__ == "__main__":
    # 示例：生成 4 音轨 MIDI
    tracks = [
        {"name": "Piano", "program": 0, "channel": 0, "volume": 100, "is_drum": False},
        {"name": "Bass", "program": 32, "channel": 1, "volume": 90, "is_drum": False},
        {"name": "Drums", "program": 0, "channel": 9, "volume": 95, "is_drum": True},
        {"name": "Strings", "program": 48, "channel": 2, "volume": 80, "is_drum": False}
    ]

    output = generate_multitrack_midi(
        tracks_config=tracks,
        duration_minutes=3.0,
        tempo_bpm=120,
        output_path="output/example_composition.mid"
    )

    print(f"生成完成: {output}")