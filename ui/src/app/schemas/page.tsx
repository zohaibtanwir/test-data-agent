'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Database,
  Code,
  Copy,
  Check,
  ChevronRight,
  FileJson,
  Package,
  ShoppingCart,
  CreditCard,
  User,
  Star,
  AlertCircle
} from 'lucide-react';
import { api } from '@/lib/api-client';

interface SchemaField {
  name: string;
  type: string;
  required?: boolean;
  description?: string;
  example?: any;
}

interface Schema {
  name: string;
  domain: string;
  description: string;
  fields: SchemaField[];
}

// Predefined schemas data
const predefinedSchemas: Schema[] = [
  {
    name: 'cart',
    domain: 'ecommerce',
    description: 'Shopping cart with items and metadata',
    fields: [
      { name: 'cart_id', type: 'string', required: true, description: 'Unique cart identifier', example: 'CART-123456' },
      { name: 'user_id', type: 'string', required: true, description: 'User who owns the cart', example: 'USER-789' },
      { name: 'items', type: 'array', required: true, description: 'Array of cart items' },
      { name: 'items[].product_id', type: 'string', required: true, description: 'Product identifier', example: 'PROD-001' },
      { name: 'items[].quantity', type: 'integer', required: true, description: 'Item quantity', example: 2 },
      { name: 'items[].price', type: 'float', required: true, description: 'Item price', example: 29.99 },
      { name: 'total', type: 'float', required: true, description: 'Cart total amount', example: 59.98 },
      { name: 'created_at', type: 'datetime', required: true, description: 'Creation timestamp' },
      { name: 'updated_at', type: 'datetime', required: false, description: 'Last update timestamp' }
    ]
  },
  {
    name: 'order',
    domain: 'ecommerce',
    description: 'Purchase order with billing and shipping details',
    fields: [
      { name: 'order_id', type: 'string', required: true, description: 'Unique order identifier', example: 'ORD-2024-001' },
      { name: 'customer_id', type: 'string', required: true, description: 'Customer identifier', example: 'CUST-456' },
      { name: 'status', type: 'enum', required: true, description: 'Order status', example: 'completed' },
      { name: 'items', type: 'array', required: true, description: 'Ordered items' },
      { name: 'subtotal', type: 'float', required: true, description: 'Subtotal before tax', example: 149.99 },
      { name: 'tax', type: 'float', required: true, description: 'Tax amount', example: 12.75 },
      { name: 'shipping', type: 'float', required: true, description: 'Shipping cost', example: 9.99 },
      { name: 'total', type: 'float', required: true, description: 'Total amount', example: 172.73 },
      { name: 'shipping_address', type: 'object', required: true, description: 'Shipping address' },
      { name: 'billing_address', type: 'object', required: false, description: 'Billing address' },
      { name: 'created_at', type: 'datetime', required: true, description: 'Order creation time' }
    ]
  },
  {
    name: 'product',
    domain: 'ecommerce',
    description: 'Product catalog information',
    fields: [
      { name: 'product_id', type: 'string', required: true, description: 'Unique product identifier', example: 'PROD-SKU-123' },
      { name: 'name', type: 'string', required: true, description: 'Product name', example: 'Wireless Headphones' },
      { name: 'description', type: 'string', required: true, description: 'Product description' },
      { name: 'category', type: 'string', required: true, description: 'Product category', example: 'Electronics' },
      { name: 'price', type: 'float', required: true, description: 'Product price', example: 79.99 },
      { name: 'cost', type: 'float', required: false, description: 'Product cost', example: 35.00 },
      { name: 'stock_quantity', type: 'integer', required: true, description: 'Available stock', example: 150 },
      { name: 'sku', type: 'string', required: true, description: 'Stock keeping unit', example: 'WH-BT-001' },
      { name: 'brand', type: 'string', required: false, description: 'Product brand', example: 'TechBrand' },
      { name: 'weight', type: 'float', required: false, description: 'Product weight (kg)', example: 0.25 },
      { name: 'dimensions', type: 'object', required: false, description: 'Product dimensions' },
      { name: 'images', type: 'array', required: false, description: 'Product images' },
      { name: 'is_active', type: 'boolean', required: true, description: 'Product availability', example: true }
    ]
  },
  {
    name: 'user',
    domain: 'ecommerce',
    description: 'User account and profile information',
    fields: [
      { name: 'user_id', type: 'string', required: true, description: 'Unique user identifier', example: 'USER-ABC123' },
      { name: 'email', type: 'email', required: true, description: 'User email address', example: 'john.doe@example.com' },
      { name: 'username', type: 'string', required: false, description: 'Username', example: 'johndoe' },
      { name: 'first_name', type: 'string', required: true, description: 'First name', example: 'John' },
      { name: 'last_name', type: 'string', required: true, description: 'Last name', example: 'Doe' },
      { name: 'phone', type: 'phone', required: false, description: 'Phone number', example: '+1-555-0123' },
      { name: 'date_of_birth', type: 'date', required: false, description: 'Birth date', example: '1990-01-15' },
      { name: 'address', type: 'object', required: false, description: 'User address' },
      { name: 'preferences', type: 'object', required: false, description: 'User preferences' },
      { name: 'created_at', type: 'datetime', required: true, description: 'Account creation time' },
      { name: 'last_login', type: 'datetime', required: false, description: 'Last login time' },
      { name: 'is_verified', type: 'boolean', required: true, description: 'Email verification status', example: true }
    ]
  },
  {
    name: 'payment',
    domain: 'ecommerce',
    description: 'Payment transaction details',
    fields: [
      { name: 'payment_id', type: 'string', required: true, description: 'Payment identifier', example: 'PAY-789XYZ' },
      { name: 'order_id', type: 'string', required: true, description: 'Associated order', example: 'ORD-2024-001' },
      { name: 'amount', type: 'float', required: true, description: 'Payment amount', example: 172.73 },
      { name: 'currency', type: 'string', required: true, description: 'Currency code', example: 'USD' },
      { name: 'method', type: 'enum', required: true, description: 'Payment method', example: 'credit_card' },
      { name: 'status', type: 'enum', required: true, description: 'Payment status', example: 'approved' },
      { name: 'card_last_four', type: 'string', required: false, description: 'Last 4 card digits', example: '4242' },
      { name: 'processor', type: 'string', required: false, description: 'Payment processor', example: 'stripe' },
      { name: 'transaction_id', type: 'string', required: false, description: 'Processor transaction ID' },
      { name: 'processed_at', type: 'datetime', required: true, description: 'Processing timestamp' }
    ]
  },
  {
    name: 'review',
    domain: 'ecommerce',
    description: 'Product review and rating',
    fields: [
      { name: 'review_id', type: 'string', required: true, description: 'Review identifier', example: 'REV-456789' },
      { name: 'product_id', type: 'string', required: true, description: 'Reviewed product', example: 'PROD-001' },
      { name: 'user_id', type: 'string', required: true, description: 'Reviewer', example: 'USER-123' },
      { name: 'rating', type: 'integer', required: true, description: 'Rating (1-5 stars)', example: 5 },
      { name: 'title', type: 'string', required: false, description: 'Review title', example: 'Great product!' },
      { name: 'comment', type: 'string', required: true, description: 'Review text' },
      { name: 'verified_purchase', type: 'boolean', required: true, description: 'Purchase verification', example: true },
      { name: 'helpful_count', type: 'integer', required: false, description: 'Helpful votes', example: 24 },
      { name: 'images', type: 'array', required: false, description: 'Review images' },
      { name: 'created_at', type: 'datetime', required: true, description: 'Review date' }
    ]
  }
];

