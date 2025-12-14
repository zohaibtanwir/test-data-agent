# Test Data Agent UI - Implementation Tasks

> **Usage:** Copy individual tasks into your IDE's AI chat (Claude Code, Cursor, Windsurf) to implement incrementally. Each task is self-contained with clear acceptance criteria.

---

## Phase 1: Project Setup

### Task 1.1: Initialize Next.js Project

```
Create the Next.js 14 project in the ui/ directory of the monorepo.

Directory: test-data-agent/ui/

Commands to run:
cd test-data-agent
mkdir ui && cd ui
pnpm create next-app@14 . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

After creation, update package.json:
- name: "test-data-agent-ui"
- Add scripts:
  - "dev": "next dev"
  - "build": "next build"
  - "start": "next start"
  - "lint": "next lint"
  - "type-check": "tsc --noEmit"
  - "test": "vitest"
  - "test:e2e": "playwright test"

Create .env.example:
```
# gRPC Service
GRPC_SERVICE_HOST=localhost
GRPC_SERVICE_PORT=9001

# UI Settings
NEXT_PUBLIC_APP_NAME=TestDataAgent
NEXT_PUBLIC_MAX_RECORDS=1000
NEXT_PUBLIC_DEFAULT_COUNT=50
```

Update .gitignore to include:
- .env
- .env.local

Acceptance Criteria:
- [ ] pnpm dev starts development server on port 3000
- [ ] TypeScript compiles without errors
- [ ] Tailwind CSS is configured
- [ ] Environment variables load correctly
```

---

### Task 1.2: Install Dependencies

```
Install all required dependencies for the UI project.

In ui/ directory, run:

# Core dependencies
pnpm add @tanstack/react-query zustand lucide-react clsx tailwind-merge

# gRPC (for BFF)
pnpm add @grpc/grpc-js @grpc/proto-loader

# Code editor
pnpm add @monaco-editor/react

# shadcn/ui setup
pnpm add class-variance-authority @radix-ui/react-slot
pnpm dlx shadcn-ui@latest init

When prompted for shadcn-ui:
- Style: Default
- Base color: Slate
- CSS variables: Yes

# Dev dependencies
pnpm add -D vitest @vitejs/plugin-react @testing-library/react @testing-library/jest-dom
pnpm add -D playwright @playwright/test
pnpm add -D ts-proto

Update next.config.js:
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

Create vitest.config.ts:
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

Create tests/setup.ts:
```typescript
import '@testing-library/jest-dom'
```

Acceptance Criteria:
- [ ] All dependencies install without conflicts
- [ ] pnpm build succeeds
- [ ] vitest runs (even with no tests)
- [ ] shadcn-ui init completes
```

---

### Task 1.3: Configure Tailwind with Custom Theme

```
Update Tailwind configuration with the design system colors from the wireframe.

Update tailwind.config.ts:

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Backgrounds
        'bg-primary': '#0a0f1a',
        'bg-secondary': '#111827',
        'bg-tertiary': '#1a2235',
        'bg-elevated': '#1e293b',
        
        // Borders
        'border-default': '#2d3a4f',
        'border-light': '#374357',
        
        // Text
        'text-primary': '#f1f5f9',
        'text-secondary': '#94a3b8',
        'text-muted': '#64748b',
        
        // Accent (emerald)
        accent: {
          DEFAULT: '#10b981',
          hover: '#34d399',
          muted: 'rgba(16, 185, 129, 0.15)',
        },
        
        // Status
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#6366f1',
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '6px',
        lg: '8px',
        xl: '12px',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}

export default config
```

Update src/app/globals.css:

```css
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 222 47% 6%;
    --foreground: 210 40% 96%;
    --card: 222 47% 8%;
    --card-foreground: 210 40% 96%;
    --popover: 222 47% 8%;
    --popover-foreground: 210 40% 96%;
    --primary: 160 84% 39%;
    --primary-foreground: 210 40% 98%;
    --secondary: 217 33% 17%;
    --secondary-foreground: 210 40% 96%;
    --muted: 217 33% 17%;
    --muted-foreground: 215 20% 50%;
    --accent: 160 84% 39%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 84% 60%;
    --destructive-foreground: 210 40% 98%;
    --border: 217 33% 20%;
    --input: 217 33% 17%;
    --ring: 160 84% 39%;
    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border-default;
  }
  body {
    @apply bg-bg-primary text-text-primary font-sans;
  }
}
```

Acceptance Criteria:
- [ ] Custom colors work in components (bg-bg-primary, text-accent, etc.)
- [ ] Fonts load correctly (Plus Jakarta Sans, JetBrains Mono)
- [ ] Dark theme is the default
- [ ] shadcn/ui components use custom theme
```

---

### Task 1.4: Generate TypeScript Types from Proto

```
Generate TypeScript types from the existing proto file in the service.

Create a script to generate types:

1. Create ui/scripts/generate-proto.sh:
```bash
#!/bin/bash

# Generate TypeScript types from proto
PROTO_PATH="../service/protos"
OUT_PATH="./src/proto"

mkdir -p $OUT_PATH

npx protoc \
  --plugin=./node_modules/.bin/protoc-gen-ts_proto \
  --ts_proto_out=$OUT_PATH \
  --ts_proto_opt=outputServices=generic-definitions,outputClientImpl=false,esModuleInterop=true \
  -I $PROTO_PATH \
  $PROTO_PATH/test_data.proto

echo "Proto types generated in $OUT_PATH"
```

2. Add to package.json scripts:
```json
"proto:generate": "bash scripts/generate-proto.sh"
```

3. Create src/proto/.gitkeep for the directory

4. After generation, create src/types/api.ts with REST API types:

```typescript
// REST API types (used by frontend)

export interface GenerateRequestBody {
  domain: string;
  entity: string;
  count: number;
  context?: string;
  scenarios?: Scenario[];
  hints?: string[];
  outputFormat?: OutputFormat;
  options?: GenerationOptions;
  generationPath?: GenerationPath;
}

export interface Scenario {
  name: string;
  count: number;
  description?: string;
  overrides?: Record<string, string>;
}

export interface GenerationOptions {
  useCache?: boolean;
  learnFromHistory?: boolean;
  defectTriggering?: boolean;
  productionLike?: boolean;
}

export type OutputFormat = 'JSON' | 'CSV' | 'SQL';
export type GenerationPath = 'auto' | 'traditional' | 'llm' | 'rag' | 'hybrid';

export interface GenerateResponseBody {
  success: boolean;
  requestId: string;
  data: string;
  recordCount: number;
  metadata: GenerationMetadata;
  error?: string;
}

export interface GenerationMetadata {
  generationPath: string;
  llmTokensUsed?: number;
  generationTimeMs: number;
  coherenceScore?: number;
  scenarioCounts: Record<string, number>;
}

export interface SchemaInfo {
  name: string;
  domain: string;
  description: string;
  fields: string[];
}

export interface SchemasResponseBody {
  schemas: SchemaInfo[];
}

export interface HealthResponseBody {
  status: 'healthy' | 'degraded' | 'unhealthy';
  service: {
    status: string;
    components: Record<string, string>;
  };
}
```

5. Create src/types/index.ts to re-export:
```typescript
export * from './api';
```

Acceptance Criteria:
- [ ] pnpm proto:generate runs without errors
- [ ] TypeScript types exist in src/proto/
- [ ] API types are defined and exported
- [ ] Types compile without errors
```

---

### Task 1.5: Set Up Project Structure

```
Create the directory structure and placeholder files for the UI.

Create these directories and files:

src/
├── app/
│   ├── layout.tsx         (update existing)
│   ├── page.tsx           (update existing)
│   ├── api/
│   │   ├── generate/
│   │   │   └── route.ts   (create placeholder)
│   │   ├── schemas/
│   │   │   └── route.ts   (create placeholder)
│   │   └── health/
│   │       └── route.ts   (create placeholder)
│   ├── history/
│   │   └── page.tsx       (create placeholder)
│   └── settings/
│       └── page.tsx       (create placeholder)
│
├── components/
│   ├── ui/                (shadcn components - leave for now)
│   ├── layout/
│   │   └── .gitkeep
│   ├── generator/
│   │   └── .gitkeep
│   ├── preview/
│   │   └── .gitkeep
│   ├── schemas/
│   │   └── .gitkeep
│   └── shared/
│       └── .gitkeep
│
├── lib/
│   ├── utils.ts           (create with cn helper)
│   ├── api-client.ts      (create placeholder)
│   └── constants.ts       (create)
│
├── hooks/
│   └── .gitkeep
│
├── stores/
│   └── .gitkeep
│
├── types/
│   ├── api.ts             (already created)
│   └── index.ts           (already created)
│
└── proto/
    └── .gitkeep

