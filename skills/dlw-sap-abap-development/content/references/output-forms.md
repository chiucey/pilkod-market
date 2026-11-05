---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 3d259081b6f2691cc3e68075e4698811
    PropagateID: 3d259081b6f2691cc3e68075e4698811
    ReservedCode1: 304502203a4c7fed2af8216473d97950f0fae5aac840bbda59d38321df1dc28aa417aff0022100a85ed6ba32af2ef8f8e4fe26c88bbf0fb100f461b49a5527c000cfa99a308e8b
    ReservedCode2: 30450221009e3e2f46d35315babd49b4ad6cab72dc961fa94851d9183110be00213e02d0ab022075ebc9807c4a083772094f00cb99bd9e5ee2c4f4816f74b7375ccd8018b43f1d
---

# SAP S/4HANA Forms Architecture

**Version:** 2.0 | **Last Updated:** October 2025

## Technology Overview

| Technology | Status | Use Case |
|------------|--------|----------|
| **SAPscript** | Legacy/Supported | Simple documents |
| **Smart Forms** | Legacy/Supported | Complex layouts |
| **Adobe Forms** | Recommended | Interactive PDFs, archiving |
| **BRF+ Integration** | Standard (S/4HANA 1610+) | Output management |
| **Forms Service by Adobe** | Cloud-First (2023+) | SaaS-based PDF |

## BRF+ Object Model

```
Application (FDT_APPL_*)
|
+-- Context (Input Parameters)
|   +-- Data Objects
|   +-- Database Lookups
|   +-- Importing Parameters
|
+-- Functions (Processing Logic)
|   +-- Decision Tables
|   +-- Formula Expressions
|   +-- Rule Sets
|
+-- Result (Output Parameters)
```

## Decision Table Structure

```
+--------------------------------------------------------+
|                    DECISION TABLE                        |
+--------------------------------------------------------+
| Condition Columns        |  Result Columns              |
+-------------+-----------+-------------+----------------+
| Doc Type    | Sales Org | Form Template| Output Channel|
+-------------+-----------+-------------+----------------+
| OR          | 1000      | Z_INV_TEMP_DE| EMAIL         |
| OR          | 2000      | Z_INV_TEMP_EN| PRINT         |
| IV          | *         | Z_CREDIT_NOTE | EMAIL         |
| *           | *         | Z_DEFAULT     | PRINT         |
+-------------+-----------+-------------+----------------+
```

## Output Management Framework

```
+------------------------------------------------------+
|         Output Parameter Determination (OPD)           |
+------------------------------------------------------+
|  - Form Template Selection (BRF+)                     |
|  - Recipient Determination (BRF+)                     |
|  - Channel Selection (BRTP+)                         |
|  - Timing Control (Immediate/Deferred)               |
+------------------------------------------------------+
```

## Configuration Transactions

| Transaction | Description |
|------------|-------------|
| **OPD** | Output Parameter Determination |
| **NACE** | Output Control (legacy compatibility) |
| **FDT_WORKBENCH** | BRF+ Workbench |
| **SBGRFCMON** | bgRFC Monitor |
| **SLG1** | Application Log |

## Form Data Provider Best Practices

```abap
FUNCTION z_fp_invoice_provide_data.
  " 1. Input Validation
  IF iv_invoice_number IS INITIAL.
    RAISE EXCEPTION TYPE zcx_form_error.
  ENDIF.

  " 2. Data Selection (Single SELECT for performance)
  SELECT SINGLE vbeln, fkdat, kunrg, netwr, waerk
    FROM vbrk
    INTO @DATA(ls_header)
    WHERE vbeln = @iv_invoice_number.

  " 3. Related Data (Optimized with FOR ALL ENTRIES)
  SELECT matnr, arktx, fkimg, vrkme, netwr
    FROM vbrp
    INTO TABLE @DATA(lt_items)
    WHERE vbeln = @iv_invoice_number
    ORDER BY posnr.

  " 4. Data Transformation
  es_form_data-header = CORRESPONDING #( ls_header ).
ENDFUNCTION.
```

## Form Interface Structure

```abap
TYPES: BEGIN OF ty_header,
         invoice_no    TYPE vbeln_vf,
         invoice_date  TYPE fkdat,
         customer_no   TYPE kunnr,
         customer_name TYPE name1_gp,
         total_amount  TYPE wrbtr,
         currency      TYPE waers,
       END OF ty_header.

TYPES: BEGIN OF ty_item,
         item_no       TYPE posnr_vf,
         material_no   TYPE matnr,
         description   TYPE arktx,
         quantity      TYPE fkimg,
         unit          TYPE vrkme,
         unit_price    TYPE netpr,
         line_total    TYPE wrbtr,
       END OF ty_item.

TYPES: ty_items TYPE STANDARD TABLE OF ty_item.

TYPES: BEGIN OF ty_form_data,
         header TYPE ty_header,
         items  TYPE ty_items,
         logo   TYPE xstring,
       END OF ty_form_data.
```

## Output Channels

| Channel | Implementation |
|---------|----------------|
| Print | Spool |
| Email | SMTP via SCOT |
| Archive | Content Server (PDF/A) |
| XML/EDI | File/IDoc |

## Performance Targets

| Document Complexity | Target | Max |
|-------------------|--------|-----|
| Simple (1 page) | < 1s | 2s |
| Standard (2-5 pages) | < 3s | 5s |
| Complex (10+ pages) | < 10s | 15s |

## Naming Conventions

| Object Type | Prefix | Example |
|-------------|--------|---------|
| Application | `Z_APPL_` | `Z_APPL_SD_OUTPUT` |
| Function | `Z_FUNC_` | `Z_FUNC_DET_FORM` |
| Decision Table | `Z_DT_` | `Z_DT_FORM_SELECTION` |
| Data Object | `Z_DO_` | `Z_DO_CUSTOMER_DATA` |
| Action | `Z_ACT_` | `Z_ACT_SEND_EMAIL` |
