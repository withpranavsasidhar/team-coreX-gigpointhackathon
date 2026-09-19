# YAAD — Product Requirements Specification
## Requirements Gathering & Analysis Document

**Project:** YAAD (AI Business Memory)
**Document Version:** 1.0
**Date:** September 19, 2026
**Document Type:** Product Requirements Specification (PRS)

---

## Executive Summary

YAAD is a voice-first AI-powered business memory platform designed for small businesses in India. It converts natural speech conversations into structured business events, maintains complete inventory history, understands regional and mixed-language speech, and provides intelligent insights about stock movement, predictions, and reorder recommendations.

**Core Philosophy:** "A shopkeeper should not have to maintain their inventory. Their business should remember itself."

---

## 1. Problem Statement

Small businesses in India manage inventory using notebooks, memory, WhatsApp messages, calculators, or informal conversations. This approach creates:
- Stock shortages and excess inventory
- Missing items and inaccurate records
- Forgotten credit transactions
- Inability to understand why stock changed
- No predictive insights for reordering
- Language barriers with existing software

Existing inventory solutions require typing, technical terminology, English-heavy interfaces, and rigid units—creating high friction for small business owners.

---

## 2. Problem Background

### Market Context
- India has ~63 million MSMEs (Micro, Small & Medium Enterprises)
- Majority are small retail shops, kirana stores, pharmacies, and wholesalers
- Limited digital adoption due to language barriers and technical complexity
- High operational friction in inventory management

### Current Landscape
- Existing inventory apps are form-based, keyboard-heavy, and English-centric
- Voice assistants are general-purpose, not business-specific
- No solution maintains traceable business event history
- Regional language support is poor or non-existent
- Trade units (cartons, dozens, quintals) are not understood

### The Gap
The market lacks a solution that:
- Understands natural business speech
- Supports regional + mixed languages
- Maintains complete business memory
- Explains inventory changes
- Predicts stock needs

---

## 3. Target Users

### Primary Target Market
- **Geographic:** Tier 2, 3, 4 cities and rural India
- **Business Size:** 1-10 employees
- **Business Types:**
  - Kirana stores / General stores
  - Small retail shops
  - Pharmacies
  - Wholesalers
  - Provision stores
  - Electronics shops
  - Hardware stores

### Secondary Target Market
- Small manufacturing units
- Service businesses with inventory needs
- Agricultural input suppliers

---

## 4. User Personas

### Persona A: Ravi — The Kirana Store Owner
**Demographics:**
- Age: 45
- Location: Tier 3 city in Telangana
- Education: High school
- Languages: Telugu (fluent), Hindi (conversational), English (basic)

**Behavior:**
- Manages inventory mentally and in a notebook
- Uses WhatsApp for supplier communication
- Remembers customer credits in memory
- Works 12-14 hours daily
- Tech-savvy enough to use smartphone apps

**Goals:**
- Never run out of fast-moving items
- Remember who owes money
- Understand why stock changes
- Order the right quantities

**Pain Points:**
- Forgets to record transactions
- Cannot explain stock discrepancies
- Doesn't know what to order
- Struggles with English interfaces

---

### Persona B: Meena — The Pharmacy Owner
**Demographics:**
- Age: 38
- Location: Tier 2 city in Karnataka
- Education: College graduate
- Languages: Kannada (fluent), English (good), Hindi (basic)

**Behavior:**
- Uses basic inventory software but finds it slow
- Has to type every transaction
- Manages expiry dates manually
- Needs to track batch numbers

**Goals:**
- Faster stock updates
- Expiry tracking
- Reorder before stockouts
- Customer credit tracking

**Pain Points:**
- Typing is time-consuming
- Software doesn't understand local language terms
- No predictive insights
- Manual expiry management

---

### Persona C: Suresh — The Wholesaler
**Demographics:**
- Age: 52
- Location: Tier 2 city in Maharashtra
- Education: College
- Languages: Marathi (fluent), Hindi (fluent), English (good)

**Behavior:**
- Deals in bulk quantities (quintals, cartons)
- Multiple suppliers
- High transaction volume
- Needs to track stock movement precisely

**Goals:**
- Accurate bulk tracking
- Supplier management
- Movement history
- Reorder timing

**Pain Points:**
- Units like quintals not supported
- Cannot trace where stock went
- No bulk-optimized workflows
- English-only interfaces

---

## 5. Current User Behavior

### Inventory Management Methods
1. **Mental Memory (40%)** — Remember everything
2. **Notebook/Physical Ledger (35%)** — Handwritten records
3. **WhatsApp/Phone (15%)** — Informal communication
4. **Basic Software (8%)** — Simple inventory apps
5. **Calculator (2%)** — Manual calculations

### Recording Habits
- Record during free time (not in real-time)
- Forget to record small transactions
- Mix personal and business transactions
- Inconsistent units (sometimes pieces, sometimes boxes)
- Write in local language/script

### Question-Asking Behavior
- Ask themselves: "What do I have?"
- Ask suppliers: "What should I order?"
- Ask memory: "Who took what?"
- Guess based on recent sales
- No historical analysis

---

## 6. Pain Points

### Operational Pain Points
1. **Time-Consuming Recording** — Typing takes 30-60 seconds per transaction
2. **Language Barrier** — English interfaces require translation effort
3. **Unit Confusion** — Cannot handle cartons, dozens, quintals naturally
4. **Credit Amnesia** — Forget who owes what
5. **Stockout Anxiety** — Constant worry about running out
6. **Excess Inventory** — Over-ordering due to poor visibility

### Cognitive Pain Points
1. **Memory Burden** — Must remember everything mentally
2. **Explainability Gap** — Cannot explain why stock changed
3. **Decision Uncertainty** — Don't know what to order
4. **Discrepancy Confusion** — Stock doesn't match physical count
5. **Historical Blindness** — No access to past patterns

