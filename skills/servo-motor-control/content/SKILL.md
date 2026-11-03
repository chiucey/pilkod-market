---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 91aacc300c0a35fd8192856985d5c782
    PropagateID: 91aacc300c0a35fd8192856985d5c782
    ReservedCode1: 3046022100cfa096f8e612e90e82b727f113a11a04633a682cf1b5d403e5a4d56ddfdc2125022100af671b032d70dccaaa2a2d2b4afdd6eb3f1f2013e1107e9b13f4bbd083120d60
    ReservedCode2: 3045022100eadf39b52e9049acb288c2586072ab133a9b71f68cdf6e1616676e7c23900781022019cd7ae79a6992d6860d33d4c5b1990c98889ad132b03d2b1579ba8cd72a03cc
description: Professional skill for servo motor control. Use when users ask to control servo motors, configure CIA402/CANopen/CANopenFD/EtherCAT protocols, set motor parameters, execute motion commands, diagnose servo system faults, or develop servo applications across platforms (Windows/Ubuntu/Embedded).
name: servo-motor-control
---

# Servo Motor Control Skill

## Trigger Conditions

Activate this skill when user requests:
- Servo motor control or programming
- CIA402 (CANopen over EtherCAT) protocol configuration
- CANopen or CANopenFD communication
- EtherCAT bus control
- Motor parameter settings and tuning
- Motion control commands (position/velocity/torque modes)
- Servo system fault diagnosis
- Cross-platform servo development (Windows/Linux/Embedded)

## Core Features

### 1. Protocol Support

| Protocol | Description | Typical Application |
|----------|-------------|---------------------|
| CIA402 | CANopen device profile for motion control | EtherCAT motion control |
| CANopen | Classic CAN bus protocol | Industrial automation |
| CANopenFD | High-speed CAN bus protocol | Large data transfer |
| EtherCAT | Ethernet Control Automation Technology | High-speed real-time control |

### 2. Master Station Real-Time Control

The master station performs real-time trajectory planning and distributes target values to slave axes.

```
+------------------+     +------------------+     +------------------+
|  Master Station  | --> |  Trajectory      | --> |  Multi-Axis      |
|  (Real-time)     |     |  Planner         |     |  Synchronization |
+------------------+     +------------------+     +------------------+
        |                       |                        |
        v                       v                        v
+------------------+     +------------------+     +------------------+
|  EtherCAT Bus    | --> |  Target Values   | --> |  Slave Axes      |
|  (PDO Transfer)  |     |  (CVP/CVS/CVT)  |     |  (CIA402)        |
+------------------+     +------------------+     +------------------+
```

### 3. Motion Modes (CVP/CVS/CVT/CSP/CSV/CST)

| Mode | Abbreviation | Description | Object Dictionary |
|------|--------------|-------------|------------------|
| Profile Position | CVP | Position profile mode with S-curve | 0x6060 = 1 |
| Profile Velocity | CVS | Velocity profile mode | 0x6060 = 2 |
| Profile Torque | CVT | Torque profile mode | 0x6060 = 4 |
| Cyclic Synchronous Position | CSP | Cyclic position mode | 0x6060 = 8 |
| Cyclic Synchronous Velocity | CSV | Cyclic velocity mode | 0x6060 = 9 |
| Cyclic Synchronous Torque | CST | Cyclic torque mode | 0x6060 = 10 |

### 4. Multi-Axis Synchronization Control

| Sync Mode | Description | Use Case |
|-----------|-------------|----------|
| Electronic Gear | Master-slave ratio coupling | Conveyor systems |
| Electronic Cam | Position-based cam profiling | Packaging machines |
| Phasing | Phase offset control | Robotic arms |
| Gearing with Phase | Speed ratio + phase sync | Printing machines |

### 5. Keyboard Control Interface

