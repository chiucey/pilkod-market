---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 53b929bd48dc3bb2bf8dc10227491216
    PropagateID: 53b929bd48dc3bb2bf8dc10227491216
    ReservedCode1: 3045022017c4c98bb2d15305dec9ebe8d568b69e5cd20ac4f48f287bea5049383a9e3a6d022100a58da542cf3c7697ab1eeb710470306a11e205878eee6b80dfbdba651bac1abc
    ReservedCode2: 30450220063f432e5adee9aed9eb5d9b5f1c61096a3f6aec1c21ad001189c4e531c8c483022100c0080a9e0e1948afa4ab63bafcce0d3106a1744ada56362275c140a2dfa3265c
author: MiniMax Agent
description: Intelligent network topology generation skill supporting 100+ device types, arbitrary topology structures, natural language description, and multi-format output. Use when users need to create network architecture diagrams, data center topologies, enterprise network topologies, or cloud network architectures.
name: network-topology-generator
tags:
    - network
    - topology
    - architecture
    - drawio
    - xml-generation
    - visualization
version: 2.0.0
---

# Network Topology Generator

## Table of Contents

- [1. Quick Start](#1-quick-start)
- [2. Core Capabilities](#2-core-capabilities)
- [3. Device Library](#3-device-library)
- [4. Topology Description Language (TDL)](#4-topology-description-language-tdl)
- [5. Natural Language Topology Description](#5-natural-language-topology-description)
- [6. Topology Generator API](#6-topology-generator-api)
- [7. Smart Layout Engine](#7-smart-layout-engine)
- [8. Usage Workflows](#8-usage-workflows)
- [9. Reference Resources](#9-reference-resources)
- [10. FAQ](#10-faq)
- [11. Troubleshooting Guide](#11-troubleshooting-guide)

---

## 1. Quick Start

### 1.1 5-Minute Guide

This skill allows you to generate professional network topology diagrams through simple descriptions. Here are three quick-start methods:

**Method 1: Natural Language Description**

```
Input: Create a data center network with 2 core switches, 4 aggregation switches, 8 access switches, and 10 servers connected to each access switch

Output: Automatically generates complete draw.io XML code
```

**Method 2: Topology Description Language (TDL)**

```
Input: @tdl
topology datacenter {
  core: switch x2
  aggregation: switch x4
  access: switch x8
  servers: server x80 distributed
}
connect all
output: xml

Output: Generates complete XML code
```

**Method 3: API Call**

```python
from topology_generator import Generator

gen = Generator()
topology = {
    "type": "spine_leaf",
    "spine": 2,
    "leaf": 4,
    "servers_per_leaf": 10
}
xml = gen.generate(topology, format="xml")
```

### 1.2 Minimal Example

The following is the simplest network topology generation example:

```python
from topology_generator import Generator, DeviceLibrary

# Initialize generator
gen = Generator()

# Method 1: Use predefined architecture
xml_code = gen.create_architecture("three_tier")

# Method 2: Custom topology
custom_topology = {
    "name": "Enterprise Network",
    "devices": [
        {"type": "router", "name": "Border Router", "position": {"x": 100, "y": 100}},
        {"type": "firewall", "name": "Firewall", "position": {"x": 250, "y": 100}},
        {"type": "switch", "name": "Core Switch", "position": {"x": 400, "y": 100}},
        {"type": "server", "name": "Web Server", "position": {"x": 400, "y": 250}},
    ],
    "connections": [
        {"source": "Border Router", "target": "Firewall"},
        {"source": "Firewall", "target": "Core Switch"},
        {"source": "Core Switch", "target": "Web Server"}
    ]
}
xml_code = gen.generate(custom_topology)
print(xml_code)
```

### 1.3 Output Format

The generator supports multiple output formats:

**XML Format (Default)**: Pure mxCell elements for direct use in draw.io

```xml
<mxCell id="2" value="Border Router" style="shape=mxgraph.cisco.routers.router;html=1;fillColor=#3366CC;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="80" height="60" as="geometry"/>
</mxCell>
<mxCell id="3" style="edgeStyle=orthogonalEdgeStyle;endArrow=classic;html=1;" edge="1" parent="1" source="2" target="4">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

**JSON Format**: Easy for programmatic processing

```json
{
  "devices": [
    {"id": "dev_1", "type": "router", "name": "Border Router", "x": 100, "y": 100},
    {"id": "dev_2", "type": "firewall", "name": "Firewall", "x": 250, "y": 100}
  ],
  "connections": [
    {"source": "dev_1", "target": "dev_2"}
  ]
}
```

---

## 2. Core Capabilities

### 2.1 Skill Overview

The Network Topology Generator is an intelligent tool for network architecture visualization. The core goal is to lower the barrier to network topology design, improve work efficiency, and ensure output quality meets enterprise standards.

**Core Advantages**:

- Extensive device support covering 100+ device types from global mainstream vendors
- Flexible topology construction supporting arbitrary complexity
- Natural language interaction capability
- Multi-format output support (draw.io XML, PNG, SVG, PDF)

### 2.2 Capability Matrix

| Category | Feature | Support | Description |
|---------|---------|---------|-------------|
| Device Support | Network devices | 100+ | Routers, switches, firewalls |
| Device Support | Cloud services | 50+ | AWS, Azure, GCP full support |
| Device Support | Custom devices | Supported | User-defined device types |
| Topology Structure | Predefined | 10+ | Three-tier, Spine-Leaf |
| Topology Structure | Custom topology | Full support | Arbitrary nodes and connections |
| Topology Structure | Dynamic adjustment | Supported | Real-time modification |
| Input Methods | Natural language | Supported | Smart parsing |
| Input Methods | TDL language | Supported | Structured description |
| Input Methods | API calls | Supported | Programmatic interface |
| Output Formats | draw.io XML | Supported | Direct paste use |
| Output Formats | PNG image | Supported | High-definition output |
| Output Formats | SVG vector | Supported | Lossless scaling |
| Output Formats | PDF document | Supported | Print and share |

### 2.3 Technical Architecture

```
+-------------------------------------------------------------+
|                      User Interface Layer                    |
|  +----------+  +----------+  +----------+  +----------+    |
|  | Natural  |  |   TDL    |  |   API    |  | Visual   |    |
|  | Language |  | Parser   |  | Interface|  | Editor   |    |
|  +----------+  +----------+  +----------+  +----------+    |
+-------------------------------------------------------------+
                              |
+-------------------------------------------------------------+
|                       Core Engine Layer                       |
|  +----------+  +----------+  +----------+  +----------+    |
|  | Topology |  |  Layout  |  |  Style   |  |  Output  |    |
|  |  Engine  |  |  Engine  |  |  Engine  |  |  Engine  |    |
|  +----------+  +----------+  +----------+  +----------+    |
+-------------------------------------------------------------+
                              |
+-------------------------------------------------------------+
|                       Data Resource Layer                    |
|  +----------+  +----------+  +----------+  +----------+    |
|  |  Device  |  |   Icon   |  | Template |  |  Style   |    |
|  |  Library |  |  Library |  |  Library |  |  Library |    |
|  +----------+  +----------+  +----------+  +----------+    |
+-------------------------------------------------------------+
```

---

## 3. Device Library

### 3.1 Device Library Overview

The device library contains 100+ device types from global mainstream vendors. Devices are classified by vendor and function.

**Main Categories**:

- Traditional network devices (routers, switches, firewalls)
- Security devices (IDS/IPS, WAF, VPN)
- Wireless devices (AP, controllers)
- Servers and terminals
- Storage devices
- Load balancers
- Cloud service components

### 3.2 Router Devices (45 Types)

**Cisco Router Series** (12 types)

| Model | Icon Name | Default Size | Use Case | Priority |
|-------|-----------|--------------|----------|----------|
| ISR 800 | mxgraph.cisco.routers.isr_800 | 80x60 | Small office | High |
| ISR 1900 | mxgraph.cisco.routers.isr_1900 | 80x60 | SMB | High |
| ISR 2900 | mxgraph.cisco.routers.isr_2900 | 80x60 | Mid-size enterprise | High |
| ISR 3900 | mxgraph.cisco.routers.isr_3900 | 100x70 | Large enterprise | High |
| ASR 1001 | mxgraph.cisco.routers.asr_1001 | 100x70 | Enterprise/ISP edge | High |
| ASR 9000 | mxgraph.cisco.routers.asr_9000 | 120x80 | ISP core | Medium |
| Nexus 7000 | mxgraph.cisco.switchs.catalyst_lg | 120x80 | Data center core | Medium |
| Meraki MX | mxgraph.cisco.routers.router | 80x60 | Cloud-managed | Medium |

**Huawei Router Series** (10 types)

| Model | Icon Name | Default Size | Use Case | Priority |
|-------|-----------|--------------|----------|----------|
| AR1220 | mxgraph.huawei.router.ar | 80x60 | Small enterprise | High |
| AR2240 | mxgraph.huawei.router.ar | 80x60 | Mid-size enterprise | High |
| NE40E-X8 | mxgraph.huawei.router.ne40e | 100x70 | ISP aggregation | High |
| NE5000E | mxgraph.huawei.router.ne5000e | 120x80 | ISP core | Medium |
| NetEngine 8000 | mxgraph.huawei.router.ne8000 | 120x80 | ISP backbone | Medium |

**H3C Router Series** (8 types)

| Model | Icon Name | Default Size | Use Case | Priority |
|-------|-----------|--------------|----------|----------|
| MSR2600 | mxgraph.cisco.routers.router | 80x60 | Small enterprise | High |
| MSR3600 | mxgraph.cisco.routers.router | 80x60 | Mid-size enterprise | High |
| MSR5600 | mxgraph.cisco.routers.router | 100x70 | Large enterprise | High |
| SR6608 | mxgraph.cisco.routers.router | 100x70 | Enterprise core | High |

**Juniper Router Series** (6 types)

| Model | Icon Name | Default Size | Use Case | Priority |
|-------|-----------|--------------|----------|----------|
| MX204 | mxgraph.juniper.mx | 80x60 | ISP edge | High |
| MX480 | mxgraph.juniper.mx | 100x70 | ISP aggregation | High |
| MX960 | mxgraph.juniper.mx | 120x80 | ISP core | High |
| PTX1000 | mxgraph.juniper.ptx | 100x70 | Data center | Medium |

### 3.3 Switch Devices (52 Types)

**Cisco Switch Series** (14 types)

| Model | Icon Name | Default Size | Use Case | Priority |
|-------|-----------|--------------|----------|----------|
| Catalyst 2960 | mxgraph.cisco.switchs.catalyst | 80x60 | Access switch | High |
| Catalyst 3750 | mxgraph.cisco.switchs.catalyst | 80x60 | Aggregation switch | High |
| Catalyst 6500 | mxgraph.cisco.switchs.catalyst_lg | 120x80 | Core switch | High |
| Nexus 3000 | mxgraph.cisco.switchs.nexus | 80x60 | DC access | High |
| Nexus 7000 | mxgraph.cisco.switchs.catalyst_lg | 120x80 | DC core | High |
| Nexus 9000 | mxgraph.cisco.switchs.nexus | 100x70 | Spine/Leaf | High |

**Huawei Switch Series** (12 types)

| Model | Icon Name | Default Size | Use Case | Priority |
|-------|-----------|--------------|----------|----------|
| S2700 | mxgraph.huawei.switch.s2700 | 80x60 | Access switch | High |
| S5700 | mxgraph.huawei.switch.s5700 | 80x60 | Aggregation switch | High |
| S6700 | mxgraph.huawei.switch.s6700 | 100x70 | Aggregation switch | High |
| S7700 | mxgraph.huawei.switch.s7700 | 100x70 | Core switch | High |
| CloudEngine 16800 | mxgraph.huawei.switch.ce16800 | 120x80 | DC core | High |

**H3C Switch Series** (10 types)

| Model | Icon Name | Default Size | Use Case | Priority |
|-------|-----------|--------------|----------|----------|
| S5130 | mxgraph.cisco.switchs.catalyst | 80x60 | Access switch | High |
| S5800 | mxgraph.cisco.switchs.catalyst | 100x70 | Aggregation switch | High |
| S6800 | mxgraph.cisco.switchs.catalyst | 100x70 | DC aggregation | High |
| S12500 | mxgraph.cisco.switchs.catalyst_lg | 120x80 | DC core | High |

### 3.4 Security Devices (38 Types)

**Firewall Devices** (15 types)

| Vendor | Model | Icon Name | Default Size | Priority |
|--------|-------|-----------|--------------|----------|
| Cisco | ASA 5505 | mxgraph.cisco.security.firewall | 80x60 | High |
| Cisco | ASA 5585 | mxgraph.cisco.security.firewall | 100x70 | High |
| Huawei | USG6320 | mxgraph.huawei.security.usg6000e | 80x60 | High |
| Huawei | USG9500 | mxgraph.huawei.security.usg9500 | 120x80 | High |
| Fortinet | FortiGate 60F | mxgraph.fortinet.fortigate | 80x60 | High |
| Fortinet | FortiGate 3000E | mxgraph.fortinet.fortigate | 100x70 | High |
| Palo Alto | PA-220 | mxgraph.paloalto.pa | 80x60 | High |
| Palo Alto | PA-3220 | mxgraph.paloalto.pa | 100x70 | High |

**IDS/IPS Devices** (8 types)

| Vendor | Model | Icon Name | Default Size | Priority |
|--------|-------|-----------|--------------|----------|
| Cisco | Firepower 4110 | mxgraph.cisco.security.ids | 80x60 | High |
| Huawei | NIP6300 | mxgraph.huawei.security.nip | 80x60 | High |
| Fortinet | FortiIPS | mxgraph.fortinet.ips | 80x60 | High |

**WAF Devices** (6 types)

| Vendor | Model | Icon Name | Default Size | Priority |
|--------|-------|-----------|--------------|----------|
| Fortinet | FortiWeb | mxgraph.fortinet.fortiweb | 80x60 | High |
| Cisco | ACE WAF | mxgraph.cisco.security.waf | 80x60 | High |

**VPN Gateways** (9 types)

| Vendor | Model | Icon Name | Default Size | Priority |
|--------|-------|-----------|--------------|----------|
| Cisco | ASA VPN | mxgraph.cisco.security.vpn_gateway | 80x60 | High |
| Fortinet | SSL VPN | mxgraph.fortinet.vpn | 80x60 | High |
| Huawei | VPN Gateway | mxgraph.huawei.vpn.gateway | 80x60 | High |

### 3.5 Load Balancers (18 Types)

| Vendor | Model | Icon Name | Default Size | Priority |
|--------|-------|-----------|--------------|----------|
| F5 | BIG-IP LTM 1600 | mxgraph.f5.ltm | 80x60 | High |
| F5 | BIG-IP LTM 6900 | mxgraph.f5.ltm | 120x80 | High |
| Citrix | NetScaler MPX | mxgraph.citrix.netscaler | 80x60 | High |
| Huawei | AD9430 | mxgraph.huawei.load_balancer | 80x60 | High |
| A10 | Thunder | mxgraph.a10.thunder | 80x60 | High |
| AWS | ALB | mxgraph.aws.load_balancer | 80x60 | High |
| AWS | NLB | mxgraph.aws.load_balancer | 80x60 | High |
| Azure | Load Balancer | mxgraph.azure.load_balancer | 80x60 | High |

### 3.6 Wireless Devices (15 Types)

| Device Type | Vendor Model | Icon Name | Default Size | Priority |
|-------------|--------------|-----------|--------------|----------|
| Wireless AP | Cisco Aironet 2800 | mxgraph.cisco.wireless.access_point | 80x60 | High |
| Wireless AP | Huawei AP4050 | mxgraph.huawei.wireless.airengine | 80x60 | High |
| Wireless AP | Aruba AP-515 | mxgraph.aruba.ap | 80x60 | High |
| Wireless Controller | Cisco WLC 5520 | mxgraph.cisco.wireless.wireless_controller | 100x70 | High |
| Wireless Controller | Huawei AC6005 | mxgraph.huawei.wireless.ac | 80x60 | High |

### 3.7 Servers and Terminals (25 Types)

**Server Devices** (12 types)

| Device Type | Vendor Model | Icon Name | Default Size | Priority |
|-------------|--------------|-----------|--------------|----------|
| Generic Server | Cisco UCS C220 | mxgraph.cisco.servers.generic_server | 80x60 | High |
| Blade Server | Cisco UCS B200 | mxgraph.cisco.servers.blade_server | 80x60 | High |
| Database Server | Oracle Exadata | mxgraph.database.exadata | 100x70 | High |
| GPU Server | AI Training Server | mxgraph.ai.server | 100x70 | High |
| Virtualization | VMware ESXi | mxgraph.vmware.esxi | 80x60 | High |
| Edge Server | Edge Server | mxgraph.edge.server | 80x60 | High |

**Terminal Devices** (13 types)

| Device Type | Icon Name | Default Size | Priority |
|-------------|-----------|--------------|----------|
| Desktop PC | mxgraph.cisco.workstations.pc | 80x60 | High |
| Laptop | mxgraph.cisco.workstations.laptop | 80x60 | High |
| Smartphone | mxgraph.mobile.phone | 60x60 | High |
| IP Phone | mxgraph.cisco.voice.ip_phone | 60x60 | High |
| Video Conference | mxgraph.video.conference | 80x60 | High |

### 3.8 Storage Devices (20 Types)

| Device Type | Vendor Model | Icon Name | Default Size | Priority |
|-------------|--------------|-----------|--------------|----------|
| NAS Storage | Synology DS918+ | mxgraph.storage.nas | 80x60 | High |
| SAN Storage | EMC VMAX | mxgraph.storage.san | 100x70 | High |
| SAN Switch | Cisco MDS 9148 | mxgraph.cisco.storage.san_switch | 80x60 | High |
| Hyper-converged | Nutanix | mxgraph.nutanix.node | 100x70 | High |
| Object Storage | AWS S3 | mxgraph.aws.s3 | 80x60 | High |
| Database Storage | OceanStor 18000 | mxgraph.huawei.storage.oceanstor | 120x80 | High |

### 3.9 Cloud Service Components (55 Types)

**AWS Cloud Services** (20 types)

| Service | Name | Icon Name | Default Size | Priority |
|---------|------|-----------|--------------|----------|
| Compute | EC2 | mxgraph.aws.ec2 | 80x60 | High |
| Compute | Lambda | mxgraph.aws.lambda | 80x60 | High |
| Compute | ECS | mxgraph.aws.ecs | 80x60 | High |
| Compute | EKS | mxgraph.aws.eks | 80x60 | High |
| Network | VPC | mxgraph.aws.vpc | Custom | High |
| Network | ELB | mxgraph.aws.load_balancer | 80x60 | High |
| Database | RDS | mxgraph.aws.rds | 80x60 | High |
| Database | DynamoDB | mxgraph.aws.dynamodb | 80x60 | High |
| Storage | S3 | mxgraph.aws.s3 | 80x60 | High |

**Azure Cloud Services** (18 types)

| Service | Name | Icon Name | Default Size | Priority |
|---------|------|-----------|--------------|----------|
| Compute | Virtual Machine | mxgraph.azure.compute.virtual_machine | 80x60 | High |
| Compute | AKS | mxgraph.azure.compute.aks | 80x60 | High |
| Network | Virtual Network | mxgraph.azure.networking.virtual_network | Custom | High |
| Database | SQL Database | mxgraph.azure.database.sql_database | 80x60 | High |
| Storage | Blob Storage | mxgraph.azure.storage.blob_storage | 80x60 | High |

**GCP Cloud Services** (10 types)

| Service | Name | Icon Name | Default Size | Priority |
|---------|------|-----------|--------------|----------|
| Compute | Compute Engine | mxgraph.gcp.compute_engine | 80x60 | High |
| Compute | GKE | mxgraph.gcp.gke | 80x60 | High |
| Network | VPC Network | mxgraph.gcp.vpc_network | Custom | High |
| Database | Cloud SQL | mxgraph.gcp.cloud_sql | 80x60 | High |

**Alibaba Cloud Services** (7 types)

| Service | Name | Icon Name | Default Size | Priority |
|---------|------|-----------|--------------|----------|
| Compute | ECS | mxgraph.aliyun.ecs | 80x60 | High |
| Network | VPC | mxgraph.aliyun.vpc | Custom | High |
| Network | SLB | mxgraph.aliyun.slb | 80x60 | High |
| Database | RDS | mxgraph.aliyun.rds | 80x60 | High |

### 3.10 Device Library Usage Guide

#### 3.10.1 Device Selection Principles

**Select by Vendor**: If your network primarily uses one vendor's devices, prioritize that vendor's icon library for visual consistency.

**Select by Device Type**: Different device types should use corresponding icon types. Routers use router icons, switches use switch icons, firewalls use security device icons.

**Select by Device Layer**: Core layer devices typically use large icons (120x80), aggregation layer uses medium (100x70), access layer uses standard (80x60).

#### 3.10.2 Device Naming Convention

```
[Location]-[Type]-[Model]-[Number]

Examples:
- BJ-CORE-S9500-01    # Beijing Core Switch 9500 No.01
- SH-AGG-S5700-02    # Shanghai Aggregation Switch 5700 No.02
- BJ-FW-FGT100F-01   # Beijing Firewall FortiGate 100F No.01
```

#### 3.10.3 Device Library Extension

```python
from topology_generator import DeviceLibrary

# Add custom device
DeviceLibrary.register({
    "name": "Custom Router",
    "type": "router",
    "vendor": "custom",
    "icon": "mxgraph.cisco.routers.router",
    "size": {"width": 80, "height": 60},
    "color": "#FF6600",
    "description": "Custom vendor router"
})

# Use custom device
topology = {
    "devices": [
        {"type": "Custom Router", "name": "Test Router"}
    ]
}
```

---

## 4. Topology Description Language (TDL)

### 4.1 TDL Overview

TDL (Topology Description Language) is a domain-specific language for describing network topology structures. TDL provides a concise, readable, and powerful way to express arbitrary complex network topologies.

**Design Principles**:

- Declarative syntax: Focus on describing desired results
- Hierarchical structure: Support from simple star topologies to complex multi-tier data centers
- Flexible extensibility: Allow user-defined custom device types and connection patterns

### 4.2 Basic Syntax

#### 4.2.1 Device Definition

```tdl
# Basic syntax
device_type [name] [quantity] [properties]

# Examples
router Core-Router           # Define a router named Core-Router
switch x4                    # Define 4 unnamed switches
firewall FW-01               # Define a firewall named FW-01
server Web-Server x3         # Define 3 web servers
loadbalancer LB-01           # Define a load balancer
```

#### 4.2.2 Quantity Modifiers

| Modifier | Syntax | Example | Description |
|----------|--------|---------|-------------|
| Single | No modifier | router R1 | 1 device |
| Multiple | xN | switch x4 | N devices |
| Range | N-M | server 2-4 | 2-4 devices |
| List | (a,b,c) | router (R1,R2,R3) | Named devices |
| Distributed | distributed | server x20 distributed | Evenly distributed |

#### 4.2.3 Connection Definition

```tdl
# Basic connection
router -- switch          # Router connects to switch

# Labeled connection
router --[bandwidth:10Gbps]--> switch   # Connection with bandwidth label
switch --[VLAN:100]--> server          # Connection with VLAN label

# Batch connection
core -- all aggregation   # Core connects to all aggregation devices
spine -- leaf            # Spine connects to all leaves

# Group connection
firewall -- (web, app, db)  # Firewall connects to web, app, db groups
```

#### 4.2.4 Property Definition

```tdl
# Device property syntax
device [property=value, property=value]

# Examples
router Core-R1 [vendor=cisco, model=ASR9000, bandwidth=100Gbps]
switch Access [vendor=huawei, ports=48, poe=yes]
server Web [os=centos, cpu=8core, ram=32GB]
```

### 4.3 Advanced Syntax

#### 4.3.1 Layer Definition

```tdl
# Layer definition syntax
topology topology_name {
  layer layer_name {
    device definitions
  }
  layer layer_name {
    device definitions
  }
}

# Example: Three-tier network architecture
topology Enterprise {
  layer core {
    router Core-Router
  }
  layer aggregation {
    switch Agg-1
    switch Agg-2
  }
  layer access {
    switch Acc-1
    switch Acc-2
  }
}
```

#### 4.3.2 Group Definition

```tdl
# Group definition syntax
group group_name {
  device definitions
}

# Example: DMZ zone
group DMZ {
  firewall FW-DMZ
  server Web-1
  server Web-2
  loadbalancer LB-DMZ
}
```

#### 4.3.3 Container Definition

```tdl
# Container definition syntax
container container_name [size=WxH] {
  device or group definitions
}

# Example: Data Center A
container "DataCenter-A" [size=800x600] {
  group Servers {
    server Web x4
    server App x2
    server DB x2
  }
}
```

### 4.4 Complete Examples

#### 4.4.1 Spine-Leaf Architecture

```tdl
// Spine-Leaf Data Center Architecture
topology Spine_Leaf_DC {
  // SDN Controller
  controller SDN-Controller [vendor=vmware, platform=NSX]

  // Spine layer: 2 spine switches
  spine Spine-1 [vendor=cisco, model=Nexus9000, ports=64x100G]
  spine Spine-2 [vendor=cisco, model=Nexus9000, ports=64x100G]

  // Leaf layer: 4 leaf switches
  leaf Leaf-1 [vendor=cisco, model=Nexus9000]
  leaf Leaf-2 [vendor=cisco, model=Nexus9000]
  leaf Leaf-3 [vendor=cisco, model=Nexus9000]
  leaf Leaf-4 [vendor=cisco, model=Nexus9000]

  // Connections
  connections {
    // SDN controller management connections
    SDN-Controller --[mgmt]--> spine Spine-1
    SDN-Controller --[mgmt]--> spine Spine-2

    // Spine-Leaf full mesh
    spine Spine-1 --[40Gbps]--> leaf Leaf-1
    spine Spine-1 --[40Gbps]--> leaf Leaf-2
    spine Spine-1 --[40Gbps]--> leaf Leaf-3
    spine Spine-1 --[40Gbps]--> leaf Leaf-4
    spine Spine-2 --[40Gbps]--> leaf Leaf-1
    spine Spine-2 --[40Gbps]--> leaf Leaf-2
    spine Spine-2 --[40Gbps]--> leaf Leaf-3
    spine Spine-2 --[40Gbps]--> leaf Leaf-4
  }
}

output: xml
```

#### 4.4.2 Hybrid Cloud Architecture

```tdl
// Hybrid Cloud Architecture
topology HybridCloud {
  // On-Premise Data Center
  container "On-Premise DC" [size=600x500] {
    group Edge {
      router Internet-RTR [vendor=cisco, model=ASR1001]
      firewall FW-Edge [vendor=fortinet, model=FG200E]
    }

    group Core {
      switch Core-SW-1 [vendor=cisco, model=Catalyst9500]
      switch Core-SW-2 [vendor=cisco, model=Catalyst9500]
    }

    group Compute {
      server App-Server x6 [type=kvm, cpu=32core]
      server DB-Server x3 [type=physical]
    }
  }

  // Public Cloud (AWS)
  container "AWS VPC" [size=600x500] {
    group Network {
      vpc VPC-Main [cidr=10.0.0.0/16]
      igw Internet-Gateway
      nat NAT-Gateway
    }

    group Compute {
      ec2 Web-Server x4 [instance=t3.large]
      ec2 App-Server x2 [instance=t3.xlarge]
    }

    group Data {
      rds Primary-DB [engine=mysql, class=db.r5.large]
      s3 Backup-Bucket [storage=1TB]
    }
  }

  // Hybrid connections
  connections {
    // On-premise to AWS
    router Internet-RTR --[DirectConnect=1Gbps]--> igw Internet-Gateway

    // Local firewall to VPC
    firewall FW-Edge --[VPN=100Mbps]--> vpc VPC-Main
  }
}

output: xml
style: professional
```

### 4.5 TDL Command Reference

| Command | Syntax | Description | Example |
|---------|--------|-------------|---------|
| topology | topology name { } | Define top-level topology | topology DC { } |
| layer | layer name { } | Define network layer | layer core { } |
| group | group name { } | Define device group | group Servers { } |
| container | container name { } | Define container area | container DMZ { } |
| connections | connections { } | Define connections | connections { } |
| output | output: format | Specify output format | output: xml |
| style | style: style_name | Specify visual style | style: professional |
| include | include file_path | Include external TDL | include base.tdl |
| extend | extend topology_name | Extend existing topology | extend SpineLeaf |

---

## 5. Natural Language Topology Description

### 5.1 Natural Language Parsing Overview

Natural language parsing allows users to describe network topologies using everyday language. The system automatically understands and generates corresponding topology structures.

**Parsing Methods**: Pattern matching combined with semantic understanding. The engine identifies key entities in user descriptions (device types, quantities, positions) and matches them to topology templates.

### 5.2 Supported Expression Patterns

#### 5.2.1 Device Description Patterns

| Pattern Type | Example Statement | Parsing Result |
|--------------|-------------------|----------------|
| Single device | "a router" | 1 router device |
| Multiple devices | "4 switches" | 4 switch devices |
| Named device | "a router named Core-Router" | 1 router named Core-Router |
| Modeled device | "Cisco 2960 switch" | 1 Cisco 2960 switch |
| Combined | "3 Huawei S5700 aggregation switches" | 3 Huawei S5700 switches |

#### 5.2.2 Connection Patterns

| Pattern Type | Example Statement | Parsing Result |
|--------------|-------------------|----------------|
| Simple | "router connects to switch" | Router-to-switch connection |
| Multi-point | "core switch connects to all access switches" | Core to each access connection |
| Bandwidth | "10G link between two cores" | Connection with 10Gbps label |
| Protocol | "connect using RIP protocol" | Connection with RIP protocol label |

#### 5.2.3 Topology Structure Patterns

| Pattern Type | Example Statement | Parsing Result |
|--------------|-------------------|----------------|
| Standard | "three-tier network architecture" | Auto-create three-tier topology |
| Spine-Leaf | "Spine-Leaf architecture" | Auto-create Spine-Leaf topology |
| Star | "star topology" | All terminals connect to center |
| Ring | "ring topology" | Devices connected end-to-end |
| Mesh | "full mesh connection" | All devices interconnect |

#### 5.2.4 Layout Patterns

| Pattern Type | Example Statement | Parsing Result |
|--------------|-------------------|----------------|
| Horizontal | "arrange from left to right" | Horizontal distribution |
| Vertical | "arrange from top to bottom" | Vertical distribution |
| Grid | "arrange in 3 rows 4 columns" | Grid distribution |
| Circular | "arrange in a circle" | Circular distribution |

### 5.3 Complex Description Parsing

#### 5.3.1 Data Center Network Description

```
Input:
"Design a data center network with 2 core switches, 4 aggregation switches, 8 access switches per aggregation, 20 servers per access switch, using Spine-Leaf architecture with SDN controller"

Parsing Result:
{
    "architecture": "spine_leaf",
    "spine_count": 2,
    "leaf_count": 4,
    "servers_per_aggregation": 8,
    "servers_per_access": 20,
    "include_controller": true
}
```

#### 5.3.2 Enterprise Network Description

```
Input:
"Create an enterprise network with 1000 terminals, using hierarchical structure, 10G core, 1G aggregation, 48 ports per access switch, with redundancy"

Parsing Result:
{
    "architecture": "three_tier",
    "terminal_count": 1000,
    "core_bandwidth": "10Gbps",
    "aggregation_bandwidth": "1Gbps",
    "access_ports_per_switch": 48,
    "redundancy": true
}
```

### 5.4 Natural Language Command Set

| Command Type | Example | Function |
|--------------|---------|----------|
| Create | "create a network topology" | Initialize new topology |
| Add device | "add a router" | Add device to topology |
| Delete device | "delete that switch" | Remove device |
| Modify | "change connection to 10G" | Modify connection |
| Export | "export as PNG" | Generate image file |
| Reset | "relayout" | Auto-optimize layout |

### 5.5 Natural Language Processing Limits

- Ambiguous descriptions may not be accurately understood
- Very large-scale topologies (>1000 devices) may take longer to process
- Non-standard configurations should use TDL language

---

## 6. Topology Generator API

### 6.1 API Overview

The topology generator provides complete API interfaces supporting programmatic calls and secondary development.

**API Support**:

- Python SDK: Complete functionality, suitable for deep integration
- REST API: Cross-language support, suitable for microservices
- CLI: Quick integration and script automation

### 6.2 Python SDK

#### 6.2.1 Core Classes

**Generator Class**:

```python
from topology_generator import Generator

# Initialize generator
gen = Generator()

# Basic usage
topology = gen.create_architecture("three_tier")
xml_code = gen.generate(topology, format="xml")
```

**Generator Class Main Methods**:

| Method | Parameters | Return Value | Description |
|--------|------------|--------------|-------------|
| create_architecture | architecture_type | Topology | Create predefined architecture |
| generate | topology, format | str/bytes | Generate topology code |
| add_device | device_info | str | Add device |
| add_connection | source, target | str | Add connection |
| remove_device | device_id | bool | Delete device |
| get_layout | - | Layout | Get current layout |
| export | format, path | bool | Export file |
| import_tdl | tdl_code | Topology | Parse TDL |
| parse_natural | text | Topology | Parse natural language |

#### 6.2.2 Topology Class

```python
from topology_generator import Topology, Device, Connection

# Create topology object
topo = Topology(name="Enterprise Network")

# Add devices
router = Device(type="router", name="Border Router")
firewall = Device(type="firewall", name="Firewall")
switch = Device(type="switch", name="Core Switch")

topo.add_device(router)
topo.add_device(firewall)
topo.add_device(switch)

# Add connections
topo.add_connection(router, firewall)
topo.add_connection(firewall, switch)

# Generate code
xml = gen.generate(topo)
```

#### 6.2.3 Layout Class

```python
from topology_generator import Layout, LayoutAlgorithm

# Create layout configuration
layout = Layout()

# Set layout algorithm
layout.algorithm = LayoutAlgorithm.HIERARCHICAL
layout.direction = Layout.DIRECTION_TB  # Top to bottom
layout.spacing_x = 100
layout.spacing_y = 80
layout.node_size = (80, 60)

# Apply layout
topo.set_layout(layout)
```

#### 6.2.4 Style Class

```python
from topology_generator import Style, ColorScheme

# Create style configuration
style = Style()

# Set color scheme
style.color_scheme = ColorScheme.CISCO
style.background_color = "#FFFFFF"
style.grid_visible = True

# Set device styles
style.device_style = {
    "router": {"fill_color": "#3366CC", "icon": "cisco_router"},
    "switch": {"fill_color": "#3366CC", "icon": "cisco_switch"},
    "firewall": {"fill_color": "#FF9966", "icon": "cisco_firewall"}
}

# Apply style
topo.set_style(style)
```

### 6.3 Complete API Reference

#### 6.3.1 Device API

```python
# Create device
device = Device(
    type="router",
    name="Core-Router",
    model="ASR9000",
    vendor="cisco",
    properties={
        "ports": 24,
        "bandwidth": "100Gbps"
    }
)

# Add to topology
device_id = topo.add_device(device)
device_info = topo.get_device(device_id)

# Update device
device_info.name = "New-Name"
topo.update_device(device_id, device_info)

# Delete device (also removes related connections)
topo.remove_device(device_id)
```

#### 6.3.2 Connection API

```python
# Add connection
conn = Connection(
    source=device_id_1,
    target=device_id_2,
    bandwidth="10Gbps",
    protocol="ethernet",
    label="Trunk"
)
conn_id = topo.add_connection(conn)

# Update connection
conn_info = topo.get_connection(conn_id)
conn_info.bandwidth = "40Gbps"
topo.update_connection(conn_id, conn_info)

# Delete connection
topo.remove_connection(conn_id)
```

#### 6.3.3 Layout API

```python
# Get current layout
layout = topo.get_layout()

# Set predefined layout
topo.set_layout_type("hierarchical")    # Hierarchical layout
topo.set_layout_type("force_directed")  # Force-directed layout
topo.set_layout_type("circular")        # Circular layout
topo.set_layout_type("grid")            # Grid layout

# Manual position
topo.set_position(device_id, x=100, y=200)

# Auto-align
topo.align_devices("x")                 # Align by X-axis
topo.align_devices("y")                 # Align by Y-axis
```

#### 6.3.4 Import/Export API

```python
# Import TDL
tdl_code = """
topology MyNetwork {
  router R1
  switch S1
  R1 -- S1
}
"""
topo = gen.import_tdl(tdl_code)

# Import natural language
text = "create a network with router and switch"
topo = gen.parse_natural(text)

# Export XML
xml_code = gen.generate(topo, format="xml")

# Export image
gen.export(topo, format="png", path="output.png")
gen.export(topo, format="svg", path="output.svg")
gen.export(topo, format="pdf", path="output.pdf", page_size="A3")
```

### 6.4 REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/topology | Create topology |
| GET | /api/v1/topology/{id} | Get topology |
| PUT | /api/v1/topology/{id} | Update topology |
| DELETE | /api/v1/topology/{id} | Delete topology |
| POST | /api/v1/topology/{id}/generate | Generate code |
| POST | /api/v1/topology/import | Import TDL/natural language |
| GET | /api/v1/templates | Get template list |
| POST | /api/v1/export | Export file |

### 6.5 CLI

```bash
# Basic commands
topology-cli create --name "MyNetwork" --output mynetwork.xml
topology-cli add-device --type router --name R1
topology-cli add-connection --from R1 --to S1

# Import TDL
topology-cli import --input network.tdl --output result.xml

# Import natural language
topology-cli parse --text "create a three-tier network" --output result.xml

# Generate image
topology-cli generate --input network.xml --format png --output network.png
```

---

## 7. Smart Layout Engine

### 7.1 Layout Engine Overview

The smart layout engine automatically calculates optimal positions for each device based on topology structure and device properties. Good layouts make topology diagrams clear and readable while accurately reflecting network design intent.

**Layout Engine Features**:

- Multiple layout algorithms optimized for network topology
- Automatic layer recognition
- Dynamic adjustment support
- Fine-grained parameter control

### 7.2 Layout Algorithms

#### 7.2.1 Hierarchical Layout

Hierarchical layout is the most commonly used algorithm for network topologies with clear layer structures (three-tier, Spine-Leaf).

**Algorithm Flow**:

```
1. Analyze topology structure, identify layer relationships
   - Root layer: Nodes without incoming edges
   - Core layer: Backbone connection devices
   - Aggregation layer: Traffic aggregation devices
   - Access layer: Terminal connection devices

2. Assign Y coordinates by layer
   - Layer N Y = (N-1) * (node_height + vertical_spacing)

3. Horizontally arrange devices in same layer
   - Calculate total width for each layer
   - Evenly distribute within container width
   - Maintain alignment with adjacent layers

4. Optimize connection lines
   - Use orthogonal routing
   - Minimize line crossings
   - Auto-routing around obstacles
```

**Parameters**:

```python
layout = Layout()
layout.algorithm = LayoutAlgorithm.HIERARCHICAL
layout.direction = Layout.DIRECTION_TB  # TB, BT, LR, RL
layout.level_spacing = 100              # Layer spacing
layout.node_spacing = 60                # Node spacing
layout.align_same_level = True          # Align same level
```

#### 7.2.2 Force-Directed Layout

Force-directed layout simulates physical forces. Nodes are like charged particles, connections like springs.

**Algorithm Principle**:

```python
def force_directed_layout(nodes, edges):
    # Initialize random positions
    for node in nodes:
        node.position = random_position()

    # Iterative optimization
    for iteration in range(MAX_ITERATIONS):
        for node in nodes:
            # Repulsion force (from all other nodes)
            repulsion_force = sum(coulomb_force(node, other) for other in nodes)

            # Attraction force (from connected nodes)
            attraction_force = sum(hooke_force(node, connected) for connected in get_connected_nodes(node))

            # Gravity (toward center)
            gravity_force = gravity_toward_center(node, center)

            # Update position
            node.velocity = (repulsion_force + attraction_force + gravity_force) * damping
            node.position += node.velocity

        if total_energy < THRESHOLD:
            break

    return nodes
```

#### 7.2.3 Circular Layout

Circular layout arranges devices in a circle, suitable for peer networks and ring redundancy topologies.

#### 7.2.4 Grid Layout

Grid layout arranges devices in a matrix form, suitable for large groups of similar devices.

```python
def grid_layout(container_width, container_height, nodes, columns=None, spacing=(80, 60)):
    if columns is None:
        columns = int(sqrt(len(nodes)))

    rows = ceil(len(nodes) / columns)
    total_width = columns * spacing[0]
    start_x = (container_width - total_width) / 2

    for i, node in enumerate(nodes):
        row = i // columns
        col = i % columns
        node.x = start_x + col * spacing[0]
        node.y = row * spacing[1]
```

### 7.3 Coordinate Calculation

#### 7.3.1 Device Size Specifications

| Device Type | Standard Size | Large Size | Description |
|-------------|---------------|-------------|-------------|
| Router | 80x60 | 100x70 | Large core routers use large size |
| Switch | 80x60 | 120x80 | Core switches use large size |
| Firewall | 80x60 | 100x70 | High-end firewalls use large size |
| Server | 80x60 | 100x70 | Blade servers can use small size |
| Load Balancer | 80x60 | 100x70 | Cluster devices use large size |
| Terminal | 60x60 | 80x60 | Desktop and mobile devices |

#### 7.3.2 Spacing Calculation

```python
class LayoutSpacing:
    HORIZONTAL_SPACING = 80    # Center-to-center distance
    VERTICAL_SPACING = 100     # Between layers
    MARGIN_LEFT = 40
    MARGIN_RIGHT = 40
    MARGIN_TOP = 40
    MARGIN_BOTTOM = 40
    GROUP_PADDING = 30
    LABEL_LINE_HEIGHT = 14
```

#### 7.3.3 Coordinate Calculation Formula

**Hierarchical Layout Coordinate Calculation**:

```python
def calculate_hierarchical_coordinates(topo, config):
    # Identify layers
    levels = topo.identify_levels()

    # Calculate position for each layer
    y_position = config.margin_top

    for level_name, nodes in levels.items():
        total_width = sum(node.width for node in nodes)
        total_spacing = (len(nodes) - 1) * config.horizontal_spacing

        level_width = total_width + total_spacing
        x_start = (config.container_width - level_width) / 2

        current_x = x_start
        for node in nodes:
            node.x = current_x + node.width / 2
            node.y = y_position + node.height / 2
            current_x += node.width + config.horizontal_spacing

        y_position += max(node.height for node in nodes) + config.vertical_spacing

    return topo
```

### 7.4 Layout Optimization

#### 7.4.1 Minimize Edge Crossings

```python
def minimize_edge_crossings(topo):
    # Strategy 1: Adjust order of same-level devices
    for level in topo.levels[1:]:
        for node in level:
            connected_below = topo.get_connected_nodes_below(node)
            if len(connected_below) > 1:
                targets = sorted(connected_below, key=lambda n: n.x)
                node.x = (targets[0].x + targets[-1].x) / 2
```

#### 7.4.2 Label Position Optimization

```python
def optimize_label_positions(topo):
    # Device labels: Below icon
    for node in topo.nodes:
        node.label_position = {
            "x": node.x,
            "y": node.y + node.height/2 + 5,
            "align": "center",
            "valign": "top"
        }

    # Connection labels: Midpoint of line
    for edge in topo.edges:
        mid_x = (edge.source.x + edge.target.x) / 2
        mid_y = (edge.source.y + edge.target.y) / 2
        edge.label_position = (mid_x, mid_y)
```

#### 7.4.3 Auto Scaling

```python
def auto_scale(topo, container_width, container_height):
    bounds = topo.calculate_bounds()

    scale_x = container_width / (bounds.width + 100)
    scale_y = container_height / (bounds.height + 100)
    scale = min(scale_x, scale_y, 1.0)

    if scale < 1.0:
        for node in topo.nodes:
            node.x *= scale
            node.y *= scale

    return topo
```

---

## 8. Usage Workflows

### 8.1 Typical Workflow

**Step 1: Requirements Analysis**

Before creating topology, clarify:

- Network scale (device count, user count)
- Network type (enterprise, data center, cloud)
- Architecture pattern (three-tier, Spine-Leaf, hybrid cloud)
- Device selection (vendor preference, model requirements)
- Connection bandwidth

**Step 2: Input Description**

Choose appropriate input method:

- Natural language: Quick prototyping
- TDL language: Precise control
- Python API: Programmatic integration

**Step 3: Generate Preview**

System generates topology code and provides preview for inspection.

**Step 4: Optimize Adjustments**

- Adjust device positions
- Modify connections
- Add or remove devices
- Change colors and styles

**Step 5: Export Delivery**

Choose appropriate format for export:

- XML: Continue editing in draw.io
- PNG: Documentation and presentations
- SVG: High-quality printing
- PDF: Formal delivery

### 8.2 Scenario Guides

#### 8.2.1 Data Center Network Scenario

```python
data_center_topology = {
    "name": "Data Center Network",
    "architecture": "spine_leaf",
    "scale": {
        "spine": 2,
        "leaf": 4,
        "servers_per_leaf": 40
    },
    "requirements": {
        "spine_bandwidth": "100Gbps",
        "leaf_server_bandwidth": "25Gbps",
        "include_controllers": True
    }
}

gen = Generator()
topo = gen.generate(data_center_topology)
topo.set_layout_type("hierarchical")
topo.set_layout_direction("TB")
topo.set_spacing(horizontal=100, vertical=80)
gen.export(topo, format="xml", path="datacenter.xml")
gen.export(topo, format="png", path="datacenter.png", dpi=300)
```

#### 8.2.2 Enterprise Network Scenario

```python
enterprise_topology = {
    "name": "Enterprise Network",
    "regions": [
        {"name": "Internet Edge", "devices": ["router", "firewall"]},
        {"name": "DMZ", "devices": ["web_server", "lb"]},
        {"name": "Core Network", "devices": ["core_switch"]},
        {"name": "Office Area", "devices": ["access_switch", "pc"]}
    ]
}

gen = Generator()
topo = gen.generate(enterprise_topology)
topo.set_layout_type("region_based")
gen.export(topo, format="xml", path="enterprise.xml")
```

#### 8.2.3 Cloud Architecture Scenario

```python
cloud_topology = {
    "platform": "aws",
    "region": "ap-east-1",
    "vpc": {
        "cidr": "10.0.0.0/16",
        "availability_zones": 2
    },
    "subnets": {
        "public_web": {"cidr": "10.0.1.0/24"},
        "private_db": {"cidr": "10.0.3.0/24"}
    },
    "components": {
        "load_balancer": {"type": "alb"},
        "web_servers": {"type": "ec2", "count": 4},
        "database": {"type": "rds", "engine": "mysql"}
    }
}

gen = Generator()
topo = gen.generate(cloud_topology)
gen.export(topo, format="xml", path="cloud_architecture.xml")
```

### 8.3 Batch Processing

```python
from topology_generator import BatchProcessor

batch = BatchProcessor()

template = """
topology Branch-Office-{id} {
  layer wan { router Router-{id} }
  layer lan {
    switch Switch-1
    switch Switch-2
    server Server-1
  }
  Router-{id} -- Switch-1
  Switch-1 -- Switch-2
}
"""

configs = [
    {"id": "001", "location": "Beijing"},
    {"id": "002", "location": "Shanghai"},
    {"id": "003", "location": "Guangzhou"}
]

for config in configs:
    tdl = template.format(**config)
    topo = gen.import_tdl(tdl)
    batch.add(topo, f"branch_office_{config['id']}.xml")

batch.export_all(format="xml", output_dir="branches/")
```

---

## 9. Reference Resources

### 9.1 Internal Resources

| Resource | Path | Description |
|----------|------|-------------|
| Icon Library Mapping | references/icon-library-mapping.md | Complete icon mapping table |
| H3C Icon Mapping | references/h3c-icon-mapping.md | H3C device icon guide |
| XML Structure Guide | references/xml-structure-guide.md | draw.io XML structure |
| XML Code Standard | references/xml-code-standard.md | XML code standards |
| Common Topologies | references/common-topologies.md | Typical topology examples |
| Network Design | references/network-design-methodology.md | Network design methodology |
| Data Center Guide | references/datacenter-guide.md | Data center network design |
| Cloud Architecture | references/cloud-architectures.md | Cloud platform architecture |
| Security Architecture | references/security-architecture-guide.md | Secure network design |

### 9.2 External Resources

| Resource | Link | Description |
|----------|------|-------------|
| draw.io Official | https://www.draw.io | Official drawing tool |
| draw.io Icons | https://app.diagrams.net/ | Online icon library |
| Cisco Icons | https://www.cisco.com/ | Cisco network icons |
| AWS Icons | https://aws.amazon.com/architecture/icons/ | AWS architecture icons |
| Azure Icons | https://learn.microsoft.com/azure/architecture/icons/ | Azure architecture icons |

---

## 10. FAQ

### 10.1 Basic Usage Questions

**Q1: How to choose the right icon?**

Consider three factors: vendor match, icon availability, visual consistency. Prioritize vendor-specific icons when available, otherwise use similar generic icons.

**Q2: How to handle large-scale topology performance?**

For topologies with >500 devices: Enable grouping to reduce render elements; use simplified icons; turn off unnecessary animations; consider pagination layout.

**Q3: How to ensure professional and aesthetic topology diagrams?**

Follow principles: Consistency (uniform icon size, colors, fonts), Hierarchy (clear core/aggregation/access layers), Simplicity (avoid unnecessary decorations), Completeness (key connections labeled), Symmetry (alignment and uniform distribution).

### 10.2 Technical Questions

**Q4: What if XML code displays abnormally in draw.io?**

Check: Ensure mxCell IDs are unique; confirm parent attributes are correct; verify XML syntax (special characters escaped); check icon style names exist.

**Q5: How to add custom device icons?**

Prepare SVG format icon; upload to draw.io local icon library or reference via URL; register custom icon in device library.

**Q6: Why aren't connection lines showing arrows?**

Ensure edgeStyle includes endArrow or startArrow parameter, e.g., endArrow=classic for solid triangle.

### 10.3 Architecture Design Questions

**Q7: How to choose between three-tier and Spine-Leaf?**

Three-tier: Suitable for small-medium networks (<1000 devices), simple configuration, mature technology. Spine-Leaf: Suitable for large-scale data centers, horizontal scaling, excellent east-west traffic performance.

**Q8: How to design high-availability network topology?**

Consider: Core device redundancy, link redundancy (Eth-Trunk), routing redundancy (dual uplinks), load balancing for important services, fast failover configuration.

**Q9: How to design hybrid cloud architecture?**

Focus on: Network connectivity (dedicated lines or VPN), IP address planning (avoid conflicts), unified security policies, application architecture adaptation, unified operations management.

### 10.4 Format Conversion Questions

**Q10: What if PNG export resolution is insufficient?**

Set higher DPI (300 or 600); use SVG format for lossless scaling; in draw.io export dialog select higher resolution; consider block export for large topologies.

**Q11: How to embed topology in PPT?**

Use SVG format for best results: Export as SVG from draw.io; insert as picture in PowerPoint; for editing, double-click to open in draw.io.

**Q12: How to batch export multiple topologies to different formats?**

```python
from topology_generator import BatchExporter

exporter = BatchExporter()
exporter.add_topology(topo1, "topo1")
exporter.add_topology(topo2, "topo2")
exporter.export_all_formats(output_dir="exports/")
```

---

## 11. Troubleshooting Guide

### 11.1 Common Error Types

#### 11.1.1 XML Generation Errors

**Error Code**: TDL_001

**Description**: XML root element structure incomplete

**Symptoms**: Generated XML missing necessary wrapper tags

**Solution**:

```python
from topology_generator import Validator

validator = Validator()
result = validator.validate_xml(xml_code)

if not result.is_valid:
    print("Error position:", result.error_position)
    print("Error message:", result.error_message)
    print("Suggested fix:", result.suggestion)
```

#### 11.1.2 Device Recognition Errors

**Error Code**: DEV_001

**Description**: Cannot recognize device type

**Symptoms**: System cannot recognize certain device types in natural language

**Solution**:

```python
from topology_generator import DeviceLibrary

lib = DeviceLibrary()
results = lib.search("device_name")
if not results:
    print("Device not found. Check spelling or register custom device.")
```

#### 11.1.3 Connection Relationship Errors

**Error Code**: CONN_001

**Description**: Invalid connection relationship or non-existent device ID

**Solution**:

```python
from topology_generator import ConnectionValidator

validator = ConnectionValidator()
if validator.can_connect(device1, device2):
    topo.add_connection(device1, device2)
else:
    print("Connection validation failed:", validator.last_error)
```

#### 11.1.4 Layout Calculation Errors

**Error Code**: LAY_001

**Description**: Device positions overlapping or exceeding boundaries

**Solution**:

```python
from topology_generator import LayoutFixer

fixer = LayoutFixer()
fixer.fix_overlaps(topo)
fixer.fix_out_of_bounds(topo)
fixer.adjust_spacing(topo)
fixer.apply_auto_scaling(topo)
```

#### 11.1.5 Format Export Errors

**Error Code**: EXP_001

**Description**: Unsupported export file format

**Solution**: Check supported format list (xml, png, svg, pdf); use standard format names.

### 11.2 Error Diagnosis Flow

```
Start Diagnosis
     |
     v
Step 1: Validate Input
     - Check natural language/TDL description
     - Check API parameters
     - Check device types
     |
     v
Input Correct?
     |
    Yes -> Step 2: Validate Generation Process
     |
    No -> Return input validation error
     |
     v
Generation Success?
     |
    Yes -> Step 3: Validate Output Format
     |
    No -> Check error code
     |
     v
Export Test
     - XML validation
     - Image preview
```

### 11.3 Log Acquisition

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='topology_generator.log'
)

logger = logging.getLogger('topology_generator')
logger.setLevel(logging.DEBUG)

# Add file handler
fh = logging.FileHandler('debug.log')
fh.setLevel(logging.DEBUG)

# Add console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

logger.addHandler(fh)
logger.addHandler(ch)

# Re-run operation
gen = Generator()
topo = gen.generate(topology_spec)
```

---

## Appendix A: Complete Device Library List

| Type | Count | Description |
|------|-------|-------------|
| Routers | 45 | See section 3.2 |
| Switches | 52 | See section 3.3 |
| Security | 38 | See section 3.4 |
| Load Balancers | 18 | See section 3.5 |
| Wireless | 15 | See section 3.6 |
| Servers | 25 | See section 3.7 |
| Storage | 20 | See section 3.8 |
| Cloud Services | 55 | See section 3.9 |
| **Total** | **268** | |

## Appendix B: TDL Syntax Quick Reference

| Syntax | Example | Description |
|--------|---------|-------------|
| device type [name] [qty] | router Core x2 | Define device |
| layer name { } | layer core { } | Define layer |
| group name { } | group DMZ { } | Define group |
| container name { } | container DC { } | Define container |
| A -- B | router -- switch | Define connection |
| A --[label]--> B | SW --[10G]--> Core | Labeled connection |
| output: format | output: xml | Specify output |
| style: name | style: professional | Specify style |

---

**Version History**:

- 2.0.0 (Current): Full upgrade, supports 100+ device types, TDL language, natural language parsing, smart layout
- 1.5.0: Multi-cloud platform support added
- 1.0.0: Initial version with basic topology generation