### Technical Pain Points
1. **Complex Interfaces** — Too many fields and forms
2. **English Dominance** — Local language support poor
3. **Rigid Workflows** — Cannot speak naturally
4. **Offline Issues** — Software requires internet
5. **Learning Curve** — Weeks to become proficient

---

## 7. User Goals

### Primary Goals
1. **Speak Naturally** — Update inventory without typing
2. **Business Memory** — System remembers everything
3. **Stock Visibility** — Always know current stock
4. **Explainability** — Understand why stock changed
5. **Predictive Insights** — Know what to order next
6. **Credit Tracking** — Remember who owes money

### Secondary Goals
1. **Language Freedom** — Use preferred language
2. **Unit Flexibility** — Use familiar trade units
3. **Quick Answers** — Ask questions and get answers
4. **Alert Proactivity** — Be warned before stockouts
5. **Movement Tracing** — Know where stock went

### Aspirational Goals
1. **Zero-Touch Inventory** — Business manages itself
2. **Business Intelligence** — Understand patterns
3. **Growth Support** — Scale without chaos
4. **Peace of Mind** — Eliminate inventory anxiety

---

## 8. Product Vision

**"A shopkeeper should not have to maintain their inventory. Their business should remember itself."**

YAAD is an AI-powered business memory engine that:
- Listens to natural business speech
- Understands regional and mixed languages
- Converts conversations into structured events
- Maintains complete business history
- Explains inventory changes
- Predicts future needs
- Recommends actions

**Vision Statement:**
"YAAD transforms small business inventory management from a memory burden into an intelligent, voice-first business memory that speaks the owner's language, remembers every transaction, explains every change, and predicts every need."

---

## 9. Product Positioning

### Market Position
**Category:** Voice-First AI Business Intelligence for Small Business Inventory

### Positioning Statement
"For small business owners who struggle with inventory management, YAAD is a voice-first AI business memory that understands natural speech in regional languages, unlike traditional inventory software that requires typing and English proficiency."

### Competitive Positioning
| Feature | Traditional Inventory Apps | YAAD |
|---------|---------------------------|------|
| Input Method | Typing forms | Voice-first |
| Language Support | English-only | Regional + Mixed |
| Event History | Current state only | Complete event ledger |
| Explainability | None | Why-engine |
| Prediction | None | Stockout forecasting |
| AI Intelligence | None | Business understanding |
| Learning Curve | Weeks | Minutes |

---

## 10. Core Value Proposition

### For the Shop Owner
- **Zero Typing:** Speak to update inventory
- **Language Freedom:** Use your natural language
- **Business Memory:** Never forget a transaction
- **Explainability:** Know why stock changed
- **Predictive Power:** Know what to order
- **Peace of Mind:** Eliminate inventory anxiety

### For the Business
- **Reduced Stockouts:** Predict before running out
- **Better Purchasing:** Data-driven reordering
- **Less Leakage:** Track every movement
- **Faster Operations:** Voice is faster than typing
- **Customer Satisfaction:** Always have stock
- **Credit Control:** Never forget who owes

---

## 11. Unique Differentiation

### Signature Differentiators

**1. Business Memory Engine**
- Maintains complete event ledger, not just current state
- Every stock change is traceable to its source
- Immutable history of all business events

**2. Why-Engine**
- Explains why stock increased or decreased
- Breaks down changes by event type
- Provides natural language explanations

**3. Where-Did-It-Go Engine**
- Reconstructs complete product history
- Identifies all transactions affecting a product
- Answers "Where did my stock go?"

**4. Mixed-Language Business Understanding**
- Understands regional + English combinations
- Detects language automatically
- Normalizes business terminology

**5. Trade-Unit Intelligence**
- Understands cartons, dozens, quintals, bags, etc.
- Supports unit conversions
- Maintains original and normalized quantities

**6. Confidence-Aware AI**
- Asks when information is ambiguous
- Never hallucinates product matches
- Builds trust through clarification

**7. Explainable Inventory**
- Every stock number has a traceable history
- Can drill down to specific events
- Audit-ready business records

**8. Predictive Stock Intelligence**
- Estimates stockout timing
- Calculates reorder quantities
- Provides proactive alerts

### Competitive Moat
- **Event-Led Architecture:** Most apps store state; YAAD stores events
- **Language Understanding:** Native regional + mixed language support
- **Voice-First Design:** Not an add-on, but the primary interface
- **Business Reasoning:** AI understands business context, not just text

---

## 12. Functional Scope

### Core Functional Requirements

#### A. Voice Input Processing
- Accept voice input via microphone
- Convert speech to text using STT
- Support continuous recording with manual stop
- Display transcription for verification
- Allow text input as fallback

#### B. Language Understanding
- Detect input language automatically
- Support Hindi, Telugu, Tamil, Kannada, Marathi, Bengali
- Handle mixed-language input (e.g., "2 cartons Coke vachayi")
- Normalize regional business terminology
- Extract business intent from natural speech

#### C. Business Event Extraction
- Extract event type (STOCK_IN, SALE, STOCK_OUT, etc.)
- Extract product name
- Extract quantity
- Extract unit
- Extract customer (if applicable)
- Extract payment status (if applicable)
- Extract temporal references (today, yesterday, this morning)
- Assign confidence score to extraction

#### D. Validation Engine
- Validate product existence in inventory
- Validate quantity is positive number
- Validate unit is recognized
- Validate unit compatibility with product
- Validate customer exists (if credit sale)
- Check confidence threshold
- Flag ambiguous matches for user confirmation

#### E. Event Ledger
- Store immutable business events
- Record original voice text
- Record normalized text
- Record extracted entities
- Record confidence score
- Record timestamp
- Record source (voice/text)
- Record user confirmation status

