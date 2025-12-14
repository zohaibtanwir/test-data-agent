'use client';

import { useState } from 'react';
import { useGeneratorStore } from '@/stores/generator-store';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { ScenarioManager } from './scenario-manager';
import { SchemaEditor } from './schema-editor';
import { api } from '@/lib/api-client';
import { Sparkles, Loader2, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

const domains = [
  { value: 'ecommerce', label: 'E-commerce' },
  { value: 'financial', label: 'Financial' },
  { value: 'social_media', label: 'Social Media' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'education', label: 'Education' },
  { value: 'logistics', label: 'Logistics' },
];

const entities = [
  { value: 'cart', label: 'Cart' },
  { value: 'order', label: 'Order' },
  { value: 'product', label: 'Product' },
  { value: 'user', label: 'User' },
  { value: 'payment', label: 'Payment' },
  { value: 'review', label: 'Review' },
  { value: 'custom', label: 'Custom Entity...' },
];

const outputFormats = [
  { value: 'JSON', label: 'JSON' },
  { value: 'CSV', label: 'CSV' },
  { value: 'SQL', label: 'SQL' },
  { value: 'YAML', label: 'YAML' },
  { value: 'XML', label: 'XML' },
];

const generationPaths = [
  {
    value: 'auto',
    label: 'Auto',
    description: 'System decides best approach'
  },
  {
    value: 'traditional',
    label: 'Traditional',
    description: 'Fast rule-based generation'
  },
  {
    value: 'llm',
    label: 'LLM (AI)',
    description: 'Creative AI-generated data'
  },
  {
    value: 'rag',
    label: 'RAG',
    description: 'Pattern-based with context'
  },
  {
    value: 'hybrid',
    label: 'Hybrid',
    description: 'Combined approach'
  },
];

export function GeneratorForm() {
  const store = useGeneratorStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [customEntity, setCustomEntity] = useState('');
  const [customSchema, setCustomSchema] = useState('');
  const [schemaError, setSchemaError] = useState<string | null>(null);

  const validateJsonSchema = (schema: string): boolean => {
    if (!schema.trim()) {
      setSchemaError('Schema is required for custom entities');
      return false;
    }
    try {
      const parsed = JSON.parse(schema);
      if (typeof parsed !== 'object' || parsed === null) {
        setSchemaError('Schema must be a valid JSON object');
        return false;
      }
      if (!parsed.properties || typeof parsed.properties !== 'object') {
        setSchemaError('Schema must have a "properties" field');
        return false;
      }
      setSchemaError(null);
      return true;
    } catch (e) {
      setSchemaError('Invalid JSON: ' + (e as Error).message);
      return false;
    }
  };

  const handleGenerate = async () => {
    // Validate custom entity if selected
    if (store.entity === 'custom') {
      if (!customEntity.trim()) {
        setLocalError('Please provide a custom entity name');
        return;
      }
      if (!validateJsonSchema(customSchema)) {
        setLocalError('Please provide a valid JSON schema for the custom entity');
        return;
      }
    }

    setIsGenerating(true);
    setLocalError(null);
    store.setError(null);
    store.setResult(null);

    try {
      const requestBody = store.getRequestBody();
      // Use custom entity name if custom is selected
      if (store.entity === 'custom' && customEntity) {
        requestBody.entity = customEntity;
      }
      const result = await api.generate.data(requestBody);
      store.setResult(result);
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to generate data';
      setLocalError(errorMessage);
      store.setError(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const isValid = store.domain && store.entity && store.count > 0 && store.count <= 1000 &&
    (store.entity !== 'custom' || (customEntity.trim() && customSchema.trim() && !schemaError));

  return (
    <div className="space-y-6">
      <Card className="bg-white border-border-default shadow-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-macys-black">
            <Sparkles className="text-macys-red" />
            Test Data Generator
          </CardTitle>
          <CardDescription className="text-macys-gray">
            Configure your test data generation parameters
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Basic Configuration */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="domain">Domain</Label>
              <Select value={store.domain} onValueChange={store.setDomain}>
                <SelectTrigger id="domain">
                  <SelectValue placeholder="Select domain" />
                </SelectTrigger>
                <SelectContent>
                  {domains.map((domain) => (
                    <SelectItem key={domain.value} value={domain.value}>
                      {domain.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="entity">Entity</Label>
              <Select value={store.entity} onValueChange={(value) => {
                store.setEntity(value);
                if (value !== 'custom') {
                  setCustomEntity('');
                  setCustomSchema('');
                  store.setInlineSchema('');
                }
              }}>
                <SelectTrigger id="entity">
                  <SelectValue placeholder="Select entity" />
                </SelectTrigger>
                <SelectContent>
                  {entities.map((entity) => (
                    <SelectItem key={entity.value} value={entity.value}>
                      {entity.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Custom Entity Fields */}
          {store.entity === 'custom' && (
            <div className="space-y-4 p-4 bg-bg-secondary rounded-lg border border-border-default">
              <div className="space-y-2">
                <Label htmlFor="customEntity">Custom Entity Name</Label>
                <Input
                  id="customEntity"
                  value={customEntity}
                  onChange={(e) => setCustomEntity(e.target.value)}
                  placeholder="e.g., invoice, subscription, notification"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="customSchema" className="flex items-center gap-2">
                  <span>JSON Schema</span>
                  <Badge variant="outline" className="text-xs">Required</Badge>
                </Label>
                <Textarea
                  id="customSchema"
                  value={customSchema}
                  onChange={(e) => {
                    setCustomSchema(e.target.value);
                    if (e.target.value.trim()) {
                      validateJsonSchema(e.target.value);
                    }
                    store.setInlineSchema(e.target.value);
                  }}
                  placeholder={`{
  "type": "object",
  "properties": {
    "id": { "type": "string" },
    "name": { "type": "string" },
    "amount": { "type": "number" }
  },
  "required": ["id", "name"]
}`}
                  className="font-mono h-32"
                />
                {schemaError && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{schemaError}</AlertDescription>
                  </Alert>
                )}
              </div>
            </div>
          )}

          {/* Generation Path Selector - Prominent Position */}
          <div className="space-y-2">
            <Label htmlFor="path" className="flex items-center gap-2">
              <span>Generation Path</span>
              <Badge variant="outline" className="text-xs">
                Choose how to generate data
              </Badge>
            </Label>
            <Select value={store.generationPath} onValueChange={(value: any) => store.setGenerationPath(value)}>
              <SelectTrigger id="path" className="bg-bg-tertiary border-border-default">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {generationPaths.map((path) => (
                  <SelectItem key={path.value} value={path.value}>
                    <div>
                      <div className="font-medium">{path.label}</div>
                      <div className="text-xs text-gray-500">{path.description}</div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Count Slider */}
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label htmlFor="count">Number of Records</Label>
              <Badge variant="secondary" className="bg-macys-red/10 text-macys-red border-macys-red/20">{store.count}</Badge>
            </div>
            <Slider
              id="count"
              min={1}
              max={1000}
              step={1}
              value={[store.count]}
              onValueChange={([value]) => store.setCount(value)}
              className="w-full [&_[role=slider]]:bg-macys-red [&_[role=slider]]:border-macys-red [&_>span:first-child]:bg-macys-red"
            />
            <div className="flex justify-between text-xs text-macys-gray">
              <span>1</span>
              <span>500</span>
              <span>1000</span>
            </div>
          </div>

          {/* Context */}
          <div className="space-y-2">
            <Label htmlFor="context">Context (Optional)</Label>
            <Textarea
              id="context"
              value={store.context}
              onChange={(e) => store.setContext(e.target.value)}
              placeholder="Provide additional context for more realistic data generation..."
              className="h-24"
            />
          </div>

          {/* Advanced Options Tabs */}
          <Tabs defaultValue="options" className="w-full">
            <TabsList className="grid w-full grid-cols-4 bg-bg-secondary">
              <TabsTrigger value="options">Options</TabsTrigger>
              <TabsTrigger value="scenarios">Scenarios</TabsTrigger>
              <TabsTrigger value="schema">Schema</TabsTrigger>
              <TabsTrigger value="output">Output</TabsTrigger>
            </TabsList>

            <TabsContent value="options" className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="cache">Use Cache</Label>
                    <p className="text-xs text-gray-500">Speed up generation with cached patterns</p>
                  </div>
                  <Switch
                    id="cache"
                    checked={store.options.useCache}
                    onCheckedChange={() => store.toggleOption('useCache')}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="history">Learn from History</Label>
                    <p className="text-xs text-gray-500">Use previous generation patterns</p>
                  </div>
                  <Switch
                    id="history"
                    checked={store.options.learnFromHistory}
                    onCheckedChange={() => store.toggleOption('learnFromHistory')}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="defects">Defect Triggering</Label>
                    <p className="text-xs text-gray-500">Include edge cases and anomalies</p>
                  </div>
                  <Switch
                    id="defects"
                    checked={store.options.defectTriggering}
                    onCheckedChange={() => store.toggleOption('defectTriggering')}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="production">Production-like</Label>
                    <p className="text-xs text-gray-500">Generate realistic production data</p>
                  </div>
                  <Switch
                    id="production"
                    checked={store.options.productionLike}
                    onCheckedChange={() => store.toggleOption('productionLike')}
                  />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="scenarios">
              <ScenarioManager />
            </TabsContent>

            <TabsContent value="schema">
              <SchemaEditor />
            </TabsContent>

            <TabsContent value="output" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="format">Output Format</Label>
                <Select value={store.outputFormat} onValueChange={(value: any) => store.setOutputFormat(value)}>
                  <SelectTrigger id="format">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {outputFormats.map((format) => (
                      <SelectItem key={format.value} value={format.value}>
                        {format.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="path">Generation Path</Label>
                <Select value={store.generationPath} onValueChange={(value: any) => store.setGenerationPath(value)}>
                  <SelectTrigger id="path">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {generationPaths.map((path) => (
                      <SelectItem key={path.value} value={path.value}>
                        {path.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>
          </Tabs>

          {/* Error Alert */}
          {localError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{localError}</AlertDescription>
            </Alert>
          )}

          {/* Generate Button */}
          <div className="flex justify-end">
            <Button
              onClick={handleGenerate}
              disabled={!isValid || isGenerating}
              size="lg"
              className="min-w-[150px] bg-macys-red hover:bg-macys-red-dark text-white"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Generate Data
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}