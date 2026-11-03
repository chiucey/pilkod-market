# Domain Rubric

Use this reference for reviews in low-altitude unmanned systems, UAV photogrammetry/remote sensing, spatiotemporal intelligence, route network planning, and air-ground cooperative networking.

## Core Domain Lanes

### Low-Altitude Unmanned Systems

A strong review should connect:
- Vehicles: multirotor, fixed-wing, VTOL, airships, high-altitude platforms when relevant.
- Missions: logistics, inspection, emergency response, mapping, surveillance, agriculture, urban services.
- Operating environment: dense urban canyons, rural areas, disaster zones, weather, terrain, GNSS-denied areas, communications gaps.
- System constraints: battery/endurance, payload, sensing, computation, regulation, safety, privacy, cyber-security, social acceptance.
- Operational layers: perception, navigation, communication, route planning, traffic management, command/control, fleet scheduling, maintenance.

Red flags:
- Treating UAVs as generic mobile sensors with no airspace, safety, or endurance constraints.
- Discussing algorithms without operational assumptions.
- Ignoring regulation, detect-and-avoid, contingency management, or human oversight when claiming deployment readiness.

### UAV Photogrammetry and Remote Sensing

Check whether the review explains:
- Sensor classes: RGB, multispectral, hyperspectral, thermal, LiDAR, SAR, event cameras, GNSS/IMU, ground sensors.
- Acquisition geometry: flight altitude, overlap, baseline, viewing geometry, rolling shutter, radiometry, illumination, platform motion.
- Georeferencing: GCPs, RTK/PPK, bundle adjustment, SfM/MVS, SLAM, co-registration, coordinate frames.
- Products: orthomosaics, DSM/DTM, point clouds, 3D meshes, semantic maps, change maps, object inventories.
- Accuracy and uncertainty: spatial accuracy, radiometric calibration, classification metrics, ground truth quality, propagation of error.
- Transferability: cross-site, cross-season, cross-sensor, cross-resolution, cross-platform performance.

Red flags:
- No distinction between photogrammetric accuracy, classification accuracy, and application-level utility.
- Taxonomy organized by fashionable algorithms but not by sensing problem or information product.
- Missing calibration/validation discussion.
- Comparing papers with incompatible datasets, metrics, or spatial scales.

### Spatiotemporal Intelligent Perception

Check whether the review covers:
- Representation: raster, vector, graph, point cloud, trajectory, event stream, time series, multimodal embeddings.
- Modeling: CNN/Transformer/GNN/RNN/state-space models, foundation models, diffusion/generative models, physics-informed or causal models.
- Spatiotemporal issues: non-stationarity, irregular sampling, multi-scale processes, latency, missing data, drift, event detection.
- Perception stack: detection, segmentation, tracking, change detection, scene understanding, forecasting, anomaly detection, decision support.
- Robustness: domain adaptation, uncertainty estimation, out-of-distribution detection, adversarial/weather/occlusion stressors.
- Deployment: edge/cloud split, onboard inference, communication-limited sensing, energy/latency tradeoffs, real-time constraints.

Red flags:
- Claiming "intelligence" while only listing model architectures.
- Ignoring data quality, annotation bias, domain shift, and failure modes.
- No bridge from perception outputs to planning/control/networking decisions.

### Low-Altitude Route/Airway Network Planning

Check whether the review includes:
- Network representation: nodes/edges/corridors/volumes/layers, 2D vs 3D vs 4D, static vs dynamic networks.
- Constraints: no-fly zones, altitude layers, obstacle clearance, separation minima, noise, privacy, risk over population, weather, energy.
- Objectives: safety, capacity, travel time, reliability, equity, energy, emissions, noise, cost, service quality.
- Methods: graph theory, multi-objective optimization, stochastic optimization, robust planning, reinforcement learning, simulation, digital twins.
- Operations: demand modeling, scheduling, deconfliction, contingency routes, emergency priority, vertiports, charging/swapping, fleet management.
- Validation: real airspace data, urban morphology, demand scenarios, weather scenarios, sensitivity analysis, stress tests.