#### F. Inventory State Management
- Calculate current stock from event history
- Support multiple units per product
- Maintain unit conversion rules
- Update stock on event creation
- Prevent negative stock (with override option)
- Calculate stock value (if price available)

#### G. Business Memory Query
- Accept natural language questions
- Parse question intent
- Query event ledger
- Query inventory state
- Generate natural language response
- Support question types:
  - Current stock queries
  - Low stock queries
  - Stock movement queries
  - Credit queries
  - Historical queries

#### H. Why-Engine
- Accept "Why is [product] stock low/high?" questions
- Aggregate events by type for product
- Calculate net change by event type
- Generate natural language explanation
- Show timeline of significant events

#### I. Where-Did-It-Go Engine
- Accept "Where did my [product] go?" questions
- Retrieve complete event history for product
- Identify transactions causing stock decrease
- Group by event type and customer
- Provide movement summary

#### J. Stock Intelligence
- Calculate average daily consumption
- Estimate days until stockout
- Identify products below minimum threshold
- Generate low-stock alerts
- Calculate reorder quantities
- Provide reorder recommendations

#### K. Trade-Unit Support
- Support units: pieces, kg, litres, bags, cartons, boxes, dozens, quintals
- Allow custom unit definitions
- Support unit conversion rules (e.g., 1 carton = 24 boxes)
- Maintain original unit and normalized quantity
- Display in user's preferred unit

#### L. Confidence-Aware Interaction
- Display confidence score for extraction
- Auto-confirm high-confidence extractions (>0.85)
- Ask user confirmation for medium confidence (0.60-0.85)
- Reject low-confidence extractions (<0.60)
- Show alternative matches when ambiguous
- Allow user to correct extraction

#### M. Product Management
- Create products with name, category, unit
- Set minimum stock threshold
- Set reorder quantity
- Define unit conversion rules
- Set optional price
- Edit product details
- Delete products (with event history preservation)

#### N. Customer Management
- Create customer profiles
- Record customer name and phone
- Track outstanding credit
- View customer transaction history
- Record credit payments

#### O. Dashboard Views
- Home dashboard with stock summary
- Low-stock alerts panel
- Today's transactions timeline
- Quick voice action button
- Business health summary

#### P. Business Memory Timeline
- Chronological display of all events
- Filter by event type
- Filter by product
- Filter by date range
- Search in timeline
- Event detail view

#### Q. Inventory Views
- Product list with current stock
- Stock status indicators (normal, low, critical)
- Estimated stockout timing
- Quick actions (add/remove stock)
- Product detail view with history

#### R. Insights Views
- Fast-moving products
- Slow-moving products
- Low stock predictions
- Reorder recommendations
- Inventory discrepancies (if physical count entered)

---

## 13. Non-Functional Requirements

### Performance Requirements
- Voice processing latency: <2 seconds from end of speech to extraction
- Query response time: <1 second for stock queries
- Dashboard load time: <2 seconds
- Event creation latency: <500ms
- Support 100+ concurrent users per business
- Support 10,000+ events per business without degradation

### Scalability Requirements
- Horizontal scaling for API layer
- Database indexing for event queries
- Efficient event aggregation for large histories
- Support for multi-tenant architecture
- Future support for multi-store per business

### Reliability Requirements
- 99.5% uptime for core features
- Data persistence guarantee for events
- Graceful degradation when voice service unavailable
- Automatic retry for transient failures
- Data backup and recovery procedures

### Availability Requirements
- API available 24/7
- Voice service with fallback to text
- Offline mode for basic viewing (future)
- Queue offline events for sync (future)

### Maintainability Requirements
- Modular architecture for component replacement
- Clear separation of concerns
- Comprehensive logging
- Monitoring and alerting
- Database migration scripts

### Usability Requirements
- Learn time: <5 minutes for basic voice input
- Voice recognition accuracy: >90% for supported languages
- Natural language understanding accuracy: >85% for common phrases
- Error recovery: Clear error messages with recovery actions
- Mobile-responsive design
- Touch-friendly interface

---

## 14. Regional Language Requirements

### Supported Languages (MVP)
**Primary:**
- Hindi (Devanagari script)
- Telugu
- Tamil
- Kannada
- Marathi

**Secondary (Future):**
- Bengali
- Malayalam
- Gujarati
- Punjabi
- Odia
- Assamese

### Language Detection
- Automatic language detection from input
- Support mixed-language sentences
- Detect language within first 3 words
- Fallback to English if detection fails

### Language Normalization
- Map regional terms to standard entities
- Handle different number formats (lakhs, crores)
- Normalize regional business terminology
- Support phonetic spelling variations

### Output Language
- Respond in the same language as input
- Allow user to set preferred response language
- Support transliteration when needed

### Business Terminology Support
**Hindi Examples:**
- "आया" → STOCK_IN
- "बिक गया" → SALE
- "उधार" → CREDIT

**Telugu Examples:**
- "వచ్చాయి" → STOCK_IN
- "అమ్మాయి" → SALE
- "అప్పు" → CREDIT

**Tamil Examples:**
- "வந்தது" → STOCK_IN
- "விற்றது" → SALE
- "கடன்" → CREDIT

---

## 15. Mixed-Language Speech Requirements

### Mixed-Language Support
- Accept sentences combining regional language + English
- Example: "2 cartons Coke vachayi" (Telugu + English)
- Example: "Panch kilo rice lai liya" (Hindi + English)
- Example: "Rendu boxes biscuits selinjiruken" (Tamil + English)

### Entity Recognition in Mixed Context
- Recognize English product names in regional sentences
- Recognize regional action verbs with English quantities
- Recognize mixed units (e.g., "5 cartons")

### Normalization Strategy
- Identify language segments within sentence
- Apply appropriate NLP model per segment
- Merge extractions into unified event
- Maintain original mixed text for reference

