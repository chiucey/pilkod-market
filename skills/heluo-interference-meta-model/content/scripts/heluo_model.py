"""
HeLuo Coaxial Double Helix Interference Meta-Model v1.0

Core Purpose: Output "physical phase (one of 64 hexagrams)" instead of buy/sell signals.
Provides environmental anchoring and phase transition early warning for downstream trading systems.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class HexagramIndex(Enum):
    """64 Hexagram Index (Innate Sequence)"""
    QIAN = 1      # Pure Yang - Steadfast
    KUN = 2       # Pure Yin - Nurturing
    ZHEN = 51     # Thunder - Transformation
    XUN = 57      # Wind - Following
    KAN = 29      # Water - Danger
    LI = 30       # Fire - Opportunity
    GEN = 52      # Mountain - Observation
    DUI = 58      # Lake - Optimism
    # ... Additional hexagrams can be extended


@dataclass
class SixDimensionState:
    """Six-dimensional state vector (digital encoding of I Ching six lines)"""
    dynamic: float   # Momentum/Trend strength
    static: float    # Stability/Resistance
    transform: float # Change rate/Volatility
    harmony: float   # Synergy/Resonance degree
    clash: float     # Conflict/Deviation degree
    danger: float    # Risk/Crisis index

    def to_array(self) -> np.ndarray:
        return np.array([self.dynamic, self.static, self.transform,
                         self.harmony, self.clash, self.danger])

    def to_hexagram_code(self) -> int:
        """Map six-dimensional state to 64 hexagrams"""
        # Simplified hexagram mapping algorithm
        # Real applications require more complex mapping rules
        base = int((self.dynamic + self.static) * 32) % 64 + 1
        return base


class HeluoKernel:
    """
    Static Kernel Pool (River Map - Kernel)

    Stores immutable constants: long-term net assets, sector alpha, macro policy anchors.
    Once written, strictly prohibited from modification (unless fundamental changes like ST/delisting occur).
    Represents the underlying mathematical geometry of the world.
    """

    def __init__(self):
        self._static_tensor: Dict[str, float] = {}
        self._immutable = True

    def load_static_data(self, data: Dict[str, float]) -> None:
        """Load static constant data"""
        if self._immutable:
            raise ValueError("Kernel locked, static data modification prohibited")
        self._static_tensor.update(data)

    def get_tensor(self, key: str) -> Optional[float]:
        return self._static_tensor.get(key)

    def get_all(self) -> Dict[str, float]:
        return self._static_tensor.copy()

    def unlock(self):
        """Release lock (only for extreme cases)"""
        self._immutable = False

    def lock(self):
        """Re-lock"""
        self._immutable = True


class HeluoShell:
    """
    Dynamic Shell Pool (Luo Shu - Shell)

    Real-time high-frequency time-series data stream: minute-level sentiment scores,
    capital flow velocity, news sentiment entropy.
    Mathematical model based on the non-closure of π - no fixed periods,
    each prediction based on "spiral offset" calculation from past N periods.
    """

    def __init__(self, spiral_rate: float = 3.141592653589793):
        self.spiral_rate = spiral_rate  # π as initial spiral rate
        self.history_buffer: List[float] = []
        self._buffer_size = 1000

    def append_data(self, value: float, timestamp: Optional[float] = None) -> None:
        """Append new time-series data"""
        self.history_buffer.append(value)
        if len(self.history_buffer) > self._buffer_size:
            self.history_buffer.pop(0)

    def get_state_at_t(self, t: float) -> np.ndarray:
        """
        Calculate current dynamic vector based on time t.

        Uses the spiral property of π: never closes, continuously evolves.
        """
        if not self.history_buffer:
            return np.zeros(6)

        # Spiral index calculation (irrationality of π ensures non-repetition)
        n = len(self.history_buffer)
        spiral_idx = int((t * self.spiral_rate) % n)

        # Extract current and adjacent data points to construct vector
        state = np.zeros(6)
        for i in range(6):
            idx = (spiral_idx + i) % n
            state[i] = self.history_buffer[idx]

        return state / (np.linalg.norm(state) + 1e-10)  # Normalize


class HeluoInterferometer:
    """
    Interference Axis Core (Number 5 - Axis)

    At time t, performs inner product coupling between kernel tensor and shell tensor
    via attention mechanism.
    Calculates phase difference between static baseline (inner hexagram) and
    dynamic sentiment (outer hexagram).
    """

    def __init__(self, kernel: HeluoKernel, shell: HeluoShell):
        self.kernel = kernel
        self.shell = shell
        self._attention_weights = np.ones(6) / 6  # Default uniform attention

    def set_attention_weights(self, weights: np.ndarray) -> None:
        """Set attention weights (learnable parameters)"""
        self._attention_weights = weights / weights.sum()

    def interfere(self, current_time: float) -> float:
        """
        Execute interference calculation.

        Returns:
            float: Phase difference (-1 to 1)
            Smaller difference → System more stable
            Larger difference → System more turbulent
        """
        # 1. Extract inner hexagram (static)
        inner_vector = self._extract_inner_vector()

        # 2. Extract outer hexagram (dynamic, time spiral)
        outer_vector = self.shell.get_state_at_t(current_time)

        # 3. Attention-weighted inner product coupling
        weighted_inner = inner_vector * self._attention_weights
        weighted_outer = outer_vector * self._attention_weights

        # 4. Calculate phase difference (cosine similarity)
        norm_inner = np.linalg.norm(weighted_inner)
        norm_outer = np.linalg.norm(weighted_outer)

        if norm_inner < 1e-10 or norm_outer < 1e-10:
            return 0.0

        phase_diff = np.dot(weighted_inner, weighted_outer) / (norm_inner * norm_outer)
        return phase_diff

    def _extract_inner_vector(self) -> np.ndarray:
        """Extract six-dimensional vector from kernel"""
        tensor = self.kernel.get_all()
        if not tensor:
            return np.ones(6) / np.sqrt(6)

        values = list(tensor.values())
        # Pad or truncate to 6 dimensions
        vec = np.zeros(6)
        for i in range(min(6, len(values))):
            vec[i] = values[i]
        return vec / (np.linalg.norm(vec) + 1e-10)


class HeluoObserver:
    """
    90-Degree Rotation Observer

    Reduces high-dimensional interference results to understandable six-dimensional
    physical states.
    Output: (Dynamic, Static, Transform, Harmony, Clash, Danger)
    """

    def __init__(self, interferometer: HeluoInterferometer):
        self.interferometer = interferometer
        self._six_dim_weights = np.array([0.3, 0.2, 0.15, 0.15, 0.1, 0.1])

    def project_hexagram(self, current_time: float) -> SixDimensionState:
        """
        Project and generate six-dimensional state.

        Returns:
            SixDimensionState: Digital encoding of corresponding I Ching hexagram
        """
        phase = self.interferometer.interfere(current_time)

        # Map phase difference to six-dimensional features
        # Phase difference range: -1 to 1

        # Dynamic: Trend strength (based on historical momentum)
        dynamic = abs(phase) * self._six_dim_weights[0] * 100

        # Static: Stability (related to phase stability)
        static = (1 - abs(phase)) * self._six_dim_weights[1] * 100

        # Transform: Change rate
        transform = abs(phase - 0.5) * self._six_dim_weights[2] * 100

        # Harmony: Synergy degree
        harmony = (1 + phase) / 2 * self._six_dim_weights[3] * 100

        # Clash: Conflict degree
        clash = (1 - phase) / 2 * self._six_dim_weights[4] * 100

        # Danger: Risk index
        danger = max(0, phase) * self._six_dim_weights[5] * 100

        return SixDimensionState(
            dynamic=min(100, dynamic),
            static=min(100, static),
            transform=min(100, transform),
            harmony=min(100, harmony),
            clash=min(100, clash),
            danger=min(100, danger)
        )


class HeluoAutoCalibrator:
    """
    Adaptive Evolution Calibrator

    Automatically calibrates shell pool spiral slope based on actual outcomes
    (e.g., market actually crashed or surged).
    When prediction error is too large, the system fine-tunes the shell spiral
    advancement arc length to adapt to chaotic drift.
    """

    def __init__(self, shell: HeluoShell, learning_rate: float = 0.01):
        self.shell = shell
        self.learning_rate = learning_rate
        self._calibration_history: List[float] = []

    def calibrate(self, predicted_phase: float, actual_outcome: float) -> float:
        """
        Execute calibration.

        Args:
            predicted_phase: Predicted phase difference
            actual_outcome: Actual outcome (-1 to 1)

        Returns:
            float: New calibrated spiral rate
        """
        # Calculate prediction error
        error = actual_outcome - predicted_phase

        # Adaptive spiral rate adjustment
        adjustment = self.learning_rate * error * np.pi
        new_spiral_rate = self.shell.spiral_rate + adjustment

        # Record calibration history
        self._calibration_history.append(new_spiral_rate)

        return new_spiral_rate

    def get_calibration_stats(self) -> Dict[str, float]:
        """Get calibration statistics"""
        if not self._calibration_history:
            return {"mean": self.shell.spiral_rate, "std": 0.0}

        return {
            "mean": np.mean(self._calibration_history),
            "std": np.std(self._calibration_history),
            "current": self._calibration_history[-1] if self._calibration_history else self.shell.spiral_rate
        }


class HeLuoMetaModel:
    """
    HeLuo Coaxial Double Helix Interference Meta-Model - Main System Entry

    Integrates all modules to provide environmental anchoring and phase
    transition early warning for downstream trading systems.
    """

    def __init__(self, spiral_rate: float = 3.141592653589793):
        # Initialize three-layer architecture
        self.kernel = HeluoKernel()
        self.shell = HeluoShell(spiral_rate=spiral_rate)
        self.interferometer = HeluoInterferometer(self.kernel, self.shell)
        self.observer = HeluoObserver(self.interferometer)
        self.auto_calibrator = HeluoAutoCalibrator(self.shell)

        # Hexagram mapping table (simplified)
        self._hexagram_names = {
            1: "Qian (Pure Yang)", 2: "Kun (Pure Yin)", 26: "Da Xu", 27: "Yi",
            49: "Ge (Revolution)", 50: "Ding", 51: "Zhen (Thunder)", 52: "Gen (Mountain)",
            # ... Can extend to full 64 hexagrams
        }

    def load_fundamental_data(self, data: Dict[str, float]) -> None:
        """Load fundamental data into kernel"""
        self.kernel.unlock()
        self.kernel.load_static_data(data)
        self.kernel.lock()

    def feed_market_data(self, value: float, timestamp: Optional[float] = None) -> None:
        """Feed market data into shell"""
        self.shell.append_data(value, timestamp)

    def run(self, current_time: float) -> Dict:
        """
        Execute single interference process.

        Args:
            current_time: Current timestamp

        Returns:
            Dict: Complete output containing six-dimensional state and hexagram info
        """
        # 1. Time entry
        # 2. Phase calculation (shell pool extracts spiral vector) - Built into interfere()
        # 3. Physical collision (interferometer calculates offset overlap) - Built into interfere()
        # 4. Projection reduction (observer outputs six-dimensional features)
        six_dim_state = self.observer.project_hexagram(current_time)

        # 5. State output
        hexagram_code = six_dim_state.to_hexagram_code()
        hexagram_name = self._hexagram_names.get(hexagram_code, f"Hexagram {hexagram_code}")

        return {
            "timestamp": current_time,
            "six_dimension": {
                "dynamic": six_dim_state.dynamic,
                "static": six_dim_state.static,
                "transform": six_dim_state.transform,
                "harmony": six_dim_state.harmony,
                "clash": six_dim_state.clash,
                "danger": six_dim_state.danger
            },
            "hexagram_code": hexagram_code,
            "hexagram_name": hexagram_name,
            "phase_description": self._get_phase_description(hexagram_code),
            "action_signal": self._generate_action_signal(six_dim_state)
        }

    def _get_phase_description(self, code: int) -> str:
        """Get hexagram description"""
        descriptions = {
            1: "Pure Yang stability, suitable for following the trend",
            2: "Pure Yin nurturing, suitable for accumulation",
            26: "Great Accumulation, suitable for steady accumulation",
            27: "Nurturing, suitable for rest and recovery",
            49: "Revolution - take calculated risks, strictly control position sizing",
            50: "Ding (Cauldron) - new cycle positioning",
            51: "Thunder shaking - active response required",
            52: "Mountain stillness - observe and wait",
        }
        return descriptions.get(code, "Under observation")

    def _generate_action_signal(self, state: SixDimensionState) -> str:
        """Generate trading signal"""
        if state.danger > 70:
            return "WARNING: High risk area, reduce position or stand aside"
        elif state.harmony > 70:
            return "BULLISH: Synergy resonance, suitable for following the trend"
        elif state.clash > 60:
            return "NEUTRAL: Bull-bear divergence, operate with caution"
        else:
            return "HOLD: Wait for clear signal"


# ============================================================
# Usage Example
# ============================================================

if __name__ == "__main__":
    # Initialize model
    model = HeLuoMetaModel()

    # Load fundamental data (kernel)
    fundamental_data = {
        "roe": 0.15,           # Return on equity
        "debt_ratio": 0.4,     # Debt ratio
        "pe_ratio": 20.0,      # P/E ratio
        "market_cap": 1000.0,  # Market cap (100M)
        "sector_alpha": 0.8,   # Sector alpha factor
        "macro_anchor": 0.6    # Macro policy anchor
    }
    model.load_fundamental_data(fundamental_data)

    # Simulate market data stream (shell)
    current_time = 100.0
    for i in range(100):
        # Simulate minute-level market sentiment fluctuation
        value = np.sin(i * 0.1) + np.random.normal(0, 0.1)
        model.feed_market_data(value, timestamp=current_time + i * 60)

    # Execute interference analysis
    result = model.run(current_time)

    print("=" * 50)
    print("HeLuo Coaxial Double Helix Interference Meta-Model")
    print("=" * 50)
    print(f"Current Time: {result['timestamp']}")
    print(f"Hexagram Code: {result['hexagram_code']} ({result['hexagram_name']})")
    print(f"Hexagram Interpretation: {result['phase_description']}")
    print(f"Action Signal: {result['action_signal']}")
    print("\nSix-Dimensional State:")
    for k, v in result['six_dimension'].items():
        print(f"  {k}: {v:.2f}")
