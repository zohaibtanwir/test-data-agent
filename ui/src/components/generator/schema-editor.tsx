'use client';

import { useGeneratorStore } from '@/stores/generator-store';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Code2, AlertCircle } from 'lucide-react';
import { useState } from 'react';

export function SchemaEditor() {
  const { inlineSchema, setInlineSchema } = useGeneratorStore();
  const [error, setError] = useState<string | null>(null);

  const validateJSON = (value: string) => {
    if (!value.trim()) {
      setError(null);
      return true;
    }

    try {
      JSON.parse(value);
      setError(null);
      return true;
    } catch (e) {
      setError('Invalid JSON format');
      return false;
    }
  };

  const handleChange = (value: string) => {
    setInlineSchema(value);
    if (value.trim()) {
      validateJSON(value);
    } else {
      setError(null);
    }
  };

  const exampleSchema = `{
  "type": "object",
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "name": { "type": "string", "minLength": 2 },
    "email": { "type": "string", "format": "email" },
    "age": { "type": "integer", "minimum": 18, "maximum": 100 },
    "created_at": { "type": "string", "format": "date-time" }
  },
  "required": ["id", "name", "email"]
}`;

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <Code2 className="h-4 w-4 text-accent" />
          <Label htmlFor="schema">Inline Schema (Optional)</Label>
        </div>
        <p className="text-sm text-gray-500">
          Provide a JSON schema to guide data generation. Leave empty to use default schemas.
        </p>
      </div>

      <Textarea
        id="schema"
        value={inlineSchema}
        onChange={(e) => handleChange(e.target.value)}
        placeholder={exampleSchema}
        className="font-mono text-sm h-64"
        spellCheck={false}
      />

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {!error && inlineSchema && (
        <Alert>
          <Code2 className="h-4 w-4" />
          <AlertDescription>
            Schema validated successfully. This will override default schemas for the selected entity.
          </AlertDescription>
        </Alert>
      )}

      <div className="p-4 bg-gray-900 rounded-lg border border-gray-800">
        <h4 className="text-sm font-medium mb-2">Schema Tips:</h4>
        <ul className="text-xs text-gray-400 space-y-1">
          <li>• Use JSON Schema draft-07 format</li>
          <li>• Specify data types, formats, and constraints</li>
          <li>• Include "required" array for mandatory fields</li>
          <li>• Use "enum" for fixed value sets</li>
          <li>• Add "pattern" for regex validation</li>
        </ul>
      </div>
    </div>
  );
}