### Confidence Handling
- Lower confidence threshold for mixed-language
- Flag mixed-language for user verification
- Show original and normalized text

---

## 16. Trade-Unit Requirements

### Supported Units (MVP)
**Primary Units:**
- Pieces (individual items)
- Kilograms (kg)
- Litres (L)
- Bags
- Cartons
- Boxes
- Dozens (12 pieces)
- Quintals (100 kg)

**Custom Units (Future):**
- User-defined units
- Business-specific conversions

### Unit Conversion Rules
- Support conversion definitions per product
- Example: 1 carton = 24 boxes
- Example: 1 dozen = 12 pieces
- Example: 1 quintal = 100 kg
- Maintain both original and normalized quantities

### Unit Validation
- Validate unit compatibility with product
- Example: Cannot use "litres" for solid products
- Show warning for unusual unit-product combinations
- Allow override with confirmation

### Unit Display
- Display in user's preferred unit
- Show conversion when displaying different units
- Allow unit selection in views

### Unit Intelligence
- Infer unit from product category when not specified
- Example: "Oil" → default to litres
- Example: "Rice" → default to kg or bags
- Allow user to override inferred unit

---

## 17. Voice Interaction Requirements

### Voice Input Flow
1. User taps microphone button
2. System shows recording indicator
3. User speaks
4. System transcribes in real-time
5. User taps to stop or auto-stop on silence
6. System processes extraction
7. System shows confirmation dialog
8. User confirms or corrects
9. Event created and inventory updated

### Voice Quality Requirements
- Support noisy environments (shop background)
- Handle different accents and dialects
- Support variable speaking speeds
- Handle pauses and hesitations
- Cancel recording with swipe gesture

### Speech Recognition Requirements
- Accuracy: >90% for supported languages
- Latency: <1 second for transcription display
- Support continuous recording up to 30 seconds
- Auto-punctuation for natural reading
- Handle numbers and quantities accurately

### Voice Feedback
- Visual feedback during recording (waveform)
- Haptic feedback on start/stop
- Audio confirmation (optional)
- Error indication for failed recognition

### Fallback to Text
- Always provide text input option
- Edit transcription before processing
- Type directly if voice fails
- Support voice + text combination

---

## 18. Accessibility Requirements

### Visual Accessibility
- High contrast mode support
- Scalable text size
- Color-blind friendly indicators
- Clear icon labels
- Screen reader compatibility

### Motor Accessibility
- Large touch targets (min 44px)
- Voice-first interface reduces need for precise typing
- Swipe gestures for common actions
- Keyboard navigation support

### Cognitive Accessibility
- Simple, uncluttered interface
- Clear error messages
- Progressive disclosure of complex features
- Consistent terminology
- Contextual help

### Language Accessibility
- Multi-language interface
- Regional language display
- Voice output in preferred language
- Text-to-speech for responses (optional)

---

## 19. Performance Requirements

### Response Time Targets
- Voice transcription: <1 second
- Event extraction: <1 second
- Stock query: <500ms
- Dashboard load: <2 seconds
- Event creation: <300ms

### Throughput Targets
- Support 100 concurrent users
- Handle 1000 events/minute
- Support 10,000 events per business query
- 100ms database query latency

### Resource Requirements
- Mobile app: <50MB download
- Battery impact: Minimal for voice processing
- Network: <100KB per voice interaction
- Storage: <100MB for 10,000 events

### Caching Strategy
- Cache current inventory state
- Cache frequent queries
- Cache product metadata
- Invalidate cache on event creation

---

## 20. Security Requirements

### Authentication
- User authentication via phone number
- OTP verification
- Session management
- Auto-logout after inactivity

### Authorization
- Business-level data isolation
- Role-based access (Owner, Staff)
- Staff cannot delete events
- Audit trail for all actions

### Data Security
- Encryption in transit (TLS)
- Encryption at rest (AES-256)
- Secure API endpoints
- SQL injection prevention
- XSS protection

### API Security
- Rate limiting per user
- Request validation
- API key authentication
- CORS configuration

### Input Validation
- Server-side validation for all inputs
- Schema validation for API payloads
- Sanitization of user inputs
- Prevention of injection attacks

---

## 21. Data Privacy Requirements

### Data Collection
- Collect only necessary business data
- Explicit consent for voice recording
- Option to delete voice recordings
- Anonymize voice data for AI training (opt-in)

### Data Ownership
- User owns all business data
- Right to export data
- Right to delete account and data
- Data portability

### Data Retention
- Retain events for minimum 1 year
- Option to extend retention
- Voice recordings: 30 days (configurable)
- Audit logs: 90 days

### Compliance
- GDPR considerations (if EU users)
- India DPDP Act compliance
- Local data storage requirements
- Data residency options

### Third-Party Services
- Voice service: Clear data usage policy
- AI service: No data retention for training
- Cloud provider: SOC 2 compliance
- Data processing agreements

---

## 22. Reliability Requirements

### Uptime Targets
- Core API: 99.5% uptime
- Voice service: 99% uptime
- Database: 99.9% uptime
- Web interface: 99% uptime

### Failure Handling
- Graceful degradation when voice unavailable
- Queue events during network issues
- Retry transient failures automatically
- Clear error messages for users
- Fallback to text input

### Data Integrity
- ACID transactions for event creation
- Event immutability (no updates, only new events)
- Regular data backups
- Point-in-time recovery

### Monitoring
- Uptime monitoring
- Error rate monitoring
- Performance monitoring
- Database health monitoring
- Voice service health monitoring

---

## 23. AI Safety Requirements

### Confidence Thresholds
- High confidence (>0.85): Auto-confirm
- Medium confidence (0.60-0.85): Ask user
- Low confidence (<0.60): Reject and ask clarification

### Hallucination Prevention
- Never guess product matches
- Show alternatives when ambiguous
- Validate against existing inventory
- Require user confirmation for new products

