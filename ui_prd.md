# Test Data Agent UI - Product Requirements Document

## Overview

A React-based dashboard for the Test Data Agent service, providing a visual interface for QA engineers to generate intelligent test data without writing gRPC calls directly.

**Location:** `test-data-agent/ui/` (monorepo structure)
**Framework:** Next.js 14 (App Router)
**Styling:** Tailwind CSS + shadcn/ui
**Backend Communication:** REST API via BFF (Backend-for-Frontend) that proxies to gRPC

---

## Monorepo Structure

```
test-data-agent/
├── README.md
├── docker-compose.yml              # Runs service + ui + dependencies
├── Makefile                        # Orchestrates both
│
├── service/                        # Python gRPC service (UNCHANGED)
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── protos/
│   │   └── test_data.proto
│   ├── src/
│   │   └── test_data_agent/
│   ├── tests/
│   └── k8s/
│
└── ui/                             # React dashboard (NEW)
    ├── README.md
    ├── package.json
    ├── pnpm-lock.yaml
    ├── next.config.js
    ├── tailwind.config.js
    ├── tsconfig.json
    ├── Dockerfile
    ├── .env.example
    ├── .eslintrc.json
    │
    ├── public/
    │   └── favicon.ico
    │
    ├── src/
    │   ├── app/                    # Next.js App Router
    │   │   ├── layout.tsx
    │   │   ├── page.tsx            # Main generator page
    │   │   ├── globals.css
    │   │   ├── api/                # BFF API routes (REST → gRPC)
    │   │   │   ├── generate/
    │   │   │   │   └── route.ts
    │   │   │   ├── schemas/
    │   │   │   │   └── route.ts
    │   │   │   └── health/
    │   │   │       └── route.ts
    │   │   ├── history/
    │   │   │   └── page.tsx
    │   │   └── settings/
    │   │       └── page.tsx
    │   │
    │   ├── components/
    │   │   ├── ui/                 # shadcn/ui components
    │   │   │   ├── button.tsx
    │   │   │   ├── select.tsx
    │   │   │   ├── input.tsx
    │   │   │   ├── textarea.tsx
    │   │   │   ├── card.tsx
    │   │   │   ├── badge.tsx
    │   │   │   ├── tabs.tsx
    │   │   │   ├── checkbox.tsx
    │   │   │   ├── tooltip.tsx
    │   │   │   └── dialog.tsx
    │   │   │
    │   │   ├── layout/
    │   │   │   ├── header.tsx
    │   │   │   ├── sidebar.tsx
    │   │   │   └── main-layout.tsx
    │   │   │
    │   │   ├── generator/
    │   │   │   ├── generator-form.tsx
    │   │   │   ├── context-editor.tsx
    │   │   │   ├── scenario-builder.tsx
    │   │   │   ├── options-panel.tsx
    │   │   │   └── generate-button.tsx
    │   │   │
    │   │   ├── preview/
    │   │   │   ├── data-preview.tsx
    │   │   │   ├── json-viewer.tsx
    │   │   │   ├── csv-viewer.tsx
    │   │   │   ├── sql-viewer.tsx
    │   │   │   └── metadata-bar.tsx
    │   │   │
    │   │   ├── schemas/
    │   │   │   ├── schema-list.tsx
    │   │   │   └── schema-card.tsx
    │   │   │
    │   │   └── shared/
    │   │       ├── loading-spinner.tsx
    │   │       ├── error-message.tsx
    │   │       ├── empty-state.tsx
    │   │       └── status-indicator.tsx
    │   │
    │   ├── lib/
    │   │   ├── api-client.ts       # REST API client
    │   │   ├── grpc-client.ts      # gRPC client for BFF
    │   │   ├── utils.ts
    │   │   └── constants.ts
    │   │
    │   ├── hooks/
    │   │   ├── use-generate.ts
    │   │   ├── use-schemas.ts
    │   │   ├── use-history.ts
    │   │   └── use-service-health.ts
    │   │
    │   ├── types/
    │   │   ├── api.ts              # API request/response types
    │   │   ├── schema.ts
    │   │   └── generation.ts
    │   │
    │   ├── stores/
    │   │   ├── generator-store.ts  # Zustand store for form state
    │   │   └── history-store.ts
    │   │
    │   └── proto/                  # Generated TypeScript from proto
    │       └── test_data.ts
    │
    ├── tests/
    │   ├── components/
    │   └── e2e/
    │
    └── k8s/
        ├── deployment.yaml
        └── service.yaml
```