```
+---------------------------------------------------+
|  Servo Control Keyboard Interface                  |
+---------------------------------------------------+
|  [F1] Power On    [F2] Power Off                 |
|  [F3] Enable      [F4] Disable                   |
|  [F5] Brake Release [F6] Brake Engage            |
|  [F7] Home        [F8] Stop                      |
+---------------------------------------------------+
|  Axis Selection:                                  |
|  [1-8] Select Axis  [TAB] Next Axis             |
+---------------------------------------------------+
|  Motion Control:                                  |
|  [W/S] Forward/Reverse  [A/D] Left/Right        |
|  [+/-] Speed Increase/Decrease                  |
|  [Space] Emergency Stop                           |
+---------------------------------------------------+
|  Mode Selection:                                  |
|  [P] Position Mode  [V] Velocity Mode            |
|  [T] Torque Mode   [H] Homing Mode              |
+---------------------------------------------------+
|  [ESC] Exit       [Enter] Confirm                 |
+---------------------------------------------------+
```

### 6. Platform Adaptation

```python
# Cross-platform abstraction layer
class ServoPlatform:
    """Platform abstraction - Windows/Linux/Embedded support"""

    def __init__(self, platform: str):
        self.platform = platform.lower()

    def initialize(self):
        if self.platform in ['windows', 'win32']:
            return self._init_windows()
        elif self.platform in ['linux', 'ubuntu', 'debian']:
            return self._init_linux()
        elif self.platform in ['embedded', 'rtos', 'arm', 'cortex']:
            return self._init_embedded()
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")
```

### 3. CIA402 State Machine

```
                    +-----------------+
                    |   Not Ready to  |
                    |    Switch On    |
                    +--------+--------+
                             |
                    +--------v--------+
                    |   Switch On     |
                    |   Disabled      |
                    +--------+--------+
                             |
            +----------------+----------------+
            |                                 |
   +--------v--------+               +--------v--------+
   |    Ready to      |               |   Switch On    |
   |    Switch On     |               |   Disabled     |
   +--------+--------+               +--------+--------+
            |                                 |
   +--------v--------+               +--------v--------+
   |     Enabled      |<------------+|    Operation   |
   |    (Operable)    |   Abort      |    Enabled     |
   +--------+--------+   Fault      +--------+--------+
            |                                 |
   +--------v--------+               +--------v--------+
   |   Quick Stop    |               |   Fault         |
   |   (Quick Stop)  |               |   Reaction      |
   +--------+--------+               +--------+--------+
            |                                 |
            +----------------+----------------+
                             |
                    +--------v--------+
                    |      Fault       |
                    |   (Fault)        |
                    +--------+--------+
```

### 4. Motion Modes

| Mode | Object Dictionary | Description |
|------|-------------------|-------------|
| Position Mode | 0x6060 = 1 | Profile Position mode |
| Velocity Mode | 0x6060 = 2 | Profile Velocity mode |
| Torque Mode | 0x6060 = 4 | Torque Mode |
| Homing Mode | 0x6060 = 6 | Homing Mode |
| Interpolated Mode | 0x6060 = 7 | Interpolated Position Mode |

## Implementation Workflow

### Phase 1: Environment Detection & Initialization

```python
def detect_and_init(platform_hint: str = None) -> ServoController:
    """Detect platform and initialize appropriate driver"""
    import platform
    import sys

    if platform_hint:
        target = platform_hint
    else:
        system = platform.system().lower()
        if 'windows' in system:
            target = 'windows'
        elif 'linux' in system:
            target = 'linux'
        else:
            target = 'embedded'

    # Load corresponding driver
    if target == 'windows':
        from .drivers.windows import WindowsCANInterface
        from .drivers.ethercat_windows import IgHDriver
        return ServoController(WindowsCANInterface(), IgHDriver())
    elif target == 'linux':
        from .drivers.linux import LinuxSocketCAN
        from .drivers.ethercat_linux import IgHDriver
        return ServoController(LinuxSocketCAN(), IgHDriver())
    else:
        from .drivers.embedded import EmbeddedCAN
        from .drivers.ethercat_embedded import ECATDriver
        return ServoController(EmbeddedCAN(), ECATDriver())
```

### Phase 2: Protocol Configuration

