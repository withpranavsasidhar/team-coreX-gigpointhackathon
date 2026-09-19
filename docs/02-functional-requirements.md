# A.R.I.A. — Functional Requirements Document
## Detailed Functional Specification

**Project:** A.R.I.A. (Adaptive Retail Intelligence Assistant) - Smart Voice Inventory Assistant
**Document Version:** 1.0
**Date:** September 19, 2026
**Document Type:** Functional Requirements Document (FRD)

---

## Table of Contents

1. [Entity Extraction Schema](#entity-extraction-schema)
2. [Confidence Behavior Definition](#confidence-behavior-definition)
3. [Ambiguous Product Name Handling](#ambiguous-product-name-handling)
4. [Supported Natural-Language Questions](#supported-natural-language-questions)
5. [Inventory Operations Definition](#inventory-operations-definition)
6. [Business Rules](#business-rules)
7. [Module Specifications](#module-specifications)
   - Module 1: Authentication & Business Setup
   - Module 2: Product Management
   - Module 3: Inventory Management
   - Module 4: Voice Processing
   - Module 5: Language Understanding
   - Module 6: Business Event Engine
   - Module 7: Business Memory / Event Ledger
   - Module 8: Natural Language Stock Assistant
   - Module 9: Stock Alerts
   - Module 10: Reorder Intelligence
   - Module 11: Inventory Investigation / WHY Engine
   - Module 12: Inventory Discrepancy Detection

---

## Entity Extraction Schema

### Standard Event Extraction Schema

```json
{
  "event_type": "STOCK_IN | SALE | STOCK_OUT | PURCHASE | CREDIT_SALE | RETURN | DAMAGE | LOSS | ADJUSTMENT",
  "product": {
    "id": "string (uuid)",
    "name": "string",
    "normalized_name": "string",
    "category": "string (optional)",
    "match_confidence": "number (0-1)"
  },
  "quantity": {
    "value": "number (positive)",
    "unit": "string",
    "normalized_value": "number (after conversion)",
    "normalized_unit": "string (base unit)",
    "conversion_applied": "boolean"
  },
  "price": {
    "value": "number (optional)",
    "currency": "string (optional, default: INR)",
    "total_value": "number (optional, quantity * price)"
  },
  "customer": {
    "id": "string (uuid, optional)",
    "name": "string (optional)",
    "phone": "string (optional)",
    "match_confidence": "number (0-1, optional)"
  },
  "payment_status": "CASH | CREDIT | PARTIAL | PENDING (optional)",
  "due_date": "string (ISO 8601 date, optional)",
  "timestamp": {
    "extracted": "string (ISO 8601 datetime)",
    "normalized": "string (ISO 8601 datetime)",
    "is_relative": "boolean"
  },
  "source": "voice | text | api",
  "original_text": "string",
  "normalized_text": "string",
  "language_detected": "string (ISO 639-1 code)",
  "confidence": {
    "overall": "number (0-1)",
    "event_type": "number (0-1)",
    "product": "number (0-1)",
    "quantity": "number (0-1)",
    "unit": "number (0-1)",
    "customer": "number (0-1, optional)"
  },
  "metadata": {
    "stt_provider": "string (optional)",
    "llm_provider": "string (optional)",
    "processing_time_ms": "number (optional)"
  }
}
```

### Simplified Schema for MVP

```json
{
  "event_type": "STOCK_IN | SALE | STOCK_OUT",
  "product": "string",
  "quantity": "number",
  "unit": "string",
  "confidence": "number (0-1)",
  "original_text": "string"
}
```

---

## Confidence Behavior Definition

### Confidence Thresholds

| Confidence Range | Behavior | UI Display |
|------------------|----------|------------|
| 0.85 - 1.00 | HIGH CONFIDENCE | Auto-confirm after validation. Show brief confirmation toast. |
| 0.60 - 0.84 | MEDIUM CONFIDENCE | Show confirmation dialog with extracted details. User must confirm. |
| 0.00 - 0.59 | LOW CONFIDENCE | Reject extraction. Ask user to clarify or rephrase. |

### HIGH CONFIDENCE Behavior

**Trigger:** Overall confidence ≥ 0.85

**System Behavior:**
1. Validate extracted entities against business rules
2. If validation passes:
   - Display brief toast: "Added 5 cartons of Biscuits ✓"
   - Create event in ledger
   - Update inventory state
   - Show success animation
3. If validation fails:
   - Downgrade to MEDIUM CONFIDENCE behavior
   - Show validation error with correction option

**User Actions:**
- None required (automatic)
- Can undo via "Undo" button (available for 30 seconds)

**Validation Required:**
- Product exists in inventory
- Quantity is positive number
- Unit is recognized
- Stock will not go negative (warning only)

### MEDIUM CONFIDENCE Behavior

**Trigger:** Overall confidence 0.60 - 0.84

**System Behavior:**
1. Display confirmation dialog with:
   - Original text
   - Extracted event type
   - Product name with match indicator
   - Quantity and unit
   - Confidence score displayed
   - [Confirm] [Edit] [Cancel] buttons
2. Wait for user action
3. On Confirm:
   - Validate entities
   - Create event
   - Update inventory
4. On Edit:
   - Open edit form with pre-filled values
   - Allow user to modify any field
   - Re-validate on save
5. On Cancel:
   - Discard extraction
   - Return to voice input

**User Actions:**
- Must explicitly confirm
- Can edit extracted values
- Can cancel and retry

**Confirmation Dialog Format:**
```
┌─────────────────────────────────────┐
│ "I received five cartons of         │
│  biscuits this morning"             │
│                                     │
│ Add 5 cartons of Biscuits?         │
│                                     │
│ Event: Stock In                    │
│ Product: Biscuits (92% match)      │
│ Quantity: 5 cartons                │
│ Confidence: 78%                    │
│                                     │
│  [Confirm]  [Edit]  [Cancel]       │
└─────────────────────────────────────┘
```

### LOW CONFIDENCE Behavior

**Trigger:** Overall confidence < 0.60

**System Behavior:**
1. Display clarification dialog with:
   - Original text
   - Issue description (e.g., "Product not clear", "Quantity unclear")
   - Suggested rephrasing
   - Text input for manual entry
   - [Try Again] [Enter Manually] [Cancel] buttons
2. Wait for user action
3. On Try Again:
   - Return to voice input
   - Show suggestion for clearer phrasing
4. On Enter Manually:
   - Open manual event creation form
   - Pre-fill with any high-confidence extractions
5. On Cancel:
   - Return to home screen

**User Actions:**
- Must provide clarification
- Can rephrase and try voice again
- Can enter manually

**Clarification Dialog Format:**
```
┌─────────────────────────────────────┐
│ "Add ten Sunflower"                 │
│                                     │
│ I'm not sure which product you     │
│ mean. Multiple products match:     │
│                                     │
│ • Sunflower Oil 1L                  │
│ • Sunflower Oil 500ml              │
│ • Sunflower Seeds                   │
│                                     │
│ Please select or try again with   │
│ a more specific name.               │
│                                     │
│  [Try Again]  [Select]  [Cancel]   │
└─────────────────────────────────────┘
```

### Confidence Calculation

**Overall Confidence Formula:**
```
overall_confidence = (
  event_type_confidence * 0.3 +
  product_confidence * 0.3 +
  quantity_confidence * 0.2 +
  unit_confidence * 0.2
)
```

**Per-Entity Confidence Factors:**
- **Event Type:** Pattern match strength, verb recognition
- **Product:** Name similarity, category match, inventory existence
- **Quantity:** Number clarity, format validity
- **Unit:** Unit recognition, product compatibility

---

## Ambiguous Product Name Handling

### Ambiguity Detection

**Trigger Conditions:**
1. Product name matches multiple existing products with similarity score > 0.7
2. Product name does not match any existing product (new product)
3. Product name matches with low confidence (< 0.7)

### Ambiguity Resolution Flow

**Step 1: Detection**
- System detects multiple potential matches
- Calculates similarity score for each match
- Sorts matches by similarity score (descending)

**Step 2: Presentation**
- Display selection dialog with:
  - Original text
  - List of matching products
  - Each product shows: name, category, current stock, similarity score
  - "Create new product" option
  - [Select] [Cancel] buttons

**Step 3: User Selection**
- User selects specific product
- OR user chooses "Create new product"
- OR user cancels

**Step 4: Confirmation**
- If product selected:
  - Update extraction with selected product
  - Recalculate confidence
  - Proceed with appropriate confidence behavior
- If create new product:
  - Open product creation form
  - Pre-fill name from extraction
  - Prompt for unit, category, opening stock
  - After creation, proceed with event creation

### Selection Dialog Format

```
┌─────────────────────────────────────┐
│ "Add ten Sunflower"                 │
│                                     │
│ I found multiple products. Which    │
│ one did you mean?                   │
│                                     │
│ ○ Sunflower Oil 1L                 │
│   Category: Oils | Stock: 12       │
│   Match: 95%                        │
│                                     │
│ ○ Sunflower Oil 500ml              │
│   Category: Oils | Stock: 8        │
│   Match: 88%                        │
│                                     │
│ ○ Sunflower Seeds                  │
│   Category: Snacks | Stock: 5       │
│   Match: 72%                        │
│                                     │
│ ○ Create new product               │
│                                     │
│  [Select]  [Cancel]                 │
└─────────────────────────────────────┘
```

### Similarity Scoring

**Algorithm:** Levenshtein distance + phonetic matching + category context

**Score Calculation:**
- Exact match: 1.0
- Partial match (contains): 0.8
- Phonetic similarity: 0.7
- Category context boost: +0.1

**Thresholds:**
- Score ≥ 0.9: Auto-select (HIGH confidence)
- Score 0.7 - 0.89: Show in selection dialog
- Score < 0.7: Do not show in selection (consider no match)

### New Product Handling

**When user selects "Create new product":**

**System Behavior:**
1. Open product creation form
2. Pre-fill:
   - Name: extracted product name
   - Unit: extracted unit (if any)
   - Category: inferred from similar products
3. Require user to enter:
   - Unit (if not extracted)
   - Opening stock (default: 0)
   - Minimum stock threshold (optional)
4. On save:
   - Create product in database
   - Create initial STOCK_IN event for opening stock
   - Return to event creation flow
   - Update extraction with new product ID

**Validation:**
- Product name required
- Unit required
- Opening stock must be ≥ 0
- Unit must be from supported units list

---

## Supported Natural-Language Questions

### Question Type Classification

### Type 1: Current Stock Query

**Patterns:**
- "How much [product] do I have?"
- "What is my [product] stock?"
- "Show me [product] stock"
- "[Product] stock"

**System Behavior:**
1. Extract product name
2. Query inventory state for product
3. Return current quantity and unit
4. Include stock status (normal/low/critical)

**Response Format:**
```
You have 25 bags of rice.
Status: Normal (minimum: 10 bags)
```

**Validation:**
- Product must exist
- If product not found: show product selection or creation option

### Type 2: Low Stock Query

**Patterns:**
- "What is running low?"
- "What products are low on stock?"
- "Show me low stock items"
- "What needs to be reordered?"

**System Behavior:**
1. Query all products
2. Filter: current_stock < minimum_threshold
3. Sort by: (current_stock / minimum_threshold) ascending
4. Return list with:
   - Product name
   - Current stock
   - Minimum threshold
   - Stock status

**Response Format:**
```
Low stock items:

1. Biscuits - 5 cartons (minimum: 10) - Critical
2. Cooking Oil - 3 litres (minimum: 5) - Low
3. Rice - 8 bags (minimum: 10) - Low
```

**Validation:**
- If no low stock: "All products are above minimum stock"
- If no thresholds set: "Set minimum stock for products to see alerts"

### Type 3: Reorder Query

**Patterns:**
- "What should I order?"
- "What do I need to reorder?"
- "Reorder recommendations"
- "Order suggestions"

**System Behavior:**
1. Calculate reorder recommendations (see Module 10)
2. Filter: products where current_stock < reorder_point
3. Sort by urgency (days until stockout)
4. Return list with:
   - Product name
   - Current stock
   - Recommended order quantity
   - Urgency level

**Response Format:**
```
Reorder recommendations:

1. Biscuits - Order 25 cartons (stockout in 3 days) - Urgent
2. Cooking Oil - Order 10 litres (stockout in 7 days) - Medium
3. Rice - Order 20 bags (stockout in 10 days) - Low
```

**Validation:**
- If insufficient data: "Need more sales data for recommendations"
- If no products need reorder: "No products need reordering currently"

### Type 4: Sales Query

**Patterns:**
- "What did I sell today?"
- "Today's sales"
- "Sales today"
- "What sold today?"

**System Behavior:**
1. Calculate date range: today (start of day to now)
2. Query events: event_type in (SALE, CREDIT_SALE)
3. Group by product
4. Aggregate total quantity sold
5. Return list with:
   - Product name
   - Total quantity sold
   - Total value (if price available)

**Response Format:**
```
Today's sales:

• Biscuits: 8 cartons sold
• Cooking Oil: 5 litres sold
• Rice: 3 bags sold

Total: 16 transactions
```

**Validation:**
- If no sales today: "No sales recorded today"
- Date parsing: support "today", "yesterday", "this week"

### Type 5: Why Query

**Patterns:**
- "Why is my [product] stock low?"
- "Why did [product] stock decrease?"
- "Explain [product] stock"
- "[Product] stock explanation"

**System Behavior:**
1. Extract product name
2. Query event ledger for product
3. Aggregate events by type:
   - STOCK_IN: total added
   - SALE: total sold
   - CREDIT_SALE: total credit sales
   - DAMAGE: total damaged
   - LOSS: total lost
   - STOCK_OUT: total removed
4. Calculate net change
5. Generate natural language explanation
6. Show timeline of significant events

**Response Format:**
```
Your rice stock is 12 bags.

Stock breakdown:
• Purchased: +50 bags
• Sold: -25 bags
• Credit sales: -10 bags
• Damaged: -3 bags
• Removed: -0 bags

Net change: +12 bags

Your stock decreased mainly because of 35 bags sold and 3 bags damaged.
```

**Validation:**
- Product must exist
- If no events: "No transactions recorded for this product"

### Type 6: Where Query

**Patterns:**
- "Where did my [product] go?"
- "What happened to [product]?"
- "[Product] movement history"
- "Track [product]"

**System Behavior:**
1. Extract product name
2. Query event ledger for product
3. Filter: stock-decreasing events (SALE, CREDIT_SALE, DAMAGE, LOSS, STOCK_OUT)
4. Group by event type and customer (for credit sales)
5. Calculate totals per group
6. Return chronological summary

**Response Format:**
```
Biscuits movement (25 cartons removed):

• Sold: 15 cartons
• Credit sale to Ramesh: 5 cartons
• Credit sale to Suresh: 3 cartons
• Damaged: 2 cartons

Total removed: 25 cartons
```

**Validation:**
- Product must exist
- If no stock-decreasing events: "No stock has been removed from this product"

### Type 7: Customer Query

**Patterns:**
- "What did [customer] take?"
- "[Customer] transactions"
- "[Customer] credit"
- "Show [customer] history"

**System Behavior:**
1. Extract customer name
2. Query events: customer matches
3. Filter: CREDIT_SALE events
4. Group by product
5. Calculate total outstanding credit
6. Return list with:
   - Product name
   - Quantity taken
   - Date
   - Payment status

**Response Format:**
```
Ramesh's transactions:

• Biscuits: 5 cartons on credit (2026-09-18)
• Cooking Oil: 2 litres on credit (2026-09-19)

Total outstanding: 7 items
```

**Validation:**
- Customer must exist
- If no transactions: "No transactions found for this customer"

### Type 8: Time-Based Query

**Patterns:**
- "What happened to [product] this week?"
- "[Product] history this week"
- "What did I sell this week?"
- "This week's transactions"

**System Behavior:**
1. Extract time expression (this week, this month, yesterday, last 7 days)
2. Parse date range
3. Query events within date range
4. Filter by product if specified
5. Aggregate by event type
6. Return summary

**Response Format:**
```
Oil activity this week (Sep 13-19):

• Purchased: +20 litres
• Sold: -12 litres
• Credit sales: -5 litres

Net change: +3 litres
```

**Validation:**
- Date parsing: support relative expressions
- If no events in range: "No activity in this period"

---

## Inventory Operations Definition

### Operation: STOCK_IN

**Purpose:** Record stock received from supplier or added to inventory

**Trigger Conditions:**
- Voice: "Add [quantity] [unit] of [product]"
- Voice: "Received [quantity] [unit] of [product]"
- Voice: "[Quantity] [unit] of [product] came in"
- Voice: Regional equivalents (e.g., "vachayi", "aaya")

**Stock Impact:** +quantity

**Required Fields:**
- event_type: "STOCK_IN"
- product: name or ID
- quantity: positive number
- unit: recognized unit

**Optional Fields:**
- price: per-unit price
- supplier: supplier name (future)
- invoice_number: invoice reference (future)

**Validation Rules:**
- Quantity must be > 0
- Unit must be recognized
- Product must exist (or prompt to create)
- If price provided, must be ≥ 0

**Business Rules:**
- Always increases stock
- Cannot make stock negative
- Creates immutable event in ledger
- Updates current inventory state

**Error Handling:**
- Product not found → Prompt to create or select
- Invalid quantity → Show error, ask to rephrase
- Invalid unit → Show error, suggest valid units

---

### Operation: SALE

**Purpose:** Record cash sale to customer

**Trigger Conditions:**
- Voice: "Sold [quantity] [unit] of [product]"
- Voice: "[Quantity] [unit] of [product] sold"
- Voice: "Customer bought [quantity] [unit] of [product]"
- Voice: Regional equivalents (e.g., "bik gaya", "amina")

**Stock Impact:** -quantity

**Required Fields:**
- event_type: "SALE"
- product: name or ID
- quantity: positive number
- unit: recognized unit

**Optional Fields:**
- price: per-unit price
- customer: customer name (for record-keeping, not credit)
- payment_status: "CASH" (default)

**Validation Rules:**
- Quantity must be > 0
- Unit must be recognized
- Product must exist
- Sufficient stock available (warn if not)

**Business Rules:**
- Always decreases stock
- Warns if stock would go negative
- Allows override with confirmation
- Creates immutable event in ledger
- Updates current inventory state

**Error Handling:**
- Insufficient stock → Show warning, allow override
- Product not found → Prompt to select
- Invalid quantity → Show error

---

### Operation: STOCK_OUT

**Purpose:** Record stock removed for non-sale reasons (damage, loss, theft, personal use)

**Trigger Conditions:**
- Voice: "Remove [quantity] [unit] of [product]"
- Voice: "Take out [quantity] [unit] of [product]"
- Voice: "[Quantity] [unit] of [product] removed"
- Voice: "Damaged [quantity] [unit] of [product]" (can also use DAMAGE event)

**Stock Impact:** -quantity

**Required Fields:**
- event_type: "STOCK_OUT"
- product: name or ID
- quantity: positive number
- unit: recognized unit

**Optional Fields:**
- reason: "DAMAGE" | "LOSS" | "THEFT" | "PERSONAL" | "OTHER"
- notes: free text description

**Validation Rules:**
- Quantity must be > 0
- Unit must be recognized
- Product must exist
- Sufficient stock available (warn if not)

**Business Rules:**
- Always decreases stock
- Warns if stock would go negative
- Allows override with confirmation
- Creates immutable event in ledger
- Updates current inventory state

**Error Handling:**
- Insufficient stock → Show warning, allow override
- Product not found → Prompt to select
- Invalid quantity → Show error

---

### Operation: PURCHASE

**Purpose:** Record stock purchased by business (similar to STOCK_IN but with supplier context)

**Trigger Conditions:**
- Voice: "Purchased [quantity] [unit] of [product]"
- Voice: "Bought [quantity] [unit] of [product]"
- Voice: "Ordered [quantity] [unit] of [product]"

**Stock Impact:** +quantity

**Required Fields:**
- event_type: "PURCHASE"
- product: name or ID
- quantity: positive number
- unit: recognized unit

**Optional Fields:**
- price: per-unit price
- supplier: supplier name
- purchase_order: PO number
- invoice_number: invoice reference

**Validation Rules:**
- Quantity must be > 0
- Unit must be recognized
- Product must exist
- If price provided, must be ≥ 0

**Business Rules:**
- Always increases stock
- Cannot make stock negative
- Creates immutable event in ledger
- Updates current inventory state
- Differs from STOCK_IN in reporting context (purchase vs. receipt)

**Error Handling:**
- Product not found → Prompt to create or select
- Invalid quantity → Show error
- Invalid unit → Show error

---

### Operation: CREDIT_SALE

**Purpose:** Record sale on credit to customer

**Trigger Conditions:**
- Voice: "[Customer] took [quantity] [unit] of [product] on credit"
- Voice: "[Customer] will pay for [quantity] [unit] of [product] tomorrow"
- Voice: "Gave [quantity] [unit] of [product] to [customer] on credit"
- Voice: Regional equivalents (e.g., "udhaar", "appa")

**Stock Impact:** -quantity

**Required Fields:**
- event_type: "CREDIT_SALE"
- product: name or ID
- quantity: positive number
- unit: recognized unit
- customer: customer name

**Optional Fields:**
- due_date: expected payment date
- price: per-unit price
- payment_status: "CREDIT" (default)
- notes: free text

**Validation Rules:**
- Quantity must be > 0
- Unit must be recognized
- Product must exist
- Customer must exist (or prompt to create)
- Sufficient stock available (warn if not)

**Business Rules:**
- Always decreases stock
- Creates credit liability for customer
- Warns if stock would go negative
- Allows override with confirmation
- Creates immutable event in ledger
- Updates current inventory state
- Updates customer outstanding credit

**Error Handling:**
- Insufficient stock → Show warning, allow override
- Product not found → Prompt to select
- Customer not found → Prompt to create or select
- Invalid quantity → Show error

---

### Operation: RETURN

**Purpose:** Record customer return of previously sold product

**Trigger Conditions:**
- Voice: "[Customer] returned [quantity] [unit] of [product]"
- Voice: "Return [quantity] [unit] of [product]"
- Voice: "[Quantity] [unit] of [product] returned"

**Stock Impact:** +quantity

**Required Fields:**
- event_type: "RETURN"
- product: name or ID
- quantity: positive number
- unit: recognized unit

**Optional Fields:**
- customer: customer name
- reason: return reason
- original_sale_id: reference to original sale (future)

**Validation Rules:**
- Quantity must be > 0
- Unit must be recognized
- Product must exist

**Business Rules:**
- Always increases stock
- Cannot make stock negative
- Creates immutable event in ledger
- Updates current inventory state
- Optionally reduces customer credit if was credit sale

**Error Handling:**
- Product not found → Prompt to select
- Invalid quantity → Show error
- Invalid unit → Show error

---

### Operation: DAMAGE

**Purpose:** Record stock damaged (specific type of STOCK_OUT)

**Trigger Conditions:**
- Voice: "Damaged [quantity] [unit] of [product]"
- Voice: "[Quantity] [unit] of [product] got damaged"
- Voice: "Spoiled [quantity] [unit] of [product]"

**Stock Impact:** -quantity

**Required Fields:**
- event_type: "DAMAGE"
- product: name or ID
- quantity: positive number
- unit: recognized unit

**Optional Fields:**
- reason: specific damage reason
- notes: description

**Validation Rules:**
- Quantity must be > 0
- Unit must be recognized
- Product must exist
- Sufficient stock available (warn if not)

**Business Rules:**
- Always decreases stock
- Specific subtype of STOCK_OUT
- Warns if stock would go negative
- Allows override with confirmation
- Creates immutable event in ledger
- Updates current inventory state

**Error Handling:**
- Insufficient stock → Show warning, allow override
- Product not found → Prompt to select
- Invalid quantity → Show error

---

### Operation: LOSS

**Purpose:** Record stock lost or stolen (specific type of STOCK_OUT)

**Trigger Conditions:**
- Voice: "Lost [quantity] [unit] of [product]"
- Voice: "[Quantity] [unit] of [product] was stolen"
- Voice: "Missing [quantity] [unit] of [product]"

**Stock Impact:** -quantity

**Required Fields:**
- event_type: "LOSS"
- product: name or ID
- quantity: positive number
- unit: recognized unit

**Optional Fields:**
- reason: specific loss reason
- notes: description

**Validation Rules:**
- Quantity must be > 0
- Unit must be recognized
- Product must exist
- Sufficient stock available (warn if not)

**Business Rules:**
- Always decreases stock
- Specific subtype of STOCK_OUT
- Warns if stock would go negative
- Allows override with confirmation
- Creates immutable event in ledger
- Updates current inventory state

**Error Handling:**
- Insufficient stock → Show warning, allow override
- Product not found → Prompt to select
- Invalid quantity → Show error

---

### Operation: ADJUSTMENT

**Purpose:** Manual stock correction for discrepancy resolution

**Trigger Conditions:**
- Voice: "Adjust [product] stock to [quantity]"
- Voice: "Set [product] to [quantity] [unit]"
- Voice: "Correct [product] stock to [quantity]"

**Stock Impact:** + (new_quantity - current_quantity)

**Required Fields:**
- event_type: "ADJUSTMENT"
- product: name or ID
- quantity: target quantity (positive number)
- unit: recognized unit

**Optional Fields:**
- reason: adjustment reason
- notes: description
- physical_count: actual counted quantity

**Validation Rules:**
- Quantity must be ≥ 0
- Unit must be recognized
- Product must exist

**Business Rules:**
- Can increase or decrease stock
- Sets stock to exact target quantity
- Calculates delta: target - current
- Creates immutable event in ledger
- Updates current inventory state
- Used for discrepancy resolution

**Error Handling:**
- Product not found → Prompt to select
- Invalid quantity → Show error
- Invalid unit → Show error

---

## Business Rules

### Current Stock Calculation

**Rule:** Current stock is calculated from event history, not stored directly.

**Formula:**
```
current_stock = SUM(STOCK_IN) + SUM(PURCHASE) + SUM(RETURN)
               - SUM(SALE) - SUM(CREDIT_SALE) - SUM(STOCK_OUT)
               - SUM(DAMAGE) - SUM(LOSS)
               + SUM(ADJUSTMENT where delta > 0)
               - SUM(ADJUSTMENT where delta < 0)
```

**Implementation:**
- On each event creation, recalculate current stock
- Cache current stock for performance
- Invalidate cache on event creation
- Recalculate from scratch on cache miss

**Unit Handling:**
- All calculations in base unit
- Convert to user's preferred unit for display
- Store conversion rules per product

**Edge Cases:**
- No events: current_stock = 0
- Only opening stock event: current_stock = opening_stock
- Negative stock: allowed with warning, not prevented

---

### Stock Movement

**Rule:** Every stock change must be traceable to a specific event.

**Implementation:**
- Never directly update stock quantity
- Always create an event
- Event is immutable once created
- Current stock derived from events

**Movement Tracking:**
- Each event has timestamp
- Each event has event_type
- Each event has source (voice/text/API)
- Each event has original_text
- Each event has confidence score

**Movement Aggregation:**
- Group by event_type for summaries
- Group by time period for trends
- Group by customer for credit tracking
- Group by product for history

---

### Unit Conversion

**Rule:** Support trade units with conversion to base unit.

**Base Units:**
- Mass: kilograms (kg)
- Volume: litres (L)
- Count: pieces

**Supported Units:**
- pieces → base: 1 piece
- kg → base: 1 kg
- litres → base: 1 L
- bags → conversion rule per product (e.g., 1 bag = 50 kg)
- cartons → conversion rule per product (e.g., 1 carton = 24 pieces)
- boxes → conversion rule per product (e.g., 1 box = 12 pieces)
- dozens → base: 1 dozen = 12 pieces
- quintals → base: 1 quintal = 100 kg

**Conversion Storage:**
```json
{
  "product_id": "uuid",
  "base_unit": "pieces",
  "conversion_rules": {
    "carton": {
      "to_base": 24,
      "display_name": "Carton"
    },
    "box": {
      "to_base": 12,
      "display_name": "Box"
    }
  }
}
```

**Conversion Logic:**
- On event creation: convert to base unit
- Store both original unit and normalized base unit
- On display: convert from base to user's preferred unit
- If no conversion rule: treat as base unit

**Validation:**
- Unit must be in supported list
- Unit must be compatible with product category
- Conversion rule must be positive number

---

### Low Stock Detection

**Rule:** Identify products where current stock is below minimum threshold.

**Calculation:**
```
is_low_stock = current_stock < minimum_threshold
```

**Threshold Levels:**
- Normal: current_stock ≥ minimum_threshold
- Low: minimum_threshold * 0.5 ≤ current_stock < minimum_threshold
- Critical: current_stock < minimum_threshold * 0.5

**Display Indicators:**
- Normal: Green indicator
- Low: Yellow indicator
- Critical: Red indicator

**Alert Triggers:**
- When stock drops below minimum_threshold
- When stock drops to critical level
- When stock drops to zero (stockout)

**Business Rules:**
- minimum_threshold is per-product
- Default minimum_threshold: 0 (no alerts)
- User can set minimum_threshold per product
- Alerts shown in dashboard

---

### Stockout Estimation

**Rule:** Estimate days until stock runs out based on consumption rate.

**Calculation:**
```
daily_consumption = total_sold / days_with_sales
days_until_stockout = current_stock / daily_consumption
```

**Data Requirements:**
- Minimum 7 days of sales data
- At least 5 sales events in period
- Exclude days with zero sales from average

**Fallback:**
- If insufficient data: "Need more sales data"
- If zero consumption: "No recent sales"
- If stock already zero: "Already out of stock"

**Display:**
- Exact days if ≥ 1: "3 days"
- Less than 1 day: "Less than 1 day"
- Already out: "Out of stock"
- No data: "Unknown"

**Refinement:**
- Weight recent days more heavily
- Exclude outlier days (very high/low sales)
- Consider seasonal patterns (future)

---

### Reorder Recommendation

**Rule:** Calculate recommended order quantity based on current stock, consumption, and lead time.

**Calculation:**
```
avg_daily_consumption = total_sold / days_with_sales
lead_time_days = supplier_lead_time (default: 7 days)
safety_stock = avg_daily_consumption * 2 (2-day buffer)
reorder_point = (avg_daily_consumption * lead_time_days) + safety_stock
recommended_order = reorder_point - current_stock
```

**Data Requirements:**
- Minimum 14 days of sales data
- Supplier lead time (optional, default: 7 days)
- Current stock
- Average daily consumption

**Rounding:**
- Round up to nearest package size
- Round up to nearest 10 for bulk items
- Minimum order: 1 unit

**Display:**
- "Order 25 cartons of biscuits"
- Include urgency level based on days until stockout
- Include confidence level based on data quality

**Business Rules:**
- Only recommend if current_stock < reorder_point
- Never recommend if current_stock ≥ reorder_point
- Show confidence: High/Medium/Low based on data quality

---

### Credit Transactions

**Rule:** Track outstanding credit per customer.

**Calculation:**
```
customer_outstanding = SUM(CREDIT_SALE quantity) - SUM(payments)
```

**Credit Event:**
- event_type: CREDIT_SALE
- customer: customer name or ID
- quantity: quantity taken
- payment_status: "CREDIT"
- due_date: optional due date

**Payment Recording:**
- event_type: PAYMENT (future)
- customer: customer name or ID
- amount: payment amount
- reduces outstanding credit

**Display:**
- Customer profile shows outstanding credit
- Outstanding = total credit - total payments
- Show due dates if available

**Validation:**
- Customer must exist
- Quantity must be positive
- Warn if customer has high outstanding credit

---

### Discrepancy Detection

**Rule:** Compare expected inventory with physical count.

**Calculation:**
```
expected_stock = calculated from event ledger
physical_count = user-entered count
discrepancy = physical_count - expected_stock
```

**Discrepancy Types:**
- Positive discrepancy: physical > expected (extra stock found)
- Negative discrepancy: physical < expected (missing stock)
- Zero discrepancy: physical = expected (accurate)

**Recording:**
- Create ADJUSTMENT event with discrepancy
- Set reason: "DISCREPANCY_RESOLUTION"
- Record physical_count
- Record expected_stock
- Record discrepancy

**Display:**
- Show discrepancy amount
- Show percentage difference
- Show suggested action

**Business Rules:**
- Discrepancy > 5%: flag for review
- Discrepancy > 10%: require explanation
- Discrepancy > 20%: block adjustment without approval

---

## Module Specifications

### MODULE 1 — Authentication & Business Setup

#### Purpose
Enable user registration, authentication, and business profile creation. Establish the foundation for multi-tenant data isolation.

#### Inputs
- User phone number
- OTP (One-Time Password)
- User name
- Business name
- Business type
- Location
- Preferred language

#### Outputs
- User session token
- User profile
- Business profile
- Business ID

#### User Actions
1. **Register**
   - Enter phone number
   - Receive OTP via SMS
   - Enter OTP
   - Enter name
   - Create business profile
   - Select business type
   - Enter location
   - Select preferred language

2. **Login**
   - Enter phone number
   - Receive OTP
   - Enter OTP
   - Session created

3. **Setup Business**
   - Enter business name
   - Select business type (kirana, pharmacy, wholesale, etc.)
   - Enter location
   - Select preferred language
   - Save business profile

#### System Behavior

**Registration Flow:**
```
1. User enters phone number
2. System validates phone format
3. System sends OTP via SMS
4. User enters OTP
5. System validates OTP
6. User enters name
7. User creates business profile
8. System creates user account
9. System creates business account
10. System links user to business
11. System creates session
12. User redirected to dashboard
```

**Login Flow:**
```
1. User enters phone number
2. System checks if user exists
3. System sends OTP
4. User enters OTP
5. System validates OTP
6. System creates session
7. User redirected to dashboard
```

**Business Setup Flow:**
```
1. User enters business name
2. User selects business type
3. User enters location
4. User selects preferred language
5. System validates inputs
6. System creates business profile
7. System links business to user
8. User redirected to product setup
```

#### Validation Rules
- Phone number: 10 digits, Indian format (+91)
- OTP: 6 digits, numeric
- Name: 2-50 characters, letters only
- Business name: 2-100 characters
- Business type: must be from predefined list
- Location: 2-100 characters
- Preferred language: must be from supported languages

#### Error Handling
- Invalid phone format: "Please enter a valid 10-digit phone number"
- OTP expired: "OTP expired. Please request a new one"
- Invalid OTP: "Invalid OTP. Please try again"
- User already exists: "This phone number is already registered"
- Business name required: "Please enter a business name"
- Invalid business type: "Please select a valid business type"

#### Empty States
- **First-time user:** Show onboarding flow
- **No business:** Show business setup form
- **No products:** Show product setup prompt

#### Loading States
- **Sending OTP:** Show spinner with "Sending OTP..."
- **Validating OTP:** Show spinner with "Verifying..."
- **Creating account:** Show spinner with "Creating your account..."
- **Setting up business:** Show spinner with "Setting up your business..."

#### Success States
- **Registration complete:** Show success message with "Welcome to A.R.I.A.!"
- **Login complete:** Show success message with "Welcome back!"
- **Business setup complete:** Show success message with "Business setup complete! Let's add your first product."

---

### MODULE 2 — Product Management

#### Purpose
Enable creation, viewing, editing, and deletion of products. Define product attributes including units, thresholds, and conversion rules.

#### Inputs
- Product name
- Product category
- Base unit
- Opening stock
- Minimum stock threshold
- Reorder quantity
- Unit conversion rules
- Price (optional)

#### Outputs
- Product record
- Product list
- Product details

#### User Actions
1. **Create Product**
   - Enter product name
   - Select category
   - Select unit
   - Enter opening stock
   - Enter minimum stock threshold
   - Enter reorder quantity
   - Add unit conversion rules (optional)
   - Enter price (optional)
   - Save

2. **View Products**
   - View product list
   - Filter by category
   - Search by name
   - Sort by name, stock, category

3. **Edit Product**
   - Select product
   - Modify any field
   - Save changes

4. **Delete Product**
   - Select product
   - Confirm deletion
   - Product deleted (events preserved)

#### System Behavior

**Create Product Flow:**
```
1. User enters product details
2. System validates inputs
3. System checks for duplicate names
4. System creates product record
5. System creates initial STOCK_IN event for opening stock
6. System updates inventory state
7. User redirected to product list
```

**View Products Flow:**
```
1. User navigates to products
2. System fetches all products for business
3. System calculates current stock for each
4. System displays product list
5. User can filter, search, sort
```

**Edit Product Flow:**
```
1. User selects product
2. System loads product details
3. User modifies fields
4. System validates changes
5. System updates product record
6. System displays success message
```

**Delete Product Flow:**
```
1. User selects product
2. System shows confirmation dialog
3. User confirms
4. System marks product as deleted (soft delete)
5. System preserves event history
6. User redirected to product list
```

#### Validation Rules
- Product name: 2-100 characters, unique within business
- Category: from predefined list or custom
- Unit: from supported units list
- Opening stock: ≥ 0
- Minimum stock threshold: ≥ 0
- Reorder quantity: ≥ 0
- Price: ≥ 0 if provided
- Conversion rule: must be positive number

#### Error Handling
- Duplicate name: "A product with this name already exists"
- Invalid unit: "Please select a valid unit"
- Negative stock: "Stock cannot be negative"
- Invalid conversion: "Conversion must be a positive number"

#### Empty States
- **No products:** Show "No products yet. Add your first product to get started."
- **No categories:** Show "No categories. Add a category first."

#### Loading States
- **Loading products:** Show spinner with "Loading products..."
- **Creating product:** Show spinner with "Creating product..."
- **Saving changes:** Show spinner with "Saving changes..."

#### Success States
- **Product created:** Show success message with "Product created successfully!"
- **Product updated:** Show success message with "Product updated successfully!"
- **Product deleted:** Show success message with "Product deleted (history preserved)."

---

### MODULE 3 — Inventory Management

#### Purpose
Display current inventory state, enable manual stock updates, and provide inventory views and filters.

#### Inputs
- Product selection
- Quantity
- Unit
- Event type
- Filters (category, stock status)

#### Outputs
- Current inventory state
- Inventory views
- Stock updates

#### User Actions
1. **View Inventory**
   - Navigate to inventory screen
   - View all products with current stock
   - Filter by category
   - Filter by stock status (normal, low, critical)
   - Search by name

2. **Manual Stock Update**
   - Select product
   - Select action (add/remove)
   - Enter quantity
   - Select unit
   - Enter reason (optional)
   - Confirm

3. **View Product Details**
   - Select product
   - View current stock
   - View stock history
   - View recent events
   - View stock status

#### System Behavior

**View Inventory Flow:**
```
1. User navigates to inventory
2. System fetches all products
3. System calculates current stock for each
4. System determines stock status (normal/low/critical)
5. System displays inventory list
6. User can filter and search
```

**Manual Stock Update Flow:**
```
1. User selects product
2. User selects action (add/remove)
3. User enters quantity
4. User selects unit
5. User enters reason (optional)
6. System validates inputs
7. System creates appropriate event (STOCK_IN/STOCK_OUT)
8. System updates inventory state
9. System displays success message
```

**View Product Details Flow:**
```
1. User selects product
2. System fetches product details
3. System fetches current stock
4. System fetches recent events
5. System calculates stock status
6. System displays product detail view
```

#### Validation Rules
- Quantity must be > 0
- Unit must be recognized
- Product must exist
- For removal: sufficient stock available (warn if not)

#### Error Handling
- Insufficient stock: "Warning: This will make stock negative. Continue?"
- Invalid quantity: "Please enter a valid quantity"
- Invalid unit: "Please select a valid unit"

#### Empty States
- **No inventory:** Show "No products in inventory. Add products to get started."
- **No results:** Show "No products match your search."

#### Loading States
- **Loading inventory:** Show spinner with "Loading inventory..."
- **Updating stock:** Show spinner with "Updating stock..."

#### Success States
- **Stock updated:** Show success message with "Stock updated successfully!"
- **Stock added:** Show success message with "Added [quantity] [unit] of [product]!"
- **Stock removed:** Show success message with "Removed [quantity] [unit] of [product]!"

---

### MODULE 4 — Voice Processing

#### Purpose
Capture voice input, convert to text, and provide transcription for verification and processing.

#### Inputs
- Audio stream from microphone
- Microphone permission
- Recording duration

#### Outputs
- Transcribed text
- Audio recording (optional, for reprocessing)
- Transcription confidence

#### User Actions
1. **Start Recording**
   - Tap microphone button
   - Grant microphone permission
   - Speak
   - Tap stop button or auto-stop on silence

2. **Review Transcription**
   - View transcribed text
   - Edit transcription if needed
   - Reprocess or cancel

3. **Use Text Input**
   - Tap text input field
   - Type command
   - Submit

#### System Behavior

**Voice Recording Flow:**
```
1. User taps microphone button
2. System requests microphone permission
3. System starts audio recording
4. System displays recording indicator
5. User speaks
6. System transcribes in real-time (if supported)
7. User taps stop or auto-stop on silence
8. System stops recording
9. System sends audio to STT service
10. System receives transcription
11. System displays transcription
12. User can edit or confirm
```

**Text Input Flow:**
```
1. User taps text input field
2. System shows keyboard
3. User types command
4. User submits
5. System processes text directly
```

#### Validation Rules
- Audio duration: 1-30 seconds
- Audio quality: minimum threshold
- Microphone permission: required

#### Error Handling
- Microphone permission denied: "Microphone permission is required for voice input"
- No audio detected: "No audio detected. Please try again"
- Transcription failed: "Could not understand audio. Please try again or type instead"
- Network error: "Network error. Please check your connection"

#### Empty States
- **No transcription:** Show "Tap the microphone to speak"
- **Recording:** Show waveform animation

#### Loading States
- **Recording:** Show waveform with "Listening..."
- **Transcribing:** Show spinner with "Transcribing..."
- **Processing:** Show spinner with "Processing..."

#### Success States
- **Transcription complete:** Show transcribed text with "Did you mean: [text]?"
- **Text submitted:** Show "Processing your command..."

---

### MODULE 5 — Language Understanding

#### Purpose
Detect input language, normalize mixed-language input, and prepare text for entity extraction.

#### Inputs
- Transcribed text
- User's preferred language

#### Outputs
- Detected language
- Normalized text
- Language segments
- Regional terminology mapping

#### User Actions
- None (automatic processing)

#### System Behavior

**Language Detection Flow:**
```
1. System receives transcribed text
2. System analyzes text for language indicators
3. System detects primary language
4. System detects mixed-language segments
5. System normalizes regional terminology
6. System outputs normalized text
7. System outputs language metadata
```

**Mixed-Language Handling:**
```
1. System identifies language segments
2. System applies appropriate NLP per segment
3. System merges extractions
4. System outputs unified result
```

**Regional Terminology Normalization:**
```
1. System maps regional terms to standard entities
2. System normalizes number formats
3. System normalizes business terminology
4. System outputs normalized text
```

#### Validation Rules
- Text must not be empty
- Language must be from supported list

#### Error Handling
- Unsupported language: "Language not supported. Please use English or [supported languages]"
- Empty text: "No text to process"

#### Empty States
- None (module processes input)

#### Loading States
- **Detecting language:** Show spinner with "Detecting language..."
- **Normalizing:** Show spinner with "Normalizing..."

#### Success States
- **Processing complete:** Pass to entity extraction module

---

### MODULE 6 — Business Event Engine

#### Purpose
Extract structured business events from natural language text using AI/LLM.

#### Inputs
- Normalized text
- Language metadata
- User's inventory context (products, customers)

#### Outputs
- Structured event extraction
- Confidence scores
- Entity extraction schema

#### User Actions
- None (automatic processing)

#### System Behavior

**Entity Extraction Flow:**
```
1. System receives normalized text
2. System injects business context (products, customers)
3. System sends to LLM with extraction prompt
4. LLM extracts entities
5. System validates extraction schema
6. System calculates confidence scores
7. System outputs structured extraction
```

**Context Injection:**
```
1. System fetches user's product list
2. System fetches user's customer list
3. System formats context for LLM
4. System includes conversion rules
5. System includes recent events
```

**Confidence Calculation:**
```
1. System analyzes extraction quality
2. System calculates per-entity confidence
3. System calculates overall confidence
4. System outputs confidence scores
```

#### Validation Rules
- Extraction must match schema
- Confidence must be 0-1
- Entities must be valid types

#### Error Handling
- Invalid schema: "Extraction failed. Please try again"
- LLM error: "Processing error. Please try again"
- Network error: "Network error. Please check your connection"

#### Empty States
- None (module processes input)

#### Loading States
- **Extracting:** Show spinner with "Understanding your command..."
- **Analyzing:** Show spinner with "Analyzing..."

#### Success States
- **Extraction complete:** Pass to validation module

---

### MODULE 7 — Business Memory / Event Ledger

#### Purpose
Store immutable business events, maintain complete history, and enable event-based inventory calculation.

#### Inputs
- Validated event extraction
- User confirmation (if required)

#### Outputs
- Event record in ledger
- Updated inventory state
- Event timestamp

#### User Actions
- Confirm event (if medium confidence)
- Edit event (if medium confidence)
- Cancel event (if medium confidence)

#### System Behavior

**Event Creation Flow:**
```
1. System receives validated extraction
2. System generates event ID
3. System adds timestamp
4. System adds source (voice/text)
5. System stores original text
6. System stores normalized text
7. System stores confidence scores
8. System writes to event ledger (immutable)
9. System recalculates inventory state
10. System updates inventory cache
11. System triggers stock intelligence recalculation
12. System displays success message
```

**Event Retrieval Flow:**
```
1. System receives query parameters
2. System queries event ledger
3. System filters by criteria
4. System sorts by timestamp
5. System returns event list
```

**Inventory Calculation Flow:**
```
1. System queries all events for product
2. System aggregates by event type
3. System applies business rules
4. System calculates current stock
5. System updates inventory state
6. System updates cache
```

#### Validation Rules
- Event type must be valid
- Product must exist
- Quantity must be positive
- Unit must be recognized
- Customer must exist (if applicable)

#### Error Handling
- Database error: "Failed to save event. Please try again"
- Product not found: "Product not found. Please select a product"
- Invalid event type: "Invalid event type"

#### Empty States
- **No events:** Show "No events yet. Start by adding stock."
- **No events for product:** Show "No events for this product."

#### Loading States
- **Saving event:** Show spinner with "Saving event..."
- **Loading history:** Show spinner with "Loading history..."

#### Success States
- **Event saved:** Show success message with "Event saved successfully!"
- **Inventory updated:** Show updated stock in dashboard

---

### MODULE 8 — Natural Language Stock Assistant

#### Purpose
Answer natural language questions about inventory, stock, and business events.

#### Inputs
- Natural language question
- User's inventory context
- Event ledger
- Inventory state

#### Outputs
- Natural language response
- Data visualizations (optional)
- Relevant event summaries

#### User Actions
1. **Ask Question**
   - Tap query button
   - Speak or type question
   - Submit

2. **View Response**
   - Read natural language answer
   - View data summaries
   - View related events

#### System Behavior

**Question Processing Flow:**
```
1. System receives question
2. System detects question type
3. System extracts entities (product, customer, time)
4. System determines required data
5. System queries event ledger
6. System queries inventory state
7. System aggregates data
8. System generates natural language response
9. System displays response
```

**Question Type Detection:**
```
1. Current stock query → Query inventory state
2. Low stock query → Query all products, filter by threshold
3. Reorder query → Calculate reorder recommendations
4. Sales query → Query sales events, aggregate
5. Why query → Query product events, aggregate by type
6. Where query → Query product events, filter stock-decreasing
7. Customer query → Query customer events
8. Time-based query → Query events in date range
```

**Response Generation:**
```
1. System formats data for readability
2. System generates natural language explanation
3. System includes relevant metrics
4. System provides actionable insights
5. System offers follow-up questions
```

#### Validation Rules
- Question must not be empty
- Question must be supported type
- Entities must be found (if specified)

#### Error Handling
- Unsupported question: "I didn't understand that question. Try asking about stock, sales, or products."
- Product not found: "Product not found. Did you mean [suggestions]?"
- Insufficient data: "Not enough data to answer this question."

#### Empty States
- **No question:** Show "Ask me anything about your inventory"
- **No data:** Show "Add some products and events to get insights"

#### Loading States
- **Processing question:** Show spinner with "Thinking..."
- **Fetching data:** Show spinner with "Fetching data..."

#### Success States
- **Answer provided:** Show natural language response with data

---

### MODULE 9 — Stock Alerts

#### Purpose
Monitor stock levels and generate alerts for low stock, critical stock, and stockouts.

#### Inputs
- Current inventory state
- Minimum stock thresholds
- Recent events

#### Outputs
- Alert records
- Alert notifications
- Dashboard indicators

#### User Actions
1. **View Alerts**
   - Navigate to alerts screen
   - View all alerts
   - Filter by severity
   - Dismiss alerts

2. **Configure Alerts**
   - Set minimum stock thresholds per product
   - Enable/disable alert types
   - Set alert preferences

#### System Behavior

**Alert Generation Flow:**
```
1. System monitors inventory state (triggered on event creation)
2. System compares current stock to minimum threshold
3. System determines alert severity
4. System creates alert record
5. System displays alert in dashboard
6. System shows notification (if enabled)
```

**Alert Severity Levels:**
```
1. Info: Stock below minimum but above critical
2. Warning: Stock below critical (50% of minimum)
3. Critical: Stock at zero (stockout)
```

**Alert Display:**
```
1. Dashboard shows alert count
2. Alerts screen shows list
3. Each alert shows product, severity, message
4. User can dismiss alerts
5. Dismissed alerts archived
```

#### Validation Rules
- Minimum threshold must be ≥ 0
- Alert must have valid severity

#### Error Handling
- Invalid threshold: "Please enter a valid threshold"
- Alert creation failed: "Failed to create alert"

#### Empty States
- **No alerts:** Show "No alerts. Your stock is healthy!"
- **No thresholds set:** Show "Set minimum stock to receive alerts"

#### Loading States
- **Loading alerts:** Show spinner with "Loading alerts..."
- **Saving settings:** Show spinner with "Saving settings..."

#### Success States
- **Alert created:** Show alert in dashboard
- **Settings saved:** Show success message with "Alert settings saved!"

---

### MODULE 10 — Reorder Intelligence

#### Purpose
Calculate reorder recommendations based on consumption patterns, current stock, and lead times.

#### Inputs
- Current inventory state
- Historical sales data
- Supplier lead times (optional)
- Minimum stock thresholds

#### Outputs
- Reorder recommendations
- Order quantities
- Urgency levels
- Confidence scores

#### User Actions
1. **View Recommendations**
   - Navigate to insights screen
   - View reorder recommendations
   - Filter by urgency
   - View details per product

2. **Configure Reorder Settings**
   - Set supplier lead times
   - Set safety stock levels
   - Set minimum order quantities

#### System Behavior

**Reorder Calculation Flow:**
```
1. System fetches current inventory state
2. System fetches historical sales data (minimum 14 days)
3. System calculates average daily consumption
4. System fetches supplier lead time (default: 7 days)
5. System calculates safety stock (2-day buffer)
6. System calculates reorder point
7. System compares current stock to reorder point
8. System calculates recommended order quantity
9. System determines urgency level
10. System calculates confidence score
11. System displays recommendations
```

**Urgency Calculation:**
```
1. Calculate days until stockout
2. Urgency levels:
   - Urgent: < 3 days
   - High: 3-7 days
   - Medium: 7-14 days
   - Low: > 14 days
```

**Confidence Calculation:**
```
1. Assess data quality (days of data, number of sales)
2. Assess consumption pattern consistency
3. Confidence levels:
   - High: 30+ days, consistent pattern
   - Medium: 14-29 days, moderate pattern
   - Low: < 14 days or inconsistent pattern
```

#### Validation Rules
- Must have minimum 14 days of sales data
- Consumption must be > 0
- Lead time must be > 0

#### Error Handling
- Insufficient data: "Need more sales data for recommendations (minimum 14 days)"
- Zero consumption: "No recent sales for this product"
- Invalid lead time: "Please enter a valid lead time"

#### Empty States
- **No recommendations:** Show "No products need reordering currently"
- **Insufficient data:** Show "Need more sales data for recommendations"

#### Loading States
- **Calculating:** Show spinner with "Calculating recommendations..."
- **Loading data:** Show spinner with "Loading sales data..."

#### Success States
- **Recommendations displayed:** Show list with product, quantity, urgency

---

### MODULE 11 — Inventory Investigation / WHY Engine

#### Purpose
Explain why stock changed by analyzing event history and providing natural language explanations.

#### Inputs
- Product name
- Event ledger
- Inventory state

#### Outputs
- Stock change breakdown
- Natural language explanation
- Event timeline
- Attribution by event type

#### User Actions
1. **Ask Why Question**
   - Navigate to query screen
   - Ask "Why is my [product] stock low?"
   - Submit

2. **View Explanation**
   - Read natural language explanation
   - View breakdown by event type
   - View event timeline
   - Drill down to specific events

#### System Behavior

**Why Analysis Flow:**
```
1. System receives product name
2. System queries event ledger for product
3. System filters events by date range (default: all time)
4. System aggregates events by type:
   - STOCK_IN total
   - SALE total
   - CREDIT_SALE total
   - DAMAGE total
   - LOSS total
   - STOCK_OUT total
   - ADJUSTMENT total
5. System calculates net change
6. System identifies dominant change factors
7. System generates natural language explanation
8. System displays breakdown and timeline
```

**Explanation Generation:**
```
1. Format: "Your [product] stock is [current stock]."
2. List additions: "Purchased: +[quantity], Returned: +[quantity]"
3. List subtractions: "Sold: -[quantity], Credit sales: -[quantity], Damaged: -[quantity]"
4. Net change: "Net change: [+/-][quantity]"
5. Explanation: "Your stock [increased/decreased] mainly because of [reason]."
```

**Timeline Display:**
```
1. Show chronological events
2. Group by day/week
3. Show event type, quantity, customer (if applicable)
4. Allow drill-down to event details
```

#### Validation Rules
- Product must exist
- Must have event history

#### Error Handling
- Product not found: "Product not found"
- No events: "No events recorded for this product"

#### Empty States
- **No events:** Show "No events recorded for this product"
- **No changes:** Show "Stock has not changed"

#### Loading States
- **Analyzing:** Show spinner with "Analyzing stock changes..."
- **Loading events:** Show spinner with "Loading events..."

#### Success States
- **Explanation displayed:** Show breakdown and timeline

---

### MODULE 12 — Inventory Discrepancy Detection

#### Purpose
Compare expected inventory with physical count and identify discrepancies.

#### Inputs
- Expected stock (from event ledger)
- Physical count (user-entered)
- Product selection

#### Outputs
- Discrepancy amount
- Discrepancy percentage
- Suggested adjustment
- Discrepancy alert

#### User Actions
1. **Start Discrepancy Check**
   - Navigate to discrepancy screen
   - Select product
   - Enter physical count
   - Submit

2. **View Discrepancy**
   - View discrepancy amount
   - View discrepancy percentage
   - View suggested adjustment
   - Confirm or reject adjustment

3. **Create Adjustment**
   - Confirm adjustment
   - Enter reason
   - Create ADJUSTMENT event
   - Update inventory

#### System Behavior

**Discrepancy Calculation Flow:**
```
1. System receives product selection
2. System fetches expected stock from event ledger
3. User enters physical count
4. System calculates discrepancy:
   discrepancy = physical_count - expected_stock
5. System calculates percentage:
   percentage = (discrepancy / expected_stock) * 100
6. System determines severity:
   - Minor: < 5%
   - Moderate: 5-10%
   - Major: > 10%
7. System displays discrepancy with severity
8. System suggests adjustment event
```

**Adjustment Creation Flow:**
```
1. User confirms adjustment
2. User enters reason
3. System creates ADJUSTMENT event
4. System sets quantity to physical count
5. System sets reason to "DISCREPANCY_RESOLUTION"
6. System records expected_stock
7. System records discrepancy
8. System updates inventory state
9. System displays success message
```

#### Validation Rules
- Physical count must be ≥ 0
- Product must exist
- Reason required for adjustment

#### Error Handling
- Invalid count: "Please enter a valid count"
- Product not found: "Product not found"
- Adjustment failed: "Failed to create adjustment"

#### Empty States
- **No discrepancy:** Show "No discrepancy. Stock matches expected."
- **No products:** Show "No products to check"

#### Loading States
- **Calculating:** Show spinner with "Calculating discrepancy..."
- **Creating adjustment:** Show spinner with "Creating adjustment..."

#### Success States
- **Discrepancy found:** Show discrepancy with severity indicator
- **Adjustment created:** Show success message with "Adjustment created successfully!"

---

## Appendix

### A. Event Type Summary

| Event Type | Stock Impact | Required Fields | Optional Fields |
|------------|--------------|------------------|-----------------|
| STOCK_IN | + | product, quantity, unit | price, supplier |
| SALE | - | product, quantity, unit | price, customer |
| STOCK_OUT | - | product, quantity, unit | reason, notes |
| PURCHASE | + | product, quantity, unit | price, supplier |
| CREDIT_SALE | - | product, quantity, unit, customer | due_date, price |
| RETURN | + | product, quantity, unit | customer, reason |
| DAMAGE | - | product, quantity, unit | reason, notes |
| LOSS | - | product, quantity, unit | reason, notes |
| ADJUSTMENT | +/- | product, quantity, unit | reason, notes |

### B. Confidence Threshold Summary

| Range | Label | Behavior |
|-------|-------|----------|
| 0.85 - 1.00 | HIGH | Auto-confirm after validation |
| 0.60 - 0.84 | MEDIUM | Show confirmation dialog |
| 0.00 - 0.59 | LOW | Ask clarification |

### C. Supported Units Summary

| Unit | Type | Base Unit | Conversion |
|------|------|-----------|------------|
| pieces | Count | pieces | 1:1 |
| kg | Mass | kg | 1:1 |
| litres | Volume | litres | 1:1 |
| bags | Custom | kg | Product-specific |
| cartons | Custom | pieces | Product-specific |
| boxes | Custom | pieces | Product-specific |
| dozens | Count | pieces | 1:12 |
| quintals | Mass | kg | 1:100 |

### D. Question Type Summary

| Type | Pattern | Output |
|------|---------|--------|
| Current Stock | "How much [product]?" | Current quantity |
| Low Stock | "What is running low?" | List of low-stock products |
| Reorder | "What should I order?" | Reorder recommendations |
| Sales | "What did I sell today?" | Sales summary |
| Why | "Why is [product] low?" | Stock change explanation |
| Where | "Where did [product] go?" | Movement breakdown |
| Customer | "What did [customer] take?" | Customer transactions |
| Time-based | "What happened this week?" | Time-based summary |

---

**End of Functional Requirements Document**
