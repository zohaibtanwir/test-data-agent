import { describe, it, expect, beforeEach } from 'vitest';
import { act, renderHook } from '@testing-library/react';
import { useGeneratorStore } from '@/stores/generator-store';
import { DEFAULT_COUNT } from '@/lib/constants';

describe('GeneratorStore', () => {
  beforeEach(() => {
    // Reset store to initial state
    act(() => {
      useGeneratorStore.getState().reset();
    });
  });

  describe('Initial State', () => {
    it('has correct default values', () => {
      const { result } = renderHook(() => useGeneratorStore());

      expect(result.current.domain).toBe('ecommerce');
      expect(result.current.entity).toBe('cart');
      expect(result.current.count).toBe(DEFAULT_COUNT);
      expect(result.current.context).toBe('');
      expect(result.current.scenarios).toHaveLength(1);
      expect(result.current.scenarios[0]).toEqual({
        name: 'happy_path',
        count: DEFAULT_COUNT,
      });
      expect(result.current.outputFormat).toBe('JSON');
      expect(result.current.generationPath).toBe('auto');
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
      expect(result.current.result).toBe(null);
    });

    it('has all options disabled by default', () => {
      const { result } = renderHook(() => useGeneratorStore());

      expect(result.current.options.useCache).toBe(false);
      expect(result.current.options.learnFromHistory).toBe(false);
      expect(result.current.options.defectTriggering).toBe(false);
      expect(result.current.options.productionLike).toBe(false);
    });
  });

  describe('Field Setters', () => {
    it('sets domain', () => {
      const { result } = renderHook(() => useGeneratorStore());

      act(() => {
        result.current.setDomain('supply_chain');
      });

      expect(result.current.domain).toBe('supply_chain');
    });

    it('sets entity', () => {
      const { result } = renderHook(() => useGeneratorStore());

      act(() => {
        result.current.setEntity('order');
      });

      expect(result.current.entity).toBe('order');
    });

    it('sets count and updates default scenario', () => {
      const { result } = renderHook(() => useGeneratorStore());

      act(() => {
        result.current.setCount(100);
      });

      expect(result.current.count).toBe(100);
      expect(result.current.scenarios[0].count).toBe(100);
    });

    it('sets context', () => {
      const { result } = renderHook(() => useGeneratorStore());

      act(() => {
        result.current.setContext('Generate realistic shopping carts');
      });

      expect(result.current.context).toBe('Generate realistic shopping carts');
    });

    it('sets output format', () => {
      const { result } = renderHook(() => useGeneratorStore());

      act(() => {
        result.current.setOutputFormat('CSV');
      });

      expect(result.current.outputFormat).toBe('CSV');
    });

    it('sets generation path', () => {
      const { result } = renderHook(() => useGeneratorStore());

      act(() => {
        result.current.setGenerationPath('llm');
      });

      expect(result.current.generationPath).toBe('llm');
    });
  });

  describe('Scenario Management', () => {
    it('adds a scenario', () => {
      const { result } = renderHook(() => useGeneratorStore());

      act(() => {
        result.current.addScenario({ name: 'edge_case', count: 10 });
      });

      expect(result.current.scenarios).toHaveLength(2);
      expect(result.current.scenarios[1]).toEqual({
        name: 'edge_case',
        count: 10,
      });
    });

    it('removes a scenario', () => {
      const { result } = renderHook(() => useGeneratorStore());

      act(() => {
        result.current.addScenario({ name: 'edge_case', count: 10 });
        result.current.addScenario({ name: 'performance', count: 5 });
      });

      expect(result.current.scenarios).toHaveLength(3);

      act(() => {
        result.current.removeScenario(1); // Remove edge_case
      });

      expect(result.current.scenarios).toHaveLength(2);
      expect(result.current.scenarios[0].name).toBe('happy_path');
      expect(result.current.scenarios[1].name).toBe('performance');
    });

    it('updates a scenario', () => {
      const { result } = renderHook(() => useGeneratorStore());

      act(() => {
        result.current.updateScenario(0, { name: 'success_flow', count: 75 });
      });

      expect(result.current.scenarios[0]).toEqual({
        name: 'success_flow',
        count: 75,
      });
    });

    it('does not update scenario count when multiple scenarios exist', () => {
      const { result } = renderHook(() => useGeneratorStore());

      act(() => {
        result.current.addScenario({ name: 'edge_case', count: 10 });
        result.current.setCount(200);
      });

      // Should not auto-update when multiple scenarios
      expect(result.current.scenarios[0].count).toBe(DEFAULT_COUNT);
      expect(result.current.scenarios[1].count).toBe(10);
    });
  });

  describe('Options Toggle', () => {
    it('toggles useCache option', () => {
      const { result } = renderHook(() => useGeneratorStore());

      expect(result.current.options.useCache).toBe(false);

      act(() => {
        result.current.toggleOption('useCache');
      });

      expect(result.current.options.useCache).toBe(true);

      act(() => {
        result.current.toggleOption('useCache');
      });

      expect(result.current.options.useCache).toBe(false);
    });

    it('toggles multiple options independently', () => {
      const { result } = renderHook(() => useGeneratorStore());

      act(() => {
        result.current.toggleOption('learnFromHistory');
        result.current.toggleOption('productionLike');
      });

      expect(result.current.options.learnFromHistory).toBe(true);
      expect(result.current.options.productionLike).toBe(true);
      expect(result.current.options.defectTriggering).toBe(false);
      expect(result.current.options.useCache).toBe(false);
    });
  });

  describe('Result Management', () => {
    it('sets result', () => {
      const { result } = renderHook(() => useGeneratorStore());

      const mockResult = {
        success: true,
        requestId: 'req-123',
        data: '{"test": "data"}',
        recordCount: 10,
        metadata: {
          generationPath: 'llm',
          generationTimeMs: 1000,
        },
      };

      act(() => {
        result.current.setResult(mockResult as any);
      });

      expect(result.current.result).toEqual(mockResult);
    });

    it('sets loading state', () => {
      const { result } = renderHook(() => useGeneratorStore());

      act(() => {
        result.current.setLoading(true);
      });

      expect(result.current.isLoading).toBe(true);

      act(() => {
        result.current.setLoading(false);
      });

      expect(result.current.isLoading).toBe(false);
    });

    it('sets error', () => {
      const { result } = renderHook(() => useGeneratorStore());

      act(() => {
        result.current.setError('Connection failed');
      });

      expect(result.current.error).toBe('Connection failed');

      act(() => {
        result.current.setError(null);
      });

      expect(result.current.error).toBe(null);
    });
  });

  describe('Utility Functions', () => {
    it('resets to initial state', () => {
      const { result } = renderHook(() => useGeneratorStore());

      // Make changes
      act(() => {
        result.current.setDomain('loyalty');
        result.current.setEntity('points');
        result.current.setCount(200);
        result.current.addScenario({ name: 'test', count: 10 });
        result.current.toggleOption('useCache');
        result.current.setError('Some error');
      });

      // Reset
      act(() => {
        result.current.reset();
      });

      // Check all values are back to initial
      expect(result.current.domain).toBe('ecommerce');
      expect(result.current.entity).toBe('cart');
      expect(result.current.count).toBe(DEFAULT_COUNT);
      expect(result.current.scenarios).toHaveLength(1);
      expect(result.current.options.useCache).toBe(false);
      expect(result.current.error).toBe(null);
    });

    it('loads preset configuration', () => {
      const { result } = renderHook(() => useGeneratorStore());

      const preset = {
        domain: 'marketing',
        entity: 'campaign',
        count: 150,
        context: 'Marketing campaign data',
        options: {
          useCache: true,
          learnFromHistory: true,
          defectTriggering: false,
          productionLike: false,
        },
      };

      act(() => {
        result.current.loadPreset(preset);
      });

      expect(result.current.domain).toBe('marketing');
      expect(result.current.entity).toBe('campaign');
      expect(result.current.count).toBe(150);
      expect(result.current.context).toBe('Marketing campaign data');
      expect(result.current.options.useCache).toBe(true);
      expect(result.current.options.learnFromHistory).toBe(true);
    });

    it('generates correct request body', () => {
      const { result } = renderHook(() => useGeneratorStore());

      // Set up state
      act(() => {
        result.current.setDomain('ecommerce');
        result.current.setEntity('order');
        result.current.setCount(25);
        result.current.setContext('Generate orders with payment issues');
        result.current.toggleOption('defectTriggering');
        result.current.toggleOption('learnFromHistory');
      });

      const requestBody = result.current.getRequestBody();

      expect(requestBody).toEqual({
        domain: 'ecommerce',
        entity: 'order',
        count: 25,
        context: 'Generate orders with payment issues',
        scenarios: [{ name: 'happy_path', count: 25 }],
        hints: ['learn_from_history', 'edge_case', 'realistic'],
        outputFormat: 'JSON',
        options: {
          useCache: false,
          learnFromHistory: true,
          defectTriggering: true,
          productionLike: false,
        },
        generationPath: 'auto',
      });
    });

    it('generates hints based on options', () => {
      const { result } = renderHook(() => useGeneratorStore());

      // No hints initially
      let requestBody = result.current.getRequestBody();
      expect(requestBody.hints).toBeUndefined();

      // Add options that generate hints
      act(() => {
        result.current.toggleOption('learnFromHistory');
        result.current.toggleOption('productionLike');
      });

      requestBody = result.current.getRequestBody();
      expect(requestBody.hints).toContain('learn_from_history');
      expect(requestBody.hints).toContain('production_like');

      // Add context (should add 'realistic' hint)
      act(() => {
        result.current.setContext('Some context');
      });

      requestBody = result.current.getRequestBody();
      expect(requestBody.hints).toContain('realistic');
    });

    it('excludes undefined fields from request body', () => {
      const { result } = renderHook(() => useGeneratorStore());

      const requestBody = result.current.getRequestBody();

      // Context should be undefined when empty
      expect(requestBody.context).toBeUndefined();

      // Hints should be undefined when no options are selected
      act(() => {
        result.current.setContext('');
      });

      const updatedBody = result.current.getRequestBody();
      expect(updatedBody.hints).toBeUndefined();
    });
  });
});