### AI Guardrails
- AI cannot directly modify inventory
- AI proposes → Backend validates → Event created
- Schema validation for AI output
- Confidence-based routing

### Human-in-the-Loop
- Low-confidence extractions require confirmation
- Ambiguous matches require user selection
- Unusual quantities require verification
- New products require explicit creation

### Output Validation
- Validate AI-generated events before storage
- Check for negative quantities
- Check for impossible values
- Validate against business rules

---

## 24. Offline/Failure Considerations

### Network Failure Handling
- Queue events when offline
- Sync when connection restored
- Show offline status indicator
- Allow viewing cached inventory
- Prevent conflicting edits

### Voice Service Failure
- Fallback to text input
- Clear error message
- Retry option
- Alternative voice service (future)

### Database Failure
- Retry with exponential backoff
- Queue writes until recovery
- Read from cache if available
- Graceful error display

### Partial Failure Modes
- Dashboard may load with cached data
- Voice may fail but text works
- Queries may be delayed
- Event creation queued

### Data Conflict Resolution
- Last-write-wins for event creation
- Timestamp-based ordering
- Manual resolution for conflicts (future)
- Conflict notification to user

---

## 25. Hackathon MVP Scope

### MVP Definition
**Timeframe:** 1-day hackathon
**Goal:** Demonstrate core voice-to-inventory loop with business memory

### MUST HAVE Features (Priority 1)

#### Core Loop
- [x] Voice input → Speech-to-text
- [x] Language detection (Hindi, Telugu, English)
- [x] Business event extraction (STOCK_IN, SALE, STOCK_OUT)
- [x] Product, quantity, unit extraction
- [x] Confidence scoring
- [x] User confirmation dialog
- [x] Event ledger storage
- [x] Inventory state calculation
- [x] Current stock display

#### Product Management
- [x] Create product (name, unit, opening stock)
- [x] View product list
- [x] View current stock

#### Voice Interactions
- [x] "Add [quantity] [unit] of [product]"
- [x] "Sold [quantity] [unit] of [product]"
- [x] "Remove [quantity] [unit] of [product]"

#### Mixed-Language Demo
- [x] One regional language example (Telugu + English)
- [x] "2 cartons Coke vachayi" → STOCK_IN

#### Query Capabilities
- [x] "How much [product] do I have?"
- [x] "What is running low?"
- [x] Simple stock display

#### Basic Dashboard
- [x] Product list with stock
- [x] Recent events timeline
- [x] Voice input button

### SHOULD HAVE Features (Priority 2)

#### Enhanced AI
- [ ] Credit sale detection
- [ ] Customer extraction
- [ ] Better confidence thresholds
- [ ] Ambiguity detection

#### Enhanced Queries
- [ ] "Why is [product] stock low?"
- [ ] "Where did my [product] go?"
- [ ] "What did I sell today?"

#### Stock Intelligence
- [ ] Low-stock alerts
- [ ] Stockout estimation
- [ ] Reorder recommendations

#### Trade Units
- [ ] Unit conversion rules
- [ ] Multiple units per product
- [ ] Unit inference from product

#### Timeline
- [ ] Filter by event type
- [ ] Filter by product
- [ ] Event detail view

### NICE TO HAVE Features (Priority 3)

#### Advanced AI
- [ ] More regional languages
- [ ] Better mixed-language handling
- [ ] Temporal expression handling

#### Advanced Queries
- [ ] "What did [customer] take?"
- [ ] "What happened this week?"
- [ ] Natural language date ranges

#### Advanced Intelligence
- [ ] Fast-moving products
- [ ] Slow-moving products
- [ ] Consumption rate calculation

#### User Experience
- [ ] Audio confirmation
- [ ] Voice output
- [ ] Dark mode
- [ ] Better error messages

### FUTURE Features (Post-Hackathon)

#### Phase 2
- Credit management
- Customer profiles
- Payment tracking
- Outstanding credit reports

#### Phase 3
- Supplier management
- Purchase orders
- Supplier lead times
- Purchase suggestions

#### Phase 4
- Advanced forecasting
- Demand prediction
- Seasonal patterns
- AI purchasing assistant

#### Phase 5
- WhatsApp integration
- Phone call interface
- SMS updates
- Multi-channel input

#### Phase 6
- Offline mode
- Local data sync
- Background sync
- Conflict resolution

#### Phase 7
- Multi-store support
- Store transfer events
- Consolidated reporting
- Store comparison

#### Phase 8
- Advanced analytics
- Business insights
- Trend analysis
- Performance metrics

#### Phase 9
- Web dashboard
- Desktop interface
- Export reports
- API access

---

## 26. Explicitly Excluded Features for 1-Day MVP

### Explicitly Out of Scope
- ❌ Credit tracking and management
- ❌ Customer profiles and history
- ❌ Supplier management
- ❌ Purchase order management
- ❌ Multi-language UI (English interface only, regional voice input)
- ❌ Offline mode
- ❌ WhatsApp integration
- ❌ Advanced analytics
- ❌ Expiry date tracking
- ❌ Batch number tracking
- ❌ Price tracking and sales value
- ❌ Multi-store support
- ❌ User roles and permissions
- ❌ Data export
- ❌ Advanced reporting
- ❌ Barcode scanning
- ❌ Image recognition
- ❌ Invoice generation
- ❌ GST/tax calculation
- ❌ Payment gateway integration
- ❌ Multi-currency support
- ❌ Unit conversion rules (basic units only)
- ❌ Custom units
- ❌ Why-engine (stock explanation)
- ❌ Where-did-it-go engine (complete history)
- ❌ Stockout prediction (basic low-stock only)
- ❌ Reorder quantity calculation (manual only)
- ❌ Discrepancy detection
- ❌ Physical count comparison
- ❌ Audit reports
- ❌ Web interface (mobile-first only)
- ❌ Desktop application
- ❌ Multi-user collaboration
- ❌ Real-time sync across devices
- ❌ Push notifications
- ❌ SMS alerts
- ❌ Email reports
- ❌ API for third-party integration
- ❌ White-label customization
- ❌ Enterprise features

