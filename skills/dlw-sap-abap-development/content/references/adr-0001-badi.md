---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f096d340bc63798887a35e5ea7077670
    PropagateID: f096d340bc63798887a35e5ea7077670
    ReservedCode1: 3044022062ec3e624844dec7788cd351b7661fd12c14beb6d0fc51aeee078823b77f72f702206b0d97b6648ef0eab8e0dd0ff74f56445356bc8575a5eb3d24092019fa967f5b
    ReservedCode2: 30440220462bc2607762d3cfc8837b7e1e2b32363b6c23c90d4b376b3de5de12e02c4ee4022053d9dc28f6c525f97371db28fc5883cbf89f2c0592683cceecd73f7d55e8e045
---

# ADR-0001: Developer Extensibility for BAdI Implementations

**Date:** 2025-11-17
**Status:** Proposed

## Decision

Use **Developer Extensibility (ADT/Eclipse)** as the default approach for all BAdI implementations.

- All BAdIs implemented as Z-namespace ABAP classes in ADT
- Mandatory ABAP Unit tests for all implementations
- Version control via Git/gCTS
- Use released APIs only; no standard object modifications

> **Exception:** Key User Extensibility allowed only for simple business-user-maintained validations with explicit architecture approval.

## Context Summary

S/4HANA supports both Key User Extensibility (no-code, in-app) and Developer Extensibility (full ABAP, ADT). Key user tools limit AI code generation and DevOps integration. Developer extensibility enables programmatic generation, testing, and Git-based workflows.

## Consequences

- AI agents can generate, test, and validate complete BAdI implementations
- Full Git version control and DevOps workflows
- ABAP Unit testing for automated quality assurance
- Clean core compliance via Z-namespace and released APIs

## AI Guardrails

**ALWAYS:**
- Generate full ABAP class in Z-namespace: `ZCL_BADI_<name>`
- Include ABAP Unit test class: `ZCL_TEST_BADI_<name>`
- Use only released SAP APIs
- Reference ADR-0001 in comments

**NEVER:**
- Suggest key user extensibility as default
- Modify SAP standard objects
- Use unreleased APIs or direct table access
- Skip unit test generation
