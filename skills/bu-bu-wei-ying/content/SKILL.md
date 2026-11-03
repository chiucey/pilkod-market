---
name: bu-bu-wei-ying
description: 复杂APP开发统一技能，融合敏捷开发、CI/CD、DevOps最佳实践。当用户要求 bu-bu-wei-ying、进行复杂APP开发、设计多模块架构、规划开发流程、进行模块化管理、设置验证和打包流程、执行变更验证、使用敏捷开发方法、或需要大型项目开发规范时使用。
---

# Bu-Bu-Wei-Ying - Complex APP Development Unified Skill

> **Core Philosophy**: Every step must test, every layer must verify, link by link, layer by layer
>
> **Fusion Sources**: Agile Development Principles + Step-by-Step Iron Rules + Scrum/Agile + CI/CD + DevOps

## 1. Core Iron Rules

### Five Step-by-Step Principles
1. **Every Change Must Build** - Any code modification must trigger a rebuild
2. **Every Build Must Verify** - Each build must be verified as successful
3. **Every Restart Must Check** - Each restart must include log inspection
4. **Every Verification Must Test** - Each verification must execute functional testing
5. **Every Deployment Must Monitor** - Each deployment must enable monitoring

### Development Iron Rules Quick Reference
```
Code Change → Rebuild → Restart Service → Verify Function → Check Logs
     ↓            ↓            ↓              ↓              ↓
 Must Do      Must Do       Must Do         Must Do        Must View
```

---

## 2. Modular Architecture (Four-Layer Model)

### Common Layer (P0-P1)
- Logging Module
- Configuration Management Module
- Exception Handling Module

### Foundation Layer (P0-P1)
- User Authentication Module
- Content Management Module
- User Profiling Module

### Business Layer (P0-P1)
- Playback Engine Module
- Interactive Community Module
- Recommendation Algorithm Module

### Support Layer (P2)
- Message Notification Module
- Payment Settlement Module
- Data Analytics Module

### Module Development Sequence
```
P0 Core Modules: Logging → Exception Handling → User Auth → Content Management → Playback Engine
P1 Important Modules: Config Management → User Profiling → Interactive Community → Recommendation
P2 Enhancement Modules: Notifications → Payment → Analytics
Global Integration → Final Lock
```

---

## 3. Agile Development Process

### Scrum Iteration Cycle
```
Requirement Planning → Iteration Planning → Iteration Development → Agile Retrospective
        ↑                                                                        │
        └────────────────────────────────────────────────────────────────────────┘
```

### Requirements Hierarchy
```
Epic → Feature → User Story → Task
```

### Priority Management (MoSCoW)
| Priority | Meaning | Delivery Requirement |
|----------|---------|---------------------|
| P0/Must | Must Have | Absolute Delivery |
| P1/Should | Should Have | Deliver When Possible |
| P2/Could | Could Have | Selective Delivery |

---

## 4. Quality Assurance System

### CI/CD Pipeline
```
Code Commit → Static Check → Auto Build → Auto Test → Quality Gate → Deploy Release
```

### Change Verification Flow
```
Modify Code → Rebuild → Restart Service → Functional Test → Check Logs
```

### Automated Testing Levels
| Type | Coverage | Frequency |
|------|----------|-----------|
| Unit Test | Function/Method Level | Every Commit |
| Integration Test | Module Interfaces | Every Build |
| E2E Test | Complete Business Flow | Daily/Before Release |

---

## 5. Self-Check List

### Frontend Modification Self-Check
| Check Item | Verification Method |
|------------|---------------------|
| API Path Modification | Check if dist directory updated |
| Component Modification | Verify browser refresh |
| Style Modification | Check build logs |

### Backend Modification Self-Check
| Check Item | Verification Method |
|------------|---------------------|
| New Routes | Access /docs to check routes |
| Database Modification | Check table structure |
| Model Modification | Test API endpoints |

### Package Modification Self-Check
| Check Item | Verification Method |
|------------|---------------------|
| Source Code Modification | Must rebuild |
| Config Modification | Must repackage |
| Port Modification | Must restart all services |

---

## 6. API Verification Four-Step Method

```
Step 1: Backend Test
   └─ curl http://localhost:7860/api/v1/xxx

Step 2: Frontend Build
   └─ npm run build:renderer

Step 3: Package Update
   └─ npx asar pack dist resources/app.asar

Step 4: Application Restart
   └─ Full exit and restart
```

### Common Error Troubleshooting
| Error | Root Cause | Solution |
|-------|-----------|----------|
| 404 Not Found | Path mismatch | Check router prefix |
| Port Occupied | Duplicate startup | Add port detection |
| EPIPE Error | stdout closed | Disable console.log |

---

## 7. DevOps Toolchain

| Stage | Tools |
|-------|-------|
| Version Control | Git |
| CI Server | Jenkins/GitHub Actions |
| Containerization | Docker |
| Monitoring | Prometheus/Grafana |
| Logging | ELK Stack |

### Key Monitoring Metrics
| Metric | Alert Threshold |
|--------|---------------|
| Service Uptime | < 99.9% |
| Response Time P99 | > 500ms |
| API Error Rate | > 1% |

---

## 8. Team Collaboration Standards

### Daily Standup (Three Questions)
1. What did you complete yesterday?
2. What do you plan to do today?
3. What obstacles are you facing?

### Code Review Focus Areas
- Functional Correctness
- Code Quality
- Performance Considerations
- Security Considerations

---

## 9. Version Release Standards

### Release Checklist
- [ ] Code Freeze
- [ ] Testing Complete
- [ ] Documentation Updated
- [ ] Rollback Plan Ready
- [ ] Monitoring Alerts Configured
- [ ] Release Notification Sent

### Rollback Strategy
1. Confirm rollback decision (within 2 minutes)
2. Execute rollback script
3. Verify service recovery
4. Notify stakeholders
5. Locate and fix problem

---

## 10. Common Commands Quick Reference

```bash
# Check port usage
netstat -ano | findstr 7860

# Build frontend
npm run build:renderer

# Package application
npx asar pack dist resources/app.asar

# View logs
type logs\app-2026-03-24.log
```

---

**Version**: 1.0.0 | **Fusion**: Agile Development + CI/CD + DevOps + Step-by-Step Iron Rules
