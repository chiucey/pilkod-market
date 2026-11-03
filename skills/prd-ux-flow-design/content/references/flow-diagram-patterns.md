# Flow Diagram Patterns

## Common User Flow Patterns

### 1. Authentication Flow

```mermaid
graph TD
    A[Start] --> B{Logged In?}
    B -->|No| C[Login Screen]
    B -->|Yes| D[Home]
    C --> E{Auth Method?}
    E -->|Email| F[Email Form]
    E -->|Social| G[OAuth Redirect]
    F --> H{Valid?}
    H -->|Yes| I[Verify]
    H -->|No| J[Show Error]
    J --> F
    I --> K{Verified?}
    K -->|Yes| D
    K -->|No| L[Resend Code]
    L --> I
    G --> D
```

### 2. CRUD Operations

```mermaid
graph TD
    A[List View] --> B[Tap Create]
    B --> C[Create Form]
    C --> D{Fill Details}
    D --> E{Valid?}
    E -->|No| F[Show Errors]
    F --> D
    E -->|Yes| G[Save]
    G --> H{Success?}
    H -->|Yes| I[Refresh List]
    I --> A
    H -->|No| J[Show Error]
    J --> G
```

### 3. Search & Filter Flow

```mermaid
graph LR
    A[Search Input] --> B{Query}
    B -->|Empty| C[Show Recent]
    B -->|Has Text| D[Search API]
    D --> E{Results?}
    E -->|Yes| F[Display Results]
    E -->|No| G[No Results]
    F --> H{Filter?}
    H -->|Yes| I[Apply Filters]
    I --> F
    H -->|No| J[Sort]
    J --> F
```

### 4. Checkout Flow

```mermaid
graph TD
    A[Cart] --> B{Tap Checkout}
    B --> C[Address Selection]
    C --> D{Select Address}
    D --> E[Payment Method]
    E --> F{Select Payment}
    F --> G[Review Order]
    G --> H{Tap Confirm}
    H --> I[Process Payment]
    I --> J{Success?}
    J -->|Yes| K[Create Order]
    K --> L[Order Confirmation]
    L --> M[Clear Cart]
    J -->|No| N[Show Error]
    N --> G
```

### 5. Pull-to-Refresh Pattern

```mermaid
graph TD
    A[Content Displayed] --> B{Pull Down}
    B --> C[Show Refresh Indicator]
    C --> D[Fetch Latest Data]
    D --> E{Data Changed?}
    E -->|Yes| F[Update Content]
    E -->|No| G[Keep Current]
    F --> H[Hide Indicator]
    G --> H
```

### 6. Infinite Scroll Pattern

```mermaid
graph TD
    A[Load Page 1] --> B[Display Items]
    B --> C{Scroll to Bottom?}
    C -->|No| B
    C -->|Yes| D[Show Loading]
    D --> E[Load Next Page]
    E --> F{Has More?}
    F -->|Yes| G[Append Items]
    G --> B
    F -->|No| H[Show End Message]
```

### 7. Form Validation Flow

```mermaid
graph LR
    A[Fill Form] --> B{Tab Away}
    B --> C[Validate Field]
    C --> D{Valid?}
    D -->|Yes| E[Green Checkmark]
    D -->|No| F[Show Error]
    F --> G[Field Highlighted]
    G --> A
```

### 8. Notification Handling

```mermaid
graph TD
    A[Receive Notification] --> B{App in Foreground?}
    B -->|Yes| C[Show In-App Banner]
    B -->|No| D{Device Locked?}
    D -->|Yes| E[Lock Screen Banner]
    D -->|No| F[Status Bar Icon]
    C --> G{Tap?}
    G -->|Yes| H[Open Relevant Screen]
    G -->|No| I[Dismiss]
    E --> H
    F --> H
```

## State Machine Patterns

### 1. Order State Machine

```mermaid
stateDiagram-v2
    [*] --> Pending: Create Order
    Pending --> Paid: Payment Success
    Pending --> Cancelled: User Cancel
    Paid --> Processing: Confirm Payment
    Processing --> Shipped: Dispatch
    Shipped --> Delivered: Confirm Receipt
    Delivered --> [*]: Complete
    Cancelled --> [*]: Refund Complete
```

### 2. Document Sync State

```mermaid
stateDiagram-v2
    [*] --> Local: Create/Edit
    Local --> Syncing: Auto-sync trigger
    Local --> Conflict: Manual sync
    Syncing --> Synced: Server ack
    Syncing --> Error: Network failure
    Error --> Syncing: Retry
    Error --> Local: Retry later
    Conflict --> Merged: Resolve
    Merged --> Synced: Save
    Synced --> Local: Edit
```

### 3. User Session State

```mermaid
stateDiagram-v2
    [*] --> Anonymous: App Launch
    Anonymous --> LoggingIn: Submit credentials
    LoggingIn --> Authenticated: Auth success
    LoggingIn --> Failed: Auth failed
    Failed --> LoggingIn: Retry
    Failed --> Anonymous: Cancel
    Authenticated --> Active: Use app
    Active --> Idle: Timeout
    Idle --> Active: User interaction
    Idle --> Expired: Session timeout
    Expired --> LoggingIn: Re-authenticate
    Authenticated --> Logout: User action
    Logout --> Anonymous: Clear session
```

## Decision Tree Patterns

### 1. Permission Request Flow

```mermaid
graph TD
    A[Feature Requires Permission] --> B{Permission Granted?}
    B -->|Yes| C[Access Feature]
    B -->|No| D{User Denied Before?}
    D -->|No| E[Show Explanation]
    E --> F[Request Permission]
    F --> G{Granted?}
    G -->|Yes| C
    G -->|No| D
    D -->|Yes| H[Guide to Settings]
    H --> I[Open App Settings]
```

### 2. Deep Link Handling

```mermaid
graph TD
    A[Receive Deep Link] --> B{App Installed?}
    B -->|No| C[Open Store]
    C --> D[Install & Open]
    D --> A
    B -->|Yes| E{App Running?}
    E -->|No| F[Cold Start]
    E -->|Yes| G[Bring to Foreground]
    F --> H[Handle Link]
    G --> H
    H --> I{Link Type?}
    I -->|Product| J[Open Product]
    I -->|Profile| K[Open Profile]
    I -->|Content| L[Open Content]
```