Create src/lib/utils.ts:
```typescript
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

Create src/lib/constants.ts:
```typescript
export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || 'TestDataAgent';
export const MAX_RECORDS = Number(process.env.NEXT_PUBLIC_MAX_RECORDS) || 1000;
export const DEFAULT_COUNT = Number(process.env.NEXT_PUBLIC_DEFAULT_COUNT) || 50;

export const DOMAINS = [
  'ecommerce',
  'supply_chain',
  'loyalty',
  'mobile',
  'marketing',
  'store_ops',
  'enterprise',
] as const;

export const OUTPUT_FORMATS = ['JSON', 'CSV', 'SQL'] as const;

export const GENERATION_PATHS = [
  { value: 'auto', label: 'Auto (Router decides)' },
  { value: 'traditional', label: 'Traditional (Faker)' },
  { value: 'llm', label: 'LLM (Claude)' },
  { value: 'rag', label: 'RAG (Patterns)' },
  { value: 'hybrid', label: 'Hybrid (RAG + LLM)' },
] as const;

export const GENERATION_OPTIONS = [
  { key: 'coherent', label: 'Coherent items (LLM)', hint: 'realistic' },
  { key: 'learnFromHistory', label: 'Learn from history (RAG)', hint: 'learn_from_history' },
  { key: 'defectTriggering', label: 'Defect-triggering patterns', hint: 'edge_case' },
  { key: 'productionLike', label: 'Production-like distribution', hint: 'production_like' },
] as const;
```

Create placeholder API routes (e.g., src/app/api/health/route.ts):
```typescript
import { NextResponse } from 'next/server';

export async function GET() {
  // TODO: Implement gRPC call
  return NextResponse.json({ status: 'healthy' });
}
```

Acceptance Criteria:
- [ ] All directories exist
- [ ] Placeholder files created
- [ ] cn() utility works
- [ ] Constants are exported
- [ ] pnpm dev still works
```

---

## Phase 2: Layout Components

### Task 2.1: Install shadcn/ui Components

```
Install required shadcn/ui components.

Run these commands in ui/ directory:

pnpm dlx shadcn-ui@latest add button
pnpm dlx shadcn-ui@latest add input
pnpm dlx shadcn-ui@latest add select
pnpm dlx shadcn-ui@latest add textarea
pnpm dlx shadcn-ui@latest add card
pnpm dlx shadcn-ui@latest add badge
pnpm dlx shadcn-ui@latest add tabs
pnpm dlx shadcn-ui@latest add checkbox
pnpm dlx shadcn-ui@latest add tooltip
pnpm dlx shadcn-ui@latest add dialog
pnpm dlx shadcn-ui@latest add dropdown-menu
pnpm dlx shadcn-ui@latest add separator
pnpm dlx shadcn-ui@latest add scroll-area

After installation, verify components are in src/components/ui/

Acceptance Criteria:
- [ ] All components installed in src/components/ui/
- [ ] Components import without errors
- [ ] Components render with dark theme
```

---

### Task 2.2: Create Header Component

```
Create the header component based on the wireframe.

Create src/components/layout/header.tsx:

```typescript
'use client';

