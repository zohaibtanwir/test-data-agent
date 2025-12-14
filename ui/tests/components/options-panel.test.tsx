import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { OptionsPanel } from '@/components/generator/options-panel';
import { useGeneratorStore } from '@/stores/generator-store';

// Mock the store
vi.mock('@/stores/generator-store', () => ({
  useGeneratorStore: vi.fn(),
}));

const mockStoreState = {
  options: {
    useCache: false,
    learnFromHistory: true,
    defectTriggering: false,
    productionLike: true,
  },
  toggleOption: vi.fn(),
};

describe('OptionsPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (useGeneratorStore as any).mockReturnValue(mockStoreState);
  });

  it('renders all four options', () => {
    render(<OptionsPanel />);

    expect(screen.getByText('Use cached data pools')).toBeInTheDocument();
    expect(screen.getByText('Learn from history (RAG)')).toBeInTheDocument();
    expect(screen.getByText('Defect-triggering patterns')).toBeInTheDocument();
    expect(screen.getByText('Production-like distribution')).toBeInTheDocument();
  });

  it('shows descriptions for each option', () => {
    render(<OptionsPanel />);

    expect(screen.getByText('Faster generation from pre-generated pools')).toBeInTheDocument();
    expect(screen.getByText('Use patterns from past successful generations')).toBeInTheDocument();
    expect(screen.getByText('Generate edge cases known to cause bugs')).toBeInTheDocument();
    expect(screen.getByText('Match real production data patterns')).toBeInTheDocument();
  });

  it('shows correct checked state for options', () => {
    render(<OptionsPanel />);

    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes).toHaveLength(4);

    // Based on mockStoreState.options
    expect(checkboxes[0]).not.toBeChecked(); // useCache: false
    expect(checkboxes[1]).toBeChecked();     // learnFromHistory: true
    expect(checkboxes[2]).not.toBeChecked(); // defectTriggering: false
    expect(checkboxes[3]).toBeChecked();     // productionLike: true
  });

  it('calls toggleOption when clicking on option container', () => {
    render(<OptionsPanel />);

    const optionContainers = screen.getAllByRole('checkbox').map(
      checkbox => checkbox.closest('div[class*="cursor-pointer"]')
    );

    // Click on useCache option
    if (optionContainers[0]) {
      fireEvent.click(optionContainers[0]);
      expect(mockStoreState.toggleOption).toHaveBeenCalledWith('useCache');
    }
  });

  it('calls toggleOption when clicking checkbox directly', () => {
    render(<OptionsPanel />);

    const checkboxes = screen.getAllByRole('checkbox');

    fireEvent.click(checkboxes[1]); // Click learnFromHistory checkbox
    expect(mockStoreState.toggleOption).toHaveBeenCalledWith('learnFromHistory');

    fireEvent.click(checkboxes[2]); // Click defectTriggering checkbox
    expect(mockStoreState.toggleOption).toHaveBeenCalledWith('defectTriggering');
  });

  it('highlights active options with accent color', () => {
    render(<OptionsPanel />);

    const optionContainers = screen.getAllByRole('checkbox').map(
      checkbox => checkbox.closest('div[class*="border"]')
    );

    // Check that active options have accent styling
    expect(optionContainers[1]?.className).toContain('bg-accent-muted');
    expect(optionContainers[1]?.className).toContain('border-accent');
    expect(optionContainers[3]?.className).toContain('bg-accent-muted');
    expect(optionContainers[3]?.className).toContain('border-accent');

    // Check that inactive options have default styling
    expect(optionContainers[0]?.className).toContain('bg-bg-tertiary');
    expect(optionContainers[0]?.className).toContain('border-border-default');
  });

  it('applies hover styles to option containers', () => {
    render(<OptionsPanel />);

    const optionContainers = screen.getAllByRole('checkbox').map(
      checkbox => checkbox.closest('div[class*="cursor-pointer"]')
    );

    // Check that hover styles are present
    optionContainers.forEach(container => {
      if (container && !container.className.includes('border-accent')) {
        expect(container.className).toContain('hover:border-border-light');
      }
    });
  });

  it('renders in a 2x2 grid layout', () => {
    render(<OptionsPanel />);

    const gridContainer = screen.getAllByRole('checkbox')[0].closest('.grid');
    expect(gridContainer?.className).toContain('grid-cols-2');
  });

  it('shows the correct header with icon', () => {
    render(<OptionsPanel />);

    expect(screen.getByText('Generation Options')).toBeInTheDocument();
    // The SlidersHorizontal icon should be present
    const header = screen.getByText('Generation Options').closest('div');
    expect(header?.querySelector('svg')).toBeInTheDocument();
  });

  it('toggles all options correctly', () => {
    render(<OptionsPanel />);

    const optionKeys = ['useCache', 'learnFromHistory', 'defectTriggering', 'productionLike'];
    const checkboxes = screen.getAllByRole('checkbox');

    checkboxes.forEach((checkbox, index) => {
      fireEvent.click(checkbox);
      expect(mockStoreState.toggleOption).toHaveBeenCalledWith(optionKeys[index]);
    });

    expect(mockStoreState.toggleOption).toHaveBeenCalledTimes(4);
  });
});