---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: b6eb564b970f8c3b9f4372f16a6bff15
    PropagateID: b6eb564b970f8c3b9f4372f16a6bff15
    ReservedCode1: 3046022100ee55304c1edae8c8c14f731f01ecbb94738bc879f59be7187c69b791a8092710022100cdd71986171a7be897b8e3a4d411fd5e6018d818ca7e006fc9c3c8a31a8c8b9b
    ReservedCode2: 3046022100a5633b3c6ac8f4a72f8d87689cdb763894451fb1c1359c5693e7d4b66cbd6871022100ca913aa1dd65f5b024a5987fe6d15f14e29e977646042b1b1ba8df9010680ac3
---

# SAP RAP Complete Reference

**Version:** 2.0 | **Last Updated:** October 2025
**Platform:** SAP S/4HANA 2022+ / ABAP Cloud | Fiori Elements V4

## Architecture Layers

```
+-----------------------------------------------+
|         UI Layer (Fiori Elements)             |
+-----------------------------------------------+
|    Business Service (OData V4)                 |
+-----------------------------------------------+
|    Behavior Definition (BDEF)                  |
+-----------------------------------------------+
|    CDS Projection Views (ZC_*)                 |
+-----------------------------------------------+
|    CDS Interface Views (ZI_*)                   |
+-----------------------------------------------+
|    Database Tables                            |
+-----------------------------------------------+
```

## Development Workflow

1. Create Database Table
2. Define CDS Interface View (`ZI_*`)
3. Create CDS Projection View (`ZC_*`)
4. Define Behavior Definition (BDEF)
5. Implement Behavior Pool (`ZBP_*`)
6. Create Service Definition (`ZUI_*`)
7. Create Service Binding (OData V4)

## Naming Conventions

| Object | Prefix | Example |
|--------|--------|---------|
| Interface View | `ZI_` | `ZI_Travel` |
| Projection View | `ZC_` | `ZC_Travel` |
| Behavior Pool | `ZBP_` | `ZBP_I_Travel` |
| Service Definition | `ZUI_` | `ZUI_Travel_O4` |
| Database Table | `Z*` | `ZTRAVEL` |

## Interface View Template

```abap
@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'Travel - Interface View'
@Metadata.allowExtensions: true

define root view entity ZI_Travel
  as select from ztravel as Travel

  composition [0..*] of ZI_Booking      as _Booking
  association [0..1] to /DMO/I_Agency   as _Agency
    on $projection.AgencyID = _Agency.AgencyID
{
  key Travel.travel_id              as TravelID,

      @Semantics.user.createdBy: true
      Travel.created_by             as CreatedBy,
      @Semantics.systemDateTime.lastChangedAt: true
      Travel.last_changed_at        as LastChangedAt,

      @Semantics.amount.currencyCode: 'CurrencyCode'
      Travel.total_price            as TotalPrice,

      Travel.overall_status         as OverallStatus,
      Travel.begin_date             as BeginDate,
      Travel.end_date               as EndDate,

      _Booking, _Agency
}
```

## BDEF Template (Managed)

```abap
managed implementation in class zbp_i_travel unique;
strict(2);
with draft;

define behavior for ZI_Travel alias Travel
persistent table ztravel
draft table ztravel_d
etag master LocalLastChangedAt
lock master total etag LastChangedAt
authorization master ( global, instance )
{
  create; update; delete;

  field ( readonly ) CreatedBy, CreatedAt, LastChangedAt;
  field ( mandatory ) AgencyID, CustomerID, BeginDate, EndDate;
  field ( readonly : update ) TravelID;

  association _Booking { create; with draft; }

  validation validateAgency   on save { field AgencyID; create; update; }
  validation validateDates    on save { field BeginDate, EndDate; create; update; }

  determination calculateTravelID   on modify { create; }
  determination calculateTotalPrice on modify { field BookingFee; update; }

  action ( features : instance ) acceptTravel result [1] $self;
  action ( features : instance ) rejectTravel result [1] $self;

  draft action Edit;
  draft action Activate optimized;
  draft action Discard;
  draft determine action Prepare;

  side effects {
    field BookingFee affects field TotalPrice;
  }

  mapping for ztravel {
    TravelID = travel_id; AgencyID = agency_id;
  }
}
```

