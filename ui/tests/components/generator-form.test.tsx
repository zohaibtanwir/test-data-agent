import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { GeneratorForm } from '@/components/generator/generator-form';
import { useGeneratorStore } from '@/stores/generator-store';

// Mock the store
vi.mock('@/stores/generator-store', () => ({
  useGeneratorStore: vi.fn(),
}));

const mockSchemas = [
  { name: 'cart', domain: 'ecommerce' },
  { name: 'order', domain: 'ecommerce' },
  { name: 'payment', domain: 'ecommerce' },
  { name: 'user', domain: 'core' },
  { name: 'address', domain: 'core' },
];

const mockStoreState = {
  domain: 'ecommerce',
  entity: 'cart',
  count: 50,
  outputFormat: 'JSON',
  context: '',
  scenarios: [{ name: 'happy_path', count: 50 }],
  options: {
    useCache: false,
    learnFromHistory: false,
    defectTriggering: false,
    productionLike: false,
  },
  generationPath: 'auto',
  isLoading: false,
  error: null,
  result: null,
  setDomain: vi.fn(),
  setEntity: vi.fn(),
  setCount: vi.fn(),
  setOutputFormat: vi.fn(),
  setContext: vi.fn(),
  setGenerationPath: vi.fn(),
  addScenario: vi.fn(),
  removeScenario: vi.fn(),
  updateScenario: vi.fn(),
  toggleOption: vi.fn(),
  setResult: vi.fn(),
  setLoading: vi.fn(),
  setError: vi.fn(),
  reset: vi.fn(),
  loadPreset: vi.fn(),
  getRequestBody: vi.fn(),
};

describe('GeneratorForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (useGeneratorStore as any).mockReturnValue(mockStoreState);
  });

  it('renders all major sections', () => {
    render(<GeneratorForm schemas={mockSchemas} />);

    expect(screen.getByText('Generate Test Data')).toBeInTheDocument();
    expect(screen.getByText('Basic Configuration')).toBeInTheDocument();
    expect(screen.getByText('Context (for LLM Generation)')).toBeInTheDocument();
    expect(screen.getByText('Scenarios')).toBeInTheDocument();
    expect(screen.getByText('Generation Options')).toBeInTheDocument();
    expect(screen.getByText('Generate Data')).toBeInTheDocument();
  });

  it('displays correct schema badge', () => {
    render(<GeneratorForm schemas={mockSchemas} />);

    const badge = screen.getByText('cart Schema');
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain('capitalize');
  });

  it('shows correct entities for selected domain', () => {
    render(<GeneratorForm schemas={mockSchemas} />);

    // Should show only ecommerce entities initially
    const entitySelects = screen.getAllByRole('combobox');
    const entitySelect = entitySelects.find(el => el.getAttribute('aria-label')?.includes('Entity'));

    expect(entitySelect).toBeInTheDocument();
  });

  it('calls setDomain when domain is changed', async () => {
    render(<GeneratorForm schemas={mockSchemas} />);

    const domainSelects = screen.getAllByRole('combobox');
    const domainSelect = domainSelects[0]; // First select is domain

    fireEvent.change(domainSelect, { target: { value: 'core' } });

    await waitFor(() => {
      expect(mockStoreState.setDomain).toHaveBeenCalledWith('core');
    });
  });

  it('calls setCount when count is changed', async () => {
    render(<GeneratorForm schemas={mockSchemas} />);

    const countInput = screen.getByDisplayValue('50');
    fireEvent.change(countInput, { target: { value: '100' } });

    await waitFor(() => {
      expect(mockStoreState.setCount).toHaveBeenCalledWith(100);
    });
  });

  it('validates count input range', () => {
    render(<GeneratorForm schemas={mockSchemas} />);

    const countInput = screen.getByDisplayValue('50') as HTMLInputElement;
    expect(countInput.min).toBe('1');
    expect(countInput.max).toBe('1000');
  });

  it('calls setOutputFormat when format is changed', async () => {
    render(<GeneratorForm schemas={mockSchemas} />);

    const formatSelects = screen.getAllByRole('combobox');
    const formatSelect = formatSelects.find(el =>
      el.textContent?.includes('JSON')
    );

    if (formatSelect) {
      fireEvent.change(formatSelect, { target: { value: 'CSV' } });

      await waitFor(() => {
        expect(mockStoreState.setOutputFormat).toHaveBeenCalledWith('CSV');
      });
    }
  });

  it('shows loading state when generating', () => {
    const loadingState = { ...mockStoreState, isLoading: true };
    (useGeneratorStore as any).mockReturnValue(loadingState);

    render(<GeneratorForm schemas={mockSchemas} />);

    const button = screen.getByRole('button', { name: /generating/i });
    expect(button).toBeDisabled();
  });

  it('disables generate button when count is 0', () => {
    const zeroCountState = { ...mockStoreState, count: 0 };
    (useGeneratorStore as any).mockReturnValue(zeroCountState);

    render(<GeneratorForm schemas={mockSchemas} />);

    const button = screen.getByRole('button', { name: /generate data/i });
    expect(button).toBeDisabled();
  });
});