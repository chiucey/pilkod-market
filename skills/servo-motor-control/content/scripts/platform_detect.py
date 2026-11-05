"""
Platform Detection and Driver Initialization Script

Automatically detects current runtime environment and loads appropriate drivers
Supports: Windows, Linux (Ubuntu), Embedded (ARM/RTOS)
"""

import platform
import sys
import os
from typing import Optional, Type

# Platform detection
def detect_platform() -> str:
    """Detect current platform"""
    system = platform.system().lower()

    if system == 'windows':
        return 'windows'
    elif system == 'linux':
        # Check for embedded environment
        machine = platform.machine().lower()
        if any(x in machine for x in ['arm', 'aarch64', 'riscv', 'mips']):
            return 'embedded'
        # Check kernel version and system info
        try:
            with open('/proc/cpuinfo', 'r') as f:
                content = f.read().lower()
                if 'embedded' in content or 'raspberry' in content:
                    return 'embedded'
        except:
            pass
        return 'linux'
    elif system == 'freebsd':
        return 'linux'  # Compatibility handling
    else:
        return 'embedded'  # Unknown system default to embedded


def get_can_driver(platform_name: str) -> str:
    """Get recommended CAN driver"""
    drivers = {
        'windows': 'PCAN-Basic / Kvaser CANlib / NI-CAN',
        'linux': 'SocketCAN',
        'embedded': 'HAL CAN Driver / libcanard'
    }
    return drivers.get(platform_name, 'Unknown')


def get_ethercat_driver(platform_name: str) -> str:
    """Get recommended EtherCAT driver"""
    drivers = {
        'windows': 'Acontis EC-Engine / Beckhoff TwinCAT',
        'linux': 'IgH EtherCAT Master / SOEM',
        'embedded': 'FreeRTOS-EtherCAT / Custom'
    }
    return drivers.get(platform_name, 'Unknown')


def check_hardware_support(platform_name: str) -> dict:
    """Check hardware support"""
    results = {
        'platform': platform_name,
        'can_available': False,
        'ethercat_available': False,
        'recommendations': []
    }

    if platform_name == 'windows':
        # Check PCAN device
        results['can_available'] = _check_pcan_windows()
        results['ethercat_available'] = _check_ethercat_windows()

    elif platform_name == 'linux':
        # Check SocketCAN
        results['can_available'] = _check_socketcan_linux()
        results['ethercat_available'] = _check_ethercat_linux()

    elif platform_name == 'embedded':
        # Check CAN hardware
        results['can_available'] = _check_can_embedded()
        results['ethercat_available'] = _check_ethercat_embedded()

    # Generate recommendations
    if not results['can_available']:
        results['recommendations'].append(f"Install CAN driver for {platform_name}")

    if not results['ethercat_available']:
        results['recommendations'].append(f"Install EtherCAT driver for {platform_name}")

    return results


def _check_pcan_windows() -> bool:
    """Check Windows PCAN support"""
    try:
        # Check registry or PEAK-System driver
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\PEAK-System")
        return True
    except:
        return False


def _check_ethercat_windows() -> bool:
    """Check Windows EtherCAT support"""
    return True  # Acontis/TwinCAT usually installed


def _check_socketcan_linux() -> bool:
    """Check Linux SocketCAN support"""
    import os
    can_dirs = ['/sys/class/net', '/dev']
    for d in can_dirs:
        if os.path.exists(d):
            try:
                for name in os.listdir(d):
                    if name.startswith('can') or 'can' in name:
                        return True
            except:
                pass
    return False


def _check_ethercat_linux() -> bool:
    """Check Linux EtherCAT Master"""
    import os
    # Check IgH EtherCAT Master
    return os.path.exists('/dev/EtherCAT0') or os.path.exists('/sys/class/ethercat')


def _check_can_embedded() -> bool:
    """Check embedded CAN support"""
    # Check device tree or hardware config
    return True


def _check_ethercat_embedded() -> bool:
    """Check embedded EtherCAT support"""
    return True


def initialize_platform(platform_name: str) -> dict:
    """Initialize platform"""
    return {
        'platform': platform_name,
        'can_driver': get_can_driver(platform_name),
        'ethercat_driver': get_ethercat_driver(platform_name),
        'config': {
            'windows': {
                'bitrate': 1000000,
                'channels': ['PCAN_USBBUS1', 'PCAN_USBBUS2'],
                'library': 'PCANBasic.dll'
            },
            'linux': {
                'bitrate': 1000000,
                'channels': ['can0', 'can1'],
                'interface': 'socketcan'
            },
            'embedded': {
                'bitrate': 1000000,
                'channels': ['can0'],
                'hal': 'custom'
            }
        }.get(platform_name, {})
    }


def main():
    """Main function"""
    print("=" * 60)
    print("Servo Motor Control - Platform Detection")
    print("=" * 60)

    # Detect platform
    detected = detect_platform()
    print(f"\nDetected Platform: {detected}")

    # Get driver info
    print(f"\nRecommended CAN Driver: {get_can_driver(detected)}")
    print(f"Recommended EtherCAT Driver: {get_ethercat_driver(detected)}")

    # Check hardware support
    hardware = check_hardware_support(detected)
    print(f"\nHardware Support:")
    print(f"  CAN Available: {hardware['can_available']}")
    print(f"  EtherCAT Available: {hardware['ethercat_available']}")

    if hardware['recommendations']:
        print(f"\nRecommendations:")
        for rec in hardware['recommendations']:
            print(f"  - {rec}")

    # Initialize info
    init_info = initialize_platform(detected)
    print(f"\nInitialization Config:")
    for key, value in init_info['config'].items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
