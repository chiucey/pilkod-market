# Agent Team Orchestration Framework
## Version 4.0.0

A production-grade multi-Agent collaboration framework for MaxClaw, featuring standardized handoff protocols, quality iron rules, and comprehensive monitoring capabilities.

## Overview

This framework provides comprehensive multi-Agent team orchestration with the following key features:

- **Team Architecture Design**: Support for hierarchical, mesh, and hybrid organizational structures
- **Standardized Handoff Protocol**: 5-element handoff messages ensuring seamless agent collaboration
- **Quality Iron Rules**: Mandatory review mechanisms preventing quality degradation
- **Intelligent Task Assignment**: Capability-based matching algorithm
- **Comprehensive Monitoring**: KPI dashboards and real-time alerting
- **Scenario Templates**: Predefined collaboration patterns for rapid setup

## Installation

### Method 1: Direct Import

1. Create an `agent-team-orchestration` folder in your MaxClaw Agent's Skills directory
2. Maintain the directory structure as shown below
3. Import via the MaxClaw Agent Skill loading interface

### Method 2: File Copy

Copy all files to your skills directory:

```
agent-team-orchestration/
├── SKILL.md                    # Main skill documentation
├── _meta.json                  # Skill metadata
├── src/
│   └── main.py                 # Entry point with orchestration logic
├── config/
│   └── settings.yaml           # Configuration file
├── instructions/
│   └── system_prompt.md        # Orchestrator role prompt
├── tests/
│   └── test_main.py            # Unit tests
├── assets/
│   └── .gitkeep                # Asset directory placeholder
└── README.md                    # This file
```

## Usage

### Trigger Keywords

Use the following keywords to activate the framework:

- "agent team"
- "orchestration"
- "multi-agent"
- "task lifecycle"
- "handoff"
- "team collaboration"

### Quick Start: 2-Agent Setup

1. **Define Roles**:
   - You (Orchestrator): Route, track, report
   - Builder: Execute and generate artifacts

2. **Initiate Task**:
   1. Create task record
   2. Send instructions with TaskID, description, output path, handoff requirements
   3. After Builder completes, review, mark status, and report

3. **Add Reviewer (Advanced)**:
   - Flow: Builder → Reviewer → Orchestrator (Ship/Rework)

### Handoff Protocol

When transferring tasks, always include these 5 elements:

1. **Completed Work**: Summary of changes/outputs
2. **Artifact Location**: Exact file path
3. **Verification Method**: Test command or acceptance criteria
4. **Known Issues**: Incomplete items or potential risks
5. **Next Action**: Clear task for receiver

Example:
```
✅ "Auth module built at `/shared/artifacts/auth/`. Run `npm test auth` to verify.
Known issue: rate limiting not implemented. Next: Please review edge cases."
```

### Quality Iron Rules

> **IRON RULE**: Every artifact must pass through at least one pair of non-producer eyes.

| Rule | Who | When |
|------|-----|------|
| Builder Reviews Spec | Builder | Before starting |
| Reviewer Reviews Build | Reviewer | Against spec |
| Orchestrator Reviews Priority | Orchestrator | Before starting |

## Configuration

Edit `config/settings.yaml` to customize:

- Shared artifact paths
- Team size limits
- Task lifecycle settings
- Handoff validation rules
- Quality enforcement
- Monitoring thresholds
- Role-to-model mappings

## Running Tests

```bash
cd tests
python -m pytest test_main.py -v
```

Or:

```bash
python src/main.py
```

## Architecture

### Role Definitions

| Role | Responsibilities | Model Type |
|------|------------------|------------|
| Orchestrator | Task routing, state tracking | High-reasoning |
| Builder | Artifact generation | Cost-effective |
| Reviewer | Quality verification | High-reasoning |
| Ops | Scheduled tasks, health checks | Stable low-cost |
| Researcher | Information collection | Balanced |
| Analyst | Deep analysis, insights | High-reasoning |

### Task Lifecycle

```
Inbox → Assigned → In Progress → Review → Done | Failed
```

## Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| No clear output path | Always specify `/shared/artifacts/` subpath |
| Skipping reviews | Never skip for "minor" changes |
| Agent silence | Require Start/Blocker/Handoff/Done |
| Capability mismatch | Verify before assignment |
| Orchestrator doing work | Stay at 30,000 feet |

## Version History

### v4.0.0 (Current)
- Fusion release combining comprehensive functionality with engineering excellence
- Multi-file structure with executable code
- 5-element standardized handoff protocol
- Quality iron rules with mandatory enforcement
- Enhanced role definitions with model recommendations
- Configurable KPI monitoring dashboards
- Scenario template library

### v3.9.0
- Monitoring metrics system enhancements
- Scenario template library

### v3.8.2
- Initial comprehensive framework

## License

This framework is provided as-is for MaxClaw Agent usage.

## Support

For issues or questions, please refer to the SKILL.md documentation.