---

## Tech Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Framework | Next.js | 14.x | React framework with App Router |
| Language | TypeScript | 5.x | Type safety |
| Styling | Tailwind CSS | 3.4.x | Utility-first CSS |
| Components | shadcn/ui | latest | Pre-built accessible components |
| State | Zustand | 4.x | Lightweight state management |
| Data Fetching | TanStack Query | 5.x | Server state management |
| Code Editor | Monaco Editor | 0.45.x | JSON editing/viewing |
| gRPC Client | @grpc/grpc-js | 1.9.x | gRPC communication in BFF |
| Proto Gen | ts-proto | 1.x | Generate TS types from proto |
| Icons | Lucide React | 0.300.x | Icon library |
| Testing | Vitest + Playwright | latest | Unit + E2E testing |
| Package Manager | pnpm | 8.x | Fast, disk-efficient |

---

## Service Integration

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                              Browser                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                     Next.js UI (React)                        │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │  │
│  │  │ Generator   │  │ Preview     │  │ Schema Browser      │   │  │
│  │  │ Form        │  │ Panel       │  │                     │   │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘   │  │
│  └─────────┼────────────────┼────────────────────┼───────────────┘  │
│            │                │                    │                   │
│            └────────────────┼────────────────────┘                   │
│                             │ REST (fetch)                           │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Next.js API Routes (BFF)                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  /api/generate    /api/schemas    /api/health               │   │
│  │       │                │               │                     │   │
│  │       └────────────────┼───────────────┘                     │   │
│  │                        │ gRPC                                │   │
│  └────────────────────────┼─────────────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                Test Data Agent Service (gRPC)                       │
│                        Port 9001                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  GenerateData    GetSchemas    HealthCheck                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Why BFF Pattern?

The UI uses Next.js API routes as a Backend-for-Frontend (BFF) layer because:

1. **No service changes** - The gRPC service remains unchanged
2. **Browser compatibility** - Browsers can't make native gRPC calls
3. **Type safety** - TypeScript types generated from proto work seamlessly
4. **Server-side secrets** - gRPC endpoint not exposed to browser
5. **Request transformation** - REST is simpler for React Query

### gRPC Contract (Existing - DO NOT MODIFY)

The UI BFF communicates with these existing gRPC methods:

```protobuf
service TestDataService {
  rpc GenerateData(GenerateRequest) returns (GenerateResponse);
  rpc GenerateDataStream(GenerateRequest) returns (stream DataChunk);
  rpc GetSchemas(GetSchemasRequest) returns (GetSchemasResponse);
  rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
}
```

### REST API (BFF Layer)

The BFF exposes these REST endpoints:

#### POST /api/generate

Generate test data.

**Request:**
```typescript
interface GenerateRequestBody {
  domain: string;
  entity: string;
  count: number;
  context?: string;
  scenarios?: Array<{
    name: string;
    count: number;
    description?: string;
  }>;
  hints?: string[];
  outputFormat?: 'JSON' | 'CSV' | 'SQL';
  options?: {
    useCache?: boolean;
    learnFromHistory?: boolean;
    defectTriggering?: boolean;
    productionLike?: boolean;
  };
  generationPath?: 'auto' | 'traditional' | 'llm' | 'rag' | 'hybrid';
}
```

**Response:**
```typescript
interface GenerateResponseBody {
  success: boolean;
  data: string;              // JSON string of generated records
  recordCount: number;
  metadata: {
    generationPath: string;
    llmTokensUsed?: number;
    generationTimeMs: number;
    coherenceScore?: number;
    scenarioCounts: Record<string, number>;
  };
  error?: string;
}
```

#### GET /api/schemas

List available schemas.

**Query Params:**
- `domain` (optional): Filter by domain