import { useState, useEffect } from 'react';
import { Zap, Book, Settings, Circle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { APP_NAME } from '@/lib/constants';

interface HeaderProps {
  className?: string;
}

type ServiceStatus = 'connected' | 'disconnected' | 'checking';

export function Header({ className }: HeaderProps) {
  const [status, setStatus] = useState<ServiceStatus>('checking');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('/api/health');
        if (res.ok) {
          setStatus('connected');
        } else {
          setStatus('disconnected');
        }
      } catch {
        setStatus('disconnected');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <header
      className={cn(
        'h-[60px] bg-bg-secondary border-b border-border-default px-6',
        'flex items-center justify-between sticky top-0 z-50',
        className
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 bg-gradient-to-br from-accent to-emerald-600 rounded-lg flex items-center justify-center">
          <Zap className="w-5 h-5 text-white" />
        </div>
        <span className="text-lg font-bold tracking-tight">
          Test<span className="text-accent">Data</span>Agent
        </span>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        {/* Status indicator */}
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <Circle
            className={cn(
              'w-2 h-2 fill-current',
              status === 'connected' && 'text-accent',
              status === 'disconnected' && 'text-error',
              status === 'checking' && 'text-warning animate-pulse'
            )}
          />
          {status === 'connected' && 'Service Connected'}
          {status === 'disconnected' && 'Disconnected'}
          {status === 'checking' && 'Checking...'}
        </div>

        {/* Action buttons */}
        <Button variant="outline" size="sm" className="gap-2">
          <Book className="w-4 h-4" />
          API Docs
        </Button>
        <Button variant="outline" size="sm" className="gap-2">
          <Settings className="w-4 h-4" />
          Settings
        </Button>
      </div>
    </header>
  );
}
```

Acceptance Criteria:
- [ ] Header renders with logo
- [ ] Status indicator polls /api/health
- [ ] Status shows connected/disconnected state
- [ ] Buttons are styled correctly
```

---

### Task 2.3: Create Sidebar Component

```
Create the sidebar component with schema list and quick actions.

Create src/components/layout/sidebar.tsx:

```typescript
'use client';

import { useState } from 'react';
import {
  ShoppingCart,
  Package,
  CreditCard,
  User,
  Star,
  MapPin,
  Bug,
  History,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

interface Schema {
  name: string;
  domain: string;
  icon: React.ReactNode;
}

interface SidebarProps {
  selectedSchema: string | null;
  onSchemaSelect: (schema: string) => void;
  onQuickGenerate: (type: string) => void;
  className?: string;
}

const SCHEMA_ICONS: Record<string, React.ReactNode> = {
  cart: <ShoppingCart className="w-4 h-4" />,
  order: <Package className="w-4 h-4" />,
  payment: <CreditCard className="w-4 h-4" />,
  user: <User className="w-4 h-4" />,
  review: <Star className="w-4 h-4" />,
  address: <MapPin className="w-4 h-4" />,
};

const MOCK_SCHEMAS: Schema[] = [
  { name: 'cart', domain: 'ecommerce', icon: SCHEMA_ICONS.cart },
  { name: 'order', domain: 'ecommerce', icon: SCHEMA_ICONS.order },
  { name: 'payment', domain: 'ecommerce', icon: SCHEMA_ICONS.payment },
  { name: 'user', domain: 'core', icon: SCHEMA_ICONS.user },
  { name: 'review', domain: 'ecommerce', icon: SCHEMA_ICONS.review },
  { name: 'address', domain: 'core', icon: SCHEMA_ICONS.address },
];

const QUICK_ACTIONS = [
  { id: 'carts', label: 'Sample Carts', icon: <ShoppingCart className="w-4 h-4" />, count: 10 },
  { id: 'orders', label: 'Sample Orders', icon: <Package className="w-4 h-4" />, count: 10 },
  { id: 'users', label: 'Sample Users', icon: <User className="w-4 h-4" />, count: 25 },
  { id: 'edge', label: 'Edge Cases', icon: <Bug className="w-4 h-4" />, count: 20 },
];

const RECENT_ITEMS = [
  { id: '1', label: 'ApplePay checkout carts' },
  { id: '2', label: 'Failed payment scenarios' },
];

export function Sidebar({
  selectedSchema,
  onSchemaSelect,
  onQuickGenerate,
  className,
}: SidebarProps) {
  return (
    <aside
      className={cn(
        'w-[260px] bg-bg-secondary border-r border-border-default',
        'flex flex-col',
        className
      )}
    >
      <ScrollArea className="flex-1">
        <div className="py-4">
          {/* Schemas Section */}
          <div className="mb-6">
            <h3 className="px-5 mb-3 text-[11px] font-semibold uppercase tracking-wider text-text-muted">
              Schemas
            </h3>
            <ul>
              {MOCK_SCHEMAS.map((schema) => (
                <li key={schema.name}>
                  <button
                    onClick={() => onSchemaSelect(schema.name)}
                    className={cn(
                      'w-full flex items-center gap-3 px-5 py-2.5',
                      'border-l-[3px] border-transparent',
                      'transition-all duration-150',
                      'hover:bg-bg-tertiary',
                      selectedSchema === schema.name && [
                        'bg-accent-muted border-l-accent',
                        '[&_.schema-name]:text-accent',
                        '[&_.schema-icon]:bg-accent',
                      ]
                    )}
                  >
                    <div
                      className={cn(
                        'schema-icon w-8 h-8 rounded-md flex items-center justify-center',
                        'bg-bg-tertiary text-text-secondary',
                        selectedSchema === schema.name && 'bg-accent text-white'
                      )}
                    >
                      {schema.icon}
                    </div>
                    <div className="flex-1 text-left">
                      <div className="schema-name text-sm font-medium capitalize">
                        {schema.name}
                      </div>
                      <div className="text-[11px] text-text-muted">{schema.domain}</div>
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <Separator className="mx-4 bg-border-default" />

          {/* Quick Generate Section */}
          <div className="my-6">
            <h3 className="px-5 mb-3 text-[11px] font-semibold uppercase tracking-wider text-text-muted">
              Quick Generate
            </h3>
            <div className="px-4 space-y-2">
              {QUICK_ACTIONS.map((action) => (
                <Button
                  key={action.id}
                  variant="outline"
                  className={cn(
                    'w-full justify-start gap-2.5 h-auto py-2.5',
                    'bg-bg-tertiary border-border-default',
                    'hover:bg-bg-elevated hover:border-border-light',
                    'text-text-secondary hover:text-text-primary'
                  )}
                  onClick={() => onQuickGenerate(action.id)}
                >
                  {action.icon}
                  <span className="flex-1 text-left text-sm">{action.label}</span>
                  <span className="text-[11px] bg-bg-primary px-2 py-0.5 rounded">
                    {action.count}
                  </span>
                </Button>
              ))}
            </div>
          </div>

          <Separator className="mx-4 bg-border-default" />

          {/* Recent Section */}
          <div className="my-6">
            <h3 className="px-5 mb-3 text-[11px] font-semibold uppercase tracking-wider text-text-muted">
              Recent
            </h3>
            <div className="px-4 space-y-2">
              {RECENT_ITEMS.map((item) => (
                <Button
                  key={item.id}
                  variant="ghost"
                  className={cn(
                    'w-full justify-start h-auto py-2',
                    'text-text-muted hover:text-text-secondary',
                    'text-xs'
                  )}
                >
                  <History className="w-3 h-3 mr-2" />
                  {item.label}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </ScrollArea>
    </aside>
  );
}
```

Acceptance Criteria:
- [ ] Schema list renders with icons
- [ ] Selected schema is highlighted
- [ ] Quick generate buttons render with counts
- [ ] Recent section shows placeholder items
- [ ] Click handlers fire correctly
```

---

### Task 2.4: Create Main Layout

```
Create the main layout that combines header, sidebar, and content areas.

Create src/components/layout/main-layout.tsx:

```typescript
'use client';

import { ReactNode } from 'react';
import { Header } from './header';
import { Sidebar } from './sidebar';
import { cn } from '@/lib/utils';

interface MainLayoutProps {
  children: ReactNode;
  sidebar?: ReactNode;
  preview?: ReactNode;
  selectedSchema: string | null;
  onSchemaSelect: (schema: string) => void;
  onQuickGenerate: (type: string) => void;
}

export function MainLayout({
  children,
  preview,
  selectedSchema,
  onSchemaSelect,
  onQuickGenerate,
}: MainLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-bg-primary">
      <Header />
      <div className="flex-1 flex">
        <Sidebar
          selectedSchema={selectedSchema}
          onSchemaSelect={onSchemaSelect}
          onQuickGenerate={onQuickGenerate}
        />
        <main className="flex-1 p-6 overflow-y-auto">{children}</main>
        {preview && (
          <aside className="w-[400px] bg-bg-secondary border-l border-border-default flex flex-col">
            {preview}
          </aside>
        )}
      </div>
    </div>
  );
}
```

Create src/components/layout/index.ts:
```typescript
export { Header } from './header';
export { Sidebar } from './sidebar';
export { MainLayout } from './main-layout';
```

Update src/app/layout.tsx:
```typescript
import type { Metadata } from 'next';
import { APP_NAME } from '@/lib/constants';
import './globals.css';

export const metadata: Metadata = {
  title: APP_NAME,
  description: 'Generate intelligent test data for QA',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
```

Acceptance Criteria:
- [ ] Layout has header at top
- [ ] Layout has sidebar on left (260px)
- [ ] Layout has main content in center (flexible)
- [ ] Layout has preview panel on right (400px)
- [ ] Scrolling works independently for each section
```

---

### Task 2.5: Create Shared Components

```
Create reusable shared components.

Create src/components/shared/loading-spinner.tsx:
```typescript
import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizes = {
  sm: 'w-4 h-4 border-2',
  md: 'w-8 h-8 border-3',
  lg: 'w-12 h-12 border-4',
};

export function LoadingSpinner({ size = 'md', className }: LoadingSpinnerProps) {
  return (
    <div
      className={cn(
        'rounded-full border-border-default border-t-accent animate-spin',
        sizes[size],
        className
      )}
    />
  );
}
```

Create src/components/shared/empty-state.tsx:
```typescript
import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
  icon?: ReactNode;
  title?: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-12 px-6 text-center',
        className
      )}
    >
      {icon && (
        <div className="text-4xl mb-4 opacity-50">{icon}</div>
      )}
      {title && (
        <h3 className="text-lg font-medium text-text-primary mb-2">{title}</h3>
      )}
      {description && (
        <p className="text-sm text-text-muted max-w-xs">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
```

Create src/components/shared/error-message.tsx:
```typescript
import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorMessage({
  title = 'Error',
  message,
  onRetry,
  className,
}: ErrorMessageProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-8 px-6 text-center',
        className
      )}
    >
      <AlertCircle className="w-12 h-12 text-error mb-4" />
      <h3 className="text-lg font-medium text-text-primary mb-2">{title}</h3>
      <p className="text-sm text-text-muted max-w-xs mb-4">{message}</p>
      {onRetry && (
        <Button variant="outline" onClick={onRetry}>
          Retry
        </Button>
      )}
    </div>
  );
}
```

Create src/components/shared/status-indicator.tsx:
```typescript
import { Circle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatusIndicatorProps {
  status: 'success' | 'warning' | 'error' | 'info';
  label?: string;
  className?: string;
}

const statusColors = {
  success: 'text-accent',
  warning: 'text-warning',
  error: 'text-error',
  info: 'text-info',
};

export function StatusIndicator({ status, label, className }: StatusIndicatorProps) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <Circle className={cn('w-2 h-2 fill-current', statusColors[status])} />
      {label && <span className="text-sm text-text-secondary">{label}</span>}
    </div>
  );
}
```

Create src/components/shared/index.ts:
```typescript
export { LoadingSpinner } from './loading-spinner';
export { EmptyState } from './empty-state';
export { ErrorMessage } from './error-message';
export { StatusIndicator } from './status-indicator';
```

Acceptance Criteria:
- [ ] LoadingSpinner renders with animation
- [ ] EmptyState renders with customizable content
- [ ] ErrorMessage renders with retry button
- [ ] StatusIndicator shows correct colors
```

---

## Phase 3: Generator Components

### Task 3.1: Create Generator Store (Zustand)

```
Create the Zustand store for managing generator form state.

Create src/stores/generator-store.ts:

```typescript
import { create } from 'zustand';
import type {
  GenerateRequestBody,
  GenerateResponseBody,
  Scenario,
  OutputFormat,
  GenerationPath,
  GenerationOptions,
} from '@/types/api';
import { DEFAULT_COUNT } from '@/lib/constants';

interface GeneratorState {
  // Form fields
  domain: string;
  entity: string;
  count: number;
  context: string;
  scenarios: Scenario[];
  outputFormat: OutputFormat;
  options: GenerationOptions;
  generationPath: GenerationPath;

  // Result state
  result: GenerateResponseBody | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setDomain: (domain: string) => void;
  setEntity: (entity: string) => void;
  setCount: (count: number) => void;
  setContext: (context: string) => void;
  setOutputFormat: (format: OutputFormat) => void;
  setGenerationPath: (path: GenerationPath) => void;

  // Scenario actions
  addScenario: (scenario: Scenario) => void;
  removeScenario: (index: number) => void;
  updateScenario: (index: number, scenario: Partial<Scenario>) => void;

  // Option actions
  toggleOption: (key: keyof GenerationOptions) => void;

  // Generation actions
  setResult: (result: GenerateResponseBody | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Utility actions
  reset: () => void;
  loadPreset: (preset: Partial<GeneratorState>) => void;
  getRequestBody: () => GenerateRequestBody;
}

const initialState = {
  domain: 'ecommerce',
  entity: 'cart',
  count: DEFAULT_COUNT,
  context: '',
  scenarios: [{ name: 'happy_path', count: DEFAULT_COUNT }],
  outputFormat: 'JSON' as OutputFormat,
  options: {
    useCache: false,
    learnFromHistory: false,
    defectTriggering: false,
    productionLike: false,
  },
  generationPath: 'auto' as GenerationPath,
  result: null,
  isLoading: false,
  error: null,
};

export const useGeneratorStore = create<GeneratorState>((set, get) => ({
  ...initialState,

  setDomain: (domain) => set({ domain }),
  setEntity: (entity) => set({ entity }),
  setCount: (count) => {
    set({ count });
    // Update default scenario count
    const { scenarios } = get();
    if (scenarios.length === 1) {
      set({ scenarios: [{ ...scenarios[0], count }] });
    }
  },
  setContext: (context) => set({ context }),
  setOutputFormat: (outputFormat) => set({ outputFormat }),
  setGenerationPath: (generationPath) => set({ generationPath }),

  addScenario: (scenario) =>
    set((state) => ({ scenarios: [...state.scenarios, scenario] })),

  removeScenario: (index) =>
    set((state) => ({
      scenarios: state.scenarios.filter((_, i) => i !== index),
    })),

  updateScenario: (index, updates) =>
    set((state) => ({
      scenarios: state.scenarios.map((s, i) =>
        i === index ? { ...s, ...updates } : s
      ),
    })),

  toggleOption: (key) =>
    set((state) => ({
      options: { ...state.options, [key]: !state.options[key] },
    })),

  setResult: (result) => set({ result }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),

  reset: () => set(initialState),

  loadPreset: (preset) => set((state) => ({ ...state, ...preset })),

  getRequestBody: () => {
    const state = get();
    const hints: string[] = [];

    if (state.options.learnFromHistory) hints.push('learn_from_history');
    if (state.options.defectTriggering) hints.push('edge_case');
    if (state.options.productionLike) hints.push('production_like');
    // Add 'realistic' if coherent is wanted (detected by context or manual)
    if (state.context.length > 0) hints.push('realistic');

    return {
      domain: state.domain,
      entity: state.entity,
      count: state.count,
      context: state.context || undefined,
      scenarios: state.scenarios,
      hints: hints.length > 0 ? hints : undefined,
      outputFormat: state.outputFormat,
      options: state.options,
      generationPath: state.generationPath,
    };
  },
}));
```

Create src/stores/index.ts:
```typescript
export { useGeneratorStore } from './generator-store';
```

Acceptance Criteria:
- [ ] Store initializes with default values
- [ ] All setters update state correctly
- [ ] Scenarios can be added/removed/updated
- [ ] getRequestBody() returns valid request shape
- [ ] reset() restores initial state
```

---

### Task 3.2: Create Generator Form Component

```
Create the main generator form component.

Create src/components/generator/generator-form.tsx:

```typescript
'use client';

import { useGeneratorStore } from '@/stores/generator-store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Settings2 } from 'lucide-react';
import { DOMAINS, OUTPUT_FORMATS } from '@/lib/constants';
import { ContextEditor } from './context-editor';
import { ScenarioBuilder } from './scenario-builder';
import { OptionsPanel } from './options-panel';
import { GenerateButton } from './generate-button';

interface GeneratorFormProps {
  schemas: Array<{ name: string; domain: string }>;
}

export function GeneratorForm({ schemas }: GeneratorFormProps) {
  const {
    domain,
    entity,
    count,
    outputFormat,
    setDomain,
    setEntity,
    setCount,
    setOutputFormat,
  } = useGeneratorStore();

  const entities = schemas
    .filter((s) => s.domain === domain)
    .map((s) => s.name);

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold flex items-center gap-3">
          Generate Test Data
          <Badge variant="secondary" className="bg-accent-muted text-accent capitalize">
            {entity} Schema
          </Badge>
        </h1>
      </div>

      {/* Basic Configuration */}
      <Card className="bg-bg-secondary border-border-default">
        <CardHeader className="pb-4">
          <CardTitle className="text-sm font-semibold text-text-secondary flex items-center gap-2">
            <Settings2 className="w-4 h-4" />
            Basic Configuration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-xs text-text-muted">Domain</Label>
              <Select value={domain} onValueChange={setDomain}>
                <SelectTrigger className="bg-bg-tertiary border-border-default">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {DOMAINS.map((d) => (
                    <SelectItem key={d} value={d} className="capitalize">
                      {d.replace('_', ' ')}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-text-muted">Entity</Label>
              <Select value={entity} onValueChange={setEntity}>
                <SelectTrigger className="bg-bg-tertiary border-border-default">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {entities.map((e) => (
                    <SelectItem key={e} value={e} className="capitalize">
                      {e}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-xs text-text-muted">Count</Label>
              <Input
                type="number"
                value={count}
                onChange={(e) => setCount(Number(e.target.value))}
                min={1}
                max={1000}
                className="bg-bg-tertiary border-border-default"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-text-muted">Output Format</Label>
              <Select value={outputFormat} onValueChange={(v) => setOutputFormat(v as any)}>
                <SelectTrigger className="bg-bg-tertiary border-border-default">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {OUTPUT_FORMATS.map((f) => (
                    <SelectItem key={f} value={f}>
                      {f}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Context */}
      <ContextEditor />

      {/* Scenarios */}
      <ScenarioBuilder />

      {/* Options */}
      <OptionsPanel />

      {/* Generate Button */}
      <GenerateButton />
    </div>
  );
}
```

Create src/components/generator/index.ts:
```typescript
export { GeneratorForm } from './generator-form';
export { ContextEditor } from './context-editor';
export { ScenarioBuilder } from './scenario-builder';
export { OptionsPanel } from './options-panel';
export { GenerateButton } from './generate-button';
```

Acceptance Criteria:
- [ ] Form renders all sections
- [ ] Domain/Entity dropdowns work
- [ ] Count input validates 1-1000
- [ ] Output format selector works
- [ ] Form state syncs with store
```

---

### Task 3.3: Create Context Editor Component

```
Create the context textarea component.

Create src/components/generator/context-editor.tsx:

```typescript
'use client';

import { useGeneratorStore } from '@/stores/generator-store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { MessageSquare } from 'lucide-react';

export function ContextEditor() {
  const { context, setContext } = useGeneratorStore();

  return (
    <Card className="bg-bg-secondary border-border-default">
      <CardHeader className="pb-4">
        <CardTitle className="text-sm font-semibold text-text-secondary flex items-center gap-2">
          <MessageSquare className="w-4 h-4" />
          Context (for LLM Generation)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <Label className="text-xs text-text-muted">
            Describe what you need (natural language)
          </Label>
          <Textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="e.g., Generate shopping carts for ApplePay checkout testing. Carts should have 3-5 items that a real customer would buy together, like fitness gear or home decor sets..."
            className="min-h-[120px] bg-bg-tertiary border-border-default font-mono text-sm resize-y"
          />
          <p className="text-xs text-text-muted">
            Providing context enables intelligent LLM-powered generation with coherent, realistic data.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
```

Acceptance Criteria:
- [ ] Textarea renders with placeholder
- [ ] Value syncs with store
- [ ] Uses monospace font
- [ ] Shows helper text
```

---

### Task 3.4: Create Scenario Builder Component

```
Create the scenario builder for adding/removing/editing scenarios.

Create src/components/generator/scenario-builder.tsx:

```typescript
'use client';

import { useState } from 'react';
import { useGeneratorStore } from '@/stores/generator-store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Target, X, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';

export function ScenarioBuilder() {
  const { scenarios, count, addScenario, removeScenario, updateScenario } =
    useGeneratorStore();
  const [newScenarioName, setNewScenarioName] = useState('');

  const handleAddScenario = () => {
    if (!newScenarioName.trim()) return;

    const name = newScenarioName.trim().toLowerCase().replace(/\s+/g, '_');
    addScenario({ name, count: 10 });
    setNewScenarioName('');
  };

  const totalScenarioCount = scenarios.reduce((sum, s) => sum + s.count, 0);
  const isCountMismatch = totalScenarioCount !== count;

  return (
    <Card className="bg-bg-secondary border-border-default">
      <CardHeader className="pb-4">
        <CardTitle className="text-sm font-semibold text-text-secondary flex items-center gap-2">
          <Target className="w-4 h-4" />
          Scenarios
          {isCountMismatch && (
            <span className="text-xs text-warning ml-2">
              (Total: {totalScenarioCount} ≠ Count: {count})
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {scenarios.map((scenario, index) => (
          <div
            key={index}
            className={cn(
              'flex items-center gap-3 p-3 rounded-lg',
              'bg-bg-tertiary border border-border-default'
            )}
          >
            <Input
              value={scenario.name}
              onChange={(e) =>
                updateScenario(index, { name: e.target.value })
              }
              className="flex-1 bg-transparent border-none text-sm font-medium"
            />
            <Input
              type="number"
              value={scenario.count}
              onChange={(e) =>
                updateScenario(index, { count: Number(e.target.value) })
              }
              min={1}
              className="w-20 bg-bg-primary border-border-default text-center font-mono text-sm"
            />
            <Button
              variant="ghost"
              size="icon"
              onClick={() => removeScenario(index)}
              disabled={scenarios.length === 1}
              className="w-7 h-7 text-text-muted hover:text-error hover:border-error"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        ))}

        {/* Add Scenario */}
        <div className="flex gap-2">
          <Input
            value={newScenarioName}
            onChange={(e) => setNewScenarioName(e.target.value)}
            placeholder="New scenario name..."
            className="flex-1 bg-bg-tertiary border-border-default text-sm"
            onKeyDown={(e) => e.key === 'Enter' && handleAddScenario()}
          />
          <Button
            variant="outline"
            onClick={handleAddScenario}
            disabled={!newScenarioName.trim()}
            className="gap-2 border-dashed border-border-default text-text-muted hover:text-accent hover:border-accent"
          >
            <Plus className="w-4 h-4" />
            Add
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
```

Acceptance Criteria:
- [ ] Displays existing scenarios
- [ ] Can add new scenarios
- [ ] Can remove scenarios (except last one)
- [ ] Can edit scenario name and count
- [ ] Shows warning if counts don't match total
```

---

### Task 3.5: Create Options Panel Component

```
Create the options panel with toggle checkboxes.

Create src/components/generator/options-panel.tsx:

```typescript
'use client';

import { useGeneratorStore } from '@/stores/generator-store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { SlidersHorizontal } from 'lucide-react';
import { GENERATION_OPTIONS } from '@/lib/constants';
import { cn } from '@/lib/utils';

export function OptionsPanel() {
  const { options, toggleOption } = useGeneratorStore();

  const optionKeys: Array<keyof typeof options> = [
    'useCache',
    'learnFromHistory',
    'defectTriggering',
    'productionLike',
  ];

  const optionLabels: Record<string, { label: string; description: string }> = {
    useCache: {
      label: 'Use cached data pools',
      description: 'Faster generation from pre-generated pools',
    },
    learnFromHistory: {
      label: 'Learn from history (RAG)',
      description: 'Use patterns from past successful generations',
    },
    defectTriggering: {
      label: 'Defect-triggering patterns',
      description: 'Generate edge cases known to cause bugs',
    },
    productionLike: {
      label: 'Production-like distribution',
      description: 'Match real production data patterns',
    },
  };

  return (
    <Card className="bg-bg-secondary border-border-default">
      <CardHeader className="pb-4">
        <CardTitle className="text-sm font-semibold text-text-secondary flex items-center gap-2">
          <SlidersHorizontal className="w-4 h-4" />
          Generation Options
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3">
          {optionKeys.map((key) => {
            const isActive = options[key];
            const { label, description } = optionLabels[key];

            return (
              <div
                key={key}
                onClick={() => toggleOption(key)}
                className={cn(
                  'flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-all',
                  'border',
                  isActive
                    ? 'bg-accent-muted border-accent'
                    : 'bg-bg-tertiary border-border-default hover:border-border-light'
                )}
              >
                <Checkbox
                  checked={isActive}
                  className={cn(
                    'mt-0.5',
                    isActive && 'bg-accent border-accent'
                  )}
                />
                <div className="flex-1">
                  <Label
                    className={cn(
                      'text-sm cursor-pointer',
                      isActive ? 'text-text-primary' : 'text-text-secondary'
                    )}
                  >
                    {label}
                  </Label>
                  <p className="text-xs text-text-muted mt-1">{description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
```

Acceptance Criteria:
- [ ] Shows all 4 options
- [ ] Clicking toggles the option
- [ ] Active options are highlighted
- [ ] Descriptions help explain each option
```

---

### Task 3.6: Create Generate Button Component

```
Create the generate button with path selector.

Create src/components/generator/generate-button.tsx:

```typescript
'use client';

import { useGeneratorStore } from '@/stores/generator-store';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Zap, Loader2 } from 'lucide-react';
import { GENERATION_PATHS } from '@/lib/constants';
import type { GenerationPath } from '@/types/api';

interface GenerateButtonProps {
  onGenerate: () => Promise<void>;
}

export function GenerateButton({ onGenerate }: GenerateButtonProps) {
  const { generationPath, setGenerationPath, isLoading, count } =
    useGeneratorStore();

  const handleGenerate = async () => {
    await onGenerate();
  };

  return (
    <div className="flex gap-3">
      <Button
        onClick={handleGenerate}
        disabled={isLoading || count < 1}
        className="flex-1 h-12 bg-gradient-to-r from-accent to-emerald-600 hover:from-accent-hover hover:to-emerald-500 text-white font-semibold"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
            Generating...
          </>
        ) : (
          <>
            <Zap className="w-5 h-5 mr-2" />
            Generate Data
          </>
        )}
      </Button>

      <Select
        value={generationPath}
        onValueChange={(v) => setGenerationPath(v as GenerationPath)}
      >
        <SelectTrigger className="w-[180px] h-12 bg-bg-secondary border-border-default">
          <SelectValue placeholder="Generation Path" />
        </SelectTrigger>
        <SelectContent>
          {GENERATION_PATHS.map((path) => (
            <SelectItem key={path.value} value={path.value}>
              {path.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
```

Update generate-button to not need onGenerate prop - we'll handle it in the page.

Acceptance Criteria:
- [ ] Button shows Zap icon normally
- [ ] Button shows spinner when loading
- [ ] Button is disabled when loading or count < 1
- [ ] Path selector shows all options
- [ ] Has gradient background
```

---

## Phase 4: Preview Components

### Task 4.1: Create JSON Viewer Component

```
Create the JSON viewer with syntax highlighting using Monaco Editor.

Create src/components/preview/json-viewer.tsx:

```typescript
'use client';

import { useEffect, useRef } from 'react';
import Editor, { OnMount } from '@monaco-editor/react';

interface JsonViewerProps {
  data: string;
  className?: string;
}

export function JsonViewer({ data, className }: JsonViewerProps) {
  const editorRef = useRef<any>(null);

  const handleEditorMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;

    // Configure theme
    monaco.editor.defineTheme('testdata-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'string.key.json', foreground: '7dd3fc' },
        { token: 'string.value.json', foreground: '86efac' },
        { token: 'number', foreground: 'fcd34d' },
        { token: 'keyword', foreground: 'f472b6' },
      ],
      colors: {
        'editor.background': '#0a0f1a',
        'editor.foreground': '#f1f5f9',
        'editorLineNumber.foreground': '#64748b',
        'editorLineNumber.activeForeground': '#94a3b8',
        'editor.selectionBackground': '#1e293b',
        'editor.lineHighlightBackground': '#111827',
      },
    });
    monaco.editor.setTheme('testdata-dark');
  };

  // Format JSON
  let formattedData = data;
  try {
    const parsed = JSON.parse(data);
    formattedData = JSON.stringify(parsed, null, 2);
  } catch {
    // Keep original if not valid JSON
  }

  return (
    <Editor
      height="100%"
      language="json"
      value={formattedData}
      onMount={handleEditorMount}
      options={{
        readOnly: true,
        minimap: { enabled: false },
        fontSize: 12,
        fontFamily: 'JetBrains Mono, monospace',
        lineNumbers: 'on',
        scrollBeyondLastLine: false,
        wordWrap: 'on',
        folding: true,
        automaticLayout: true,
        padding: { top: 16, bottom: 16 },
      }}
      className={className}
    />
  );
}
```

Acceptance Criteria:
- [ ] Monaco editor renders
- [ ] JSON is syntax highlighted
- [ ] Custom dark theme applied
- [ ] Read-only mode
- [ ] Folding works
```

---

### Task 4.2: Create Data Preview Panel

```
Create the main preview panel component.

Create src/components/preview/data-preview.tsx:

```typescript
'use client';

import { useState } from 'react';
import { useGeneratorStore } from '@/stores/generator-store';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Copy, Download, BarChart3 } from 'lucide-react';
import { JsonViewer } from './json-viewer';
import { MetadataBar } from './metadata-bar';
import { EmptyState } from '@/components/shared/empty-state';
import { LoadingSpinner } from '@/components/shared/loading-spinner';
import { ErrorMessage } from '@/components/shared/error-message';
import { cn } from '@/lib/utils';

export function DataPreview() {
  const { result, isLoading, error } = useGeneratorStore();
  const [activeTab, setActiveTab] = useState<'json' | 'csv' | 'sql'>('json');

  const handleCopy = async () => {
    if (!result?.data) return;
    await navigator.clipboard.writeText(result.data);
    // TODO: Show toast
  };

  const handleDownload = () => {
    if (!result?.data) return;

    const extension = activeTab;
    const mimeType =
      activeTab === 'json'
        ? 'application/json'
        : activeTab === 'csv'
        ? 'text/csv'
        : 'text/plain';

    const blob = new Blob([result.data], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `test-data.${extension}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-default">
        <span className="text-sm font-semibold">Generated Data</span>
        <div className="flex items-center gap-2">
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)}>
            <TabsList className="bg-bg-tertiary">
              <TabsTrigger value="json" className="text-xs">
                JSON
              </TabsTrigger>
              <TabsTrigger value="csv" className="text-xs">
                CSV
              </TabsTrigger>
              <TabsTrigger value="sql" className="text-xs">
                SQL
              </TabsTrigger>
            </TabsList>
          </Tabs>
          <div className="flex gap-1 ml-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleCopy}
              disabled={!result?.data}
              className="w-8 h-8"
            >
              <Copy className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleDownload}
              disabled={!result?.data}
              className="w-8 h-8"
            >
              <Download className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 relative overflow-hidden">
        {/* Loading State */}
        {isLoading && (
          <div className="absolute inset-0 bg-bg-primary/80 flex flex-col items-center justify-center z-10">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-sm text-text-secondary">
              Generating with LLM...
            </p>
          </div>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <ErrorMessage
            message={error}
            onRetry={() => {
              /* TODO: Retry logic */
            }}
            className="h-full"
          />
        )}

        {/* Empty State */}
        {!result && !isLoading && !error && (
          <EmptyState
            icon={<BarChart3 className="w-12 h-12" />}
            title="No data yet"
            description="Configure your request and click Generate to see data here"
            className="h-full"
          />
        )}

        {/* Data View */}
        {result?.data && !isLoading && (
          <ScrollArea className="h-full">
            <div className="p-4">
              {activeTab === 'json' && <JsonViewer data={result.data} />}
              {activeTab === 'csv' && (
                <pre className="font-mono text-xs whitespace-pre-wrap">
                  {/* TODO: Convert JSON to CSV */}
                  {result.data}
                </pre>
              )}
              {activeTab === 'sql' && (
                <pre className="font-mono text-xs whitespace-pre-wrap">
                  {/* TODO: Convert JSON to SQL */}
                  {result.data}
                </pre>
              )}
            </div>
          </ScrollArea>
        )}
      </div>

      {/* Metadata */}
      {result?.metadata && !isLoading && <MetadataBar metadata={result.metadata} />}
    </div>
  );
}
```

Create src/components/preview/index.ts:
```typescript
export { DataPreview } from './data-preview';
export { JsonViewer } from './json-viewer';
export { MetadataBar } from './metadata-bar';
```

Acceptance Criteria:
- [ ] Shows empty state initially
- [ ] Shows loading state during generation
- [ ] Shows error state with retry
- [ ] Shows data with format tabs
- [ ] Copy and download work
```

---

### Task 4.3: Create Metadata Bar Component

```
Create the metadata bar showing generation stats.

Create src/components/preview/metadata-bar.tsx:

```typescript
import type { GenerationMetadata } from '@/types/api';
import { cn } from '@/lib/utils';

interface MetadataBarProps {
  metadata: GenerationMetadata;
  className?: string;
}

export function MetadataBar({ metadata, className }: MetadataBarProps) {
  const items = [
    {
      label: 'Path',
      value: metadata.generationPath.toUpperCase(),
    },
    {
      label: 'Tokens',
      value: metadata.llmTokensUsed?.toLocaleString() ?? '-',
    },
    {
      label: 'Time',
      value: `${(metadata.generationTimeMs / 1000).toFixed(1)}s`,
    },
    {
      label: 'Coherence',
      value: metadata.coherenceScore?.toFixed(2) ?? '-',
    },
  ];

  return (
    <div
      className={cn(
        'grid grid-cols-4 gap-4 p-4 border-t border-border-default bg-bg-tertiary',
        className
      )}
    >
      {items.map((item) => (
        <div key={item.label} className="text-center">
          <div className="text-lg font-bold text-accent font-mono">
            {item.value}
          </div>
          <div className="text-xs text-text-muted mt-1">{item.label}</div>
        </div>
      ))}
    </div>
  );
}
```

Acceptance Criteria:
- [ ] Shows 4 metrics in a row
- [ ] Values are formatted correctly
- [ ] Uses monospace font for values
- [ ] Shows '-' for missing values
```

---

## Phase 5: API Integration

### Task 5.1: Create gRPC Client for BFF

```
Create the gRPC client that the BFF API routes will use.

Create src/lib/grpc-client.ts:

```typescript
import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import path from 'path';

const PROTO_PATH = path.join(process.cwd(), '../service/protos/test_data.proto');

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

const protoDescriptor = grpc.loadPackageDefinition(packageDefinition) as any;
const TestDataService = protoDescriptor.testdata.v1.TestDataService;

const GRPC_HOST = process.env.GRPC_SERVICE_HOST || 'localhost';
const GRPC_PORT = process.env.GRPC_SERVICE_PORT || '9001';

let client: any = null;

function getClient() {
  if (!client) {
    client = new TestDataService(
      `${GRPC_HOST}:${GRPC_PORT}`,
      grpc.credentials.createInsecure()
    );
  }
  return client;
}

export async function generateData(request: any): Promise<any> {
  return new Promise((resolve, reject) => {
    getClient().GenerateData(request, (error: any, response: any) => {
      if (error) {
        reject(error);
      } else {
        resolve(response);
      }
    });
  });
}

export async function getSchemas(domain?: string): Promise<any> {
  return new Promise((resolve, reject) => {
    getClient().GetSchemas({ domain: domain || '' }, (error: any, response: any) => {
      if (error) {
        reject(error);
      } else {
        resolve(response);
      }
    });
  });
}

export async function healthCheck(): Promise<any> {
  return new Promise((resolve, reject) => {
    getClient().HealthCheck({}, (error: any, response: any) => {
      if (error) {
        reject(error);
      } else {
        resolve(response);
      }
    });
  });
}
```

Acceptance Criteria:
- [ ] Client loads proto file
- [ ] Client connects to gRPC service
- [ ] generateData() works
- [ ] getSchemas() works
- [ ] healthCheck() works
```

---

### Task 5.2: Implement API Routes

```
Implement the BFF API routes.

Update src/app/api/health/route.ts:

```typescript
import { NextResponse } from 'next/server';
import { healthCheck } from '@/lib/grpc-client';

export async function GET() {
  try {
    const response = await healthCheck();
    return NextResponse.json({
      status: response.status === 'healthy' ? 'healthy' : 'degraded',
      service: {
        status: response.status,
        components: response.components || {},
      },
    });
  } catch (error) {
    console.error('Health check failed:', error);
    return NextResponse.json(
      {
        status: 'unhealthy',
        service: { status: 'unreachable', components: {} },
      },
      { status: 503 }
    );
  }
}
```

Update src/app/api/schemas/route.ts:

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { getSchemas } from '@/lib/grpc-client';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const domain = searchParams.get('domain') || undefined;

    const response = await getSchemas(domain);

    return NextResponse.json({
      schemas: response.schemas || [],
    });
  } catch (error) {
    console.error('Get schemas failed:', error);
    return NextResponse.json(
      { error: 'Failed to fetch schemas' },
      { status: 500 }
    );
  }
}
```

Update src/app/api/generate/route.ts:

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { generateData } from '@/lib/grpc-client';
import type { GenerateRequestBody } from '@/types/api';

export async function POST(request: NextRequest) {
  try {
    const body: GenerateRequestBody = await request.json();

    // Transform REST body to gRPC request
    const grpcRequest = {
      request_id: `req-${Date.now()}`,
      domain: body.domain,
      entity: body.entity,
      count: body.count,
      context: body.context || '',
      scenarios: body.scenarios?.map((s) => ({
        name: s.name,
        count: s.count,
        description: s.description || '',
        overrides: s.overrides || {},
      })) || [],
      hints: body.hints || [],
      output_format: body.outputFormat === 'CSV' ? 1 : body.outputFormat === 'SQL' ? 2 : 0,
      use_cache: body.options?.useCache || false,
      learn_from_history: body.options?.learnFromHistory || false,
      defect_triggering: body.options?.defectTriggering || false,
      production_like: body.options?.productionLike || false,
    };

    const response = await generateData(grpcRequest);

    return NextResponse.json({
      success: response.success,
      requestId: response.request_id,
      data: response.data,
      recordCount: response.record_count,
      metadata: {
        generationPath: response.metadata?.generation_path || 'unknown',
        llmTokensUsed: response.metadata?.llm_tokens_used,
        generationTimeMs: response.metadata?.generation_time_ms || 0,
        coherenceScore: response.metadata?.coherence_score,
        scenarioCounts: response.metadata?.scenario_counts || {},
      },
      error: response.error || undefined,
    });
  } catch (error) {
    console.error('Generate data failed:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Generation failed',
      },
      { status: 500 }
    );
  }
}
```

Acceptance Criteria:
- [ ] /api/health returns service status
- [ ] /api/schemas returns schema list
- [ ] /api/generate accepts POST and returns data
- [ ] Error handling works
- [ ] Request transformation is correct
```

---

### Task 5.3: Create API Client for Frontend

```
Create the frontend API client using fetch.

Create src/lib/api-client.ts:

```typescript
import type {
  GenerateRequestBody,
  GenerateResponseBody,
  SchemasResponseBody,
  HealthResponseBody,
} from '@/types/api';

const BASE_URL = '';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiError(response.status, error.error || response.statusText);
  }

  return response.json();
}

export const api = {
  health: {
    check: () => fetchJson<HealthResponseBody>(`${BASE_URL}/api/health`),
  },

  schemas: {
    list: (domain?: string) => {
      const params = domain ? `?domain=${domain}` : '';
      return fetchJson<SchemasResponseBody>(`${BASE_URL}/api/schemas${params}`);
    },
  },

  generate: {
    data: (body: GenerateRequestBody) =>
      fetchJson<GenerateResponseBody>(`${BASE_URL}/api/generate`, {
        method: 'POST',
        body: JSON.stringify(body),
      }),
  },
};

export { ApiError };
```

Acceptance Criteria:
- [ ] api.health.check() works
- [ ] api.schemas.list() works
- [ ] api.generate.data() works
- [ ] ApiError class for error handling
```

---

### Task 5.4: Create React Query Hooks

```
Create React Query hooks for data fetching.

Create src/hooks/use-schemas.ts:

```typescript
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api-client';

export function useSchemas(domain?: string) {
  return useQuery({
    queryKey: ['schemas', domain],
    queryFn: () => api.schemas.list(domain),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

Create src/hooks/use-generate.ts:

```typescript
import { useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api-client';
import { useGeneratorStore } from '@/stores/generator-store';
import type { GenerateRequestBody } from '@/types/api';

export function useGenerate() {
  const { setResult, setLoading, setError, getRequestBody } = useGeneratorStore();

  return useMutation({
    mutationFn: (body: GenerateRequestBody) => api.generate.data(body),
    onMutate: () => {
      setLoading(true);
      setError(null);
    },
    onSuccess: (data) => {
      setResult(data);
      setLoading(false);
    },
    onError: (error) => {
      setError(error instanceof Error ? error.message : 'Generation failed');
      setLoading(false);
    },
  });
}
```

Create src/hooks/use-service-health.ts:

```typescript
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api-client';

export function useServiceHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => api.health.check(),
    refetchInterval: 30000, // 30 seconds
    retry: false,
  });
}
```

Create src/hooks/index.ts:
```typescript
export { useSchemas } from './use-schemas';
export { useGenerate } from './use-generate';
export { useServiceHealth } from './use-service-health';
```

Acceptance Criteria:
- [ ] useSchemas fetches and caches schemas
- [ ] useGenerate handles mutation lifecycle
- [ ] useServiceHealth polls service status
- [ ] Store is updated correctly on success/error
```

---

### Task 5.5: Set Up React Query Provider

```
Set up React Query provider in the app.

Create src/components/providers.tsx:

```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

Update src/app/layout.tsx:

```typescript
import type { Metadata } from 'next';
import { APP_NAME } from '@/lib/constants';
import { Providers } from '@/components/providers';
import './globals.css';

export const metadata: Metadata = {
  title: APP_NAME,
  description: 'Generate intelligent test data for QA',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

Acceptance Criteria:
- [ ] QueryClientProvider wraps app
- [ ] DevTools available in development
- [ ] Default options configured
```

---

## Phase 6: Main Page Integration

### Task 6.1: Create Main Page

```
Create the main page that brings everything together.

Update src/app/page.tsx:

```typescript
'use client';

import { useEffect } from 'react';
import { MainLayout } from '@/components/layout';
import { GeneratorForm } from '@/components/generator/generator-form';
import { DataPreview } from '@/components/preview/data-preview';
import { useGeneratorStore } from '@/stores/generator-store';
import { useSchemas } from '@/hooks/use-schemas';
import { useGenerate } from '@/hooks/use-generate';
import { LoadingSpinner } from '@/components/shared/loading-spinner';

export default function HomePage() {
  const { domain, setDomain, setEntity, loadPreset } = useGeneratorStore();
  const { data: schemasData, isLoading: schemasLoading } = useSchemas();
  const { mutate: generate } = useGenerate();

  const schemas = schemasData?.schemas || [];
  const selectedSchema = useGeneratorStore((state) => state.entity);

  // Handle schema selection from sidebar
  const handleSchemaSelect = (schemaName: string) => {
    const schema = schemas.find((s) => s.name === schemaName);
    if (schema) {
      setDomain(schema.domain);
      setEntity(schema.name);
    }
  };

  // Handle quick generate
  const handleQuickGenerate = (type: string) => {
    const presets: Record<string, any> = {
      carts: {
        domain: 'ecommerce',
        entity: 'cart',
        count: 10,
        scenarios: [{ name: 'happy_path', count: 10 }],
      },
      orders: {
        domain: 'ecommerce',
        entity: 'order',
        count: 10,
        scenarios: [{ name: 'happy_path', count: 10 }],
      },
      users: {
        domain: 'ecommerce',
        entity: 'user',
        count: 25,
        scenarios: [{ name: 'happy_path', count: 25 }],
      },
      edge: {
        domain: 'ecommerce',
        entity: 'cart',
        count: 20,
        options: { defectTriggering: true },
        scenarios: [{ name: 'edge_case', count: 20 }],
      },
    };

    const preset = presets[type];
    if (preset) {
      loadPreset(preset);
      // Auto-generate
      const requestBody = useGeneratorStore.getState().getRequestBody();
      generate(requestBody);
    }
  };

  // Handle generate
  const handleGenerate = async () => {
    const requestBody = useGeneratorStore.getState().getRequestBody();
    generate(requestBody);
  };

  if (schemasLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg-primary">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <MainLayout
      selectedSchema={selectedSchema}
      onSchemaSelect={handleSchemaSelect}
      onQuickGenerate={handleQuickGenerate}
      preview={<DataPreview />}
    >
      <GeneratorForm schemas={schemas} onGenerate={handleGenerate} />
    </MainLayout>
  );
}
```

Update GeneratorForm to accept onGenerate:
```typescript
interface GeneratorFormProps {
  schemas: Array<{ name: string; domain: string }>;
  onGenerate: () => Promise<void>;
}
```

Update GenerateButton:
```typescript
// In generator-form.tsx, pass onGenerate to GenerateButton
<GenerateButton onGenerate={onGenerate} />
```

Acceptance Criteria:
- [ ] Page loads with layout
- [ ] Schemas load and populate sidebar
- [ ] Schema selection updates form
- [ ] Quick generate works
- [ ] Generate button triggers API call
- [ ] Preview shows result
```

---

### Task 6.2: Add History Store

```
Create history store to persist recent generations.

Create src/stores/history-store.ts:

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { GenerateRequestBody } from '@/types/api';

export interface HistoryEntry {
  id: string;
  timestamp: string;
  label: string;
  request: GenerateRequestBody;
  recordCount: number;
}

interface HistoryState {
  entries: HistoryEntry[];
  addEntry: (entry: Omit<HistoryEntry, 'id' | 'timestamp'>) => void;
  removeEntry: (id: string) => void;
  clearHistory: () => void;
}

export const useHistoryStore = create<HistoryState>()(
  persist(
    (set) => ({
      entries: [],

      addEntry: (entry) =>
        set((state) => ({
          entries: [
            {
              ...entry,
              id: `hist-${Date.now()}`,
              timestamp: new Date().toISOString(),
            },
            ...state.entries.slice(0, 19), // Keep last 20
          ],
        })),

      removeEntry: (id) =>
        set((state) => ({
          entries: state.entries.filter((e) => e.id !== id),
        })),

      clearHistory: () => set({ entries: [] }),
    }),
    {
      name: 'testdata-history',
    }
  )
);
```

Update stores/index.ts:
```typescript
export { useGeneratorStore } from './generator-store';
export { useHistoryStore } from './history-store';
```

Acceptance Criteria:
- [ ] History persists to localStorage
- [ ] Entries have id and timestamp
- [ ] Max 20 entries kept
- [ ] Can clear history
```

---

### Task 6.3: Update Sidebar with Real Data

```
Update sidebar to use real schemas and history.

Update src/components/layout/sidebar.tsx to accept schemas as prop and use history store:

Add to props:
```typescript
interface SidebarProps {
  schemas: Array<{ name: string; domain: string }>;
  selectedSchema: string | null;
  onSchemaSelect: (schema: string) => void;
  onQuickGenerate: (type: string) => void;
  onHistorySelect: (entry: HistoryEntry) => void;
  className?: string;
}
```

In component, use the history store:
```typescript
import { useHistoryStore } from '@/stores/history-store';

// Inside component:
const { entries: historyEntries } = useHistoryStore();
```

Replace MOCK_SCHEMAS with schemas prop.
Replace RECENT_ITEMS with historyEntries.

Acceptance Criteria:
- [ ] Schemas come from API
- [ ] History shows recent generations
- [ ] Clicking history loads that config
```

---

## Phase 7: Testing & Polish

### Task 7.1: Write Component Tests

```
Write tests for key components using Vitest.

Create tests/components/generator-form.test.tsx:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { GeneratorForm } from '@/components/generator/generator-form';

const mockSchemas = [
  { name: 'cart', domain: 'ecommerce' },
  { name: 'order', domain: 'ecommerce' },
];

describe('GeneratorForm', () => {
  it('renders basic configuration section', () => {
    render(<GeneratorForm schemas={mockSchemas} onGenerate={vi.fn()} />);
    expect(screen.getByText('Basic Configuration')).toBeInTheDocument();
  });

  it('shows correct entities for selected domain', () => {
    render(<GeneratorForm schemas={mockSchemas} onGenerate={vi.fn()} />);
    // Check that cart and order are available
    const entitySelect = screen.getByRole('combobox', { name: /entity/i });
    expect(entitySelect).toBeInTheDocument();
  });

  it('calls onGenerate when button is clicked', async () => {
    const onGenerate = vi.fn();
    render(<GeneratorForm schemas={mockSchemas} onGenerate={onGenerate} />);
    
    const generateButton = screen.getByRole('button', { name: /generate/i });
    fireEvent.click(generateButton);
    
    expect(onGenerate).toHaveBeenCalled();
  });
});
```

Create more tests for:
- Sidebar selection
- Scenario builder add/remove
- Options toggle
- Preview states

Acceptance Criteria:
- [ ] Tests run with pnpm test
- [ ] Key interactions are tested
- [ ] Mocks are used for stores
```

---

### Task 7.2: Create Dockerfile

```
Create production Dockerfile for the UI.

Create ui/Dockerfile:

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Install pnpm
RUN corepack enable pnpm

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source
COPY . .

# Copy proto from service (needed for type generation)
COPY ../service/protos ../service/protos

# Build
ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built files
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

Update root docker-compose.yml to include UI service.

Acceptance Criteria:
- [ ] docker build -t testdata-ui ./ui works
- [ ] Container runs and serves on port 3000
- [ ] docker-compose up starts both services
```

---

### Task 7.3: Update Root Makefile

```
Update root Makefile to orchestrate both service and UI.

Update test-data-agent/Makefile:

```makefile
.PHONY: all dev build test clean

# Development
dev:
	docker-compose up

dev-service:
	cd service && make run

dev-ui:
	cd ui && pnpm dev

# Build
build:
	docker-compose build

build-service:
	cd service && make docker-build

build-ui:
	cd ui && pnpm build

# Test
test: test-service test-ui

test-service:
	cd service && make test

test-ui:
	cd ui && pnpm test

# Lint
lint: lint-service lint-ui

lint-service:
	cd service && make lint

lint-ui:
	cd ui && pnpm lint

# Proto
proto:
	cd service && make proto
	cd ui && pnpm proto:generate

# Clean
clean:
	docker-compose down -v
	cd service && make clean
	cd ui && rm -rf .next node_modules
```

Acceptance Criteria:
- [ ] make dev starts everything
- [ ] make test runs all tests
- [ ] make build builds both
- [ ] make proto generates types
```

---

### Task 7.4: Final Polish

```
Final polish and documentation.

1. Add loading states for all async operations
2. Add error boundaries
3. Add toast notifications for copy/download
4. Add keyboard shortcuts (Cmd+Enter to generate)
5. Add responsive design for smaller screens
6. Update README.md with UI documentation

Create ui/README.md with:
- Setup instructions
- Development workflow
- Environment variables
- Component structure
- Testing guide

Acceptance Criteria:
- [ ] No console errors
- [ ] All states handled (loading, error, empty, success)
- [ ] Copy shows feedback
- [ ] README is complete
```

---

## Task Checklist

### Phase 1: Project Setup
- [x] Task 1.1: Initialize Next.js Project
- [x] Task 1.2: Install Dependencies
- [x] Task 1.3: Configure Tailwind with Custom Theme
- [x] Task 1.4: Generate TypeScript Types from Proto
- [x] Task 1.5: Set Up Project Structure

### Phase 2: Layout Components
- [x] Task 2.1: Install shadcn/ui Components
- [x] Task 2.2: Create Header Component
- [x] Task 2.3: Create Sidebar Component
- [x] Task 2.4: Create Main Layout
- [x] Task 2.5: Create Shared Components

### Phase 3: Generator Components
- [x] Task 3.1: Create Generator Store (Zustand)
- [x] Task 3.2: Create Generator Form Component
- [x] Task 3.3: Create Context Editor Component
- [x] Task 3.4: Create Scenario Builder Component
- [x] Task 3.5: Create Options Panel Component
- [x] Task 3.6: Create Generate Button Component

### Phase 4: Preview Components
- [x] Task 4.1: Create JSON Viewer Component
- [x] Task 4.2: Create Data Preview Panel
- [x] Task 4.3: Create Metadata Bar Component

### Phase 5: API Integration
- [x] Task 5.1: Create gRPC Client for BFF
- [x] Task 5.2: Implement API Routes
- [x] Task 5.3: Create API Client for Frontend
- [ ] Task 5.4: Create React Query Hooks
- [ ] Task 5.5: Set Up React Query Provider

### Phase 6: Main Page Integration
- [x] Task 6.1: Create Main Page
- [ ] Task 6.2: Add History Store
- [ ] Task 6.3: Update Sidebar with Real Data

### Phase 7: Testing & Polish
- [ ] Task 7.1: Write Component Tests
- [ ] Task 7.2: Create Dockerfile
- [ ] Task 7.3: Update Root Makefile
- [ ] Task 7.4: Final Polish

---

## Usage Tips

### Starting a Task

```
I'm building the Test Data Agent UI. Here are my specs:
- UI PRD: ui_prd.md
- Wireframe: test-data-agent-wireframe.html
- Service PRD: PRD.md (backend - do not modify)

Current task:
[Paste task block here]

Implement this task.
```

### Referencing the Wireframe

```
Use the wireframe at test-data-agent-wireframe.html as visual reference
for styling and layout.
```

### Testing Integration

```
The backend service is running on localhost:9001 (gRPC).
Test the UI integration with: docker-compose up
```
