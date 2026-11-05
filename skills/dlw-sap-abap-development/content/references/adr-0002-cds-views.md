---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 1b7e87b6db2278addbaae06befe62679
    PropagateID: 1b7e87b6db2278addbaae06befe62679
    ReservedCode1: 3045022100a4747cd6e7a1dd44b0dc53107a49270632d034ead9346c5147dd7b8472cd077402200bcbe2134a2b150ee540a1637ce10bca542def47c70f09f978f1a945f575c0c2
    ReservedCode2: 30450220646fc85efdf690f9e85791e4b1ddad0fa4a2a9012501a9f2a79802dd3a97a857022100d8f81122e1be29a0b0d01fd25e908ca972efdf9690933bb63f0adad2f945e5af
---

# ADR-0002: CDS Views Over Direct Database Access

**Date:** 2025-11-17
**Status:** Proposed

## Decision

**Mandate CDS views for all data access** in custom code. Prohibit direct `SELECT` from SAP standard tables.

**Data Access Priority:**
```
1. Released SAP CDS (I_*, C_*)  <- DEFAULT for SAP data
2. Custom Z-CDS (ZI_*, ZC_*)    <- For custom tables/extensions
3. Direct SELECT                 <- Z/Y custom tables ONLY
4. SELECT FROM vbak/kna1/...    <- PROHIBITED
```

## Key Rules

### Rule P-3: CDS Views Over Direct Table Access (Mandatory)

Priority order:
1. Released SAP CDS views (`I_*` / `C_*`) - PREFERRED
2. Custom Z-namespace CDS views (`ZI_*` / `ZC_*`)
3. Direct SELECT from Z/Y custom tables only
4. Direct SELECT from SAP standard tables - PROHIBITED

```abap
" FORBIDDEN
SELECT * FROM vbak WHERE erdat >= @lv_date.
SELECT * FROM kna1 WHERE kunnr = @lv_customer.

" REQUIRED
SELECT FROM I_SalesOrder WHERE CreationDate >= @lv_date.
SELECT FROM I_Customer    WHERE Customer    =  @lv_customer.
```

### Rule P-5: Field Projection

Never use `SELECT *` - always specify fields.

```abap
" FORBIDDEN
SELECT * FROM I_SalesOrder INTO TABLE @DATA(lt_orders).

" REQUIRED - list only needed fields
SELECT FROM I_SalesOrder
  FIELDS SalesOrder, NetAmount, Currency
  WHERE CreationDate >= @lv_date
  INTO TABLE @DATA(lt_orders).
```

## Consequences

- Upgrade safety: Table structure changes don't break custom code
- Performance: 10-100x faster with HANA code pushdown
- Clean core compliance
- Built-in authorization and row-level security