### Rationale for Exclusions
- **Time constraints:** 1-day hackathon limits scope
- **Focus:** Demonstrate core voice-to-inventory loop
- **Simplicity:** Reduce complexity for MVP
- **Validation:** Test core hypothesis first
- **User feedback:** Gather feedback before building advanced features

---

## 27. User Journeys

### Journey A: Add Stock by Voice

**User Action:**
1. User taps microphone button
2. User speaks: "I received five cartons of biscuits this morning"
3. User taps stop button

**System Response:**
1. Transcribes: "I received five cartons of biscuits this morning"
2. Extracts:
   - Event type: STOCK_IN
   - Product: Biscuits
   - Quantity: 5
   - Unit: Cartons
   - Confidence: 0.92
3. Shows confirmation dialog:
   - "Add 5 cartons of Biscuits?"
   - [Confirm] [Edit] [Cancel]
4. On confirm: Creates event, updates inventory

**Data Generated:**
- Inventory event:
  ```json
  {
    "event_type": "STOCK_IN",
    "product": "Biscuits",
    "quantity": 5,
    "unit": "cartons",
    "original_text": "I received five cartons of biscuits this morning",
    "confidence": 0.92,
    "timestamp": "2026-09-19T09:10:00Z"
  }
  ```
- Inventory state update: Biscuits +5 cartons

**Validation:**
- Product exists in inventory
- Quantity is positive
- Unit is recognized
- Confidence > 0.85 → auto-confirm eligible

**Success Condition:**
- Event created in ledger
- Inventory state updated
- User sees confirmation
- Dashboard reflects new stock

**Failure Condition:**
- Product not found → Ask to create or select
- Confidence < 0.60 → Ask user to clarify
- Unit not recognized → Ask for unit
- Network error → Queue event

---

### Journey B: Remove Stock by Voice

**User Action:**
1. User taps microphone button
2. User speaks: "Take out five oil packets"
3. User taps stop button

**System Response:**
1. Transcribes: "Take out five oil packets"
2. Extracts:
   - Event type: STOCK_OUT
   - Product: Oil
   - Quantity: 5
   - Unit: Packets
   - Confidence: 0.88
3. Shows confirmation dialog:
   - "Remove 5 packets of Oil?"
   - [Confirm] [Edit] [Cancel]
4. On confirm: Creates event, updates inventory

**Data Generated:**
- Inventory event:
  ```json
  {
    "event_type": "STOCK_OUT",
    "product": "Oil",
    "quantity": 5,
    "unit": "packets",
    "original_text": "Take out five oil packets",
    "confidence": 0.88,
    "timestamp": "2026-09-19T14:30:00Z"
  }
  ```
- Inventory state update: Oil -5 packets

**Validation:**
- Product exists
- Sufficient stock available (warn if not)
- Unit recognized
- Confidence > 0.85

**Success Condition:**
- Event created
- Inventory updated
- User sees confirmation
- Stock not negative (or warning shown)

**Failure Condition:**
- Insufficient stock → Warn and allow override
- Product not found → Ask to select
- Low confidence → Ask clarification

---

### Journey C: Record Credit Sale

**User Action:**
1. User taps microphone button
2. User speaks: "Ramesh took two boxes and will pay tomorrow"
3. User taps stop button

**System Response:**
1. Transcribes: "Ramesh took two boxes and will pay tomorrow"
2. Extracts:
   - Event type: CREDIT_SALE
   - Product: (missing - ambiguous)
   - Quantity: 2
   - Unit: Boxes
   - Customer: Ramesh
   - Payment status: CREDIT
   - Due date: Tomorrow
   - Confidence: 0.72
3. Shows confirmation dialog:
   - "Ramesh took 2 boxes of [Select Product] on credit?"
   - Product dropdown shown
   - [Confirm] [Edit] [Cancel]

**Data Generated:**
- Inventory event:
  ```json
  {
    "event_type": "CREDIT_SALE",
    "product": "Cooking Oil",
    "quantity": 2,
    "unit": "boxes",
    "customer": "Ramesh",
    "payment_status": "CREDIT",
    "due_date": "2026-09-20",
    "original_text": "Ramesh took two boxes and will pay tomorrow",
    "confidence": 0.72,
    "timestamp": "2026-09-19T16:45:00Z"
  }
  ```
- Inventory state update: Cooking Oil -2 boxes
- Customer credit update: Ramesh +2 boxes outstanding

**Validation:**
- Product selected by user
- Customer exists or created
- Unit recognized
- Confidence threshold requires user input

**Success Condition:**
- Event created
- Inventory updated
- Customer credit tracked
- User confirms product selection

**Failure Condition:**
- Product not specified → User must select
- Customer not found → Create or select
- Ambiguous product → Show options

---

### Journey D: Ask Current Stock

**User Action:**
1. User taps query button or types in query box
2. User speaks/types: "How much rice do I have?"

**System Response:**
1. Parses query intent: STOCK_QUERY
2. Extracts entity: Rice
3. Queries inventory state
4. Responds: "You have 25 bags of rice"

**Data Generated:**
- Query log (for analytics)
- No state change

**Validation:**
- Product exists
- Inventory state calculated correctly

**Success Condition:**
- User receives accurate stock information
- Response in natural language
- Response time <1 second

**Failure Condition:**
- Product not found → "Product not found in inventory"
- Multiple matches → "Did you mean X, Y, or Z?"

---

### Journey E: Ask What is Running Low

**User Action:**
1. User taps query button
2. User speaks/types: "What is running low?"