**Response:**
```typescript
interface SchemasResponseBody {
  schemas: Array<{
    name: string;
    domain: string;
    description: string;
    fields: string[];
  }>;
}
```

#### GET /api/health

Check service health.

**Response:**
```typescript
interface HealthResponseBody {
  status: 'healthy' | 'degraded' | 'unhealthy';
  service: {
    status: string;
    components: Record<string, string>;
  };
}
```

---

## UI Components

### 1. Header

```
┌─────────────────────────────────────────────────────────────────────┐
│  ⚡ TestDataAgent                              ● Connected  [Docs]  │
└─────────────────────────────────────────────────────────────────────┘
```

- Logo with app name
- Service connection status (polling /api/health)
- Links to API docs, settings

### 2. Sidebar (Left Panel)

```
┌─────────────────┐
│ SCHEMAS         │
│                 │
│ 🛒 Cart      ●  │
│ 📦 Order       │
│ 💳 Payment     │
│ 👤 User        │
│ ⭐ Review      │
│                 │
│ ─────────────── │
│                 │
│ QUICK GENERATE  │
│                 │
│ [🛒 10 Carts  ] │
│ [📦 10 Orders ] │
│ [🐛 Edge Cases] │
│                 │
│ ─────────────── │
│                 │
│ RECENT          │
│ ApplePay carts  │
│ Failed payments │
└─────────────────┘
```

**Features:**
- Schema list (from GET /api/schemas)
- Click to select schema (populates form)
- Quick generate buttons (pre-configured requests)
- Recent history (from localStorage)

### 3. Generator Form (Center Panel)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Generate Test Data                                    [Cart Schema]│
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ⚙️ BASIC CONFIGURATION                                            │
│  ┌─────────────────────┐  ┌─────────────────────┐                  │
│  │ Domain  [ecommerce▼]│  │ Entity     [cart ▼] │                  │
│  └─────────────────────┘  └─────────────────────┘                  │
│  ┌─────────────────────┐  ┌─────────────────────┐                  │
│  │ Count   [50       ] │  │ Format     [JSON ▼] │                  │
│  └─────────────────────┘  └─────────────────────┘                  │
│                                                                     │
│  💬 CONTEXT                                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Generate shopping carts for ApplePay checkout testing.      │   │
│  │ Carts should have 3-5 related items that make sense...      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  🎯 SCENARIOS                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ happy_path                                           [30] ✕ │   │
│  │ high_value_cart                                      [10] ✕ │   │
│  │ single_item                                          [ 5] ✕ │   │
│  │ [+ Add Scenario]                                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  🎛️ OPTIONS                                                        │
│  ┌──────────────────┐  ┌──────────────────┐                        │
│  │ ☑ Coherent (LLM) │  │ ☐ History (RAG)  │                        │
│  │ ☐ Defect patterns│  │ ☐ Production-like│                        │
│  └──────────────────┘  └──────────────────┘                        │
│                                                                     │
│  ┌─────────────────────────────────────┐  ┌──────────────────┐     │
│  │         ⚡ Generate Data            │  │ Path: [Auto ▼]   │     │
│  └─────────────────────────────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

**Features:**
- Domain/Entity dropdowns (populated from schemas)
- Count input with validation (1-1000)
- Output format selector
- Context textarea (markdown supported)
- Dynamic scenario builder (add/remove/edit)
- Generation options (checkboxes)
- Path override selector
- Generate button with loading state

