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
  inlineSchema?: string;
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
  scenarioCounts?: Record<string, number>;
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