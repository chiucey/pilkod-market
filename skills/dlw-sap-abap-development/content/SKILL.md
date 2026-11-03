---
name: dlw-sap-abap-development
description: SAP ABAP Development Standards for S/4HANA clean core. Use when generating ABAP code, implementing BAdIs, creating CDS views, building RAP applications, setting up packages, reviewing code quality, or applying naming conventions. Triggers on: "ABAP", "S/4HANA", "CDS view", "BAdI", "RAP", "Fiori", "clean core", "user exit", "SAP development".
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 946db232ebf3eecafc44af239f080578
    PropagateID: 946db232ebf3eecafc44af239f080578
    ReservedCode1: 304502202270e1f7cbbb215dca9f827b1bde43a08edc04838b4f1441c7bd671d589f733a022100b29c34626ce86a41ac1ca7b7e298588bfea098fafd6fade89d5ebba47becf613
    ReservedCode2: 304502206b67662b6848b6c0b400a11e121d37db4ff491eab4bbff4a5e7bddcfbad1f1fc022100ee0c3189f1a807b605c81a3533655200c11a8eacdd8b00e37975c0daa3482a51
---

# SAP ABAP Development Standards

Enterprise-grade ABAP development standards for SAP S/4HANA clean core implementations.

## Core Architecture Decisions (ADRs)

| ADR | Title | Status |
|-----|-------|--------|
| ADR-0001 | Developer Extensibility for BAdI Implementations | Proposed |
| ADR-0002 | CDS Views Over Direct Database Access | Proposed |
| ADR-0003 | Object Naming Convention | Proposed |
| ADR-0004 | User Exit & BAdI via Class Delegation | Accepted |
| ADR-0005 | Custom Package Structure | Accepted |

## Naming Conventions (ADR-0003)

### Variables & Parameters

| Scope | Variable | Structure | Table | Object | Range |
|-------|----------|-----------|-------|--------|-------|
| Local | `lv_` | `ls_` | `lt_` | `lo_` | `lr_` |
| Global | `gv_` | `gs_` | `gt_` | `go_` | `gr_` |
| Importing | `iv_` | `is_` | `it_` | `io_` | `ir_` |
| Exporting | `ev_` | `es_` | `et_` | `eo_` | `er_` |
| Changing | `cv_` | `cs_` | `ct_` | `co_` | `cr_` |
| Returning | `rv_` | `rs_` | `rt_` | `ro_` | `rr_` |

### ABAP Objects

| Type | Format | Max | Example |
|------|--------|-----|---------|
| Class | `ZCL<desc>` | 30 | `ZCLCUSTOMER_MANAGER` |
| Interface | `ZIF<desc>` | 30 | `ZIFCUSTOMER_SERVICE` |
| Exception | `ZCX<desc>` | 30 | `ZCXINVALID_CUSTOMER` |

### CDS Objects

| Type | DDL Source | View Name | SQL View |
|------|------------|-----------|----------|
| Interface | `ZI_<name>` | `ZI1_CustomerBasic` | `ZI_CUSTBASIC` |
| Consumption | `ZC_<name>` | `ZC1_CustomerList` | `ZC_CUSTLIST` |
| Extension | `ZE_<name>` | `ZE1_CustomerExtra` | `ZE_CUSTEXT` |

## Package Structure (ADR-0005)

Four-level hierarchy:

```
ZAPPL                           -- Root
  +- ZAPPL_[MODULE]             -- Module (MM/PP/SD/FI/CO/CA)
      +- Z[MODULE]_[PURPOSE]    -- Purpose (APPL/CON/ENH/INT/OUT/REP/WF)
          +- Z[MODULE]_[PURPOSE]_[DESC]  -- Implementation (contains objects)
```

**ENH packages MUST match SAP enhancement name exactly:**
- `ZPP_ENH_APOCDPS` (enhancement ZAPOCDPS)
- `ZMM_ENH_MEREQ001` (user exit MEREQ001)

## Data Access (ADR-0002)

**Priority Order:**
1. Released SAP CDS (`I_*` / `C_*`) - DEFAULT
2. Custom Z-CDS (`ZI_*` / `ZC_*`)
3. Direct SELECT from Z/Y tables only
4. Direct SELECT from SAP tables - **PROHIBITED**

```abap
" [FORBIDDEN]
SELECT * FROM vbak WHERE erdat >= @lv_date.

" [REQUIRED]
SELECT FROM I_SalesOrder WHERE CreationDate >= @lv_date.
```

## BAdI Implementation (ADR-0001 + ADR-0004)

**Pattern:** Class delegation - user exit includes delegate to business logic classes.

```abap
" User Exit Include (delegation only, 5-10 lines)
TRY.
    zcl_pp_char_populator=>populate_characteristics(
      CHANGING cs_operation = <operation> ).
  CATCH cx_root.
ENDTRY.

" Business Logic Class (separate package, with unit tests)
CLASS zcl_pp_char_populator DEFINITION PUBLIC FINAL.
  PUBLIC SECTION.
    CLASS-METHODS populate_characteristics
      CHANGING cs_operation TYPE ci_heur_oprlist_str.
ENDCLASS.
```

**Required:**
- Full ABAP class in Z-namespace: `ZCL_BADI_<name>`
- ABAP Unit test class: `ZCL_TEST_BADI_<name>`
- Reference ADR in comments

## RAP Development Workflow

1. Create Database Table (`ZT*`)
2. Define CDS Interface View (`ZI_*`)
3. Create CDS Projection View (`ZC_*`)
4. Define Behavior Definition (BDEF)
5. Implement Behavior Pool (`ZBP_*`)
6. Create Service Definition (`ZUI_*`)
7. Create Service Binding (OData V4)

## Code Documentation Requirements

Every public class must have ABAP Doc header:

```abap
"! <p class="shorttext synchronized" lang="en">Sales Order Validation Engine</p>
"! This class implements credit limit checks for high-value orders (>100K).
"!
"! <strong>Architecture:</strong> ADR-0001 (BAdI pattern)<br/>
"! <strong>Dependencies:</strong> I_SalesOrder CDS view (ADR-0002)<br/>
"! <strong>Clean Core:</strong> No standard SAP modifications
"!
"! @see ADR-0001 | BAdI Implementation Standards
CLASS zcl_sales_order_validator DEFINITION PUBLIC FINAL CREATE PUBLIC.
```

## Performance Rules

| Rule | Requirement |
|------|-------------|
| P-1 | Calculations in CDS/HANA layer, not application |
| P-2 | No SELECT in LOOPs |
| P-3 | CDS views over direct table access |
| P-4 | Use HASHED tables for lookups (>1000 records) |
| P-5 | Field projection - never `SELECT *` |

## Security Requirements

- `AUTHORITY-CHECK` before all data access
- Parameterized queries (no dynamic SQL concatenation)
- Custom Z* auth objects for custom functionality
- No sensitive data in logs
- Generic error messages to users

## References

- `references/adr-0001-badi.md` - BAdI Implementation Standards
- `references/adr-0002-cds-views.md` - CDS View Standards
- `references/adr-0003-naming.md` - Naming Conventions
- `references/adr-0004-delegation.md` - Class Delegation Pattern
- `references/adr-0005-packages.md` - Package Structure
- `references/rap-reference.md` - RAP Development Guide
- `references/output-forms.md` - Forms Architecture
