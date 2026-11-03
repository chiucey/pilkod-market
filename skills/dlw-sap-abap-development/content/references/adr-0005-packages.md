---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: e21a8b0fdd094e17faf539b956d885e5
    PropagateID: e21a8b0fdd094e17faf539b956d885e5
    ReservedCode1: 30460221009fea8af32fe064d4e8b881bdcafe839b64bc096a777c39db86d2ab18240c1a9d022100fbe68a73a4e8f6f8ee770096d26ae9e7ef924d1e09c550f97ad34df1a1ace5e6
    ReservedCode2: 304402203a037bdecd7c6c7b791a692bd5b19a75947c956e2d2f1eec5346ad507bc6c29702201d00cae5beec5b3de96efe2581f7132ee8f2e94843ae0d6ab46ac78ca82eb3f3
---

# ADR-0005: Custom Package Structure

**Date:** 2025-11-19
**Status:** Accepted

## Decision

**Mandate a four-level hierarchical package structure** for all custom ABAP development.

```
Level 1: ZAPPL                              <- Single root
Level 2: ZAPPL_[MODULE]                     <- Per SAP module
Level 3: Z[MODULE]_[PURPOSE]                <- Per purpose type
Level 4: Z[MODULE]_[PURPOSE]_[DESCRIPTION]  <- Contains objects
```

> Only Level 4 packages contain actual development objects. Levels 1-3 are containers only.

## Level 2 - Module Packages

| Package | Module |
|---------|--------|
| `ZAPPL_MM` | Materials Management |
| `ZAPPL_PP` | Production Planning |
| `ZAPPL_SD` | Sales & Distribution |
| `ZAPPL_FI` | Financial Accounting |
| `ZAPPL_CO` | Controlling |
| `ZAPPL_EWM` | Extended Warehouse Management |
| `ZAPPL_QM` | Quality Management |
| `ZAPPL_PM` | Plant Maintenance |
| `ZAPPL_CA` | Cross-Application *(3+ modules only)* |

## Level 3 - Purpose Packages (7 types per module)

| Purpose | Full Name | Object Types |
|---------|-----------|-------------|
| `APPL` | Applications | Programs, tools, Fiori apps |
| `CON` | Configurations | Custom tables, config apps |
| `ENH` | Enhancements | BAdIs, user exits |
| `INT` | Integrations | OData, RFC, BTP, APIs |
| `OUT` | Outputs | Smartforms, Adobe Forms |
| `REP` | Reporting | Reports, analytical CDS |
| `WF` | Workflows | Workflow templates |

## Level 4 - Implementation Packages

General format: `Z[MODULE]_[PURPOSE]_[DESCRIPTION]`

### CRITICAL - ENH packages: Name MUST match SAP enhancement name exactly

```
ZPP_ENH_APOCDPS               <- Enhancement ZAPOCDPS (exact match!)
ZMM_ENH_MEREQ001              <- User exit MEREQ001
ZSD_ENH_BADI_SD_PRICING       <- BAdI BADI_SD_PRICING

ZPP_APPL_DEMAND_PLANNING      <- Application (descriptive)
ZPP_CON_CHAR_MAPPING          <- Configuration
ZPP_INT_MES_CONNECTION        <- Integration
ZSD_INT_BTP_ORDERS_API        <- BTP integration (belongs in SD's INT)
ZCA_APPL_AUTHORIZATION_MGR    <- Cross-app utility (3+ modules)
```

## Package Assignment Decision Tree

```
Is it used by 3+ modules?
+- YES -> ZAPPL_CA -> Z[CA]_[PURPOSE]_[DESC]
+- NO  -> Select module (MM/PP/SD/FI...)
         Select purpose:
         +- Standalone app/tool?    -> APPL -> Z[M]_APPL_[DESC]
         +- Config table/app?       -> CON  -> Z[M]_CON_[DESC]
         +- BAdI/user exit?         -> ENH  -> Z[M]_ENH_[EXACT_ENHANCEMENT_NAME]
         +- API/OData/BTP?          -> INT  -> Z[M]_INT_[DESC]
         +- Form/print?             -> OUT  -> Z[M]_OUT_[DESC]
         +- Report/analytics?       -> REP  -> Z[M]_REP_[DESC]
         +- Workflow?               -> WF   -> Z[M]_WF_[DESC]
```

## Cross-Application (CA) Rules

- Use `ZAPPL_CA` when: used by 3+ modules, core utility (auth/logging/error handling)
- Do NOT use when: primarily serves one module, or usage is uncertain
