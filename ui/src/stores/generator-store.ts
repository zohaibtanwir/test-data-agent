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
  inlineSchema: string;

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
  setInlineSchema: (schema: string) => void;

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
  scenarios: [],
  outputFormat: 'JSON' as OutputFormat,
  options: {
    useCache: false,
    learnFromHistory: false,
    defectTriggering: false,
    productionLike: false,
  },
  generationPath: 'auto' as GenerationPath,
  inlineSchema: '',
  result: null,
  isLoading: false,
  error: null,
};

export const useGeneratorStore = create<GeneratorState>((set, get) => ({
  ...initialState,

  setDomain: (domain) => set({ domain }),
  setEntity: (entity) => set({ entity }),
  setCount: (count) => set({ count }),
  setContext: (context) => set({ context }),
  setOutputFormat: (outputFormat) => set({ outputFormat }),
  setGenerationPath: (generationPath) => set({ generationPath }),
  setInlineSchema: (inlineSchema) => set({ inlineSchema }),

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

    // Add hints based on generation path
    if (state.generationPath === 'llm') {
      hints.push('use_llm', 'ai_generated', 'creative');
    } else if (state.generationPath === 'rag') {
      hints.push('use_rag', 'pattern_based');
    } else if (state.generationPath === 'traditional') {
      hints.push('use_traditional');
    }

    if (state.options.learnFromHistory) hints.push('learn_from_history');
    if (state.options.defectTriggering) hints.push('edge_case');
    if (state.options.productionLike) hints.push('production_like');

    // Only add 'realistic' hint if not using traditional path
    // Traditional should ignore context to stay fast
    if (state.context.length > 0 && state.generationPath !== 'traditional') {
      hints.push('realistic');
    }

    return {
      domain: state.domain,
      entity: state.entity,
      count: state.count,
      // Don't send context for traditional path to ensure it stays fast
      context: state.generationPath === 'traditional' ? undefined : (state.context || undefined),
      scenarios: state.scenarios.length > 0 ? state.scenarios : undefined,
      hints: hints.length > 0 ? hints : undefined,
      outputFormat: state.outputFormat,
      options: state.options,
      // generationPath is not a field in protobuf - routing is done via hints
      inlineSchema: state.inlineSchema || undefined,
    };
  },
}));