### 4. Preview Panel (Right Panel)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Generated Data                        [JSON][CSV][SQL]   📋  ⬇️   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [                                                                  │
│    {                                                                │
│      "_index": 0,                                                   │
│      "_scenario": "happy_path",                                     │
│      "_shopping_occasion": "marathon_training",                     │
│      "cart_id": "CRT-2025-8472910",                                │
│      "customer_id": "USR-4829173",                                 │
│      "items": [                                                     │
│        {                                                            │
│          "sku": "NKE-RUN-BLK-10",                                  │
│          "name": "Nike Air Zoom Pegasus 40",                       │
│          "quantity": 1,                                             │
│          "price": 129.99                                            │
│        },                                                           │
│        ...                                                          │
│      ],                                                             │
│      "total": 228.34                                                │
│    }                                                                │
│  ]                                                                  │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│   LLM      │    2,847    │    3.2s     │     0.94                   │
│   Path     │    Tokens   │    Time     │     Coherence              │
└─────────────────────────────────────────────────────────────────────┘
```

**Features:**
- Tab switcher: JSON / CSV / SQL views
- Syntax-highlighted code viewer (Monaco)
- Copy to clipboard button
- Download button (respects selected format)
- Metadata bar showing generation stats
- Empty state when no data
- Loading state during generation
- Error state with retry option

### 5. States

**Empty State:**
```
┌─────────────────────────────────────┐
│                                     │
│              📊                     │
│                                     │
│   Configure your request and       │
│   click Generate to see data       │
│                                     │
└─────────────────────────────────────┘
```

**Loading State:**
```
┌─────────────────────────────────────┐
│                                     │
│           ◠ (spinner)              │
│                                     │
│     Generating with LLM...          │
│                                     │
└─────────────────────────────────────┘
```

**Error State:**
```
┌─────────────────────────────────────┐
│                                     │
│              ⚠️                     │
│                                     │
│   Generation failed: timeout        │
│                                     │
│         [Retry]                     │
└─────────────────────────────────────┘
```

---

## User Flows

### Flow 1: Generate Basic Data

1. User selects schema from sidebar (e.g., "Cart")
2. Form auto-fills domain="ecommerce", entity="cart"
3. User sets count (e.g., 50)
4. User clicks "Generate Data"
5. Loading spinner shows in preview panel
6. Data appears with metadata
7. User clicks download or copy

### Flow 2: Generate Intelligent Data

1. User selects "Order" schema
2. User writes context: "Generate orders for refund testing with various refund states"
3. User adds scenarios:
   - full_refund: 10
   - partial_refund: 10
   - refund_denied: 5
4. User enables "Coherent (LLM)" option
5. User clicks "Generate Data"
6. Path shows "LLM" in metadata
7. Data shows coherent orders with proper refund states

### Flow 3: Quick Generate

1. User clicks "🐛 Edge Cases" in sidebar
2. Pre-configured request fires immediately
3. Edge case data appears in preview
4. User reviews data with defect patterns

### Flow 4: Re-run from History

1. User clicks "ApplePay carts" in Recent section
2. Previous request configuration loads
3. User modifies count from 20 to 100
4. User clicks "Generate Data"
5. New data generated with updated count

---

## State Management

### Generator Store (Zustand)

```typescript
interface GeneratorState {
  // Form fields
  domain: string;
  entity: string;
  count: number;
  context: string;
  scenarios: Scenario[];
  outputFormat: 'JSON' | 'CSV' | 'SQL';
  options: GenerationOptions;
  generationPath: GenerationPath;
  
  // Result
  result: GenerateResult | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setDomain: (domain: string) => void;
  setEntity: (entity: string) => void;
  setCount: (count: number) => void;
  setContext: (context: string) => void;
  addScenario: (scenario: Scenario) => void;
  removeScenario: (index: number) => void;
  updateScenario: (index: number, scenario: Scenario) => void;
  setOutputFormat: (format: OutputFormat) => void;
  toggleOption: (option: keyof GenerationOptions) => void;
  setGenerationPath: (path: GenerationPath) => void;
  generate: () => Promise<void>;
  reset: () => void;
  loadFromHistory: (entry: HistoryEntry) => void;
}
```

### History Store (Zustand + localStorage)

```typescript
interface HistoryState {
  entries: HistoryEntry[];
  addEntry: (entry: HistoryEntry) => void;
  removeEntry: (id: string) => void;
  clearHistory: () => void;
}

interface HistoryEntry {
  id: string;
  timestamp: string;
  label: string;
  request: GenerateRequestBody;
  recordCount: number;
}
```

---

## Configuration

### Environment Variables

```bash
# .env.example

# gRPC Service
GRPC_SERVICE_HOST=localhost
GRPC_SERVICE_PORT=9001

# UI Settings
NEXT_PUBLIC_APP_NAME=TestDataAgent
NEXT_PUBLIC_MAX_RECORDS=1000
NEXT_PUBLIC_DEFAULT_COUNT=50

