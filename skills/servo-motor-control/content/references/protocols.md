---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: c7a55d97991472d9c3fd31ceb8344ea2
    PropagateID: c7a55d97991472d9c3fd31ceb8344ea2
    ReservedCode1: 3046022100875351f9a69dd937794953f8fb9f1a7dd857ef9d47f21b1b08de19a9c647f9fe022100d12d58b718e40ce6e17996dc5c23218f292f7ddf779b040181dccbc4fdb9f6ec
    ReservedCode2: 3045022100c5c12311e6bfa21bd4432b6bae34cdd3f15a21e5d1303044734d421061264a0902207ab47987630125ea833af82341b7204529db6ec1d018507a0db22f629263fd89
---

# Servo Motor Control Protocol Reference

## 1. CIA402 (CANopen over EtherCAT)

CIA402 is the CANopen device profile for motion control.

### 1.1 Object Dictionary

| Index | Object | Data Type | Description |
|-------|--------|-----------|-------------|
| 0x6040 | Controlword | UINT16 | Control word |
| 0x6041 | Statusword | UINT16 | Status word |
| 0x6060 | Modes of Operation | INT8 | Operation mode |
| 0x6061 | Modes of Operation Display | INT8 | Current mode display |
| 0x6062 | Position Demand Value | INT32 | Position demand value |
| 0x6063 | Position Actual Value | INT32 | Position actual value |
| 0x6064 | Position Actual Value | INT32 | Position actual (encoder) |
| 0x606C | Velocity Actual Value | INT32 | Velocity actual value |
| 0x6071 | Target Torque | INT16 | Target torque |
| 0x6072 | Max Torque | UINT16 | Maximum torque |
| 0x6077 | Torque Actual Value | INT16 | Torque actual value |
| 0x607A | Target Position | INT32 | Target position |
| 0x6081 | Profile Velocity | UINT32 | Profile velocity |
| 0x6083 | Profile Acceleration | UINT32 | Profile acceleration |
| 0x6084 | Profile Deceleration | UINT32 | Profile deceleration |
| 0x6098 | Homing Method | INT8 | Homing method |
| 0x6099 | Homing Speeds | UINT32[] | Homing speeds |

### 1.2 Controlword Bit Definition

```
Bit 15-8: Manufacturer specific
Bit 7:    Reserved
Bit 6:    0=Continue, 1=Pause
Bit 5:    0=Continue, 1=Select trajectory
Bit 4:    Incremental motion trigger
Bit 3:    0=Relative, 1=Absolute
Bit 2:    New setpoint
Bit 1:    Immediate effect
Bit 0:    Switch on/off
```

### 1.3 Statusword Bit Definition

```
Bit 15-14: Manufacturer specific
Bit 13:    Target position reached
Bit 12:    Following error active
Bit 11:    Setpoint acknowledged
Bit 10:    New setpoint available
Bit 9:     Internal limit active
Bit 8:     Positive software limit
Bit 7:     Negative software limit
Bit 6:     Reserved
Bit 5:     Pause
Bit 4:     Drive follows command value
Bit 3:     Fault
Bit 2:     Voltage enabled
Bit 1:     Switched on
Bit 0:     Ready to switch on
```

### 1.4 CIA402 State Transitions

| Current State | Target State | Controlword | Condition |
|---------------|-------------|-------------|-----------|
| Initialization | Not Ready to Switch On | - | Power on complete |
| Not Ready to Switch On | Switch On Disabled | 0x00 | Initialization complete |
| Switch On Disabled | Ready to Switch On | 0x80 | Enable safe stop |
| Ready to Switch On | Switched On | 0x81 | Enable power |
| Switched On | Operation Enabled | 0x87 | Fault reset |
| Operation Enabled | Quick Stop Active | 0x0B | Quick stop triggered |
| Quick Stop Active | Operation Enabled | 0x07 | Stop complete |
| Any | Fault | - | Fault detected |

## 2. CANopen Protocol

### 2.1 Communication Objects

#### PDO (Process Data Object)
- Used for real-time data exchange
- Transmission type: Synchronous/Asynchronous
- Maximum 8 bytes (CAN) or 64 bytes (CANFD)

#### SDO (Service Data Object)
- Used for parameter configuration
- Client-Server mode
- Expedited and segmented transfer

#### NMT (Network Management)
- Node state control
- Start/Stop/Reset

### 2.2 CANopen Frame Format

```
CAN Standard Frame (11-bit ID):
| COB-ID | DLC | Data[0-8] |

CAN FD Frame (11-bit or 29-bit ID):
| COB-ID | DLC | Data[0-64] |
```

### 2.3 Predefined Connection Set

| Function | COB-ID |
|----------|--------|
| NMT | 0x000 |
| SYNC | 0x080 |
| Emergency | 0x080-0x0FF |
| PDO1 Transmit | 0x180-0x1FF |
| PDO1 Receive | 0x200-0x27F |
| PDO2 Transmit | 0x280-0x2FF |
| PDO2 Receive | 0x300-0x37F |
| SDO Transmit | 0x580-0x5FF |
| SDO Receive | 0x600-0x67F |
| Heartbeat | 0x700-0x77F |

## 3. CANopenFD Protocol

### 3.1 CANFD vs CAN Differences

| Feature | CAN | CANFD |
|---------|-----|-------|
| Data field | Max 8 bytes | Max 64 bytes |
| Bit rate | 1Mbps | 5-8Mbps |
| Frame format | Classic | Classic+FD |
| CRC | 15-bit | 17/21-bit |

### 3.2 CANFD Frame Format

```
ISO CAN FD Frame:
| SOF | ID | RTR | IDE | FDF | BRS | ESI | DLC | Data | CRC | ACK | EOF |
```

### 3.3 Extended PDO (EPDO)

CANFD supports larger PDO data fields:
- Can transmit complete trajectory data
- Supports multi-axis synchronized data
- Reduces bus occupation

## 4. EtherCAT Protocol

### 4.1 Frame Structure

```
Ethernet Frame:
| Dest MAC | Src MAC | EtherType | Data | FCS |
           └──────── EtherCAT Frame ────────┘
```

### 4.2 EtherCAT Data Link Layer

| Command | Description |
|---------|-------------|
| APRD | Auto Increment Read |
| APWR | Auto Increment Write |
| FPRD | Fixed Address Read |
| FPWR | Fixed Address Write |
| BRD | Broadcast Read |
| BWR | Broadcast Write |
| LRD | Logical Read |
| LWR | Logical Write |
| LRW | Logical Read Write |

### 4.3 PDO Mapping for CIA402

CIA402 object PDO mapping:
- RxPDO: Controlword, Target Position, Operation Mode
- TxPDO: Statusword, Actual Position, Actual Velocity

### 4.4 Sync Managers

| SM | Function |
|----|---------|
| SM0 | Mailbox output (Master to Slave) |
| SM1 | Mailbox input (Slave to Master) |
| SM2 | Process data output |
| SM3 | Process data input |

## 5. Platform-Specific Drivers

### 5.1 Windows Platform

Recommended drivers:
- PCAN-Basic API (PEAK-System)
- Kvaser CANLib
- NI-CAN

### 5.2 Linux Platform

Recommended drivers:
- SocketCAN (built-in)
- IgH EtherCAT Master
- SOEM (Simple Open EtherCAT Master)

### 5.3 Embedded Platform

Recommended libraries:
- libcanard (DroneCode/CANopen)
- CANopenSTM32
- FreeRTOS + CAN driver