## MODIFY ENTITIES Patterns

```abap
" CREATE
MODIFY ENTITIES OF zi_entity ENTITY entity
  CREATE FIELDS ( Name Amount ) WITH VALUE #( ( %cid = 'CID1' Name = 'Test' Amount = 100 ) )
  MAPPED DATA(mapped) FAILED DATA(failed) REPORTED DATA(reported).

" UPDATE
MODIFY ENTITIES OF zi_entity ENTITY entity
  UPDATE FIELDS ( Status ) WITH VALUE #( ( ID = '001' Status = 'A' ) )
  FAILED DATA(failed).

" DELETE
MODIFY ENTITIES OF zi_entity ENTITY entity
  DELETE FROM VALUE #( ( ID = '001' ) ) FAILED DATA(failed).

" EXECUTE ACTION
MODIFY ENTITIES OF zi_entity ENTITY entity
  EXECUTE acceptTravel FROM VALUE #( ( ID = '001' ) )
  RESULT DATA(result) FAILED DATA(failed).

" COMMIT
COMMIT ENTITIES RESPONSE OF zi_entity
  FAILED DATA(commit_failed) REPORTED DATA(commit_reported).
```

## READ ENTITIES Patterns

```abap
" Read all fields
READ ENTITIES OF zi_entity ENTITY entity
  ALL FIELDS WITH VALUE #( ( ID = '001' ) ) RESULT DATA(entities).

" Read specific fields
READ ENTITIES OF zi_entity ENTITY entity
  FIELDS ( Name Status ) WITH VALUE #( ( ID = '001' ) ) RESULT DATA(entities).

" Read by association
READ ENTITIES OF zi_entity ENTITY entity BY \_item
  ALL FIELDS WITH VALUE #( ( ID = '001' ) ) RESULT DATA(items).

" Read in local mode (inside behavior implementation)
READ ENTITIES OF zi_entity IN LOCAL MODE
  ENTITY entity ALL FIELDS WITH CORRESPONDING #( keys ) RESULT DATA(entities).
```

## Validation Implementation

```abap
METHOD validateAgency.
  READ ENTITIES OF zi_travel IN LOCAL MODE
    ENTITY travel FIELDS ( AgencyID ) WITH CORRESPONDING #( keys )
    RESULT DATA(travels).

  SELECT FROM /dmo/agency FIELDS agency_id
    FOR ALL ENTRIES IN @travels WHERE agency_id = @travels-AgencyID
    INTO TABLE @DATA(valid).

  LOOP AT travels INTO DATA(travel)
    WHERE NOT line_exists( valid[ agency_id = travel-AgencyID ] ).
    APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
    APPEND VALUE #(
      %tky = travel-%tky
      %msg = new_message_with_text( severity = if_abap_behv_message=>severity-error
                                    text = |Agency { travel-AgencyID } does not exist| )
      %element-agencyid = if_abap_behv=>mk-on
    ) TO reported-travel.
  ENDLOOP.
ENDMETHOD.
```

## Anti-Patterns to Avoid

1. **God Entity Syndrome** - One BDEF with 47 fields, 23 validations
2. **Validation Soup** - One method with 300 IF statements
3. **Anemic BDEF** - Only CRUD, no business value
4. **No Authorization** - YOLO auth checks
5. **SELECT in Loop** - N+1 query problems

## Authorization Implementation

```abap
METHOD get_global_authorizations.
  IF requested_authorizations-%create EQ if_abap_behv=>mk-on.
    AUTHORITY-CHECK OBJECT 'Z_TRAVEL' ID 'ACTVT' FIELD '01'.
    result-%create = COND #( WHEN sy-subrc = 0
                             THEN if_abap_behv=>auth-allowed
                             ELSE if_abap_behv=>auth-unauthorized ).
  ENDIF.
ENDMETHOD.
```

## Core Principles

- **Clean Core**: Upgrade-safe, Z-namespace extensions only
- **Declarative**: Annotations over code where possible
- **API-First**: OData V4 by default
- **Draft-Enabled**: Built-in draft support
- **strict(2)**: Always use for compile-time safety