# Feature Flags
NEXT_PUBLIC_ENABLE_STREAMING=false
NEXT_PUBLIC_ENABLE_HISTORY=true
```

### next.config.js

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  experimental: {
    serverComponentsExternalPackages: ['@grpc/grpc-js', '@grpc/proto-loader'],
  },
};

module.exports = nextConfig;
```

---

## Docker Configuration

### Dockerfile (ui/)

```dockerfile
FROM node:20-alpine AS base

# Install dependencies
FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile

# Build
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN corepack enable pnpm && pnpm build

# Production
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000

CMD ["node", "server.js"]
```

### docker-compose.yml (root - updated)

```yaml
version: '3.8'

services:
  service:
    build: ./service
    ports:
      - "9001:9001"
      - "8081:8081"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - REDIS_URL=redis://redis:6379/0
      - WEAVIATE_URL=http://weaviate:8080
    depends_on:
      - redis
      - weaviate

  ui:
    build: ./ui
    ports:
      - "3000:3000"
    environment:
      - GRPC_SERVICE_HOST=service
      - GRPC_SERVICE_PORT=9001
    depends_on:
      - service

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
    environment:
      - QUERY_DEFAULTS_LIMIT=25
      - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true
      - PERSISTENCE_DATA_PATH=/var/lib/weaviate
```

---

## Design Specifications

### Color Palette

Based on the wireframe:

```css
:root {
  /* Backgrounds */
  --bg-primary: #0a0f1a;
  --bg-secondary: #111827;
  --bg-tertiary: #1a2235;
  --bg-elevated: #1e293b;
  
  /* Borders */
  --border: #2d3a4f;
  --border-light: #374357;
  
  /* Text */
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  
  /* Accent */
  --accent: #10b981;
  --accent-hover: #34d399;
  --accent-muted: rgba(16, 185, 129, 0.15);
  
  /* Status */
  --warning: #f59e0b;
  --error: #ef4444;
  --info: #6366f1;
}
```

### Typography

```css
/* Headings & UI */
font-family: 'Plus Jakarta Sans', sans-serif;

/* Code & Data */
font-family: 'JetBrains Mono', monospace;
```

### Component Styling

- Border radius: 6px (buttons), 8px (inputs), 12px (cards)
- Focus ring: 3px accent-muted with accent border
- Transitions: 150-200ms ease
- Shadows: Minimal, only on elevated elements

---

## Accessibility

- All interactive elements keyboard accessible
- Focus visible styles on all focusable elements
- ARIA labels on icon-only buttons
- Color contrast meets WCAG AA
- Screen reader announcements for loading/success/error states
- Reduced motion support via `prefers-reduced-motion`

---

## Performance Requirements

| Metric | Target |
|--------|--------|
| First Contentful Paint | < 1.5s |
| Time to Interactive | < 3s |
| Largest Contentful Paint | < 2.5s |
| Bundle Size (gzipped) | < 150KB initial |
| API Response (UI → BFF) | < 100ms overhead |

---

## Error Handling

| Error | User Experience |
|-------|-----------------|
| Service unavailable | Header shows "Disconnected", generate disabled |
| Generation timeout | Error state with retry button |
| Invalid request | Inline validation errors on form |
| Partial failure | Show partial data with warning |
| Network error | Toast notification with retry |

---

## Testing Strategy

### Unit Tests (Vitest)
- Component rendering
- Store actions
- Utility functions
- API client mocking

### Integration Tests (Vitest + Testing Library)
- Form submission flow
- State management
- API route handlers

### E2E Tests (Playwright)
- Full generation flow
- Schema selection
- History functionality
- Error handling

---

## Browser Support

- Chrome 90+
- Firefox 90+
- Safari 14+
- Edge 90+

---

## Future Enhancements (Out of Scope for V1)

- Schema editor (create custom schemas)
- Team workspaces (shared history)
- Scheduled generation (cron jobs)
- Direct database seeding
- Streaming generation (GenerateDataStream)
- Comparison view (diff two generations)
- Export to Postman/Insomnia
