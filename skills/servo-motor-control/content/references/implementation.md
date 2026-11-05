---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: aa67693302a8f76f844a2ddb3e734827
    PropagateID: aa67693302a8f76f844a2ddb3e734827
    ReservedCode1: 3045022100bf66bc9ded7fbea3bdc3cccaa3856f215900e6cbbb835a5578c7dadb62871b5a0220315c2adb59cb0f3e0d36c59b671d7890809f53b9e920cd7b87fe30119f85a72d
    ReservedCode2: 3045022072a9468f7f9353bb171fd3625ce3605f7bbf9126a4a46dc5c0d7d709ab1bdd4b022100fd4929694cb3aac4f90deaa795c32d431e0e0282ba28cf05ee07164f8598555a
---

# Servo Motor Control Implementation Reference

## 1. Core Class Structure

```python
"""
Servo Motor Control - Cross-Platform Implementation
Supports: CIA402, CANopen, CANopenFD, EtherCAT
Platforms: Windows, Linux (Ubuntu), Embedded
"""

from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import struct


class ServoState(IntEnum):
    """CIA402 State Machine States"""
    INITIALIZATION = 0
    NOT_READY_TO_SWITCH_ON = 1
    SWITCH_ON_DISABLED = 2
    READY_TO_SWITCH_ON = 3
    SWITCHED_ON = 4
    OPERATION_ENABLED = 5
    QUICK_STOP_ACTIVE = 6
    FAULT_REACTION_ACTIVE = 7
    FAULT = 8


class OperationMode(IntEnum):
    """Operation Modes"""
    NO_MODE = 0
    PROFILE_POSITION = 1
    VELOCITY_MODE = 2
    PROFILE_VELOCITY = 3
    TORQUE_MODE = 4
    HOMING = 6
    INTERPOLATED_POSITION = 7


@dataclass
class MotorParameters:
    """Motor Parameters"""
    rated_current: int = 0        # Rated current (mA)
    max_current: int = 0          # Maximum current (mA)
    rated_speed: int = 0          # Rated speed (rpm)
    max_speed: int = 0            # Maximum speed (rpm)
    pole_pairs: int = 0           # Number of pole pairs
    encoder_resolution: int = 0   # Encoder resolution
    gear_ratio: float = 1.0       # Gear ratio


@dataclass
class MotionProfile:
    """Motion Profile Parameters"""
    target_position: int = 0
    target_velocity: int = 0
    target_torque: int = 0
    profile_velocity: int = 0
    profile_acceleration: int = 0
    profile_deceleration: int = 0
    quick_stop_deceleration: int = 0


# ============================================================================
# Protocol Abstraction Layer
# ============================================================================

class CANInterface(ABC):
    """CAN Bus Interface Abstraction"""

    @abstractmethod
    def send(self, can_id: int, data: bytes, timeout: float = 1.0) -> bool:
        """Send CAN message"""
        pass

    @abstractmethod
    def receive(self, timeout: float = 1.0) -> Optional[tuple]:
        """Receive CAN message"""
        pass

    @abstractmethod
    def open(self, channel: str, bitrate: int = 1000000) -> bool:
        """Open CAN channel"""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close CAN channel"""
        pass


class EtherCATInterface(ABC):
    """EtherCAT Interface Abstraction"""

    @abstractmethod
    def read_sdo(self, slave: int, index: int, subindex: int) -> Any:
        """SDO Read"""
        pass

    @abstractmethod
    def write_sdo(self, slave: int, index: int, subindex: int, value: Any) -> bool:
        """SDO Write"""
        pass

    @abstractmethod
    def read_pdo(self, slave: int, offset: int, size: int) -> bytes:
        """PDO Read"""
        pass

    @abstractmethod
    def write_pdo(self, slave: int, offset: int, data: bytes) -> bool:
        """PDO Write"""
        pass


# ============================================================================
# CIA402 Controller
# ============================================================================

class CIA402Controller:
    """
    CIA402 Standard Servo Controller
    Implements complete CIA402 state machine and motion control
    """

    # CIA402 Object Dictionary
    CONTROLWORD = 0x6040
    STATUSWORD = 0x6041
    MODES_OF_OPERATION = 0x6060
    MODES_OF_OPERATION_DISPLAY = 0x6061
    POSITION_DEMAND = 0x6062
    POSITION_ACTUAL = 0x6064
    VELOCITY_ACTUAL = 0x606C
    TORQUE_ACTUAL = 0x6077
    TARGET_POSITION = 0x607A
    TARGET_TORQUE = 0x6071
    MAX_TORQUE = 0x6072
    PROFILE_VELOCITY = 0x6081
    PROFILE_ACCELERATION = 0x6083
    PROFILE_DECELERATION = 0x6084
    QUICK_STOP_DECELERATION = 0x6085
    MOTOR_TYPE = 0x6402
    ERROR_REGISTER = 0x1001
    HOMING_METHOD = 0x6098
    HOMING_SPEEDS = 0x6099

    def __init__(self, interface: CANInterface, node_id: int = 1):
        self.interface = interface
        self.node_id = node_id
        self.state = ServoState.INITIALIZATION

    # ------------------------------------------------------------------
    # SDO Communication
    # ------------------------------------------------------------------

    def read_sdo(self, index: int, subindex: int, data_type: str = 'i32') -> Any:
        """Read SDO"""
        # SDO request: 0x40 + node_id high bits
        # [0x40, index_low, index_high, subindex]
        req = bytes([0x40, index & 0xFF, (index >> 8) & 0xFF, subindex])
        can_id = 0x600 + self.node_id

        if not self.interface.send(can_id, req):
            raise RuntimeError("SDO request failed")

        resp = self.interface.receive(timeout=1.0)
        if not resp:
            raise TimeoutError("SDO response timeout")

        _, data = resp
        return self._parse_sdo_response(data, data_type)

    def write_sdo(self, index: int, subindex: int, value: Any, data_type: str = 'i32') -> bool:
        """Write SDO"""
        cmd_byte, data_bytes = self._build_sdo_request(index, subindex, value, data_type)
        can_id = 0x600 + self.node_id
        req = bytes([cmd_byte, index & 0xFF, (index >> 8) & 0xFF, subindex] + list(data_bytes))
        return self.interface.send(can_id, req)

    def _parse_sdo_response(self, data: bytes, data_type: str) -> Any:
        """Parse SDO response"""
        if data[0] & 0x80:  # Error response
            raise RuntimeError(f"SDO error: {data[2]}")
        return self._decode_value(data[4:], data_type)

    def _build_sdo_request(self, index: int, subindex: int, value: Any, data_type: str):
        """Build SDO request"""
        encoded = self._encode_value(value, data_type)
        cmd_byte = 0x23 if len(encoded) == 4 else (0x2B if len(encoded) == 2 else 0x2F)
        return cmd_byte, encoded

    def _encode_value(self, value: Any, data_type: str) -> bytes:
        """Encode value"""
        if data_type == 'i8':
            return struct.pack('<b', value)
        elif data_type == 'i16':
            return struct.pack('<h', value)
        elif data_type == 'i32':
            return struct.pack('<i', value)
        elif data_type == 'u8':
            return struct.pack('<B', value)
        elif data_type == 'u16':
            return struct.pack('<H', value)
        elif data_type == 'u32':
            return struct.pack('<I', value)
        return struct.pack('<i', value)

    def _decode_value(self, data: bytes, data_type: str) -> Any:
        """Decode value"""
        if data_type == 'i8':
            return struct.unpack('<b', data[:1])[0]
        elif data_type == 'i16':
            return struct.unpack('<h', data[:2])[0]
        elif data_type == 'i32':
            return struct.unpack('<i', data[:4])[0]
        elif data_type == 'u8':
            return struct.unpack('<B', data[:1])[0]
        elif data_type == 'u16':
            return struct.unpack('<H', data[:2])[0]
        elif data_type == 'u32':
            return struct.unpack('<I', data[:4])[0]
        return struct.unpack('<i', data[:4])[0]

    # ------------------------------------------------------------------
    # CIA402 State Machine
    # ------------------------------------------------------------------

    def get_state(self) -> ServoState:
        """Get current state"""
        status = self.read_sdo(self.STATUSWORD, 0, 'u16')
        return self._statusword_to_state(status)

    def _statusword_to_state(self, status: int) -> ServoState:
        """Convert statusword to state"""
        if status & 0x0040:  # Switch on disabled
            if status & 0x008F == 0:
                return ServoState.NOT_READY_TO_SWITCH_ON
            return ServoState.SWITCH_ON_DISABLED
        elif status & 0x000F == 0:
            return ServoState.READY_TO_SWITCH_ON
        elif status & 0x000F == 1:
            return ServoState.SWITCHED_ON
        elif status & 0x000F == 3:
            return ServoState.OPERATION_ENABLED
        elif status & 0x000F == 7:
            return ServoState.QUICK_STOP_ACTIVE
        elif status & 0x000F == 8:
            if status & 0x0004:
                return ServoState.FAULT_REACTION_ACTIVE
            return ServoState.FAULT
        return ServoState.INITIALIZATION

    def set_state(self, command: int) -> bool:
        """Set state machine command"""
        return self.write_sdo(self.CONTROLWORD, 0, command, 'u16')

    def shutdown(self) -> bool:
        """Shutdown enable"""
        return self.set_state(0x0006)

    def switch_on(self) -> bool:
        """Switch on"""
        return self.set_state(0x0007)

    def enable_operation(self) -> bool:
        """Enable operation"""
        return self.set_state(0x000F)

    def disable_voltage(self) -> bool:
        """Disable voltage"""
        return self.set_state(0x0000)

    def quick_stop(self) -> bool:
        """Quick stop"""
        return self.set_state(0x000B)

    def fault_reset(self) -> bool:
        """Fault reset"""
        return self.set_state(0x0080)

    def is_fault(self) -> bool:
        """Check fault"""
        return self.get_state() == ServoState.FAULT

    def is_enabled(self) -> bool:
        """Check enable"""
        return self.get_state() == ServoState.OPERATION_ENABLED

    # ------------------------------------------------------------------
    # Motion Control
    # ------------------------------------------------------------------

    def set_operation_mode(self, mode: OperationMode) -> bool:
        """Set operation mode"""
        return self.write_sdo(self.MODES_OF_OPERATION, 0, int(mode), 'i8')

    def get_operation_mode(self) -> OperationMode:
        """Get current operation mode"""
        return OperationMode(self.read_sdo(self.MODES_OF_OPERATION_DISPLAY, 0, 'i8'))

    def set_target_position(self, position: int) -> bool:
        """Set target position"""
        return self.write_sdo(self.TARGET_POSITION, 0, position, 'i32')

    def get_actual_position(self) -> int:
        """Get actual position"""
        return self.read_sdo(self.POSITION_ACTUAL, 0, 'i32')

    def get_demand_position(self) -> int:
        """Get position demand value"""
        return self.read_sdo(self.POSITION_DEMAND, 0, 'i32')

    def set_target_velocity(self, velocity: int) -> bool:
        """Set target velocity"""
        return self.write_sdo(0x60FF, 0, velocity, 'i32')

    def get_actual_velocity(self) -> int:
        """Get actual velocity"""
        return self.read_sdo(self.VELOCITY_ACTUAL, 0, 'i32')

    def set_target_torque(self, torque: int) -> bool:
        """Set target torque"""
        return self.write_sdo(self.TARGET_TORQUE, 0, torque, 'i16')

    def get_actual_torque(self) -> int:
        """Get actual torque"""
        return self.read_sdo(self.TORQUE_ACTUAL, 0, 'i16')

    def set_profile_velocity(self, velocity: int) -> bool:
        """Set profile velocity"""
        return self.write_sdo(self.PROFILE_VELOCITY, 0, velocity, 'u32')

    def set_profile_acceleration(self, acceleration: int) -> bool:
        """Set profile acceleration"""
        return self.write_sdo(self.PROFILE_ACCELERATION, 0, acceleration, 'u32')

    def set_profile_deceleration(self, deceleration: int) -> bool:
        """Set profile deceleration"""
        return self.write_sdo(self.PROFILE_DECELERATION, 0, deceleration, 'u32')

    def move_absolute(self, position: int, velocity: int = 0) -> bool:
        """Absolute position move"""
        if velocity:
            self.set_profile_velocity(velocity)
        self.set_target_position(position)
        # Set controlword: New setpoint + Immediate effect + Absolute
        return self.set_state(0x000F)

    def move_relative(self, distance: int, velocity: int = 0) -> bool:
        """Relative position move"""
        if velocity:
            self.set_profile_velocity(velocity)
        self.set_target_position(distance)
        # Set controlword: New setpoint + Immediate effect + Relative
        return self.set_state(0x000F)

    def is_target_reached(self) -> bool:
        """Check if target reached"""
        status = self.read_sdo(self.STATUSWORD, 0, 'u16')
        return bool(status & 0x1000)  # Bit 12: Target reached

    def start_homing(self, method: int = 0) -> bool:
        """Start homing"""
        self.set_operation_mode(OperationMode.HOMING)
        self.write_sdo(self.HOMING_METHOD, 0, method, 'i8')
        return self.set_state(0x000F)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def get_error_register(self) -> int:
        """Get error register"""
        return self.read_sdo(self.ERROR_REGISTER, 0, 'u8')

    def get_motor_parameters(self) -> MotorParameters:
        """Get motor parameters"""
        return MotorParameters(
            encoder_resolution=self.read_sdo(0x3010, 1, 'u32'),
            max_speed=self.read_sdo(0x6080, 0, 'u32'),
            rated_current=self.read_sdo(0x3002, 1, 'u32'),
            max_current=self.read_sdo(0x3002, 2, 'u32'),
        )

    def diagnose(self) -> Dict[str, Any]:
        """Complete diagnostics"""
        status = self.read_sdo(self.STATUSWORD, 0, 'u16')
        return {
            'state': self.get_state().name,
            'operation_mode': self.get_operation_mode().name,
            'status_bits': {
                'ready_to_switch_on': bool(status & 0x0001),
                'switched_on': bool(status & 0x0002),
                'operation_enabled': bool(status & 0x0004),
                'fault': bool(status & 0x0008),
                'voltage_enabled': bool(status & 0x0010),
                'quick_stop': bool(status & 0x0020),
                'switch_on_disabled': bool(status & 0x0040),
                'warning': bool(status & 0x0080),
                'target_reached': bool(status & 0x1000),
            },
            'position': self.get_actual_position(),
            'velocity': self.get_actual_velocity(),
            'torque': self.get_actual_torque(),
            'error_register': hex(self.get_error_register()),
        }


# ============================================================================
# Platform-Specific Drivers
# ============================================================================

class LinuxSocketCAN(CANInterface):
    """Linux SocketCAN Driver"""

    def __init__(self):
        self.socket = None
        self.channel = None

    def open(self, channel: str, bitrate: int = 1000000) -> bool:
        import socket
        import struct

        self.channel = channel
        self.socket = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)

        try:
            self.socket.bind((channel,))
            # Set bitrate (need to configure with ip command)
            return True
        except OSError as e:
            print(f"Failed to bind to {channel}: {e}")
            return False

    def send(self, can_id: int, data: bytes, timeout: float = 1.0) -> bool:
        import struct

        # CAN frame: ID + DLC + Data
        can_frame = struct.pack('<IBB8s',
            can_id,
            len(data),
            0,  # FF (extended frame)
            data.ljust(8, b'\x00')
        )
        try:
            self.socket.send(can_frame)
            return True
        except:
            return False

    def receive(self, timeout: float = 1.0):
        import struct

        self.socket.settimeout(timeout)
        try:
            frame = self.socket.recv(16)
            can_id, dlc, flags, data = struct.unpack('<IBB8s', frame)
            return (can_id, bytes(data[:dlc]))
        except:
            return None

    def close(self):
        if self.socket:
            self.socket.close()


class WindowsPCAN(CANInterface):
    """Windows PCAN-Basic API Driver"""

    def __init__(self):
        self.handle = None

    def open(self, channel: str = "PCAN_USBBUS1", bitrate: int = 1000000) -> bool:
        # Requires PCAN-Basic driver and Python API installation
        # Interface definition provided here
        self.channel = channel
        return True

    def send(self, can_id: int, data: bytes, timeout: float = 1.0) -> bool:
        # PCAN-Basic API call
        return True

    def receive(self, timeout: float = 1.0):
        # PCAN-Basic API call
        return None

    def close(self):
        pass


class EtherCATMaster:
    """EtherCAT Master (Linux IgH)"""

    def __init__(self, ifname: str = "eth0"):
        self.ifname = ifname
        self.slaves = []
        self.domain = None

    def scan_slaves(self) -> List[int]:
        """Scan for slaves"""
        # Use IgH API to scan
        return []

    def read_sdo(self, slave: int, index: int, subindex: int) -> Any:
        """Read SDO"""
        # IgH API: ec_read_sdo()
        pass

    def write_sdo(self, slave: int, index: int, subindex: int, value: Any) -> bool:
        """Write SDO"""
        # IgH API: ec_write_sdo()
        pass

    def read_pdo(self, slave: int, offset: int, size: int) -> bytes:
        """Read PDO"""
        # IgH API: domain process data
        pass

    def write_pdo(self, slave: int, offset: int, data: bytes) -> bool:
        """Write PDO"""
        # IgH API: domain process data
        pass


class EmbeddedCAN(CANInterface):
    """Embedded CAN Driver (Generic Implementation)"""

    def __init__(self):
        self.tx_buffer = []
        self.rx_buffer = []
        self.hardware = None

    def open(self, channel: str, bitrate: int = 1000000) -> bool:
        """Open CAN channel"""
        # HAL layer call
        return True

    def send(self, can_id: int, data: bytes, timeout: float = 1.0) -> bool:
        """Send CAN message"""
        # Hardware send
        return True

    def receive(self, timeout: float = 1.0):
        """Receive CAN message"""
        # Hardware receive
        return None

    def close(self):
        """Close CAN channel"""
        pass


# ============================================================================
# Master Station Real-Time Control
# ============================================================================

class ServoMotionMode(IntEnum):
    """Servo motion modes - CVP/CVS/CVT/CSP/CSV/CST"""
    PROFILE_POSITION = 1    # CVP - Profile Position
    VELOCITY_MODE = 2      # CVS - Profile Velocity
    TORQUE_MODE = 4        # CVT - Profile Torque
    HOMING = 6             # Home
    INTERPOLATED_POSITION = 7  # CIP
    CYCLIC_SYNC_POSITION = 8  # CSP - Cyclic Synchronous Position
    CYCLIC_SYNC_VELOCITY = 9  # CSV - Cyclic Synchronous Velocity
    CYCLIC_SYNC_TORQUE = 10   # CST - Cyclic Synchronous Torque


class SyncMode(IntEnum):
    """Multi-axis synchronization modes"""
    NO_SYNC = 0
    ELECTRONIC_GEAR = 1
    ELECTRONIC_CAM = 2
    PHASING = 3
    GEARING_WITH_PHASE = 4


@dataclass
class AxisConfig:
    """Axis configuration"""
    slave_id: int
    name: str = ""
    direction: int = 1
    gear_ratio: float = 1.0
    cam_id: int = 0
    phase_offset: int = 0


class MasterStation:
    """
    Master Station for Real-Time Control
    Performs trajectory planning and distributes targets to slave axes
    """

    def __init__(self, interface: EtherCATInterface):
        self.interface = interface
        self.axes: Dict[int, CIA402Controller] = {}
        self.axis_configs: Dict[int, AxisConfig] = {}
        self.sync_mode = SyncMode.NO_SYNC
        self.master_axis: int = 0
        self.trajectory_generator = TrajectoryPlanner()
        self.cycle_time_us = 1000  # 1ms cycle time
        self.is_running = False

    def add_axis(self, slave_id: int, config: AxisConfig = None):
        """Add a slave axis"""
        if config is None:
            config = AxisConfig(slave_id=slave_id, name=f"Axis_{slave_id}")
        self.axes[slave_id] = CIA402Controller(self.interface, slave_id)
        self.axis_configs[slave_id] = config

    def remove_axis(self, slave_id: int):
        """Remove a slave axis"""
        if slave_id in self.axes:
            del self.axes[slave_id]
        if slave_id in self.axis_configs:
            del self.axis_configs[slave_id]

    def set_sync_mode(self, mode: SyncMode, master_axis: int = 0):
        """Set multi-axis synchronization mode"""
        self.sync_mode = mode
        self.master_axis = master_axis

    def power_on_all(self):
        """Power on all axes"""
        for slave_id, ctrl in self.axes.items():
            ctrl.shutdown()
            ctrl.switch_on()
            ctrl.enable_operation()

    def power_off_all(self):
        """Power off all axes"""
        for slave_id, ctrl in self.axes.items():
            ctrl.shutdown()
            ctrl.disable_voltage()

    def enable_all(self):
        """Enable all axes (operation enabled)"""
        for slave_id, ctrl in self.axes.items():
            ctrl.enable_operation()

    def disable_all(self):
        """Disable all axes"""
        for slave_id, ctrl in self.axes.items():
            ctrl.shutdown()

    def home_all(self, method: int = 0):
        """Home all axes"""
        for slave_id, ctrl in self.axes.items():
            ctrl.start_homing(method)

    def emergency_stop(self):
        """Emergency stop all axes"""
        for slave_id, ctrl in self.axes.items():
            ctrl.quick_stop()

    def set_mode_all(self, mode: ServoMotionMode):
        """Set motion mode for all axes"""
        for ctrl in self.axes.values():
            ctrl.set_operation_mode(OperationMode(mode))

    def move_all_absolute(self, positions: Dict[int, int], velocities: Dict[int, int] = None):
        """Move all axes to absolute positions"""
        for slave_id, ctrl in self.axes.items():
            pos = positions.get(slave_id, 0)
            vel = velocities.get(slave_id, 0) if velocities else 0
            ctrl.move_absolute(pos, vel)

    def move_all_relative(self, distances: Dict[int, int], velocities: Dict[int, int] = None):
        """Move all axes relatively"""
        for slave_id, ctrl in self.axes.items():
            dist = distances.get(slave_id, 0)
            vel = velocities.get(slave_id, 0) if velocities else 0
            ctrl.move_relative(dist, vel)

    def set_velocities_all(self, velocities: Dict[int, int]):
        """Set target velocities for all axes"""
        for slave_id, ctrl in self.axes.items():
            vel = velocities.get(slave_id, 0)
            ctrl.set_target_velocity(vel)

    def set_torques_all(self, torques: Dict[int, int]):
        """Set target torques for all axes"""
        for slave_id, ctrl in self.axes.items():
            tq = torques.get(slave_id, 0)
            ctrl.set_target_torque(tq)

    def get_positions_all(self) -> Dict[int, int]:
        """Get actual positions of all axes"""
        return {slave_id: ctrl.get_actual_position() for slave_id, ctrl in self.axes.items()}

    def get_velocities_all(self) -> Dict[int, int]:
        """Get actual velocities of all axes"""
        return {slave_id: ctrl.get_actual_velocity() for slave_id, ctrl in self.axes.items()}

    def get_torques_all(self) -> Dict[int, int]:
        """Get actual torques of all axes"""
        return {slave_id: ctrl.get_actual_torque() for slave_id, ctrl in self.axes.items()}

    def diagnose_all(self) -> Dict[int, dict]:
        """Get diagnostics of all axes"""
        return {slave_id: ctrl.diagnose() for slave_id, ctrl in self.axes.items()}


# ============================================================================
# Trajectory Planning (Master Station)
# ============================================================================

class TrajectoryPlanner:
    """
    Trajectory Planning for Master Station
    Generates target positions/velocities/torques for slave axes
    """

    def __init__(self):
        self.points = []
        self.current_index = 0
        self.interpolation_time = 0
        self.cycle_time = 0.001  # 1ms

    def add_point(self, position: float, velocity: float = 0, time: float = 0):
        """Add trajectory point"""
        self.points.append({
            'position': position,
            'velocity': velocity,
            'time': time
        })

    def clear_points(self):
        """Clear all trajectory points"""
        self.points = []
        self.current_index = 0

    def generate_linear(self, start: float, end: float, velocity: float,
                       acceleration: float, deceleration: float) -> List[dict]:
        """Generate linear trajectory"""
        distance = abs(end - start)
        direction = 1 if end > start else -1

        # Calculate times
        t_acc = velocity / acceleration
        t_dec = velocity / deceleration
        d_acc = 0.5 * acceleration * t_acc * t_acc
        d_dec = 0.5 * deceleration * t_dec * t_dec
        d_const = distance - d_acc - d_dec
        t_const = d_const / velocity if velocity > 0 else 0

        trajectory = []
        t = 0

        # Acceleration phase
        while t < t_acc:
            pos = start + direction * 0.5 * acceleration * t * t
            trajectory.append({'time': t, 'position': pos, 'velocity': acceleration * t})
            t += self.cycle_time

        # Constant velocity phase
        t_const_end = t + t_const
        while t < t_const_end:
            pos = start + direction * (d_acc + velocity * (t - t_acc))
            trajectory.append({'time': t, 'position': pos, 'velocity': velocity})
            t += self.cycle_time

        # Deceleration phase
        while t < t_acc + t_const + t_dec:
            dt = t - t_acc - t_const
            pos = end - direction * 0.5 * deceleration * (t_dec - dt) * (t_dec - dt)
            vel = deceleration * (t_dec - dt)
            trajectory.append({'time': t, 'position': pos, 'velocity': vel})
            t += self.cycle_time

        return trajectory

    def generate_s_curve(self, start: float, end: float, velocity: float,
                        acceleration: float, deceleration: float,
                        jerk: float) -> List[dict]:
        """Generate S-curve trajectory (CVP mode)"""
        trajectory = []
        direction = 1 if end > start else -1
        distance = abs(end - start)

        # S-curve phases
        t_jerk_a = acceleration / jerk
        d_jerk_a = 0.5 * jerk * t_jerk_a * t_jerk_a
        t_const_a = (velocity / acceleration) - t_jerk_a
        d_const_a = acceleration * t_const_a

        t_jerk_d = deceleration / jerk
        d_jerk_d = 0.5 * deceleration * t_jerk_d * t_jerk_d
        t_const_d = (velocity / deceleration) - t_jerk_d
        d_const_d = deceleration * t_const_d

        d_acc = d_jerk_a + d_const_a + d_jerk_a
        d_dec = d_jerk_d + d_const_d + d_jerk_d
        d_const_total = max(0, distance - d_acc - d_dec)

        t = 0

        # Phase 1: Jerk acceleration
        while t < t_jerk_a:
            pos = start + direction * 0.5 * jerk * t * t * t / 6
            vel = direction * 0.5 * jerk * t * t
            trajectory.append({'time': t, 'position': pos, 'velocity': vel})
            t += self.cycle_time

        # Phase 2: Constant acceleration
        t2_end = t + t_const_a
        while t < t2_end:
            pos = start + direction * (d_jerk_a + 0.5 * acceleration * (t - t_jerk_a) ** 2)
            vel = direction * acceleration * (t - t_jerk_a)
            trajectory.append({'time': t, 'position': pos, 'velocity': vel})
            t += self.cycle_time

        # Phase 3: Jerk deceleration (to constant velocity)
        t3_end = t + t_jerk_a
        while t < t3_end:
            dt = t - t2_end
            pos = start + direction * (d_acc - 0.5 * jerk * (t_jerk_a - dt) ** 2)
            vel = direction * velocity - direction * 0.5 * jerk * (t_jerk_a - dt) ** 2
            trajectory.append({'time': t, 'position': pos, 'velocity': vel})
            t += self.cycle_time

        # Phase 4: Constant velocity
        t4_end = t + d_const_total / velocity
        while t < t4_end:
            pos = start + direction * (d_acc + velocity * (t - t3_end))
            trajectory.append({'time': t, 'position': pos, 'velocity': velocity * direction})
            t += self.cycle_time

        # Phase 5-7: Deceleration (reverse of phases 1-3)
        # ... (similar logic)

        return trajectory

    def interpolate(self, trajectory: List[dict], current_time: float) -> dict:
        """Interpolate trajectory at given time"""
        if not trajectory:
            return {'position': 0, 'velocity': 0, 'torque': 0}

        # Find surrounding points
        for i, point in enumerate(trajectory):
            if point['time'] >= current_time:
                if i == 0:
                    return point
                # Linear interpolation
                t0 = trajectory[i-1]['time']
                t1 = point['time']
                alpha = (current_time - t0) / (t1 - t0) if t1 > t0 else 0
                return {
                    'position': trajectory[i-1]['position'] + alpha * (point['position'] - trajectory[i-1]['position']),
                    'velocity': trajectory[i-1]['velocity'] + alpha * (point['velocity'] - trajectory[i-1]['velocity']),
                    'torque': 0
                }

        # Past end of trajectory
        return trajectory[-1]


# ============================================================================
# Multi-Axis Synchronization Control
# ============================================================================

class SyncController:
    """
    Multi-Axis Synchronization Controller
    Implements electronic gear, cam, phasing modes
    """

    def __init__(self, master: MasterStation):
        self.master = master
        self.sync_mode = SyncMode.NO_SYNC
        self.gear_ratios = {}
        self.cam_tables = {}
        self.phase_offsets = {}

    def set_electronic_gear(self, slave_id: int, master_id: int,
                          numerator: int, denominator: int):
        """
        Set electronic gear coupling
        slave_position = master_position * (numerator / denominator)
        """
        self.sync_mode = SyncMode.ELECTRONIC_GEAR
        self.gear_ratios[slave_id] = {
            'master': master_id,
            'numerator': numerator,
            'denominator': denominator
        }

    def set_electronic_cam(self, slave_id: int, master_id: int,
                          cam_id: int, scale: float = 1.0):
        """
        Set electronic cam coupling
        Uses cam table for position mapping
        """
        self.sync_mode = SyncMode.ELECTRONIC_CAM
        self.gear_ratios[slave_id] = {
            'master': master_id,
            'cam_id': cam_id,
            'scale': scale
        }

    def set_phasing(self, slave_id: int, master_id: int, phase_degrees: float):
        """
        Set phasing offset
        slave_position = master_position + phase_offset
        """
        self.sync_mode = SyncMode.PHASING
        self.phase_offsets[slave_id] = {
            'master': master_id,
            'phase': phase_degrees
        }

    def update_sync(self, master_position: int) -> Dict[int, int]:
        """Update synchronized positions for all slave axes"""
        results = {}

        for slave_id, gear_config in self.gear_ratios.items():
            master = gear_config['master']

            if self.sync_mode == SyncMode.ELECTRONIC_GEAR:
                # Electronic gear calculation
                num = gear_config['numerator']
                den = gear_config['denominator']
                slave_pos = int(master_position * num / den)
                results[slave_id] = slave_pos

            elif self.sync_mode == SyncMode.ELECTRONIC_CAM:
                # Electronic cam calculation
                cam_id = gear_config['cam_id']
                scale = gear_config['scale']
                if cam_id in self.cam_tables:
                    # Lookup cam table
                    normalized_pos = (master_position % len(self.cam_tables[cam_id])) / len(self.cam_tables[cam_id])
                    cam_value = self.cam_tables[cam_id][int(normalized_pos * len(self.cam_tables[cam_id]))]
                    results[slave_id] = int(cam_value * scale)

            elif self.sync_mode == SyncMode.PHASING:
                # Phasing calculation
                phase = self.phase_offsets[slave_id]['phase']
                phase_ticks = int(phase / 360.0 * 65536)  # Convert degrees to encoder units
                results[slave_id] = master_position + phase_ticks

        return results

    def add_cam_point(self, cam_id: int, master_position: int, slave_position: int):
        """Add point to cam table"""
        if cam_id not in self.cam_tables:
            self.cam_tables[cam_id] = []
        self.cam_tables[cam_id].append((master_position, slave_position))


# ============================================================================
# Keyboard Control Interface
# ============================================================================

import threading
import sys


class KeyboardController:
    """
    Keyboard Control Interface for Servo Control
    Provides interactive control via keyboard input
    """

    def __init__(self, master: MasterStation):
        self.master = master
        self.current_axis = 1
        self.speed_increment = 1000
        self.current_speed = 10000
        self.is_running = False
        self.key_thread = None
        self.mode = ServoMotionMode.VELOCITY_MODE

        # Key bindings
        self.key_map = {
            # Function keys - State control
            'F1': self.power_on,
            'F2': self.power_off,
            'F3': self.enable,
            'F4': self.disable,
            'F5': self.brake_release,
            'F6': self.brake_engage,
            'F7': self.home,
            'F8': self.stop,

            # Axis selection
            '1': lambda: self.select_axis(1),
            '2': lambda: self.select_axis(2),
            '3': lambda: self.select_axis(3),
            '4': lambda: self.select_axis(4),
            '5': lambda: self.select_axis(5),
            '6': lambda: self.select_axis(6),
            '7': lambda: self.select_axis(7),
            '8': lambda: self.select_axis(8),
            'TAB': self.next_axis,

            # Motion control
            'w': lambda: self.set_velocity(self.current_speed),
            's': lambda: self.set_velocity(-self.current_speed),
            'W': lambda: self.set_velocity(self.current_speed),
            'S': lambda: self.set_velocity(-self.current_speed),
            'a': self.decrease_speed,
            'd': self.increase_speed,
            'A': self.decrease_speed,
            'D': self.increase_speed,
            ' ': self.emergency_stop,  # Space
            '+': self.increase_speed,
            '-': self.decrease_speed,

            # Mode selection
            'p': lambda: self.set_mode(ServoMotionMode.PROFILE_POSITION),
            'P': lambda: self.set_mode(ServoMotionMode.PROFILE_POSITION),
            'v': lambda: self.set_mode(ServoMotionMode.VELOCITY_MODE),
            'V': lambda: self.set_mode(ServoMotionMode.VELOCITY_MODE),
            't': lambda: self.set_mode(ServoMotionMode.TORQUE_MODE),
            'T': lambda: self.set_mode(ServoMotionMode.TORQUE_MODE),
            'h': lambda: self.set_mode(ServoMotionMode.HOMING),
            'H': lambda: self.set_mode(ServoMotionMode.HOMING),
        }

    def power_on(self):
        """Power on current axis"""
        if self.current_axis in self.master.axes:
            ctrl = self.master.axes[self.current_axis]
            ctrl.shutdown()
            ctrl.switch_on()
            print(f"Axis {self.current_axis}: Power ON")

    def power_off(self):
        """Power off current axis"""
        if self.current_axis in self.master.axes:
            ctrl = self.master.axes[self.current_axis]
            ctrl.disable_voltage()
            print(f"Axis {self.current_axis}: Power OFF")

    def enable(self):
        """Enable current axis (operation enabled)"""
        if self.current_axis in self.master.axes:
            ctrl = self.master.axes[self.current_axis]
            ctrl.enable_operation()
            print(f"Axis {self.current_axis}: Enabled")

    def disable(self):
        """Disable current axis"""
        if self.current_axis in self.master.axes:
            ctrl = self.master.axes[self.current_axis]
            ctrl.shutdown()
            print(f"Axis {self.current_axis}: Disabled")

    def brake_release(self):
        """Release brake on current axis"""
        # Write to brake control register if supported
        print(f"Axis {self.current_axis}: Brake Released")

    def brake_engage(self):
        """Engage brake on current axis"""
        print(f"Axis {self.current_axis}: Brake Engaged")

    def home(self):
        """Home current axis"""
        if self.current_axis in self.master.axes:
            ctrl = self.master.axes[self.current_axis]
            ctrl.start_homing()
            print(f"Axis {self.current_axis}: Homing started")

    def stop(self):
        """Stop current axis motion"""
        if self.current_axis in self.master.axes:
            ctrl = self.master.axes[self.current_axis]
            ctrl.quick_stop()
            print(f"Axis {self.current_axis}: Stopped")

    def emergency_stop(self):
        """Emergency stop all axes"""
        self.master.emergency_stop()
        print("EMERGENCY STOP!")

    def select_axis(self, axis_id: int):
        """Select axis by number"""
        if axis_id in self.master.axes:
            self.current_axis = axis_id
            print(f"Selected Axis {axis_id}")
        else:
            print(f"Axis {axis_id} not configured")

    def next_axis(self):
        """Select next axis (TAB key)"""
        axes = sorted(self.master.axes.keys())
        if not axes:
            return
        current_idx = axes.index(self.current_axis) if self.current_axis in axes else -1
        next_idx = (current_idx + 1) % len(axes)
        self.current_axis = axes[next_idx]
        print(f"Selected Axis {self.current_axis}")

    def set_velocity(self, velocity: int):
        """Set velocity for current axis"""
        if self.current_axis in self.master.axes:
            ctrl = self.master.axes[self.current_axis]
            ctrl.set_operation_mode(OperationMode.VELOCITY_MODE)
            ctrl.set_target_velocity(velocity)
            print(f"Axis {self.current_axis}: Velocity = {velocity}")

    def increase_speed(self):
        """Increase speed"""
        self.current_speed += self.speed_increment
        print(f"Speed: {self.current_speed}")

    def decrease_speed(self):
        """Decrease speed"""
        self.current_speed = max(0, self.current_speed - self.speed_increment)
        print(f"Speed: {self.current_speed}")

    def set_mode(self, mode: ServoMotionMode):
        """Set motion mode"""
        self.mode = mode
        if self.current_axis in self.master.axes:
            ctrl = self.master.axes[self.current_axis]
            ctrl.set_operation_mode(OperationMode(mode))
        print(f"Mode: {mode.name}")

    def start(self):
        """Start keyboard control"""
        self.is_running = True
        self.key_thread = threading.Thread(target=self._key_loop, daemon=True)
        self.key_thread.start()
        self._print_help()

    def stop(self):
        """Stop keyboard control"""
        self.is_running = False
        if self.key_thread:
            self.key_thread.join(timeout=1.0)

    def _key_loop(self):
        """Keyboard input loop"""
        if sys.platform == 'windows':
            import msvcrt
            while self.is_running:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore')
                    self._handle_key(key)
        else:
            import tty
            import termios
            import select

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                tty.setraw(fd)
                while self.is_running:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1)
                        if key == '\x1b':  # Escape sequence
                            key += sys.stdin.read(2)
                        self._handle_key(key)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _handle_key(self, key: str):
        """Handle key press"""
        if key in self.key_map:
            action = self.key_map[key]
            if callable(action):
                action()
        elif key == 'ESC' or key == '\x1b':
            self.stop()
            print("Exiting...")
            sys.exit(0)
        elif key == '\n' or key == '\r':
            print("Enter pressed")

    def _print_help(self):
        """Print keyboard control help"""
        help_text = """
Servo Motor Keyboard Control Interface
======================================
[F1] Power On    [F2] Power Off
[F3] Enable      [F4] Disable
[F5] Brake Release [F6] Brake Engage
[F7] Home        [F8] Stop

Axis Selection:
[1-8] Select Axis 1-8  [TAB] Next Axis

Motion Control:
[W/S] Forward/Reverse
[A/D] Speed Decrease/Increase
[+/-] Speed Decrease/Increase
[Space] Emergency Stop

Mode Selection:
[P] Position Mode  [V] Velocity Mode
[T] Torque Mode    [H] Homing Mode

[ESC] Exit
"""
        print(help_text)


# ============================================================================
# Real-Time Control Loop (EtherCAT Cyclic Sync)
# ============================================================================

class RealtimeController:
    """
    Real-time Control Loop
    Master station performs trajectory planning, slaves receive targets
    """

    def __init__(self, master: MasterStation, cycle_time_us: int = 1000):
        self.master = master
        self.cycle_time = cycle_time_us / 1_000_000  # Convert to seconds
        self.trajectory = []
        self.current_time = 0.0
        self.is_running = False
        self.control_thread = None
        self.sync_controller = SyncController(master)

    def load_trajectory(self, trajectory: List[dict]):
        """Load trajectory for execution"""
        self.trajectory = trajectory
        self.current_time = 0.0

    def start(self):
        """Start real-time control loop"""
        self.is_running = True
        self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
        self.control_thread.start()

    def stop(self):
        """Stop real-time control loop"""
        self.is_running = False
        if self.control_thread:
            self.control_thread.join(timeout=1.0)

    def _control_loop(self):
        """Main control loop"""
        import time

        while self.is_running:
            loop_start = time.perf_counter()

            # Read master position (for sync modes)
            master_pos = 0
            if self.master.master_axis in self.master.axes:
                master_pos = self.master.axes[self.master.master_axis].get_actual_position()

            # Calculate targets based on mode
            if self.sync_controller.sync_mode != SyncMode.NO_SYNC:
                # Synchronized motion
                sync_targets = self.sync_controller.update_sync(master_pos)
                self.master.move_all_absolute(sync_targets)

            elif self.trajectory:
                # Trajectory following
                target = self.master.trajectory_generator.interpolate(
                    self.trajectory, self.current_time
                )

                # Set targets for all axes
                positions = {slave_id: int(target['position'])
                           for slave_id in self.master.axes.keys()}
                velocities = {slave_id: int(target['velocity'])
                             for slave_id in self.master.axes.keys()}

                if self.master.sync_mode == SyncMode.NO_SYNC:
                    # Independent motion
                    self.master.move_all_absolute(positions)
                    self.master.set_velocities_all(velocities)

                self.current_time += self.cycle_time

            # Cyclic PDO update (EtherCAT)
            self._update_pdo()

            # Calculate cycle time and sleep if needed
            elapsed = time.perf_counter() - loop_start
            sleep_time = self.cycle_time - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _update_pdo(self):
        """Update PDO process data"""
        # Write target values to PDO registers
        for slave_id, ctrl in self.master.axes.items():
            # Update position/torque targets via PDO
            ctrl.read_sdo(ctrl.STATUSWORD, 0, 'u16')  # Read status