**System Response:**
1. Parses query intent: LOW_STOCK_QUERY
2. Queries all products
3. Filters: current_stock < minimum_threshold
4. Returns list with:
   - Product name
   - Current stock
   - Minimum threshold
   - Estimated stockout (if available)
5. Responds: "Biscuits (5 cartons, min: 10), Oil (3 litres, min: 5)"

**Data Generated:**
- Query log
- No state change

**Validation:**
- Thresholds are set for products
- Stock calculated correctly

**Success Condition:**
- User sees list of low-stock products
- Products ordered by urgency
- Clear indication of stock status

**Failure Condition:**
- No thresholds set → "Set minimum stock for products to see alerts"
- No low stock → "All products are above minimum stock"

---

### Journey F: Ask Why Stock Decreased

**User Action:**
1. User taps query button
2. User speaks/types: "Why is my rice stock low?"

**System Response:**
1. Parses query intent: WHY_QUERY
2. Extracts entity: Rice
3. Queries event ledger for Rice
4. Aggregates by event type:
   - STOCK_IN: +50 bags
   - SALE: -25 bags
   - CREDIT_SALE: -10 bags
   - DAMAGE: -3 bags
5. Calculates net: +12 bags
6. Responds: "Your rice stock is 12 bags. You purchased 50 bags, sold 25 bags, gave 10 bags on credit, and recorded 3 bags as damaged."

**Data Generated:**
- Query log
- No state change

**Validation:**
- Product exists
- Event history available
- Aggregation correct

**Success Condition:**
- User sees breakdown by event type
- Natural language explanation
- Can drill down to specific events

**Failure Condition:**
- Product not found → Error message
- No events → "No transactions recorded for this product"

---

### Journey G: Ask Where Stock Went

**User Action:**
1. User taps query button
2. User speaks/types: "Where did my biscuits go?"

**System Response:**
1. Parses query intent: WHERE_QUERY
2. Extracts entity: Biscuits
3. Queries event ledger for Biscuits
4. Filters for stock-decreasing events (SALE, CREDIT_SALE, DAMAGE, LOSS)
5. Groups by event type and customer:
   - Sale: 15 cartons
   - Credit sale to Ramesh: 5 cartons
   - Credit sale to Suresh: 3 cartons
   - Damage: 2 cartons
6. Responds: "You sold 15 cartons, Ramesh took 5 cartons on credit, Suresh took 3 cartons on credit, and 2 cartons were damaged."

**Data Generated:**
- Query log
- No state change

**Validation:**
- Product exists
- Event history available
- Filtering correct

**Success Condition:**
- User sees complete movement breakdown
- Customer attribution for credit sales
- Can view detailed timeline

**Failure Condition:**
- Product not found → Error message
- No stock-decreasing events → "No stock has been removed"

---

### Journey H: Receive Reorder Recommendation

**User Action:**
1. User views insights dashboard
2. System automatically shows reorder recommendations

**System Response:**
1. Calculates for each product:
   - Current stock
   - Average daily consumption
   - Days until stockout
   - Recommended reorder quantity
2. Displays:
   - Products needing reorder
   - Suggested quantity
   - Urgency level
3. Example: "Order 25 cartons of biscuits (stockout in 3 days)"

**Data Generated:**
- No state change
- Calculations on demand

**Validation:**
- Consumption data available
- Thresholds set
- Calculation logic correct

**Success Condition:**
- User sees actionable recommendations
- Quantities are reasonable
- Urgency is clear

**Failure Condition:**
- Insufficient history → "Need more data for recommendations"
- No consumption pattern → "Not enough sales data"

---

### Journey I: Use Mixed Regional-Language Speech

**User Action:**
1. User taps microphone button
2. User speaks: "2 cartons Coke vachayi" (Telugu + English)
3. User taps stop button

**System Response:**
1. Transcribes: "2 cartons Coke vachayi"
2. Detects mixed language (Telugu + English)
3. Extracts:
   - Event type: STOCK_IN (from "vachayi" = came)
   - Product: Coke
   - Quantity: 2
   - Unit: Cartons
   - Confidence: 0.89
4. Shows confirmation dialog:
   - "Add 2 cartons of Coke?"
   - [Confirm] [Edit] [Cancel]
5. On confirm: Creates event, updates inventory

**Data Generated:**
- Inventory event:
  ```json
  {
    "event_type": "STOCK_IN",
    "product": "Coke",
    "quantity": 2,
    "unit": "cartons",
    "original_text": "2 cartons Coke vachayi",
    "language_detected": "telugu+english",
    "confidence": 0.89,
    "timestamp": "2026-09-19T11:20:00Z"
  }
  ```
- Inventory state update: Coke +2 cartons

**Validation:**
- Language detection successful
- Regional term "vachayi" mapped to STOCK_IN
- Product recognized
- Unit recognized
- Confidence > 0.85

**Success Condition:**
- Mixed-language understood correctly
- Event created accurately
- User can speak naturally
- Response in appropriate language

**Failure Condition:**
- Language not detected → Fallback to English NLP
- Regional term not recognized → Ask for clarification
- Low confidence → Require user confirmation

---

## 28. Success Metrics

### MVP Success Criteria
- [ ] Core voice-to-inventory loop working end-to-end
- [ ] At least 3 voice commands working (add, remove, sale)
- [ ] Mixed-language demo successful
- [ ] Event ledger storing and retrieving events
- [ ] Inventory state calculating correctly
- [ ] Basic queries working (stock, low stock)
- [ ] Demo ready within 1 day

### User Experience Metrics
- Voice recognition accuracy > 85%
- Event extraction accuracy > 80%
- Query response time < 2 seconds
- User can complete first task in < 2 minutes

### Technical Metrics
- API response time < 500ms
- Database query time < 200ms
- Zero data loss during event creation
- 100% event immutability