Red flags:
- Treating route planning as shortest path without airspace management.
- No distinction between strategic network design, pre-flight planning, and real-time tactical deconfliction.
- No discussion of scalability, safety assurance, or integration with ground transport.

### Air-Ground Cooperative Networking and Space-Air-Ground Integration

Check whether the review covers:
- Architecture: UAV ad hoc networks, aerial base stations, satellite-aerial-terrestrial integration, IoT/MEC/cloud-edge collaboration.
- Channel and mobility: air-ground channel models, blockage, fading, Doppler, interference, handover, topology dynamics.
- Resource dimensions: spectrum, power, bandwidth, compute, storage, trajectory, task offloading, energy.
- Protocols: routing, scheduling, multiple access, beamforming, RIS, security, privacy, resilience.
- Co-design: trajectory-communication, sensing-communication-computation, task-network-airspace coupling.
- Evaluation: realistic mobility, channel assumptions, workload models, QoS/QoE, delay, reliability, energy, fairness, security.

Red flags:
- Communication is treated as a black box.
- No channel/interference model when making wireless claims.
- No coupling between UAV mobility and network resource allocation.
- The review ignores testbeds/prototypes when claiming maturity.

## Review Quality Rubric

Score each axis from 0-3.

| Axis | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- |
| Field problem | No clear problem | General motivation | Specific timely problem | Field-level problem with stakes |
| Taxonomy | List of topics | Conventional categories | Useful organizing framework | Framework changes how field is understood |
| Evidence coverage | Patchy | Covers common papers | Balanced and current | Balanced, current, cross-community, and explains omissions |
| Synthesis | Paper-by-paper summary | Some comparisons | Clear patterns and tensions | Generates new insights, agenda, or decision logic |
| Technical depth | Superficial | Adequate basics | Strong technical interpretation | Deep cross-layer/system reasoning |
| Validation awareness | Absent | Mentions datasets/metrics | Compares validation practices | Explains uncertainty, transferability, and benchmark limits |
| Interdisciplinary fit | Single-silo | Adjacent fields named | Cross-field links explained | Integrates sensing, planning, networking, and operations |
| Figures/tables | Decorative | Summaries | Useful synthesis | Essential intellectual scaffolding |
| Future agenda | Generic | Trend list | Specific open problems | Prioritized roadmap with testable research questions |

## Required Matrices for Strong Reviews

Encourage the author to add or improve these when missing:

- **Landscape matrix**: problem class x sensing/platform/network/planning method x application domain.
- **Benchmark matrix**: dataset, platform, scale, sensor, metric, baseline, validation type, limitations.
- **Assumption matrix**: airspace/weather/channel/demand/energy/safety assumptions and their consequences.
- **Maturity matrix**: concept, simulation, offline benchmark, field test, operational deployment.
- **Gap-to-agenda matrix**: unresolved gap, why it persists, needed data/method/system change, likely impact.

## Figure Blueprint

High-value figures for this domain:

1. Layered low-altitude system architecture from sensing to networking to route planning to operations.
2. Taxonomy of UAV remote-sensing products and processing chains.
3. 4D low-altitude route network and deconfliction workflow.
4. Space-air-ground integrated network architecture with sensing-communication-computation loops.
5. Timeline of field inflection points, not just publication count.
6. Failure-mode map linking technical failure to operational risk.
7. Roadmap from data/model/system gaps to deployable low-altitude infrastructure.

## Common Reviewer Objections

- "The scope is too broad and the manuscript lacks a controlling question."
- "The taxonomy follows paper categories rather than real system problems."
- "The review does not distinguish simulation assumptions from deployable systems."
- "Important work from photogrammetry/transportation/communications is missing."
- "The manuscript overstates AI progress without discussing data quality and domain shift."
- "The figures summarize content but do not synthesize mechanisms or decisions."
- "The conclusion lists trends but does not provide a research agenda."