const getIconForEntity = (name: string) => {
  switch (name) {
    case 'cart': return <ShoppingCart className="h-5 w-5" />;
    case 'order': return <Package className="h-5 w-5" />;
    case 'product': return <Database className="h-5 w-5" />;
    case 'user': return <User className="h-5 w-5" />;
    case 'payment': return <CreditCard className="h-5 w-5" />;
    case 'review': return <Star className="h-5 w-5" />;
    default: return <FileJson className="h-5 w-5" />;
  }
};

const getTypeColor = (type: string) => {
  switch (type) {
    case 'string': return 'bg-blue-100 text-blue-700';
    case 'integer': return 'bg-green-100 text-green-700';
    case 'float': return 'bg-purple-100 text-purple-700';
    case 'boolean': return 'bg-yellow-100 text-yellow-700';
    case 'array': return 'bg-orange-100 text-orange-700';
    case 'object': return 'bg-pink-100 text-pink-700';
    case 'datetime':
    case 'date': return 'bg-gray-100 text-gray-700';
    case 'enum': return 'bg-indigo-100 text-indigo-700';
    case 'email':
    case 'phone': return 'bg-cyan-100 text-cyan-700';
    default: return 'bg-gray-100 text-gray-700';
  }
};

export default function SchemasPage() {
  const [selectedSchema, setSelectedSchema] = useState<Schema>(predefinedSchemas[0]);
  const [copiedSchema, setCopiedSchema] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  const handleCopySchema = (schemaName: string, content: string) => {
    navigator.clipboard.writeText(content);
    setCopiedSchema(schemaName);
    setTimeout(() => setCopiedSchema(null), 2000);
  };

  const generateSchemaJson = (schema: Schema) => {
    const schemaObj: any = {
      name: schema.name,
      domain: schema.domain,
      fields: {}
    };

    schema.fields.forEach(field => {
      if (!field.name.includes('[].') && !field.name.includes('.')) {
        schemaObj.fields[field.name] = {
          type: field.type,
          required: field.required || false,
          description: field.description
        };
        if (field.example !== undefined) {
          schemaObj.fields[field.name].example = field.example;
        }
      }
    });

    return JSON.stringify(schemaObj, null, 2);
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Schema Library</h1>
        <p className="text-gray-500">Explore and use predefined schemas for test data generation</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Schema List */}
        <div className="lg:col-span-1">
          <Card className="bg-white border-border-default">
            <CardHeader>
              <CardTitle className="text-lg">Available Schemas</CardTitle>
              <CardDescription>Select a schema to view details</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <div className="space-y-1">
                {predefinedSchemas.map(schema => (
                  <button
                    key={schema.name}
                    onClick={() => {
                      setSelectedSchema(schema);
                      setActiveTab('overview');
                    }}
                    className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-colors ${
                      selectedSchema.name === schema.name
                        ? 'bg-macys-red/10 text-macys-red border-l-2 border-macys-red'
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    {getIconForEntity(schema.name)}
                    <div className="flex-1">
                      <div className="font-medium capitalize">{schema.name}</div>
                      <div className="text-xs text-gray-500">{schema.fields.length} fields</div>
                    </div>
                    {selectedSchema.name === schema.name && (
                      <ChevronRight className="h-4 w-4" />
                    )}
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Schema Details */}
        <div className="lg:col-span-3">
          <Card className="bg-white border-border-default">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {getIconForEntity(selectedSchema.name)}
                  <div>
                    <CardTitle className="capitalize">{selectedSchema.name} Schema</CardTitle>
                    <CardDescription>{selectedSchema.description}</CardDescription>
                  </div>
                </div>
                <Badge variant="outline" className="capitalize">
                  {selectedSchema.domain}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="bg-bg-secondary mb-4">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="fields">Fields</TabsTrigger>
                  <TabsTrigger value="json">JSON Schema</TabsTrigger>
                  <TabsTrigger value="example">Example Data</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="text-xs text-gray-500 mb-1">Total Fields</div>
                      <div className="text-2xl font-bold text-gray-900">
                        {selectedSchema.fields.filter(f => !f.name.includes('[].')).length}
                      </div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="text-xs text-gray-500 mb-1">Required</div>
                      <div className="text-2xl font-bold text-macys-red">
                        {selectedSchema.fields.filter(f => f.required && !f.name.includes('[].')).length}
                      </div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="text-xs text-gray-500 mb-1">Optional</div>
                      <div className="text-2xl font-bold text-blue-600">
                        {selectedSchema.fields.filter(f => !f.required && !f.name.includes('[].')).length}
                      </div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="text-xs text-gray-500 mb-1">Nested</div>
                      <div className="text-2xl font-bold text-purple-600">
                        {selectedSchema.fields.filter(f => f.type === 'array' || f.type === 'object').length}
                      </div>
                    </div>
                  </div>

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                      <div className="text-sm text-blue-900">
                        <p className="font-semibold mb-1">Usage Tip</p>
                        <p>
                          Select this schema in the Generator form by choosing <strong>{selectedSchema.name}</strong> from
                          the Entity dropdown. The schema will be automatically applied to generate properly structured data.
                        </p>
                      </div>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="fields" className="space-y-2">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2 px-3">Field Name</th>
                          <th className="text-left py-2 px-3">Type</th>
                          <th className="text-left py-2 px-3">Required</th>
                          <th className="text-left py-2 px-3">Description</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedSchema.fields.map((field, index) => (
                          <tr key={index} className="border-b hover:bg-gray-50">
                            <td className="py-2 px-3 font-mono text-xs">
                              {field.name}
                            </td>
                            <td className="py-2 px-3">
                              <Badge variant="secondary" className={getTypeColor(field.type)}>
                                {field.type}
                              </Badge>
                            </td>
                            <td className="py-2 px-3">
                              {field.required ? (
                                <Badge variant="outline" className="text-macys-red border-macys-red">
                                  Yes
                                </Badge>
                              ) : (
                                <Badge variant="outline">No</Badge>
                              )}
                            </td>
                            <td className="py-2 px-3 text-gray-600">
                              {field.description}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </TabsContent>

                <TabsContent value="json" className="space-y-4">
                  <div className="flex justify-end">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleCopySchema(selectedSchema.name, generateSchemaJson(selectedSchema))}
                    >
                      {copiedSchema === selectedSchema.name ? (
                        <>
                          <Check className="h-4 w-4 mr-2" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="h-4 w-4 mr-2" />
                          Copy Schema
                        </>
                      )}
                    </Button>
                  </div>
                  <pre className="bg-gray-50 border border-gray-200 rounded-lg p-4 overflow-x-auto text-sm">
                    <code>{generateSchemaJson(selectedSchema)}</code>
                  </pre>
                </TabsContent>

                <TabsContent value="example" className="space-y-4">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <pre className="overflow-x-auto text-sm">
                      <code>
{JSON.stringify({
  [selectedSchema.name]: selectedSchema.fields
    .filter(f => !f.name.includes('[].'))
    .reduce((obj, field) => {
      if (field.example !== undefined) {
        obj[field.name] = field.example;
      } else {
        // Provide default examples based on type
        switch (field.type) {
          case 'string': obj[field.name] = 'example-string'; break;
          case 'integer': obj[field.name] = 123; break;
          case 'float': obj[field.name] = 99.99; break;
          case 'boolean': obj[field.name] = true; break;
          case 'datetime': obj[field.name] = '2024-01-15T10:30:00Z'; break;
          case 'date': obj[field.name] = '2024-01-15'; break;
          case 'email': obj[field.name] = 'user@example.com'; break;
          case 'phone': obj[field.name] = '+1-555-0123'; break;
          case 'array': obj[field.name] = []; break;
          case 'object': obj[field.name] = {}; break;
          case 'enum': obj[field.name] = 'option1'; break;
          default: obj[field.name] = null;
        }
      }
      return obj;
    }, {} as any)
}, null, 2)}
                      </code>
                    </pre>
                  </div>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-sm text-yellow-900">
                      This is a sample structure. Actual generated data will have realistic values based on your
                      selected generation path and context.
                    </p>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}