```python
class CIA402Controller:
    """CIA402 standard servo controller"""

    CONTROLWORD = 0x6040
    STATUSWORD = 0x6041
    MODES_OF_OPERATION = 0x6060
    POSITION_ACTUAL = 0x6064
    POSITION_DEMAND = 0x6062
    VELOCITY_ACTUAL = 0x606C
    TORQUE_ACTUAL = 0x6077

    def set_position_mode(self, profile_velocity: int, profile_acceleration: int):
        """Set position mode"""
        self.write_object(0x6060, 0, 1)  # Position mode
        self.write_object(0x6081, 0, profile_velocity)
        self.write_object(0x6083, 0, profile_acceleration)

    def move_to_position(self, target: int, absolute: bool = True):
        """Execute position move"""
        controlword = 0x000F if absolute else 0x001F
        self.write_object(self.CONTROLWORD, 0, controlword)
        self.write_object(0x607A, 0, target)
```

### Phase 3: Motion Control

```python
async def execute_motion(ctrl: CIA402Controller, trajectory: list):
    """Execute trajectory motion"""
    for point in trajectory:
        # Set target position
        await ctrl.set_target_position(point['position'])
        await ctrl.set_target_velocity(point.get('velocity', 0))
        await ctrl.set_target_torque(point.get('torque', 0))

        # Start motion
        await ctrl.start_motion()

        # Wait for target reached
        while not await ctrl.is_target_reached():
            await asyncio.sleep(0.001)

        # Record actual position
        actual = await ctrl.get_actual_position()
        print(f"Target: {point['position']}, Actual: {actual}")
```

## Cross-Platform Driver Architecture

```
+-------------------------------------------------------------+
|                    Application Layer                         |
+-------------------------------------------------------------+
|                  CIA402 State Machine (CIA402 FSM)           |
+------------------+------------------+-------------------------+
|  CANopen         |  CANopenFD       |  EtherCAT (CIA402)       |
+------------------+------------------+-------------------------+
|                 Protocol Abstraction Layer                   |
+------------------+------------------+-------------------------+
| Windows Driver   | Linux Driver     | Embedded Driver          |
| (PCAN/Kvaser)    | (SocketCAN)      | (CANable/CAN232)         |
+------------------+------------------+-------------------------+
```

## Error Diagnosis

### Common Error Codes (CIA402)

| Error Code | Meaning | Handling |
|------------|---------|----------|
| 0x0001 | Initialization failed | Check hardware connection |
| 0x0002 | SDO failed | Check SDO configuration |
| 0x0004 | Hardware fault | Motor or encoder fault |
| 0x0008 | Overcurrent | Check motor parameters |
| 0x0010 | Overvoltage | Check power supply |
| 0x0020 | Undervoltage | Check power supply |
| 0x0040 | Overtemperature | Check cooling system |

### Diagnostic Commands

```python
def diagnose_servo(ctrl: CIA402Controller) -> dict:
    """Complete diagnostic routine"""
    status = ctrl.get_status_word()
    error = ctrl.get_error_register()

    return {
        'status': {
            'ready_to_switch_on': bool(status & 0x0001),
            'switched_on': bool(status & 0x0002),
            'operation_enabled': bool(status & 0x0004),
            'fault': bool(status & 0x0008),
            'voltage_enabled': bool(status & 0x0010),
            'quick_stop': bool(status & 0x0020),
            'switch_on disabled': bool(status & 0x0040),
            'warning': bool(status & 0x0080),
        },
        'error_register': hex(error),
        'actual_position': ctrl.get_actual_position(),
        'actual_velocity': ctrl.get_actual_velocity(),
        'actual_torque': ctrl.get_actual_torque(),
    }
```

## Output Format

When skill completes, return:
1. **Control Code** - Complete runnable servo control code
2. **Configuration Files** - Motor parameters and PDO mapping configuration
3. **Diagnostic Scripts** - Diagnostic tools for troubleshooting

## Quality Checklist

- [ ] Code supports at least 2 protocols (CANopen/EtherCAT)
- [ ] Include Windows/Linux/Embedded platform adaptation
- [ ] Implement CIA402 state machine
- [ ] Include complete error handling
- [ ] Provide diagnostic tools