---

## 29. Risk Assessment

### Technical Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Voice service accuracy low | High | Medium | Fallback to text, improve prompts |
| Language detection fails | Medium | Medium | Default to English, show confidence |
| AI hallucinates products | High | Low | Require user confirmation for new products |
| Database performance issues | Medium | Low | Indexing, caching, query optimization |
| Network reliability | Medium | Medium | Queue events, sync later |

### Product Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Users don't trust AI | High | Medium | Show confidence, allow confirmation |
| Regional language support poor | High | Medium | Focus on 1-2 languages for MVP |
| Mixed-language understanding weak | Medium | High | Simplify to basic patterns |
| Learning curve too steep | Medium | Low | Simple onboarding, clear UI |

### Business Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Cannot complete MVP in 1 day | High | Medium | Strict scope prioritization |
| Demo fails during presentation | High | Low | Prepare fallback scenarios |
| Integration with voice service fails | High | Low | Have backup STT option |

---

## 30. Assumptions

### Technical Assumptions
- Voice-to-text API available and reliable
- LLM API available for entity extraction
- Can deploy backend in cloud (Render/Railway)
- Can use PostgreSQL or MongoDB
- Mobile web app sufficient for MVP

### User Assumptions
- Users have smartphones with microphones
- Users have basic internet connectivity
- Users can read basic English (interface language)
- Users willing to try voice input

### Business Assumptions
- 1-day hackathon sufficient for MVP
- Focus on demo over production readiness
- Can defer advanced features to future phases
- Single developer or small team

---

## 31. Dependencies

### External Services
- Speech-to-Text API (Google, AWS, or Azure)
- LLM API (OpenAI, Anthropic, or similar)
- Cloud hosting (Render, Railway, or AWS)
- Database service (Supabase, MongoDB Atlas, or similar)

### Internal Dependencies
- Product database schema designed
- API endpoints specified
- Frontend framework chosen
- Event extraction prompts designed

### Technical Dependencies
- Python 3.9+ or Node.js 18+
- React or Next.js for frontend
- FastAPI or Express for backend
- PostgreSQL or MongoDB for database

---

## 32. Constraints

### Time Constraints
- 1-day hackathon timeframe
- Hard deadline for demo
- Limited time for testing

### Resource Constraints
- Single developer or small team
- Limited budget for paid APIs
- Limited infrastructure

### Technical Constraints
- Cannot build native mobile app (web only)
- Cannot implement offline mode
- Cannot support all regional languages
- Cannot build complete feature set

### Scope Constraints
- MVP focus only
- Single business per user
- English interface only
- Basic units only

---

## 33. Open Questions

### Technical Questions
1. Which STT service to use? (Google, AWS, Azure, or other)
2. Which LLM to use for extraction? (OpenAI, Anthropic, or other)
3. Which database? (PostgreSQL or MongoDB)
4. Which frontend framework? (React, Next.js, or Vue)

### Product Questions
1. Which regional languages to prioritize for MVP?
2. How to handle ambiguous product matches?
3. What confidence thresholds to use?
4. How to display mixed-language text?

### Business Questions
1. Target demo scenario for hackathon?
2. Success criteria for judges?
3. Expected audience for demo?
4. Follow-up plan after hackathon?

---

## 34. Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| Event Ledger | Immutable record of all business events |
| Business Memory | Complete history of all inventory transactions |
| Why-Engine | Feature that explains why stock changed |
| Trade Units | Business-specific units (cartons, dozens, quintals) |
| Mixed-Language | Sentences combining regional language + English |
| Confidence Score | AI's certainty about extraction accuracy (0-1) |
| Stockout | When inventory reaches zero |
| Reorder Recommendation | Suggested quantity to order based on consumption |

### B. Event Types

| Event Type | Description | Stock Impact |
|------------|-------------|--------------|
| STOCK_IN | Stock received from supplier | + |
| SALE | Cash sale to customer | - |
| STOCK_OUT | Stock removed (not sold) | - |
| PURCHASE | Stock purchased by business | + |
| CREDIT_SALE | Sale on credit to customer | - |
| DAMAGE | Stock damaged | - |
| LOSS | Stock lost/stolen | - |
| RETURN | Customer return | + |
| ADJUSTMENT | Manual stock correction | +/- |
| STOCK_TRANSFER | Stock moved between locations | 0 (transfer) |

### C. Sample Voice Commands

**English:**
- "Add 20 bags of rice"
- "I sold 5 boxes of biscuits"
- "Remove 3 litres of oil"
- "Ramesh took 2 packets on credit"
- "I damaged 1 carton of soap"

**Mixed-Language:**
- "2 cartons Coke vachayi" (Telugu: came)
- "Panch kilo rice lai liya" (Hindi: took)
- "Rendu boxes biscuits selinjiruken" (Tamil: selling)

**Questions:**
- "How much rice do I have?"
- "What is running low?"
- "Why is my oil stock low?"
- "Where did my biscuits go?"
- "What should I order?"

### D. Technology Stack Options

**Frontend:**
- Option 1: React + Tailwind CSS
- Option 2: Next.js + Tailwind CSS
- Option 3: Vue.js + Tailwind CSS

**Backend:**
- Option 1: FastAPI + Python
- Option 2: Express + Node.js
- Option 3: Django + Python

**Database:**
- Option 1: PostgreSQL (Supabase)
- Option 2: MongoDB (MongoDB Atlas)
- Option 3: SQLite (local, for MVP)

**AI Services:**
- STT: Google Cloud Speech-to-Text
- LLM: OpenAI GPT-4 or Anthropic Claude
- Alternative: Local models (Whisper, LLaMA)

---

## 35. Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | | | |
| Tech Lead | | | |
| Developer | | | |

---

## 36. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-19 | Devin | Initial requirements specification |

---

**End of Requirements Specification**
