'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import {
  BookOpen,
  Code,
  Sparkles,
  Database,
  GitBranch,
  Layers,
  Terminal,
  FileCode,
  Settings,
  Zap
} from 'lucide-react';

export default function DocumentationPage() {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Documentation</h1>
        <p className="text-gray-500">Learn how to use the Test Data Agent effectively</p>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="bg-bg-secondary">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="generation-paths">Generation Paths</TabsTrigger>
          <TabsTrigger value="api">API Reference</TabsTrigger>
          <TabsTrigger value="examples">Examples</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <Card className="bg-white border-border-default">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-macys-red" />
                Getting Started
              </CardTitle>
              <CardDescription>Quick introduction to Test Data Agent</CardDescription>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p className="text-gray-700">
                The Test Data Agent is an AI-powered service that generates realistic test data for your applications.
                It supports multiple generation strategies including traditional rule-based generation, LLM-powered generation,
                RAG (Retrieval Augmented Generation), and hybrid approaches.
              </p>

              <h3 className="text-lg font-semibold mt-4 text-gray-900">Key Features</h3>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                <li>Multiple generation paths for different use cases</li>
                <li>Custom entity support with JSON schema validation</li>
                <li>Scenario-based generation for edge cases</li>
                <li>Production-like data distributions</li>
                <li>Real-time generation with streaming support</li>
                <li>Comprehensive API for programmatic access</li>
              </ul>

              <h3 className="text-lg font-semibold mt-4 text-gray-900">Supported Entities</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                {['Cart', 'Order', 'Product', 'User', 'Payment', 'Review'].map((entity) => (
                  <Badge key={entity} variant="secondary" className="justify-center">
                    {entity}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white border-border-default">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5 text-macys-red" />
                Configuration
              </CardTitle>
              <CardDescription>Set up your environment</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Environment Variables</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto">
{`ANTHROPIC_API_KEY=your-api-key
WEAVIATE_URL=http://localhost:8080
GRPC_PORT=9091
HTTP_PORT=8091`}
                </pre>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Docker Setup</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto">
{`docker-compose up -d
python -m test_data_agent.main`}
                </pre>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="generation-paths" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="bg-white border-border-default">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code className="h-5 w-5 text-blue-600" />
                  Traditional
                </CardTitle>
                <Badge className="bg-blue-100 text-blue-700 border-blue-200">Rule-based</Badge>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-4">
                  Uses predefined rules and patterns to generate data. Fast and deterministic.
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <Zap className="h-4 w-4 text-green-600" />
                    <span className="text-gray-600">Speed: Very Fast (~100ms)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Database className="h-4 w-4 text-blue-600" />
                    <span className="text-gray-600">Consistency: High</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white border-border-default">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-macys-red" />
                  LLM
                </CardTitle>
                <Badge className="bg-macys-red/10 text-macys-red border-macys-red/20">AI-Powered</Badge>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-4">
                  Uses Claude to generate contextually relevant and creative data.
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <Zap className="h-4 w-4 text-yellow-600" />
                    <span className="text-gray-600">Speed: Moderate (~2-5s)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-purple-600" />
                    <span className="text-gray-600">Creativity: High</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white border-border-default">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <GitBranch className="h-5 w-5 text-green-600" />
                  RAG
                </CardTitle>
                <Badge className="bg-green-100 text-green-700 border-green-200">Pattern-based</Badge>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-4">
                  Retrieves and adapts patterns from existing data using vector search.
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <Zap className="h-4 w-4 text-yellow-600" />
                    <span className="text-gray-600">Speed: Fast (~500ms)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Database className="h-4 w-4 text-blue-600" />
                    <span className="text-gray-600">Realism: Very High</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white border-border-default">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Layers className="h-5 w-5 text-orange-600" />
                  Hybrid
                </CardTitle>
                <Badge className="bg-orange-100 text-orange-700 border-orange-200">Combined</Badge>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-4">
                  Intelligently combines multiple strategies for optimal results.
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <Zap className="h-4 w-4 text-green-600" />
                    <span className="text-gray-600">Speed: Variable</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Layers className="h-4 w-4 text-purple-600" />
                    <span className="text-gray-600">Flexibility: Maximum</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="api" className="space-y-6">
          {/* gRPC API Examples */}
          <Card className="bg-white border-border-default">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Terminal className="h-5 w-5 text-macys-red" />
                gRPC API - All Generation Paths
              </CardTitle>
              <CardDescription>Complete examples for each generation strategy</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Traditional Path */}
              <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                  <Code className="h-4 w-4 text-blue-600" />
                  Traditional Generation (Rule-based)
                </h4>
                <pre className="text-sm bg-white p-3 rounded overflow-x-auto">
{`# Traditional generation - Fast, deterministic
grpcurl -plaintext -d '{
  "request_id": "trad-001",
  "domain": "ecommerce",
  "entity": "product",
  "count": 100,
  "hints": ["use_traditional"],
  "use_cache": true,
  "production_like": true
}' localhost:9091 testdata.v1.TestDataService/GenerateData`}
                </pre>
              </div>

              {/* LLM Path */}
              <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-macys-red" />
                  LLM Generation (AI-Powered)
                </h4>
                <pre className="text-sm bg-white p-3 rounded overflow-x-auto">
{`# LLM generation - Creative, contextual
grpcurl -plaintext -d '{
  "request_id": "llm-002",
  "domain": "ecommerce",
  "entity": "user",
  "count": 50,
  "context": "Generate diverse user profiles for a luxury fashion e-commerce platform. Include millennials and Gen-Z with high disposable income, interest in sustainable fashion, and varied geographic locations.",
  "hints": ["use_llm", "ai_generated", "creative"],
  "scenarios": [
    {
      "name": "vip_customer",
      "count": 10,
      "description": "High-value customers with premium membership"
    },
    {
      "name": "new_customer",
      "count": 20,
      "description": "Recently registered users exploring the platform"
    },
    {
      "name": "loyal_customer",
      "count": 20,
      "description": "Regular shoppers with purchase history"
    }
  ]
}' localhost:9091 testdata.v1.TestDataService/GenerateData`}
                </pre>
              </div>

              {/* RAG Path */}
              <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                  <GitBranch className="h-4 w-4 text-green-600" />
                  RAG Generation (Pattern-based)
                </h4>
                <pre className="text-sm bg-white p-3 rounded overflow-x-auto">
{`# RAG generation - Learn from existing patterns
grpcurl -plaintext -d '{
  "request_id": "rag-003",
  "domain": "ecommerce",
  "entity": "order",
  "count": 200,
  "context": "Generate orders similar to Black Friday 2023 patterns",
  "hints": ["use_rag", "pattern_based"],
  "learn_from_history": true,
  "production_like": true,
  "constraints": {
    "field_constraints": {
      "total": {
        "min": 50.0,
        "max": 5000.0
      },
      "items": {
        "min_length": 1,
        "max_length": 10
      }
    }
  }
}' localhost:9091 testdata.v1.TestDataService/GenerateData`}
                </pre>
              </div>

              {/* Hybrid Path */}
              <div className="bg-orange-50 border border-orange-200 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                  <Layers className="h-4 w-4 text-orange-600" />
                  Hybrid Generation (Combined Strategy)
                </h4>
                <pre className="text-sm bg-white p-3 rounded overflow-x-auto">
{`# Hybrid generation - Best of all approaches
grpcurl -plaintext -d '{
  "request_id": "hybrid-004",
  "domain": "ecommerce",
  "entity": "review",
  "count": 500,
  "context": "Generate product reviews with realistic sentiment distribution",
  "hints": ["use_hybrid", "balanced"],
  "use_cache": true,
  "learn_from_history": true,
  "defect_triggering": true,
  "scenarios": [
    {
      "name": "positive_verified",
      "count": 300,
      "overrides": {
        "rating": "5",
        "verified_purchase": "true"
      }
    },
    {
      "name": "critical_detailed",
      "count": 100,
      "overrides": {
        "rating": "2"
      }
    },
    {
      "name": "neutral_helpful",
      "count": 100,
      "overrides": {
        "rating": "3"
      }
    }
  ]
}' localhost:9091 testdata.v1.TestDataService/GenerateData`}
                </pre>
              </div>

              {/* Custom Schema */}
              <div className="bg-purple-50 border border-purple-200 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                  <Database className="h-4 w-4 text-purple-600" />
                  Custom Schema Generation
                </h4>
                <pre className="text-sm bg-white p-3 rounded overflow-x-auto">
{`# Custom entity with inline schema definition
grpcurl -plaintext -d '{
  "request_id": "custom-005",
  "domain": "custom",
  "entity": "subscription",
  "count": 50,
  "context": "SaaS subscription plans for enterprise customers",
  "hints": ["use_llm", "creative"],
  "inline_schema": "{
    \\"type\\": \\"object\\",
    \\"properties\\": {
      \\"subscription_id\\": {
        \\"type\\": \\"string\\",
        \\"pattern\\": \\"^SUB-[A-Z0-9]{8}$\\"
      },
      \\"customer_id\\": {
        \\"type\\": \\"string\\"
      },
      \\"plan_type\\": {
        \\"type\\": \\"string\\",
        \\"enum\\": [\\"basic\\", \\"professional\\", \\"enterprise\\"]
      },
      \\"billing_cycle\\": {
        \\"type\\": \\"string\\",
        \\"enum\\": [\\"monthly\\", \\"quarterly\\", \\"annual\\"]
      },
      \\"price\\": {
        \\"type\\": \\"number\\",
        \\"minimum\\": 0,
        \\"maximum\\": 10000
      },
      \\"features\\": {
        \\"type\\": \\"array\\",
        \\"items\\": {
          \\"type\\": \\"string\\"
        }
      },
      \\"status\\": {
        \\"type\\": \\"string\\",
        \\"enum\\": [\\"active\\", \\"cancelled\\", \\"suspended\\", \\"trial\\"]
      },
      \\"start_date\\": {
        \\"type\\": \\"string\\",
        \\"format\\": \\"date-time\\"
      },
      \\"renewal_date\\": {
        \\"type\\": \\"string\\",
        \\"format\\": \\"date-time\\"
      }
    },
    \\"required\\": [\\"subscription_id\\", \\"customer_id\\", \\"plan_type\\", \\"price\\", \\"status\\"]
  }"
}' localhost:9091 testdata.v1.TestDataService/GenerateData`}
                </pre>
              </div>

              {/* Streaming for Large Datasets */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Stream Large Datasets (Any Path)</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto">
{`# Stream generation for large datasets (>1000 records)
grpcurl -plaintext -d '{
  "request_id": "stream-006",
  "domain": "ecommerce",
  "entity": "product",
  "count": 50000,
  "hints": ["use_hybrid"],
  "context": "Large product catalog for marketplace",
  "use_cache": true,
  "production_like": true
}' localhost:9091 testdata.v1.TestDataService/GenerateDataStream`}
                </pre>
              </div>
            </CardContent>
          </Card>

          {/* REST API Examples */}
          <Card className="bg-white border-border-default">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileCode className="h-5 w-5 text-macys-red" />
                REST API - All Generation Paths
              </CardTitle>
              <CardDescription>HTTP endpoints for each generation strategy</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Traditional REST */}
              <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Traditional Generation (REST)</h4>
                <pre className="text-sm bg-white p-3 rounded overflow-x-auto">
{`curl -X POST http://localhost:3000/api/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "domain": "ecommerce",
    "entity": "cart",
    "count": 25,
    "generationPath": "traditional",
    "options": {
      "useCache": true,
      "productionLike": true
    }
  }'`}
                </pre>
              </div>

              {/* LLM REST */}
              <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">LLM Generation (REST)</h4>
                <pre className="text-sm bg-white p-3 rounded overflow-x-auto">
{`curl -X POST http://localhost:3000/api/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "domain": "ecommerce",
    "entity": "payment",
    "count": 30,
    "generationPath": "llm",
    "context": "Holiday shopping payments with mix of credit cards, PayPal, and gift cards. Include some declined transactions and refunds.",
    "scenarios": [
      {
        "name": "successful_payment",
        "percentage": 80
      },
      {
        "name": "declined_payment",
        "percentage": 15
      },
      {
        "name": "refunded",
        "percentage": 5
      }
    ]
  }'`}
                </pre>
              </div>

              {/* RAG REST */}
              <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">RAG Generation (REST)</h4>
                <pre className="text-sm bg-white p-3 rounded overflow-x-auto">
{`curl -X POST http://localhost:3000/api/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "domain": "ecommerce",
    "entity": "user",
    "count": 100,
    "generationPath": "rag",
    "context": "Similar to our Q4 2023 user base",
    "options": {
      "learnFromHistory": true,
      "productionLike": true
    }
  }'`}
                </pre>
              </div>

              {/* Hybrid REST */}
              <div className="bg-orange-50 border border-orange-200 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Hybrid Generation (REST)</h4>
                <pre className="text-sm bg-white p-3 rounded overflow-x-auto">
{`curl -X POST http://localhost:3000/api/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "domain": "ecommerce",
    "entity": "order",
    "count": 250,
    "generationPath": "hybrid",
    "context": "Realistic order distribution for load testing",
    "options": {
      "useCache": true,
      "learnFromHistory": true,
      "defectTriggering": true,
      "productionLike": true
    },
    "scenarios": [
      {
        "name": "standard_order",
        "percentage": 70
      },
      {
        "name": "express_shipping",
        "percentage": 20
      },
      {
        "name": "international",
        "percentage": 10
      }
    ]
  }'`}
                </pre>
              </div>

              {/* Custom Entity REST */}
              <div className="bg-purple-50 border border-purple-200 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Custom Entity (REST)</h4>
                <pre className="text-sm bg-white p-3 rounded overflow-x-auto">
{`curl -X POST http://localhost:3000/api/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "domain": "custom",
    "entity": "custom",
    "customEntity": "inventory",
    "count": 200,
    "generationPath": "llm",
    "context": "Warehouse inventory with seasonal items",
    "inlineSchema": {
      "type": "object",
      "properties": {
        "sku": {
          "type": "string",
          "pattern": "^[A-Z]{3}-[0-9]{6}$"
        },
        "product_name": {
          "type": "string"
        },
        "quantity": {
          "type": "integer",
          "minimum": 0,
          "maximum": 10000
        },
        "warehouse_location": {
          "type": "string",
          "enum": ["NYC-01", "LAX-02", "CHI-03", "DAL-04"]
        },
        "reorder_point": {
          "type": "integer"
        },
        "unit_cost": {
          "type": "number"
        },
        "last_restock_date": {
          "type": "string",
          "format": "date"
        },
        "expiry_date": {
          "type": "string",
          "format": "date"
        },
        "category": {
          "type": "string"
        }
      },
      "required": ["sku", "product_name", "quantity", "warehouse_location"]
    }
  }'`}
                </pre>
              </div>
            </CardContent>
          </Card>

          {/* Advanced Features */}
          <Card className="bg-white border-border-default">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-macys-red" />
                Advanced API Features
              </CardTitle>
              <CardDescription>Special parameters and optimization flags</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Defect Triggering Mode</h4>
                <pre className="text-sm bg-white p-3 rounded overflow-x-auto">
{`# Generate edge cases and anomalies for testing
grpcurl -plaintext -d '{
  "request_id": "defect-test",
  "domain": "ecommerce",
  "entity": "payment",
  "count": 100,
  "defect_triggering": true,
  "hints": ["edge_case", "anomaly", "boundary_values"],
  "context": "Generate payments with edge cases: negative amounts, huge values, special characters, null fields"
}' localhost:9091 testdata.v1.TestDataService/GenerateData`}
                </pre>
              </div>

              <div className="bg-indigo-50 border border-indigo-200 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Production-Like Distribution</h4>
                <pre className="text-sm bg-white p-3 rounded overflow-x-auto">
{`# Generate data matching production patterns
grpcurl -plaintext -d '{
  "request_id": "prod-like",
  "domain": "ecommerce",
  "entity": "order",
  "count": 1000,
  "production_like": true,
  "learn_from_history": true,
  "hints": ["realistic", "production_distribution"],
  "context": "Match our production order distribution: 60% mobile, 40% web, peak hours 12-2pm and 7-9pm"
}' localhost:9091 testdata.v1.TestDataService/GenerateData`}
                </pre>
              </div>

              <div className="bg-pink-50 border border-pink-200 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Multi-Scenario Testing</h4>
                <pre className="text-sm bg-white p-3 rounded overflow-x-auto">
{`# Complex scenario-based generation
grpcurl -plaintext -d '{
  "request_id": "scenario-test",
  "domain": "ecommerce",
  "entity": "user",
  "count": 1000,
  "hints": ["use_hybrid"],
  "scenarios": [
    {
      "name": "active_premium",
      "count": 200,
      "description": "Active premium subscribers",
      "overrides": {
        "subscription": "premium",
        "is_active": "true"
      }
    },
    {
      "name": "churned_users",
      "count": 150,
      "description": "Users who cancelled subscription",
      "overrides": {
        "subscription": "none",
        "churned_date": "2024-*"
      }
    },
    {
      "name": "trial_users",
      "count": 300,
      "description": "Users in trial period",
      "overrides": {
        "subscription": "trial",
        "trial_ends": "2024-12-*"
      }
    },
    {
      "name": "inactive_basic",
      "count": 350,
      "description": "Inactive basic tier users",
      "overrides": {
        "subscription": "basic",
        "last_login": "2024-01-*"
      }
    }
  ]
}' localhost:9091 testdata.v1.TestDataService/GenerateData`}
                </pre>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="examples" className="space-y-6">
          {/* Traditional Generation Example */}
          <Card className="bg-white border-border-default">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="h-5 w-5 text-blue-600" />
                Traditional Generation Example
              </CardTitle>
              <CardDescription>Fast, rule-based generation for consistent test data</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Request</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto">
{`{
  "domain": "ecommerce",
  "entity": "product",
  "count": 5,
  "generationPath": "traditional",
  "options": {
    "useCache": true,
    "productionLike": true
  }
}`}
                </pre>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Response</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto text-xs">
{`{
  "success": true,
  "recordCount": 5,
  "metadata": {
    "generation_path": "traditional",
    "generation_time_ms": 89,
    "coherence_score": 0.95
  },
  "data": [
    {
      "product_id": "PROD-SKU-001234",
      "name": "Wireless Bluetooth Headphones",
      "description": "High-quality wireless headphones with noise cancellation",
      "category": "Electronics",
      "price": 149.99,
      "stock_quantity": 250,
      "sku": "WH-BT-001234",
      "brand": "TechBrand",
      "is_active": true
    },
    {
      "product_id": "PROD-SKU-001235",
      "name": "Smart Watch Pro",
      "description": "Advanced fitness tracking and smartphone integration",
      "category": "Electronics",
      "price": 299.99,
      "stock_quantity": 150,
      "sku": "SW-PR-001235",
      "brand": "TechBrand",
      "is_active": true
    }
  ]
}`}
                </pre>
              </div>
            </CardContent>
          </Card>

          {/* LLM Generation Example */}
          <Card className="bg-white border-border-default">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-macys-red" />
                LLM Generation Example
              </CardTitle>
              <CardDescription>AI-powered creative generation with context understanding</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Request</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto">
{`{
  "domain": "ecommerce",
  "entity": "review",
  "count": 4,
  "generationPath": "llm",
  "context": "Generate diverse product reviews for a new iPhone 15 Pro. Include both positive experiences highlighting camera quality and battery life, and constructive criticism about price and learning curve. Make reviews feel authentic with specific use cases.",
  "scenarios": [
    { "name": "enthusiastic_photographer", "count": 1 },
    { "name": "business_professional", "count": 1 },
    { "name": "student_budget_conscious", "count": 1 },
    { "name": "tech_enthusiast", "count": 1 }
  ]
}`}
                </pre>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Response</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto text-xs">
{`{
  "success": true,
  "recordCount": 4,
  "metadata": {
    "generation_path": "llm",
    "llm_tokens_used": 2847,
    "generation_time_ms": 3421,
    "coherence_score": 0.98
  },
  "data": [
    {
      "review_id": "REV-PH-789012",
      "product_id": "IPHONE-15-PRO",
      "user_id": "USER-PHOTO-456",
      "rating": 5,
      "title": "Game-changer for mobile photography!",
      "comment": "As a wedding photographer, I'm blown away by the ProRAW capabilities. The 48MP main camera captures incredible detail, and the new 5x telephoto is perfect for candid shots. Battery easily lasts through a full day of shooting. The Action button is now my quick camera launcher. Worth every penny for professionals.",
      "verified_purchase": true,
      "helpful_count": 127,
      "scenario": "enthusiastic_photographer",
      "created_at": "2024-11-28T14:32:00Z"
    },
    {
      "review_id": "REV-BP-789013",
      "product_id": "IPHONE-15-PRO",
      "user_id": "USER-BIZ-789",
      "rating": 4,
      "title": "Excellent for productivity, steep price",
      "comment": "The A17 Pro chip handles multitasking brilliantly. I run Slack, Teams, and Excel simultaneously without hiccups. USB-C finally lets me use one cable for everything. Dynamic Island is surprisingly useful for call management. Docked one star for the price - hard to justify $1200 for corporate use.",
      "verified_purchase": true,
      "helpful_count": 89,
      "scenario": "business_professional",
      "created_at": "2024-11-25T09:15:00Z"
    }
  ]
}`}
                </pre>
              </div>
            </CardContent>
          </Card>

          {/* RAG Generation Example */}
          <Card className="bg-white border-border-default">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GitBranch className="h-5 w-5 text-green-600" />
                RAG Generation Example
              </CardTitle>
              <CardDescription>Pattern-based generation using historical data</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Request</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto">
{`{
  "domain": "ecommerce",
  "entity": "cart",
  "count": 3,
  "generationPath": "rag",
  "context": "Generate shopping carts similar to Black Friday patterns - multiple items, electronics focus, some abandoned carts",
  "options": {
    "learnFromHistory": true,
    "productionLike": true
  }
}`}
                </pre>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Response</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto text-xs">
{`{
  "success": true,
  "recordCount": 3,
  "metadata": {
    "generation_path": "rag",
    "generation_time_ms": 487,
    "coherence_score": 0.97,
    "patterns_retrieved": 15
  },
  "data": [
    {
      "cart_id": "CART-BF-234567",
      "user_id": "USER-DEAL-Hunter-123",
      "items": [
        {
          "product_id": "TV-SAMSUNG-65Q90",
          "name": "Samsung 65\" QLED 4K Smart TV",
          "quantity": 1,
          "price": 899.99,
          "original_price": 1499.99,
          "discount_percentage": 40
        },
        {
          "product_id": "SOUND-BOSE-700",
          "name": "Bose Soundbar 700",
          "quantity": 1,
          "price": 449.99,
          "original_price": 799.99,
          "discount_percentage": 44
        },
        {
          "product_id": "HDMI-CABLE-3PK",
          "name": "Premium HDMI 2.1 Cables (3-pack)",
          "quantity": 2,
          "price": 19.99,
          "original_price": 39.99,
          "discount_percentage": 50
        }
      ],
      "subtotal": 1389.96,
      "savings": 950.01,
      "status": "active",
      "created_at": "2024-11-24T02:45:00Z",
      "updated_at": "2024-11-24T02:58:00Z",
      "session_id": "BF-SESS-2024-98765"
    }
  ]
}`}
                </pre>
              </div>
            </CardContent>
          </Card>

          {/* Hybrid Generation Example */}
          <Card className="bg-white border-border-default">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Layers className="h-5 w-5 text-orange-600" />
                Hybrid Generation Example
              </CardTitle>
              <CardDescription>Intelligent combination of multiple generation strategies</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Request</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto">
{`{
  "domain": "ecommerce",
  "entity": "order",
  "count": 5,
  "generationPath": "hybrid",
  "context": "Generate realistic order data for stress testing. Mix of order values, statuses, and customer types. Include edge cases.",
  "options": {
    "useCache": true,
    "learnFromHistory": true,
    "defectTriggering": true,
    "productionLike": true
  },
  "scenarios": [
    { "name": "standard_checkout", "count": 2 },
    { "name": "guest_checkout", "count": 1 },
    { "name": "high_value_vip", "count": 1 },
    { "name": "edge_case_order", "count": 1 }
  ]
}`}
                </pre>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Response</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto text-xs">
{`{
  "success": true,
  "recordCount": 5,
  "metadata": {
    "generation_path": "hybrid",
    "generation_time_ms": 1256,
    "coherence_score": 0.96,
    "strategies_used": ["traditional", "llm", "rag"],
    "scenario_counts": {
      "standard_checkout": 2,
      "guest_checkout": 1,
      "high_value_vip": 1,
      "edge_case_order": 1
    }
  },
  "data": [
    {
      "order_id": "ORD-2024-STD-445566",
      "customer_id": "CUST-REG-789123",
      "status": "processing",
      "items": [
        {
          "product_id": "SHOES-NIKE-AF1",
          "name": "Nike Air Force 1",
          "quantity": 1,
          "price": 110.00
        },
        {
          "product_id": "SHIRT-POLO-BLU",
          "name": "Polo Ralph Lauren Blue Shirt",
          "quantity": 2,
          "price": 89.50
        }
      ],
      "subtotal": 289.00,
      "tax": 24.57,
      "shipping": 9.99,
      "total": 323.56,
      "payment_method": "credit_card",
      "shipping_address": {
        "street": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip": "10001"
      },
      "scenario": "standard_checkout",
      "created_at": "2024-12-15T10:30:00Z"
    },
    {
      "order_id": "ORD-2024-EDGE-999999",
      "customer_id": "CUST-TEST-000001",
      "status": "pending_review",
      "items": [
        {
          "product_id": "TEST-EDGE-CASE",
          "name": "Product with Unicode: café ñoño 好的 🎉",
          "quantity": 9999,
          "price": 0.01
        }
      ],
      "subtotal": 99.99,
      "tax": -0.01,
      "shipping": 999999.99,
      "total": 1000099.97,
      "payment_method": "unknown",
      "notes": "Edge case: extreme values for stress testing",
      "scenario": "edge_case_order",
      "created_at": "2024-12-15T00:00:00Z"
    }
  ]
}`}
                </pre>
              </div>
            </CardContent>
          </Card>

          {/* Custom Entity Example */}
          <Card className="bg-white border-border-default">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5 text-purple-600" />
                Custom Entity with Schema Example
              </CardTitle>
              <CardDescription>Define your own entity structure with JSON Schema</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Request - Loyalty Points System</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto">
{`{
  "domain": "custom",
  "entity": "custom",
  "customEntity": "loyalty_transaction",
  "count": 3,
  "generationPath": "llm",
  "context": "Generate loyalty point transactions for a retail rewards program. Include purchases, redemptions, and bonus point events.",
  "inlineSchema": {
    "type": "object",
    "properties": {
      "transaction_id": {
        "type": "string",
        "pattern": "^LYL-[0-9]{10}$"
      },
      "member_id": {
        "type": "string",
        "pattern": "^MEM-[A-Z0-9]{6}$"
      },
      "transaction_type": {
        "type": "string",
        "enum": ["earn_purchase", "earn_bonus", "redeem_reward", "expire", "adjust"]
      },
      "points": {
        "type": "integer",
        "minimum": -10000,
        "maximum": 10000
      },
      "balance_after": {
        "type": "integer",
        "minimum": 0
      },
      "description": {
        "type": "string",
        "maxLength": 200
      },
      "reference_order_id": {
        "type": "string"
      },
      "tier_multiplier": {
        "type": "number",
        "minimum": 1.0,
        "maximum": 3.0
      },
      "transaction_date": {
        "type": "string",
        "format": "date-time"
      },
      "expiry_date": {
        "type": "string",
        "format": "date"
      }
    },
    "required": ["transaction_id", "member_id", "transaction_type", "points", "balance_after", "transaction_date"]
  }
}`}
                </pre>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Response</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto text-xs">
{`{
  "success": true,
  "recordCount": 3,
  "metadata": {
    "generation_path": "llm",
    "llm_tokens_used": 1523,
    "generation_time_ms": 2189,
    "coherence_score": 0.97
  },
  "data": [
    {
      "transaction_id": "LYL-2024121501",
      "member_id": "MEM-PLT789",
      "transaction_type": "earn_purchase",
      "points": 458,
      "balance_after": 12750,
      "description": "Purchase at Macy's Herald Square - Double points Tuesday",
      "reference_order_id": "ORD-2024-998877",
      "tier_multiplier": 2.0,
      "transaction_date": "2024-12-15T14:23:00Z",
      "expiry_date": "2025-12-31"
    },
    {
      "transaction_id": "LYL-2024121502",
      "member_id": "MEM-GLD456",
      "transaction_type": "redeem_reward",
      "points": -5000,
      "balance_after": 3200,
      "description": "$50 Macy's Gift Card Redemption",
      "tier_multiplier": 1.0,
      "transaction_date": "2024-12-15T15:45:00Z"
    },
    {
      "transaction_id": "LYL-2024121503",
      "member_id": "MEM-SLV123",
      "transaction_type": "earn_bonus",
      "points": 1000,
      "balance_after": 2500,
      "description": "Birthday Month Bonus Points",
      "tier_multiplier": 1.0,
      "transaction_date": "2024-12-15T00:00:00Z",
      "expiry_date": "2025-01-15"
    }
  ]
}`}
                </pre>
              </div>
            </CardContent>
          </Card>

          {/* Complex Multi-Entity Example */}
          <Card className="bg-white border-border-default">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-600" />
                Advanced: Multi-Entity Relationship Example
              </CardTitle>
              <CardDescription>Generate interconnected data with relationships</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                <p className="text-sm text-yellow-900 mb-2">
                  <strong>Pro Tip:</strong> Generate related entities sequentially, using IDs from previous responses
                  to maintain referential integrity across your test dataset.
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Step 1: Generate User</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto">
{`// First, generate a user
{
  "entity": "user",
  "count": 1,
  "generationPath": "llm",
  "context": "Premium customer with purchase history"
}
// Response: { "user_id": "USER-PREM-123", ... }`}
                </pre>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Step 2: Generate Order with User Reference</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto">
{`// Then, generate order for that user
{
  "entity": "order",
  "count": 1,
  "generationPath": "llm",
  "context": "Order for user USER-PREM-123",
  "scenarios": [{
    "name": "user_order",
    "overrides": {
      "customer_id": "USER-PREM-123"
    }
  }]
}
// Response: { "order_id": "ORD-2024-7789", "customer_id": "USER-PREM-123", ... }`}
                </pre>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Step 3: Generate Payment for Order</h4>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto">
{`// Finally, generate payment for that order
{
  "entity": "payment",
  "count": 1,
  "generationPath": "llm",
  "context": "Payment for order ORD-2024-7789",
  "scenarios": [{
    "name": "order_payment",
    "overrides": {
      "order_id": "ORD-2024-7789",
      "amount": 323.56
    }
  }]
}`}
                </pre>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}