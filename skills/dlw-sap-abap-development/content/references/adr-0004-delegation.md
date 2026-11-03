# ADR-0004: User Exit & BAdI Implementation via Class Delegation

**Date:** 2025-11-19
**Status:** Accepted

## Decision

**Mandate class-based delegation pattern** for all user exit and BAdI implementations. Business logic must NOT reside in user exit includes.

## Architecture Pattern

```
User Exit Package: ZPP_ENH_APOCDPS
+- Include: ZXCDPSUSERU05          <- Delegation only (5-10 lines)
|   +- Calls: zcl_pp_char_populator=>populate_characteristics(...)
|   +- Calls: zcl_another_feature=>process(...)

Feature Packages (separate):
+- ZPP_ADD_CHAR_FIELDS
|   +- ZCL_PP_CHAR_POPULATOR       <- All business logic + unit tests
+- ZPP_ANOTHER_FEATURE
    +- ZCL_ANOTHER_HANDLER
```

## Implementation Rules

1. **User exit package** - contains ONLY includes with delegation calls, no business logic
2. **Feature package** - one package per feature, contains business logic class + unit tests
3. **Naming** - handler classes: `ZCL_<MODULE>_<FEATURE>_HANDLER`
4. **Unit tests** - 80% coverage requirement on all business logic classes

## Code Templates

### User Exit Include (delegation only)

```abap
" ZXCDPSUSERU05 - Delegation only (ADR-0004)
TRY.
    zcl_pp_char_populator=>populate_characteristics(
      CHANGING cs_operation = <operation> ).
  CATCH cx_root.
    " Log error, continue
ENDTRY.
```

### Business Logic Class

```abap
CLASS zcl_pp_char_populator DEFINITION PUBLIC FINAL.
  PUBLIC SECTION.
    CLASS-METHODS populate_characteristics
      CHANGING cs_operation TYPE ci_heur_oprlist_str.
ENDCLASS.

CLASS zcl_pp_char_populator IMPLEMENTATION.
  METHOD populate_characteristics.
    " All business logic here - testable in isolation
    SELECT SINGLE floatingpointvalue
      FROM zi_vc_charval
      WHERE objectid = @cs_operation-object_id
        AND charname = 'SHEET_LENGTH'
      INTO @cs_operation-zz_sheetlength.
  ENDMETHOD.
ENDCLASS.
```

## Consequences

- Clear separation: user exits contain only wiring
- Unit testable in isolation
- Changes to one feature don't affect others
- Logic classes reusable from multiple user exits/BAdIs

## Migration Strategy

Refactor on touch: when modifying existing user exits, extract logic to class delegation pattern.
