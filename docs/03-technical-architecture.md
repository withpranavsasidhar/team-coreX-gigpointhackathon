# YAAD — Technical Architecture Document
## Production-Style System Architecture

**Project:** YAAD (AI Business Memory)
**Document Version:** 1.0
**Date:** September 19, 2026
**Document Type:** Technical Architecture Document (TAD)

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Component Architecture](#component-architecture)
3. [Frontend Architecture](#frontend-architecture)
4. [Backend Architecture](#backend-architecture)
5. [AI Pipeline Architecture](#ai-pipeline-architecture)
6. [Voice Pipeline](#voice-pipeline)
7. [Business Event Engine](#business-event-engine)
8. [Business Memory Architecture](#business-memory-architecture)
9. [Inventory Calculation Architecture](#inventory-calculation-architecture)
10. [Analytics Architecture](#analytics-architecture)
11. [Security Architecture](#security-architecture)
12. [Error-Handling Architecture](#error-handling-architecture)
13. [Deployment Architecture](#deployment-architecture)
14. [Core Flow](#core-flow)
15. [Database Schema](#database-schema)
16. [REST API Specification](#rest-api-specification)
17. [Provider Interfaces](#provider-interfaces)
18. [Folder Structure](#folder-structure)
19. [Environment Configuration](#environment-configuration)

---

## High-Level Architecture

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Web App    │  │  Mobile Web  │  │   Future:    │          │
│  │  (Next.js)   │  │  (PWA)       │  │   Native     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘          │
└─────────┼──────────────────┼───────────────────────────────────┘
          │                  │
          │ HTTPS/REST       │
          ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend Service                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │   │
│  │  │   Auth   │  │  Voice   │  │   AI     │  │ Query  │ │   │
│  │  │  Module  │  │  Module  │  │  Module  │  │ Module │ │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │   │
│  │  │ Product  │  │Inventory │  │ Business │  │Analytics│ │   │
│  │  │  Module  │  │  Module  │  │  Memory  │  │ Module  │ │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────┐
│                   EXTERNAL SERVICES LAYER                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │   STT    │  │   LLM    │  │   SMS    │  │  Future  │         │
│  │ Provider │  │ Provider │  │ Provider │  │ Services │         │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────┐
│                      DATA LAYER                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              PostgreSQL Database                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │   │
│  │  │  users   │  │businesses│  │ products │  │ events  │ │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │   │
│  │  │customers │  │  alerts  │  │conversions│               │   │
│  │  └──────────┘  └──────────┘  └──────────┘               │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

1. **AI Interprets, Backend Validates, Database Decides Truth**
   - AI extracts structured data from natural language
   - Backend validates against business rules
   - Database is the single source of truth

2. **Event-Led Architecture**
   - All state changes through immutable events
   - Current state derived from event history
   - Complete audit trail

3. **Provider Abstraction**
   - Speech-to-text providers behind interface
   - LLM providers behind interface
   - Easy to swap without changing business logic

4. **Separation of Concerns**
   - Frontend: UI and user interaction
   - Backend: Business logic and validation
   - Database: Data persistence and truth

5. **API-First Design**
   - RESTful API with clear contracts
   - Request/response schemas defined
   - Versioned endpoints

---

## Component Architecture

### Component Diagram

```mermaid
graph TB
    subgraph "Frontend Components"
        UI[UI Components]
        State[State Management]
        API[API Client]
        Voice[Voice Recorder]
    end

    subgraph "Backend Components"
        Router[API Router]
        Auth[Auth Service]
        VoiceProcessor[Voice Processor]
        AIExtractor[AI Extractor]
        Validator[Event Validator]
        InventoryCalc[Inventory Calculator]
        QueryEngine[Query Engine]
        Analytics[Analytics Engine]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL)]
        Cache[(Redis Cache)]
    end

    subgraph "External Services"
        STT[STT Provider]
        LLM[LLM Provider]
        SMS[SMS Provider]
    end

    UI --> State
    State --> API
    Voice --> API
    API --> Router
    Router --> Auth
    Router --> VoiceProcessor
    Router --> AIExtractor
    Router --> Validator
    Router --> InventoryCalc
    Router --> QueryEngine
    Router --> Analytics

    VoiceProcessor --> STT
    AIExtractor --> LLM
    Auth --> SMS

    Auth --> DB
    VoiceProcessor --> DB
    AIExtractor --> DB
    Validator --> DB
    InventoryCalc --> DB
    QueryEngine --> DB
    Analytics --> DB

    InventoryCalc --> Cache
    QueryEngine --> Cache
```

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| UI Components | Render UI, handle user interactions |
| State Management | Manage application state, API responses |
| API Client | Make HTTP requests, handle responses |
| Voice Recorder | Capture audio, handle permissions |
| API Router | Route requests to appropriate handlers |
| Auth Service | Authentication, session management |
| Voice Processor | STT integration, audio processing |
| AI Extractor | LLM integration, entity extraction |
| Event Validator | Validate events against business rules |
| Inventory Calculator | Calculate current stock from events |
| Query Engine | Process natural language queries |
| Analytics Engine | Calculate insights, recommendations |
| PostgreSQL | Persist data, maintain truth |
| Redis Cache | Cache inventory state, query results |

---

## Frontend Architecture

### Technology Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** React Context + useState/useReducer
- **HTTP Client:** fetch API with TypeScript types
- **Forms:** React Hook Form
- **Validation:** Zod
- **Voice:** Web Speech API (browser native)

### Frontend Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home/Dashboard
│   ├── login/
│   │   └── page.tsx        # Login page
│   ├── products/
│   │   ├── page.tsx        # Product list
│   │   └── [id]/
│   │       └── page.tsx    # Product details
│   ├── inventory/
│   │   └── page.tsx        # Inventory view
│   ├── events/
│   │   └── page.tsx        # Event timeline
│   ├── query/
│   │   └── page.tsx        # Query interface
│   └── insights/
│       └── page.tsx        # Insights & alerts
├── components/
│   ├── ui/                 # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   └── ...
│   ├── voice/              # Voice components
│   │   ├── VoiceRecorder.tsx
│   │   ├── TranscriptionDisplay.tsx
│   │   └── ConfirmationDialog.tsx
│   ├── inventory/          # Inventory components
│   │   ├── ProductCard.tsx
│   │   ├── StockIndicator.tsx
│   │   └── EventTimeline.tsx
│   └── query/              # Query components
│       ├── QueryInput.tsx
│       └── ResponseDisplay.tsx
├── lib/
│   ├── api.ts              # API client
│   ├── types.ts            # TypeScript types
│   ├── utils.ts            # Utility functions
│   └── constants.ts        # Constants
├── hooks/
│   ├── useVoice.ts         # Voice recording hook
│   ├── useInventory.ts     # Inventory data hook
│   └── useQuery.ts         # Query processing hook
├── contexts/
│   ├── AuthContext.tsx     # Authentication context
│   └── BusinessContext.tsx # Business context
└── styles/
    └── globals.css         # Global styles
```

### State Management Strategy

**Context-based State:**
- `AuthContext`: User session, authentication state
- `BusinessContext`: Current business, products, customers

**Component-level State:**
- Form state (React Hook Form)
- UI state (modals, loading, errors)
- Voice recording state

**Server State:**
- Fetch data directly in Next.js Server Components
- Use SWR or React Query for client-side caching (optional for MVP)

### API Client Design

```typescript
// lib/api.ts
class APIClient {
  private baseURL: string;
  private token: string | null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('token');
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new APIError(response.status, await response.json());
    }

    return response.json();
  }

  // Voice processing
  async processVoice(audioBlob: Blob): Promise<VoiceResponse> {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    return this.request('/api/voice/process', {
      method: 'POST',
      body: formData,
    });
  }

  // Events
  async createEvent(event: EventCreate): Promise<Event> {
    return this.request('/api/events', {
      method: 'POST',
      body: JSON.stringify(event),
    });
  }

  // Inventory
  async getInventory(): Promise<InventoryItem[]> {
    return this.request('/api/inventory');
  }

  async getProductHistory(productId: string): Promise<Event[]> {
    return this.request(`/api/inventory/${productId}/history`);
  }

  // Query
  async askQuery(query: string): Promise<QueryResponse> {
    return this.request('/api/query', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }

  // Products
  async createProduct(product: ProductCreate): Promise<Product> {
    return this.request('/api/products', {
      method: 'POST',
      body: JSON.stringify(product),
    });
  }

  async updateProduct(id: string, product: ProductUpdate): Promise<Product> {
    return this.request(`/api/products/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(product),
    });
  }

  // Customers
  async createCustomer(customer: CustomerCreate): Promise<Customer> {
    return this.request('/api/customers', {
      method: 'POST',
      body: JSON.stringify(customer),
    });
  }

  // Alerts
  async getAlerts(): Promise<Alert[]> {
    return this.request('/api/alerts');
  }

  // Analytics
  async getAnalytics(): Promise<Analytics> {
    return this.request('/api/analytics');
  }
}
```

### Voice Recording Component

```typescript
// components/voice/VoiceRecorder.tsx
import { useState, useRef, useCallback } from 'react';

interface VoiceRecorderProps {
  onTranscription: (text: string) => void;
  onError: (error: Error) => void;
}

export function VoiceRecorder({ onTranscription, onError }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      const chunks: BlobPart[] = [];
      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        // Send to backend for STT processing
        onTranscription(''); // Placeholder - will be replaced with backend response
      };

      mediaRecorder.start();
      setIsRecording(true);

      // Also use Web Speech API for real-time transcription
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-IN'; // Default to Indian English

        recognition.onresult = (event) => {
          const current = event.resultIndex;
          const transcript = event.results[current][0].transcript;
          setTranscript(transcript);
        };

        recognition.onerror = (event) => {
          onError(new Error(event.error));
        };

        recognition.start();
        recognitionRef.current = recognition;
      }
    } catch (error) {
      onError(error as Error);
    }
  }, [onTranscription, onError]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsRecording(false);
  }, []);

  return (
    <div className="voice-recorder">
      <button
        onClick={isRecording ? stopRecording : startRecording}
        className={`mic-button ${isRecording ? 'recording' : ''}`}
      >
        {isRecording ? '⏹️' : '🎤'}
      </button>
      {isRecording && (
        <div className="transcript-display">
          {transcript || 'Listening...'}
        </div>
      )}
    </div>
  );
}
```

---

## Backend Architecture

### Technology Stack

- **Framework:** FastAPI 0.104+
- **Language:** Python 3.11+
- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0+
- **Validation:** Pydantic 2.0+
- **Async:** asyncio
- **CORS:** fastapi-cors
- **Authentication:** JWT (python-jose)

### Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry
│   ├── config.py            # Configuration management
│   ├── dependencies.py      # Dependency injection
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── business.py
│   │   ├── product.py
│   │   ├── event.py
│   │   ├── customer.py
│   │   ├── alert.py
│   │   └── conversion.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── business.py
│   │   ├── product.py
│   │   ├── event.py
│   │   ├── customer.py
│   │   ├── alert.py
│   │   └── query.py
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── voice.py
│   │   ├── events.py
│   │   ├── inventory.py
│   │   ├── query.py
│   │   ├── products.py
│   │   ├── customers.py
│   │   ├── alerts.py
│   │   └── analytics.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── voice_service.py
│   │   ├── ai_service.py
│   │   ├── event_service.py
│   │   ├── inventory_service.py
│   │   ├── query_service.py
│   │   ├── alert_service.py
│   │   └── analytics_service.py
│   ├── providers/           # External service providers
│   │   ├── __init__.py
│   │   ├── base.py          # Base provider interfaces
│   │   ├── stt/
│   │   │   ├── __init__.py
│   │   │   ├── base.py      # STT provider interface
│   │   │   ├── google.py    # Google Cloud STT
│   │   │   └── openai.py    # OpenAI Whisper
│   │   └── llm/
│   │       ├── __init__.py
│   │       ├── base.py      # LLM provider interface
│   │       ├── openai.py    # OpenAI GPT
│   │       └── anthropic.py # Anthropic Claude
│   ├── core/                # Core business logic
│   │   ├── __init__.py
│   │   ├── event_validator.py
│   │   ├── inventory_calculator.py
│   │   ├── confidence_engine.py
│   │   └── business_rules.py
│   ├── utils/               # Utility functions
│   │   ├── __init__.py
│   │   ├── language.py      # Language detection
│   │   ├── normalization.py # Text normalization
│   │   └── cache.py         # Cache utilities
│   └── middleware/          # Custom middleware
│       ├── __init__.py
│       ├── auth.py
│       └── error_handler.py
├── tests/                   # Tests
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_services.py
│   └── test_core.py
├── alembic/                 # Database migrations
│   ├── versions/
│   └── env.py
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
└── run.py                   # Application entry point
```

### FastAPI Application Structure

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api import auth, voice, events, inventory, query, products, customers, alerts, analytics
from app.middleware.error_handler import error_handler

# Create FastAPI app
app = FastAPI(
    title="YAAD API",
    description="AI Business Memory Platform",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handler
app.exception_handler(Exception)(error_handler)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(query.router, prefix="/api/query", tags=["Query"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

# Startup event
@app.on_event("startup")
async def startup():
    # Create tables (for development - use migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Dependency Injection

```python
# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import AuthService
from app.config import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user"""
    token = credentials.credentials
    auth_service = AuthService(db)
    user = await auth_service.verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user

async def get_current_business(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current business for user"""
    # Assuming user has one business for MVP
    return current_user.business_id
```

---

## AI Pipeline Architecture

### AI Pipeline Flow

```mermaid
graph LR
    A[Audio Input] --> B[Speech-to-Text]
    B --> C[Language Detection]
    C --> D[Language Normalization]
    D --> E[Business Context Injection]
    E --> F[LLM Structured Extraction]
    F --> G[JSON Schema Validation]
    G --> H[Confidence Check]
    H --> I{Confidence Level}
    I -->|High| J[Business Rule Validation]
    I -->|Medium| K[User Confirmation]
    I -->|Low| L[Ask Clarification]
    K --> J
    J --> M[Create Business Event]
    M --> N[Event Ledger]
    N --> O[Inventory State Update]
    O --> P[Analytics Recalculation]
    P --> Q[Response Generation]
```

### AI Pipeline Components

#### 1. Speech-to-Text (STT)

**Provider Interface:**
```python
# app/providers/stt/base.py
from abc import ABC, abstractmethod
from typing import Optional

class SpeechToTextProvider(ABC):
    """Base interface for speech-to-text providers"""

    @abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio to text

        Args:
            audio_data: Raw audio bytes
            language: Language code (e.g., 'en-IN', 'hi-IN')

        Returns:
            Dict with:
                - text: Transcribed text
                - confidence: Transcription confidence (0-1)
                - language: Detected language
        """
        pass

    @abstractmethod
    async def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None
    ) -> dict:
        """Transcribe audio file"""
        pass
```

**Google Cloud STT Implementation:**
```python
# app/providers/stt/google.py
from app.providers.stt.base import SpeechToTextProvider
from google.cloud.speech import SpeechClient, RecognitionConfig, RecognitionAudio

class GoogleSpeechToText(SpeechToTextProvider):
    def __init__(self, credentials_path: str):
        self.client = SpeechClient.from_service_account_file(credentials_path)

    async def transcribe(self, audio_data: bytes, language: str = "en-IN") -> dict:
        audio = RecognitionAudio(content=audio_data)
        config = RecognitionConfig(
            encoding=RecognitionConfig.Encoding.WEBM_OPUS,
            language_code=language,
            enable_automatic_punctuation=True,
        )

        response = self.client.recognize(config=config, audio=audio)

        text = " ".join(result.alternatives[0].transcript for result in response.results)
        confidence = response.results[0].alternatives[0].confidence if response.results else 0.0

        return {
            "text": text,
            "confidence": confidence,
            "language": language,
        }
```

#### 2. Language Detection

```python
# app/utils/language.py
from typing import Optional
import re

class LanguageDetector:
    """Detect language from text"""

    # Simple pattern-based detection for MVP
    LANGUAGE_PATTERNS = {
        "hi": r"[\u0900-\u097F]",  # Devanagari (Hindi)
        "te": r"[\u0C00-\u0C7F]",  # Telugu
        "ta": r"[\u0B80-\u0BFF]",  # Tamil
        "kn": r"[\u0C80-\u0CFF]",  # Kannada
        "mr": r"[\u0900-\u097F]",  # Marathi (same as Hindi)
    }

    @classmethod
    def detect(cls, text: str) -> str:
        """Detect primary language from text"""
        for lang, pattern in cls.LANGUAGE_PATTERNS.items():
            if re.search(pattern, text):
                return lang
        return "en"  # Default to English

    @classmethod
    def is_mixed(cls, text: str) -> bool:
        """Check if text contains multiple languages"""
        detected_languages = set()
        for lang, pattern in cls.LANGUAGE_PATTERNS.items():
            if re.search(pattern, text):
                detected_languages.add(lang)
        if re.search(r"[a-zA-Z]", text):
            detected_languages.add("en")
        return len(detected_languages) > 1
```

#### 3. Language Normalization

```python
# app/utils/normalization.py
from typing import Dict, List

class TextNormalizer:
    """Normalize text for AI processing"""

    # Regional term mappings
    REGIONAL_MAPPINGS = {
        "hi": {
            "आया": "STOCK_IN",
            "बिक गया": "SALE",
            "उधार": "CREDIT",
            "निकाला": "STOCK_OUT",
        },
        "te": {
            "వచ్చాయి": "STOCK_IN",
            "అమ్మాయి": "SALE",
            "అప్పు": "CREDIT",
        },
        "ta": {
            "வந்தது": "STOCK_IN",
            "விற்றது": "SALE",
            "கடன்": "CREDIT",
        },
    }

    @classmethod
    def normalize(cls, text: str, language: str) -> str:
        """Normalize regional terminology"""
        if language in cls.REGIONAL_MAPPINGS:
            for regional_term, standard_term in cls.REGIONAL_MAPPINGS[language].items():
                text = text.replace(regional_term, standard_term)
        return text

    @classmethod
    def normalize_numbers(cls, text: str, language: str) -> str:
        """Normalize number formats (e.g., lakhs, crores)"""
        # MVP: Basic normalization
        # Future: Handle regional number formats
        return text
```

#### 4. Business Context Injection

```python
# app/services/ai_service.py
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.models.customer import Customer

class AIContextBuilder:
    """Build business context for AI extraction"""

    @staticmethod
    async def build_context(
        db: AsyncSession,
        business_id: str
    ) -> Dict:
        """Build context dictionary for LLM"""
        # Fetch products
        from sqlalchemy import select
        result = await db.execute(
            select(Product).where(Product.business_id == business_id)
        )
        products = result.scalars().all()

        # Fetch customers
        result = await db.execute(
            select(Customer).where(Customer.business_id == business_id)
        )
        customers = result.scalars().all()

        return {
            "products": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "category": p.category,
                    "base_unit": p.base_unit,
                }
                for p in products
            ],
            "customers": [
                {
                    "id": str(c.id),
                    "name": c.name,
                    "phone": c.phone,
                }
                for c in customers
            ],
        }
```

#### 5. LLM Structured Extraction

**Provider Interface:**
```python
# app/providers/llm/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class AIExtractionProvider(ABC):
    """Base interface for AI extraction providers"""

    @abstractmethod
    async def extract_event(
        self,
        text: str,
        context: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract structured event from text

        Args:
            text: Normalized text
            context: Business context (products, customers)
            schema: Expected output schema

        Returns:
            Structured event extraction with confidence scores
        """
        pass
```

**OpenAI Implementation:**
```python
# app/providers/llm/openai.py
from openai import AsyncOpenAI
from app.providers.llm.base import AIExtractionProvider
from typing import Dict, Any

class OpenAIExtraction(AIExtractionProvider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def extract_event(
        self,
        text: str,
        context: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = self._build_prompt(text, context, schema)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a business event extraction system. Extract structured events from natural language."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3,  # Low temperature for consistent extraction
        )

        import json
        extraction = json.loads(response.choices[0].message.content)

        # Add confidence scores (simplified for MVP)
        extraction["confidence"] = {
            "overall": 0.85,  # Placeholder - would be calculated based on model confidence
            "event_type": 0.9,
            "product": 0.85,
            "quantity": 0.9,
            "unit": 0.85,
        }

        return extraction

    def _build_prompt(self, text: str, context: Dict, schema: Dict) -> str:
        return f"""
Extract a business event from the following text:

Text: "{text}"

Available Products:
{self._format_products(context['products'])}

Available Customers:
{self._format_customers(context['customers'])}

Output Schema:
{json.dumps(schema, indent=2)}

Extract the event and return as JSON.
"""

    def _format_products(self, products: List[Dict]) -> str:
        return "\n".join([f"- {p['name']} (ID: {p['id']}, Unit: {p['base_unit']})" for p in products])

    def _format_customers(self, customers: List[Dict]) -> str:
        return "\n".join([f"- {c['name']} (ID: {c['id']})" for c in customers])
```

#### 6. JSON Schema Validation

```python
# app/core/event_validator.py
from pydantic import BaseModel, ValidationError
from typing import Optional, Literal
from decimal import Decimal

class EventExtractionSchema(BaseModel):
    event_type: Literal["STOCK_IN", "SALE", "STOCK_OUT", "PURCHASE", "CREDIT_SALE", "RETURN", "DAMAGE", "LOSS", "ADJUSTMENT"]
    product: str
    quantity: int
    unit: str
    confidence: dict
    customer: Optional[str] = None
    price: Optional[Decimal] = None
    payment_status: Optional[Literal["CASH", "CREDIT", "PARTIAL", "PENDING"]] = None
    due_date: Optional[str] = None

class EventValidator:
    """Validate event extraction against schema"""

    @staticmethod
    def validate(extraction: dict) -> tuple[bool, Optional[str], Optional[EventExtractionSchema]]:
        """Validate extraction and return (is_valid, error_message, validated_data)"""
        try:
            validated = EventExtractionSchema(**extraction)
            return True, None, validated
        except ValidationError as e:
            return False, str(e), None
```

#### 7. Confidence Check

```python
# app/core/confidence_engine.py
from typing import Literal

class ConfidenceEngine:
    """Determine confidence level and behavior"""

    THRESHOLDS = {
        "HIGH": 0.85,
        "MEDIUM": 0.60,
    }

    @staticmethod
    def get_level(confidence: float) -> Literal["HIGH", "MEDIUM", "LOW"]:
        """Get confidence level from score"""
        if confidence >= ConfidenceEngine.THRESHOLDS["HIGH"]:
            return "HIGH"
        elif confidence >= ConfidenceEngine.THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        else:
            return "LOW"

    @staticmethod
    def should_auto_confirm(confidence: float) -> bool:
        """Check if extraction should be auto-confirmed"""
        return confidence >= ConfidenceEngine.THRESHOLDS["HIGH"]

    @staticmethod
    def should_ask_confirmation(confidence: float) -> bool:
        """Check if user confirmation is needed"""
        level = ConfidenceEngine.get_level(confidence)
        return level == "MEDIUM"

    @staticmethod
    def should_reject(confidence: float) -> bool:
        """Check if extraction should be rejected"""
        return confidence < ConfidenceEngine.THRESHOLDS["MEDIUM"]
```

---

## Voice Pipeline

### Voice Processing Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant STT as STT Provider
    participant AI as AI Provider
    participant DB as Database

    U->>F: Tap microphone
    F->>F: Start recording
    U->>F: Speak
    F->>F: Stop recording
    F->>B: POST /api/voice/process (audio)
    B->>STT: Transcribe audio
    STT->>B: Return transcription
    B->>B: Detect language
    B->>B: Normalize text
    B->>B: Build context
    B->>AI: Extract event
    AI->>B: Return extraction
    B->>B: Validate schema
    B->>B: Check confidence
    B->>F: Return extraction with confidence
    F->>U: Show confirmation (if needed)
    U->>F: Confirm
    F->>B: POST /api/events
    B->>DB: Create event
    B->>DB: Update inventory
    B->>F: Return success
    F->>U: Show success
```

### Voice Service Implementation

```python
# app/services/voice_service.py
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.providers.stt.base import SpeechToTextProvider
from app.providers.llm.base import AIExtractionProvider
from app.utils.language import LanguageDetector
from app.utils.normalization import TextNormalizer
from app.services.ai_service import AIContextBuilder
from app.core.event_validator import EventValidator
from app.core.confidence_engine import ConfidenceEngine

class VoiceService:
    def __init__(
        self,
        stt_provider: SpeechToTextProvider,
        llm_provider: AIExtractionProvider,
        db: AsyncSession
    ):
        self.stt_provider = stt_provider
        self.llm_provider = llm_provider
        self.db = db

    async def process_voice(
        self,
        audio_data: bytes,
        business_id: str,
        language: Optional[str] = None
    ) -> Dict:
        """Process voice input through complete pipeline"""

        # Step 1: Speech-to-Text
        transcription_result = await self.stt_provider.transcribe(audio_data, language)
        text = transcription_result["text"]
        detected_language = transcription_result.get("language", "en")

        # Step 2: Language Detection
        if not language:
            language = LanguageDetector.detect(text)

        # Step 3: Language Normalization
        normalized_text = TextNormalizer.normalize(text, language)

        # Step 4: Business Context Injection
        context = await AIContextBuilder.build_context(self.db, business_id)

        # Step 5: LLM Structured Extraction
        schema = self._get_extraction_schema()
        extraction = await self.llm_provider.extract_event(normalized_text, context, schema)

        # Step 6: JSON Schema Validation
        is_valid, error, validated = EventValidator.validate(extraction)
        if not is_valid:
            return {
                "success": False,
                "error": f"Validation failed: {error}",
                "original_text": text,
                "normalized_text": normalized_text,
            }

        # Step 7: Confidence Check
        overall_confidence = extraction["confidence"]["overall"]
        confidence_level = ConfidenceEngine.get_level(overall_confidence)

        return {
            "success": True,
            "original_text": text,
            "normalized_text": normalized_text,
            "language_detected": detected_language,
            "extraction": extraction,
            "confidence_level": confidence_level,
            "should_auto_confirm": ConfidenceEngine.should_auto_confirm(overall_confidence),
            "should_ask_confirmation": ConfidenceEngine.should_ask_confirmation(overall_confidence),
            "should_reject": ConfidenceEngine.should_reject(overall_confidence),
        }

    def _get_extraction_schema(self) -> Dict:
        """Return expected extraction schema"""
        return {
            "type": "object",
            "properties": {
                "event_type": {"type": "string"},
                "product": {"type": "string"},
                "quantity": {"type": "integer"},
                "unit": {"type": "string"},
                "customer": {"type": "string", "optional": True},
                "confidence": {
                    "type": "object",
                    "properties": {
                        "overall": {"type": "number"},
                        "event_type": {"type": "number"},
                        "product": {"type": "number"},
                        "quantity": {"type": "number"},
                        "unit": {"type": "number"},
                    }
                }
            },
            "required": ["event_type", "product", "quantity", "unit", "confidence"]
        }
```

---

## Business Event Engine

### Event Engine Architecture

```mermaid
graph TB
    subgraph "Event Engine"
        A[Event Extraction] --> B[Schema Validation]
        B --> C[Confidence Check]
        C --> D{Confidence Level}
        D -->|High| E[Business Rule Validation]
        D -->|Medium| F[User Confirmation]
        D -->|Low| G[Ask Clarification]
        F --> E
        G --> H[Retry]
        E --> I[Event Creation]
        I --> J[Event Ledger]
        J --> K[Inventory Update]
        K --> L[Analytics Trigger]
    end
```

### Event Service Implementation

```python
# app/services/event_service.py
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.event import Event
from app.models.product import Product
from app.core.business_rules import BusinessRules
from app.core.inventory_calculator import InventoryCalculator

class EventService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.business_rules = BusinessRules()
        self.inventory_calculator = InventoryCalculator(db)

    async def create_event(
        self,
        event_data: Dict,
        business_id: str,
        user_id: str
    ) -> Event:
        """Create validated business event"""

        # Validate product exists
        product = await self._validate_product(event_data["product"], business_id)
        if not product:
            raise ValueError(f"Product not found: {event_data['product']}")

        # Validate against business rules
        validation_result = await self.business_rules.validate_event(
            event_data,
            product,
            business_id
        )
        if not validation_result["valid"]:
            raise ValueError(f"Business rule validation failed: {validation_result['error']}")

        # Create event
        event = Event(
            business_id=business_id,
            product_id=product.id,
            event_type=event_data["event_type"],
            quantity=event_data["quantity"],
            unit=event_data["unit"],
            original_text=event_data.get("original_text"),
            normalized_text=event_data.get("normalized_text"),
            confidence=event_data.get("confidence", {}).get("overall", 0.0),
            source=event_data.get("source", "voice"),
            customer_id=event_data.get("customer_id"),
            price=event_data.get("price"),
            payment_status=event_data.get("payment_status"),
            due_date=event_data.get("due_date"),
            created_by=user_id,
        )

        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)

        # Update inventory state
        await self.inventory_calculator.update_inventory(product.id)

        # Trigger analytics recalculation
        await self._trigger_analytics(business_id, product.id)

        return event

    async def _validate_product(self, product_name: str, business_id: str) -> Optional[Product]:
        """Validate product exists and return product object"""
        result = await self.db.execute(
            select(Product).where(
                Product.business_id == business_id,
                Product.name.ilike(f"%{product_name}%")
            )
        )
        return result.scalar_one_or_none()

    async def _trigger_analytics(self, business_id: str, product_id: str):
        """Trigger analytics recalculation (async)"""
        # For MVP: simple trigger
        # Future: Use background tasks or message queue
        pass
```

### Business Rules Implementation

```python
# app/core/business_rules.py
from typing import Dict
from app.models.product import Product

class BusinessRules:
    """Business rule validation engine"""

    SUPPORTED_UNITS = ["pieces", "kg", "litres", "bags", "cartons", "boxes", "dozens", "quintals"]

    STOCK_DECREASING_EVENTS = ["SALE", "STOCK_OUT", "CREDIT_SALE", "DAMAGE", "LOSS"]

    async def validate_event(
        self,
        event_data: Dict,
        product: Product,
        business_id: str
    ) -> Dict:
        """Validate event against business rules"""

        # Rule 1: Quantity must be positive
        if event_data["quantity"] <= 0:
            return {
                "valid": False,
                "error": "Quantity must be positive"
            }

        # Rule 2: Unit must be supported
        if event_data["unit"] not in self.SUPPORTED_UNITS:
            return {
                "valid": False,
                "error": f"Unit not supported: {event_data['unit']}"
            }

        # Rule 3: Unit must be compatible with product
        if not self._is_unit_compatible(event_data["unit"], product):
            return {
                "valid": False,
                "error": f"Unit {event_data['unit']} not compatible with product {product.name}"
            }

        # Rule 4: Stock-decreasing events must have sufficient stock (warning only)
        if event_data["event_type"] in self.STOCK_DECREASING_EVENTS:
            current_stock = await self._get_current_stock(product.id)
            if current_stock < event_data["quantity"]:
                # Warning, not error - allow override
                return {
                    "valid": True,
                    "warning": f"This will make stock negative. Current: {current_stock}, Removing: {event_data['quantity']}"
                }

        return {"valid": True}

    def _is_unit_compatible(self, unit: str, product: Product) -> bool:
        """Check if unit is compatible with product"""
        # MVP: Simple check - unit must match base unit or be in conversion rules
        if unit == product.base_unit:
            return True
        # Future: Check conversion rules
        return True  # Allow for MVP

    async def _get_current_stock(self, product_id: str) -> int:
        """Get current stock for product"""
        # This would call InventoryCalculator
        # For now, return placeholder
        return 0
```

---

## Business Memory Architecture

### Event Ledger Design

```mermaid
erDiagram
    EVENT ||--o{ PRODUCT : "references"
    EVENT ||--o{ BUSINESS : "belongs to"
    EVENT ||--o{ USER : "created by"
    EVENT ||--o| CUSTOMER : "references"

    EVENT {
        uuid id PK
        uuid business_id FK
        uuid product_id FK
        string event_type
        integer quantity
        string unit
        uuid customer_id FK
        decimal price
        string payment_status
        date due_date
        string original_text
        string normalized_text
        float confidence
        string source
        uuid created_by FK
        timestamp created_at
    }
```

### Event Ledger Implementation

```python
# app/models/event.py
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit = Column(String(50), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    payment_status = Column(String(50), nullable=True)
    due_date = Column(DateTime, nullable=True)
    original_text = Column(Text, nullable=True)
    normalized_text = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)
    source = Column(String(50), default="voice")
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="events")
    product = relationship("Product", back_populates="events")
    customer = relationship("Customer", back_populates="events")
    creator = relationship("User", back_populates="created_events")

    def __repr__(self):
        return f"<Event {self.event_type} {self.quantity} {self.unit} of {self.product.name}>"
```

### Event Query Service

```python
# app/services/event_service.py (continued)
from typing import List, Optional
from sqlalchemy import select, and_
from datetime import datetime, timedelta

class EventQueryService:
    """Query event ledger"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_product_events(
        self,
        product_id: str,
        business_id: str,
        limit: int = 100
    ) -> List[Event]:
        """Get all events for a product"""
        result = await self.db.execute(
            select(Event)
            .where(
                and_(
                    Event.product_id == product_id,
                    Event.business_id == business_id
                )
            )
            .order_by(Event.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_events_by_type(
        self,
        event_type: str,
        business_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Get events by type"""
        query = select(Event).where(
            and_(
                Event.event_type == event_type,
                Event.business_id == business_id
            )
        )

        if start_date:
            query = query.where(Event.created_at >= start_date)
        if end_date:
            query = query.where(Event.created_at <= end_date)

        result = await self.db.execute(query.order_by(Event.created_at.desc()))
        return result.scalars().all()

    async def get_events_by_customer(
        self,
        customer_id: str,
        business_id: str
    ) -> List[Event]:
        """Get events for a customer"""
        result = await self.db.execute(
            select(Event)
            .where(
                and_(
                    Event.customer_id == customer_id,
                    Event.business_id == business_id
                )
            )
            .order_by(Event.created_at.desc())
        )
        return result.scalars().all()

    async def aggregate_events_by_type(
        self,
        product_id: str,
        business_id: str
    ) -> Dict[str, int]:
        """Aggregate events by type for a product"""
        from sqlalchemy import func

        result = await self.db.execute(
            select(Event.event_type, func.sum(Event.quantity))
            .where(
                and_(
                    Event.product_id == product_id,
                    Event.business_id == business_id
                )
            )
            .group_by(Event.event_type)
        )

        return {row[0]: row[1] for row in result.all()}
```

---

## Inventory Calculation Architecture

### Inventory Calculator

```python
# app/core/inventory_calculator.py
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.event import Event
from app.models.product import Product

class InventoryCalculator:
    """Calculate current stock from event history"""

    STOCK_INCREASING_EVENTS = ["STOCK_IN", "PURCHASE", "RETURN", "ADJUSTMENT"]
    STOCK_DECREASING_EVENTS = ["SALE", "STOCK_OUT", "CREDIT_SALE", "DAMAGE", "LOSS"]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_current_stock(self, product_id: str, business_id: str) -> int:
        """Calculate current stock from event history"""

        # Sum stock-increasing events
        stock_in_result = await self.db.execute(
            select(func.sum(Event.quantity))
            .where(
                and_(
                    Event.product_id == product_id,
                    Event.business_id == business_id,
                    Event.event_type.in_(self.STOCK_INCREASING_EVENTS)
                )
            )
        )
        stock_in = stock_in_result.scalar() or 0

        # Sum stock-decreasing events
        stock_out_result = await self.db.execute(
            select(func.sum(Event.quantity))
            .where(
                and_(
                    Event.product_id == product_id,
                    Event.business_id == business_id,
                    Event.event_type.in_(self.STOCK_DECREASING_EVENTS)
                )
            )
        )
        stock_out = stock_out_result.scalar() or 0

        # Handle ADJUSTMENT events separately (can be positive or negative)
        adjustment_result = await self.db.execute(
            select(Event.quantity)
            .where(
                and_(
                    Event.product_id == product_id,
                    Event.business_id == business_id,
                    Event.event_type == "ADJUSTMENT"
                )
            )
        )
        adjustments = adjustment_result.scalars().all()
        # For MVP, adjustments are treated as setting absolute value
        # This is simplified - proper implementation would calculate delta
        adjustment = sum(adjustments) if adjustments else 0

        current_stock = stock_in - stock_out + adjustment
        return max(0, current_stock)  # Don't return negative stock

    async def update_inventory(self, product_id: str):
        """Update cached inventory state for product"""
        # For MVP: Calculate on demand
        # Future: Update inventory_state table
        pass

    async def get_all_inventory(self, business_id: str) -> Dict[str, int]:
        """Get current stock for all products"""
        result = await self.db.execute(
            select(Product)
            .where(Product.business_id == business_id)
        )
        products = result.scalars().all()

        inventory = {}
        for product in products:
            inventory[str(product.id)] = await self.calculate_current_stock(
                product.id, business_id
            )

        return inventory
```

### Unit Conversion

```python
# app/core/unit_converter.py
from typing import Dict, Optional

class UnitConverter:
    """Handle unit conversions"""

    BASE_UNITS = {
        "pieces": "pieces",
        "kg": "kg",
        "litres": "litres",
    }

    CONVERSION_RULES = {
        "dozens": {"to_base": 12, "base_unit": "pieces"},
        "quintals": {"to_base": 100, "base_unit": "kg"},
    }

    @classmethod
    def to_base_unit(cls, quantity: int, unit: str, conversion_rules: Optional[Dict] = None) -> tuple[int, str]:
        """Convert quantity to base unit"""
        if unit in cls.BASE_UNITS:
            return quantity, unit

        if unit in cls.CONVERSION_RULES:
            rule = cls.CONVERSION_RULES[unit]
            converted = quantity * rule["to_base"]
            return converted, rule["base_unit"]

        if conversion_rules and unit in conversion_rules:
            rule = conversion_rules[unit]
            converted = quantity * rule["to_base"]
            return converted, rule["base_unit"]

        # If no conversion rule, assume it's already in base unit
        return quantity, unit

    @classmethod
    def from_base_unit(cls, quantity: int, base_unit: str, target_unit: str, conversion_rules: Optional[Dict] = None) -> int:
        """Convert from base unit to target unit"""
        if base_unit == target_unit:
            return quantity

        # Find conversion rule
        if conversion_rules and target_unit in conversion_rules:
            rule = conversion_rules[target_unit]
            return quantity // rule["to_base"]

        if target_unit in cls.CONVERSION_RULES:
            rule = cls.CONVERSION_RULES[target_unit]
            return quantity // rule["to_base"]

        return quantity
```

---

## Analytics Architecture

### Analytics Engine

```python
# app/services/analytics_service.py
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from app.models.event import Event
from app.models.product import Product
from app.core.inventory_calculator import InventoryCalculator

class AnalyticsService:
    """Calculate business analytics and insights"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.inventory_calculator = InventoryCalculator(db)

    async def get_low_stock_products(self, business_id: str) -> List[Dict]:
        """Get products with low stock"""
        result = await self.db.execute(
            select(Product)
            .where(Product.business_id == business_id)
        )
        products = result.scalars().all()

        low_stock = []
        for product in products:
            current_stock = await self.inventory_calculator.calculate_current_stock(
                product.id, business_id
            )

            if current_stock < product.minimum_quantity:
                low_stock.append({
                    "product_id": str(product.id),
                    "name": product.name,
                    "current_stock": current_stock,
                    "minimum_quantity": product.minimum_quantity,
                    "status": "critical" if current_stock < product.minimum_quantity * 0.5 else "low"
                })

        return low_stock

    async def get_sales_summary(
        self,
        business_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Get sales summary for date range"""
        result = await self.db.execute(
            select(
                func.sum(Event.quantity).label("total_quantity"),
                func.count(Event.id).label("total_transactions")
            )
            .where(
                and_(
                    Event.business_id == business_id,
                    Event.event_type.in_(["SALE", "CREDIT_SALE"]),
                    Event.created_at >= start_date,
                    Event.created_at <= end_date
                )
            )
        )
        row = result.one()

        return {
            "total_quantity": row.total_quantity or 0,
            "total_transactions": row.total_transactions or 0,
        }

    async def calculate_consumption_rate(
        self,
        product_id: str,
        business_id: str,
        days: int = 14
    ) -> float:
        """Calculate average daily consumption"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        result = await self.db.execute(
            select(func.sum(Event.quantity))
            .where(
                and_(
                    Event.product_id == product_id,
                    Event.business_id == business_id,
                    Event.event_type.in_(["SALE", "CREDIT_SALE"]),
                    Event.created_at >= start_date,
                    Event.created_at <= end_date
                )
            )
        )
        total_sold = result.scalar() or 0

        return total_sold / days if days > 0 else 0

    async def estimate_stockout_days(
        self,
        product_id: str,
        business_id: str
    ) -> Optional[int]:
        """Estimate days until stockout"""
        current_stock = await self.inventory_calculator.calculate_current_stock(
            product_id, business_id
        )

        if current_stock <= 0:
            return 0

        daily_consumption = await self.calculate_consumption_rate(product_id, business_id)

        if daily_consumption <= 0:
            return None  # No consumption data

        return int(current_stock / daily_consumption)

    async def calculate_reorder_recommendation(
        self,
        product_id: str,
        business_id: str,
        lead_time_days: int = 7
    ) -> Dict:
        """Calculate reorder recommendation"""
        current_stock = await self.inventory_calculator.calculate_current_stock(
            product_id, business_id
        )

        daily_consumption = await self.calculate_consumption_rate(product_id, business_id)

        if daily_consumption <= 0:
            return {
                "should_reorder": False,
                "reason": "Insufficient consumption data"
            }

        safety_stock = daily_consumption * 2  # 2-day buffer
        reorder_point = (daily_consumption * lead_time_days) + safety_stock

        if current_stock >= reorder_point:
            return {
                "should_reorder": False,
                "current_stock": current_stock,
                "reorder_point": reorder_point,
            }

        recommended_order = int(reorder_point - current_stock)

        days_until_stockout = await self.estimate_stockout_days(product_id, business_id)

        return {
            "should_reorder": True,
            "current_stock": current_stock,
            "recommended_order": recommended_order,
            "reorder_point": reorder_point,
            "days_until_stockout": days_until_stockout,
            "urgency": self._get_urgency(days_until_stockout),
        }

    def _get_urgency(self, days_until_stockout: Optional[int]) -> str:
        """Determine urgency level"""
        if days_until_stockout is None:
            return "unknown"
        if days_until_stockout <= 3:
            return "urgent"
        if days_until_stockout <= 7:
            return "high"
        if days_until_stockout <= 14:
            return "medium"
        return "low"
```

---

## Security Architecture

### Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB as Database
    participant SMS as SMS Provider

    U->>F: Enter phone number
    F->>B: POST /api/auth/send-otp
    B->>B: Generate OTP
    B->>SMS: Send OTP
    SMS->>U: Receive OTP
    B->>DB: Store OTP (with expiry)
    B->>F: Return success
    U->>F: Enter OTP
    F->>B: POST /api/auth/verify-otp
    B->>DB: Verify OTP
    B->>B: Generate JWT token
    B->>F: Return token
    F->>F: Store token
```

### JWT Authentication

```python
# app/services/auth_service.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.config import settings

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(self, data: dict) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def verify_token(self, token: str) -> Optional[User]:
        """Verify JWT token and return user"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None

            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            return user

        except JWTError:
            return None

    async def send_otp(self, phone: str) -> bool:
        """Send OTP to phone number"""
        # Generate OTP
        otp = str(100000 + (hash(phone) % 900000))  # Simple hash-based OTP
        expiry = datetime.utcnow() + timedelta(minutes=5)

        # Store OTP (would use Redis in production)
        # For MVP: Store in database or memory
        # Send via SMS provider
        return True

    async def verify_otp(self, phone: str, otp: str) -> Optional[User]:
        """Verify OTP and return user"""
        # Verify OTP
        # Create user if not exists
        # Return user
        return None
```

### Authorization Middleware

```python
# app/middleware/auth.py
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.dependencies import get_current_user

security = HTTPBearer()

async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user = Depends(get_current_user)
):
    """Require authentication for endpoint"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return current_user

async def require_business_access(
    current_user = Depends(require_auth),
    business_id: str = None
):
    """Require user has access to business"""
    # Check if user belongs to business
    return current_user
```

---

## Error-Handling Architecture

### Error Response Schema

```python
# app/schemas/error.py
from pydantic import BaseModel
from typing import Optional, Any

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[list[ErrorDetail]] = None
    request_id: Optional[str] = None
```

### Error Handler Middleware

```python
# app/middleware/error_handler.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

async def error_handler(request: Request, exc: Exception):
    """Global error handler"""

    request_id = request.headers.get("X-Request-ID", "unknown")

    # Handle HTTP exceptions
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.detail,
                "request_id": request_id,
            }
        )

    # Handle database errors
    if isinstance(exc, SQLAlchemyError):
        logger.error(f"Database error: {exc}", extra={"request_id": request_id})
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Database error occurred",
                "request_id": request_id,
            }
        )

    # Handle validation errors
    if isinstance(exc, ValueError):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": str(exc),
                "request_id": request_id,
            }
        )

    # Handle unknown errors
    logger.error(f"Unexpected error: {exc}", extra={"request_id": request_id})
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An unexpected error occurred",
            "request_id": request_id,
        }
    )
```

### Custom Exceptions

```python
# app/core/exceptions.py
class YAADException(Exception):
    """Base exception for YAAD"""
    pass

class ProductNotFoundError(YAADException):
    """Product not found"""
    pass

class InsufficientStockError(YAADException):
    """Insufficient stock"""
    pass

class InvalidEventError(YAADException):
    """Invalid event"""
    pass

class ConfidenceError(YAADException):
    """Low confidence extraction"""
    pass
```

---

## Deployment Architecture

### Deployment Diagram

```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "Frontend"
            Vercel[Vercel - Next.js]
        end

        subgraph "Backend"
            Render[Render - FastAPI]
        end

        subgraph "Database"
            Supabase[Supabase - PostgreSQL]
        end

        subgraph "Cache"
            Redis[Redis - Optional]
        end

        subgraph "External Services"
            STT[STT Provider]
            LLM[LLM Provider]
            SMS[SMS Provider]
        end
    end

    Vercel -->|HTTPS| Render
    Render -->|Connection Pool| Supabase
    Render -->|Optional| Redis
    Render -->|API Calls| STT
    Render -->|API Calls| LLM
    Render -->|API Calls| SMS
```

### Environment Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "YAAD API"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "https://yaad.app"]

    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # External Services
    STT_PROVIDER: str = "google"  # google, openai
    STT_API_KEY: str = ""
    STT_CREDENTIALS_PATH: str = ""

    LLM_PROVIDER: str = "openai"  # openai, anthropic
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4"

    SMS_PROVIDER: str = "twilio"  # twilio
    SMS_API_KEY: str = ""
    SMS_API_SECRET: str = ""
    SMS_FROM_NUMBER: str = ""

    # Cache (Optional)
    REDIS_URL: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### Deployment Configuration

**Frontend (Vercel):**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://yaad-api.onrender.com"
  }
}
```

**Backend (Render):**
```yaml
# render.yaml
services:
  - type: web
    name: yaad-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: yaad-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: STT_API_KEY
        sync: false
      - key: LLM_API_KEY
        sync: false
```

---

## Core Flow

### Complete Voice-to-Inventory Flow

```mermaid
graph TD
    A[AUDIO INPUT] --> B[SPEECH TO TEXT]
    B --> C[LANGUAGE DETECTION]
    C --> D[LANGUAGE NORMALIZATION]
    D --> E[BUSINESS CONTEXT INJECTION]
    E --> F[LLM STRUCTURED EXTRACTION]
    F --> G[JSON SCHEMA VALIDATION]
    G --> H[CONFIDENCE CHECK]
    H --> I{CONFIDENCE LEVEL}
    I -->|HIGH >= 0.85| J[BUSINESS RULE VALIDATION]
    I -->|MEDIUM 0.60-0.84| K[USER CONFIRMATION]
    I -->|LOW < 0.60| L[ASK CLARIFICATION]
    K --> J
    L --> M[RETRY]
    J --> N{VALIDATION RESULT}
    N -->|PASS| O[CREATE BUSINESS EVENT]
    N -->|FAIL| P[SHOW ERROR]
    O --> Q[EVENT LEDGER]
    Q --> R[INVENTORY STATE UPDATE]
    R --> S[ANALYTICS RECALCULATION]
    S --> T[RESPONSE GENERATION]
    T --> U[DISPLAY TO USER]
```

### Flow Implementation

```python
# app/api/voice.py
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_business
from app.services.voice_service import VoiceService
from app.services.event_service import EventService
from app.providers.stt.google import GoogleSpeechToText
from app.providers.llm.openai import OpenAIExtraction
from app.config import settings

router = APIRouter()

@router.post("/process")
async def process_voice(
    audio: UploadFile = File(...),
    business_id: str = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    """Process voice input through complete pipeline"""

    # Read audio data
    audio_data = await audio.read()

    # Initialize providers
    stt_provider = GoogleSpeechToText(settings.STT_CREDENTIALS_PATH)
    llm_provider = OpenAIExtraction(settings.LLM_API_KEY, settings.LLM_MODEL)

    # Process voice
    voice_service = VoiceService(stt_provider, llm_provider, db)
    result = await voice_service.process_voice(audio_data, business_id)

    if not result["success"]:
        return result

    # Handle based on confidence
    if result["should_auto_confirm"]:
        # Auto-create event
        event_service = EventService(db)
        event = await event_service.create_event(
            result["extraction"],
            business_id,
            "system"  # user_id would come from auth
        )
        return {
            "success": True,
            "event": event,
            "auto_confirmed": True,
        }
    elif result["should_ask_confirmation"]:
        # Return for user confirmation
        return {
            "success": True,
            "requires_confirmation": True,
            "extraction": result["extraction"],
            "original_text": result["original_text"],
        }
    else:
        # Low confidence - ask clarification
        return {
            "success": False,
            "requires_clarification": True,
            "message": "Could not understand. Please rephrase.",
        }
```

---

## Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ BUSINESS : "owns"
    USER ||--o{ EVENT : "creates"
    BUSINESS ||--o{ PRODUCT : "has"
    BUSINESS ||--o{ EVENT : "has"
    BUSINESS ||--o{ CUSTOMER : "has"
    BUSINESS ||--o{ ALERT : "has"
    PRODUCT ||--o{ EVENT : "references"
    PRODUCT ||--o{ UNIT_CONVERSION : "has"
    PRODUCT ||--o{ ALERT : "generates"
    CUSTOMER ||--o{ EVENT : "references"

    USER {
        uuid id PK
        string name
        string phone
        string email
        string preferred_language
        uuid business_id FK
        timestamp created_at
    }

    BUSINESS {
        uuid id PK
        string name
        string business_type
        string location
        string default_language
        timestamp created_at
    }

    PRODUCT {
        uuid id PK
        uuid business_id FK
        string name
        string category
        string base_unit
        integer current_quantity
        integer minimum_quantity
        integer reorder_quantity
        decimal price
        timestamp created_at
        timestamp updated_at
    }

    EVENT {
        uuid id PK
        uuid business_id FK
        uuid product_id FK
        string event_type
        integer quantity
        string unit
        uuid customer_id FK
        decimal price
        string payment_status
        date due_date
        string original_text
        string normalized_text
        float confidence
        string source
        uuid created_by FK
        timestamp created_at
    }

    CUSTOMER {
        uuid id PK
        uuid business_id FK
        string name
        string phone
        decimal outstanding_credit
        timestamp created_at
    }

    ALERT {
        uuid id PK
        uuid product_id FK
        uuid business_id FK
        string alert_type
        string severity
        string message
        boolean is_dismissed
        timestamp created_at
    }

    UNIT_CONVERSION {
        uuid id PK
        uuid product_id FK
        string from_unit
        string to_unit
        float conversion_factor
        timestamp created_at
    }
```

### Database Migration

```python
# alembic/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(20), unique=True, nullable=False),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('preferred_language', sa.String(10), default='en'),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('businesses.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Businesses
    op.create_table(
        'businesses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('business_type', sa.String(50)),
        sa.Column('location', sa.String(100)),
        sa.Column('default_language', sa.String(10), default='en'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Products
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('businesses.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50)),
        sa.Column('base_unit', sa.String(50), nullable=False),
        sa.Column('current_quantity', sa.Integer, default=0),
        sa.Column('minimum_quantity', sa.Integer, default=0),
        sa.Column('reorder_quantity', sa.Integer, default=0),
        sa.Column('price', sa.Numeric(10, 2)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Events
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('businesses.id'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('customers.id')),
        sa.Column('price', sa.Numeric(10, 2)),
        sa.Column('payment_status', sa.String(50)),
        sa.Column('due_date', sa.DateTime),
        sa.Column('original_text', sa.Text),
        sa.Column('normalized_text', sa.Text),
        sa.Column('confidence', sa.Float, default=0.0),
        sa.Column('source', sa.String(50), default='voice'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Customers
    op.create_table(
        'customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('businesses.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(20)),
        sa.Column('outstanding_credit', sa.Numeric(10, 2), default=0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Alerts
    op.create_table(
        'alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id')),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('businesses.id'), nullable=False),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('is_dismissed', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Unit Conversions
    op.create_table(
        'unit_conversions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('from_unit', sa.String(50), nullable=False),
        sa.Column('to_unit', sa.String(50), nullable=False),
        sa.Column('conversion_factor', sa.Float, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table('unit_conversions')
    op.drop_table('alerts')
    op.drop_table('customers')
    op.drop_table('events')
    op.drop_table('products')
    op.drop_table('businesses')
    op.drop_table('users')
```

---

## REST API Specification

### API Endpoints

#### POST /api/voice/process

Process voice input and extract business event.

**Request:**
```http
POST /api/voice/process
Content-Type: multipart/form-data
Authorization: Bearer <token>

audio: <binary audio data>
```

**Response (Success):**
```json
{
  "success": true,
  "original_text": "I received five cartons of biscuits",
  "normalized_text": "I received five cartons of biscuits",
  "language_detected": "en",
  "extraction": {
    "event_type": "STOCK_IN",
    "product": "Biscuits",
    "quantity": 5,
    "unit": "cartons",
    "confidence": {
      "overall": 0.92,
      "event_type": 0.95,
      "product": 0.90,
      "quantity": 0.95,
      "unit": 0.90
    }
  },
  "confidence_level": "HIGH",
  "should_auto_confirm": true,
  "should_ask_confirmation": false,
  "should_reject": false
}
```

**Response (Requires Confirmation):**
```json
{
  "success": true,
  "requires_confirmation": true,
  "extraction": {
    "event_type": "STOCK_IN",
    "product": "Biscuits",
    "quantity": 5,
    "unit": "cartons",
    "confidence": {
      "overall": 0.78
    }
  },
  "original_text": "I received five cartons of biscuits"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Could not understand audio",
  "request_id": "abc123"
}
```

---

#### POST /api/events

Create a validated business event.

**Request:**
```http
POST /api/events
Content-Type: application/json
Authorization: Bearer <token>

{
  "event_type": "STOCK_IN",
  "product": "Biscuits",
  "quantity": 5,
  "unit": "cartons",
  "original_text": "I received five cartons of biscuits",
  "normalized_text": "I received five cartons of biscuits",
  "confidence": {
    "overall": 0.92
  },
  "source": "voice"
}
```

**Response (Success):**
```json
{
  "success": true,
  "event": {
    "id": "uuid",
    "business_id": "uuid",
    "product_id": "uuid",
    "event_type": "STOCK_IN",
    "quantity": 5,
    "unit": "cartons",
    "created_at": "2026-09-19T09:10:00Z"
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Product not found: Biscuits",
  "details": [
    {
      "field": "product",
      "message": "Product not found"
    }
  ]
}
```

---

#### GET /api/inventory

Get current inventory for all products.

**Request:**
```http
GET /api/inventory
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "inventory": [
    {
      "product_id": "uuid",
      "name": "Biscuits",
      "category": "Snacks",
      "current_stock": 25,
      "unit": "cartons",
      "minimum_quantity": 10,
      "status": "normal"
    },
    {
      "product_id": "uuid",
      "name": "Cooking Oil",
      "category": "Oils",
      "current_stock": 3,
      "unit": "litres",
      "minimum_quantity": 5,
      "status": "critical"
    }
  ]
}
```

---

#### GET /api/inventory/:id/history

Get event history for a specific product.

**Request:**
```http
GET /api/inventory/{product_id}/history
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "product": {
    "id": "uuid",
    "name": "Biscuits",
    "current_stock": 25
  },
  "events": [
    {
      "id": "uuid",
      "event_type": "STOCK_IN",
      "quantity": 5,
      "unit": "cartons",
      "created_at": "2026-09-19T09:10:00Z",
      "original_text": "I received five cartons of biscuits"
    },
    {
      "id": "uuid",
      "event_type": "SALE",
      "quantity": 2,
      "unit": "cartons",
      "created_at": "2026-09-19T14:30:00Z",
      "original_text": "Sold two cartons of biscuits"
    }
  ]
}
```

---

#### POST /api/query

Ask natural language question about inventory.

**Request:**
```http
POST /api/query
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": "How much rice do I have?"
}
```

**Response:**
```json
{
  "success": true,
  "query_type": "current_stock",
  "response": "You have 25 bags of rice.",
  "data": {
    "product": "Rice",
    "current_stock": 25,
    "unit": "bags",
    "status": "normal"
  }
}
```

---

#### GET /api/alerts

Get current alerts for the business.

**Request:**
```http
GET /api/alerts
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "alerts": [
    {
      "id": "uuid",
      "product_id": "uuid",
      "product_name": "Cooking Oil",
      "alert_type": "low_stock",
      "severity": "critical",
      "message": "Cooking Oil is critically low (3 litres, minimum: 5)",
      "created_at": "2026-09-19T10:00:00Z"
    }
  ]
}
```

---

#### GET /api/analytics

Get business analytics and insights.

**Request:**
```http
GET /api/analytics
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "analytics": {
    "low_stock_products": [
      {
        "product_id": "uuid",
        "name": "Cooking Oil",
        "current_stock": 3,
        "minimum_quantity": 5,
        "status": "critical"
      }
    ],
    "reorder_recommendations": [
      {
        "product_id": "uuid",
        "name": "Biscuits",
        "should_reorder": true,
        "recommended_order": 25,
        "urgency": "high",
        "days_until_stockout": 5
      }
    ],
    "sales_summary": {
      "today": {
        "total_quantity": 15,
        "total_transactions": 8
      },
      "this_week": {
        "total_quantity": 85,
        "total_transactions": 42
      }
    }
  }
}
```

---

#### POST /api/products

Create a new product.

**Request:**
```http
POST /api/products
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Biscuits",
  "category": "Snacks",
  "base_unit": "cartons",
  "opening_stock": 10,
  "minimum_quantity": 5,
  "reorder_quantity": 20,
  "price": 250.00
}
```

**Response:**
```json
{
  "success": true,
  "product": {
    "id": "uuid",
    "name": "Biscuits",
    "category": "Snacks",
    "base_unit": "cartons",
    "current_quantity": 10,
    "minimum_quantity": 5,
    "reorder_quantity": 20,
    "price": 250.00,
    "created_at": "2026-09-19T08:00:00Z"
  }
}
```

---

#### PATCH /api/products/:id

Update an existing product.

**Request:**
```http
PATCH /api/products/{product_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "minimum_quantity": 8,
  "reorder_quantity": 25
}
```

**Response:**
```json
{
  "success": true,
  "product": {
    "id": "uuid",
    "name": "Biscuits",
    "minimum_quantity": 8,
    "reorder_quantity": 25,
    "updated_at": "2026-09-19T12:00:00Z"
  }
}
```

---

#### POST /api/customers

Create a new customer.

**Request:**
```http
POST /api/customers
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Ramesh",
  "phone": "+919876543210"
}
```

**Response:**
```json
{
  "success": true,
  "customer": {
    "id": "uuid",
    "name": "Ramesh",
    "phone": "+919876543210",
    "outstanding_credit": 0,
    "created_at": "2026-09-19T08:00:00Z"
  }
}
```

---

## Provider Interfaces

### SpeechToTextProvider Interface

```python
# app/providers/stt/base.py
from abc import ABC, abstractmethod
from typing import Optional

class SpeechToTextProvider(ABC):
    """Base interface for speech-to-text providers"""

    @abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio to text

        Args:
            audio_data: Raw audio bytes
            language: Language code (e.g., 'en-IN', 'hi-IN')

        Returns:
            Dict with:
                - text: Transcribed text
                - confidence: Transcription confidence (0-1)
                - language: Detected language
        """
        pass

    @abstractmethod
    async def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None
    ) -> dict:
        """Transcribe audio file"""
        pass
```

### AIExtractionProvider Interface

```python
# app/providers/llm/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class AIExtractionProvider(ABC):
    """Base interface for AI extraction providers"""

    @abstractmethod
    async def extract_event(
        self,
        text: str,
        context: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract structured event from text

        Args:
            text: Normalized text
            context: Business context (products, customers)
            schema: Expected output schema

        Returns:
            Structured event extraction with confidence scores
        """
        pass
```

### Provider Factory

```python
# app/providers/factory.py
from app.config import settings
from app.providers.stt.base import SpeechToTextProvider
from app.providers.stt.google import GoogleSpeechToText
from app.providers.stt.openai import OpenAISpeechToText
from app.providers.llm.base import AIExtractionProvider
from app.providers.llm.openai import OpenAIExtraction
from app.providers.llm.anthropic import AnthropicExtraction

class ProviderFactory:
    """Factory for creating provider instances"""

    @staticmethod
    def create_stt_provider() -> SpeechToTextProvider:
        """Create speech-to-text provider based on configuration"""
        if settings.STT_PROVIDER == "google":
            return GoogleSpeechToText(settings.STT_CREDENTIALS_PATH)
        elif settings.STT_PROVIDER == "openai":
            return OpenAISpeechToText(settings.STT_API_KEY)
        else:
            raise ValueError(f"Unknown STT provider: {settings.STT_PROVIDER}")

    @staticmethod
    def create_llm_provider() -> AIExtractionProvider:
        """Create LLM provider based on configuration"""
        if settings.LLM_PROVIDER == "openai":
            return OpenAIExtraction(settings.LLM_API_KEY, settings.LLM_MODEL)
        elif settings.LLM_PROVIDER == "anthropic":
            return AnthropicExtraction(settings.LLM_API_KEY)
        else:
            raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")
```

---

## Folder Structure

### Complete Project Structure

```
yaad-project/
├── frontend/                    # Next.js Frontend
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── login/
│   │   ├── products/
│   │   ├── inventory/
│   │   ├── events/
│   │   ├── query/
│   │   └── insights/
│   ├── components/
│   │   ├── ui/
│   │   ├── voice/
│   │   ├── inventory/
│   │   └── query/
│   ├── lib/
│   │   ├── api.ts
│   │   ├── types.ts
│   │   ├── utils.ts
│   │   └── constants.ts
│   ├── hooks/
│   │   ├── useVoice.ts
│   │   ├── useInventory.ts
│   │   └── useQuery.ts
│   ├── contexts/
│   │   ├── AuthContext.tsx
│   │   └── BusinessContext.tsx
│   ├── styles/
│   │   └── globals.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── next.config.js
│
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── business.py
│   │   │   ├── product.py
│   │   │   ├── event.py
│   │   │   ├── customer.py
│   │   │   ├── alert.py
│   │   │   └── conversion.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── business.py
│   │   │   ├── product.py
│   │   │   ├── event.py
│   │   │   ├── customer.py
│   │   │   ├── alert.py
│   │   │   └── query.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── voice.py
│   │   │   ├── events.py
│   │   │   ├── inventory.py
│   │   │   ├── query.py
│   │   │   ├── products.py
│   │   │   ├── customers.py
│   │   │   ├── alerts.py
│   │   │   └── analytics.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── voice_service.py
│   │   │   ├── ai_service.py
│   │   │   ├── event_service.py
│   │   │   ├── inventory_service.py
│   │   │   ├── query_service.py
│   │   │   ├── alert_service.py
│   │   │   └── analytics_service.py
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── factory.py
│   │   │   ├── stt/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── google.py
│   │   │   │   └── openai.py
│   │   │   └── llm/
│   │   │       ├── __init__.py
│   │   │       ├── base.py
│   │   │       ├── openai.py
│   │   │       └── anthropic.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── event_validator.py
│   │   │   ├── inventory_calculator.py
│   │   │   ├── confidence_engine.py
│   │   │   ├── business_rules.py
│   │   │   └── unit_converter.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── language.py
│   │   │   ├── normalization.py
│   │   │   └── cache.py
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── error_handler.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_services.py
│   │   └── test_core.py
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── .env.example
│   ├── requirements.txt
│   └── run.py
│
├── docs/                        # Documentation
│   ├── 01-requirements-specification.md
│   ├── 02-functional-requirements.md
│   ├── 03-technical-architecture.md
│   └── 04-api-documentation.md
│
├── .gitignore
└── README.md
```

---

## Environment Configuration

### Environment Variables Template

```bash
# .env.example

# Application
APP_NAME=YAAD API
DEBUG=false
API_V1_PREFIX=/api

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yaad.app

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/yaad

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Speech-to-Text
STT_PROVIDER=google
STT_API_KEY=
STT_CREDENTIALS_PATH=./credentials/google-stt.json

# LLM
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4

# SMS
SMS_PROVIDER=twilio
SMS_API_KEY=
SMS_API_SECRET=
SMS_FROM_NUMBER=

# Cache (Optional)
REDIS_URL=redis://localhost:6379

# Frontend (for Next.js)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Security Notes

**NEVER hardcode secrets in code.** Always use environment variables.

**Secret Management:**
- Use `.env` file for local development
- Use environment variables in production
- Use secret management services (Render Secrets, AWS Secrets Manager, etc.)
- Never commit `.env` file to version control
- Add `.env` to `.gitignore`

**API Keys:**
- Store API keys in environment variables
- Rotate keys regularly
- Use scoped keys with minimal permissions
- Monitor key usage

---

## Appendix

### Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 14 | React framework with App Router |
| Frontend | TypeScript | Type safety |
| Frontend | Tailwind CSS | Styling |
| Backend | FastAPI 0.104+ | Async Python web framework |
| Backend | Python 3.11+ | Backend language |
| Database | PostgreSQL 15+ | Relational database |
| ORM | SQLAlchemy 2.0+ | Database ORM |
| Validation | Pydantic 2.0+ | Data validation |
| STT | Google Cloud Speech | Speech-to-text |
| LLM | OpenAI GPT-4 | Entity extraction |
| Deployment | Vercel | Frontend hosting |
| Deployment | Render | Backend hosting |
| Database | Supabase | Managed PostgreSQL |

### Architecture Decisions

**Why Next.js?**
- Server-side rendering for performance
- API routes for backend proxy (optional)
- Built-in routing and optimization
- Strong TypeScript support

**Why FastAPI?**
- Native async support
- Automatic API documentation
- Type hints everywhere
- Fast performance

**Why PostgreSQL?**
- ACID compliance for event ledger
- Relational model for business entities
- JSON support for flexible data
- Strong consistency

**Why Event-Led Architecture?**
- Complete audit trail
- Explainable inventory
- Temporal queries
- Immutable history

**Why Provider Abstraction?**
- Easy to swap STT/LLM providers
- Test with mock providers
- Cost optimization
- Vendor independence

---

**End of Technical Architecture Document**
