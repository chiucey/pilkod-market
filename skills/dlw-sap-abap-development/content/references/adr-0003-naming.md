# ADR-0003: Object Naming Convention

**Date:** 2025-11-18
**Status:** Proposed

## Decision

Adopt **Delaware Consulting's ABAP naming conventions** for all custom objects. All objects use Z-namespace. Names are UPPERCASE and descriptive.

## Variable & Parameter Prefixes

### Programming Data Objects

| Object Type | Scope | Prefix | Example |
|-------------|-------|--------|---------|
| Variable | Local | `lv_` | `lv_customer_name` |
| Variable | Global | `gv_` | `gv_counter` |
| Constant | Local | `lc_` | `lc_max_records` |
| Constant | Global | `gc_` | `gc_company_code` |
| Structure | Local | `ls_` | `ls_customer` |
| Structure | Global | `gs_` | `gs_header` |
| Table | Local | `lt_` | `lt_items` |
| Table | Global | `gt_` | `gt_results` |
| Object | Local | `lo_` | `lo_instance` |
| Object | Global | `go_` | `go_factory` |
| Range | Local | `lr_` | `lr_date_range` |
| Range | Global | `gr_` | `gr_selection` |

**Field Symbols** use angle brackets: `<lv_variable>`, `<ls_line>`, `<lt_table>`

### Method Parameters

| Direction | Variable | Structure | Table | Object | Range |
|-----------|----------|-----------|-------|--------|-------|
| Importing | `iv_` | `is_` | `it_` | `io_` | `ir_` |
| Exporting | `ev_` | `es_` | `et_` | `eo_` | `er_` |
| Changing | `cv_` | `cs_` | `ct_` | `co_` | `cr_` |
| Returning | `rv_` | `rs_` | `rt_` | `ro_` | `rr_` |

### Class Attributes

| Attribute | Static (Class) | Instance |
|-----------|----------------|----------|
| Variable | `v_` | `mv_` |
| Structure | `s_` | `ms_` |
| Table | `t_` | `mt_` |
| Object | `o_` | `mo_` |
| Constants | `c_` | `mc_` |

## ABAP Object Classes

| Type | Format | Max Length | Example |
|------|--------|------------|---------|
| Interface | `ZIF<description>` | 30 | `ZIFCUSTOMER_SERVICE` |
| Class | `ZCL<description>` | 30 | `ZCLCUSTOMER_MANAGER` |
| Exception Class | `ZCX<description>` | 30 | `ZCXINVALID_CUSTOMER` |
| Local Class | `LCL<description>` | 30 | `LCLHELPER_UTIL` |

## CDS Objects

| Type | DDL Source | View Name (UpperCamelCase) | SQL View (max 16 chars) |
|------|------------|---------------------------|----------------------|
| Interface | `ZI_<name>` | `ZI1_CustomerBasic` | `ZI_CUSTBASIC` |
| Consumption | `ZC_<name>` | `ZC1_CustomerList` | `ZC_CUSTLIST` |
| Extension | `ZE_<name>` | `ZE1_CustomerExtra` | `ZE_CUSTEXT` |
| Value Help | `*_VH` suffix | `ZC1_CustomerVH` | `ZV_CUSTOMER` |

> CDS View Name must **differ** from DDL Source Name. Keep consumption view names max 28 chars for OData.

## Dictionary Objects

| Type | Format | Max | Example |
|------|--------|-----|---------|
| Table | `ZT<AppArea><desc>` | 16 | `ZTFI_CUSTOMER` |
| Table Type | `ZTT<AppArea><desc>` | 30 | `ZTTFI_CUSTOMER_TAB` |
| Data Element | `Z<desc>` | 30 | `ZCUSTOMER_NAME` |
| Append Field | `ZZ<desc>` | 16 | `ZZSPECIAL_CODE` *(append only)* |

## Application Area Codes

`FI` | `CO` | `SD` | `MM` | `PP` | `QM` | `PM` | `HR` | `PS` | `WM` | `LE` | `TR`

Cross-functional: `AI` | `UT` | `IF` | `WF`
