import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ScenarioBuilder } from '@/components/generator/scenario-builder';
import { useGeneratorStore } from '@/stores/generator-store';

// Mock the store
vi.mock('@/stores/generator-store', () => ({
  useGeneratorStore: vi.fn(),
}));

const mockStoreState = {
  scenarios: [
    { name: 'happy_path', count: 30 },
    { name: 'edge_case', count: 20 },
  ],
  count: 50,
  addScenario: vi.fn(),
  removeScenario: vi.fn(),
  updateScenario: vi.fn(),
};

describe('ScenarioBuilder', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (useGeneratorStore as any).mockReturnValue(mockStoreState);
  });

  it('renders all scenarios', () => {
    render(<ScenarioBuilder />);

    expect(screen.getByDisplayValue('happy_path')).toBeInTheDocument();
    expect(screen.getByDisplayValue('edge_case')).toBeInTheDocument();
    expect(screen.getByDisplayValue('30')).toBeInTheDocument();
    expect(screen.getByDisplayValue('20')).toBeInTheDocument();
  });

  it('shows count mismatch warning when totals dont match', () => {
    render(<ScenarioBuilder />);

    // Total is 50 (30 + 20) which matches, so no warning
    expect(screen.getByText('Scenarios')).toBeInTheDocument();
    expect(screen.getByText(/Total: 50 = Count: 50/)).toBeInTheDocument();
  });

  it('shows warning when scenario totals dont match count', () => {
    const mismatchState = {
      ...mockStoreState,
      count: 60, // Different from total (50)
    };
    (useGeneratorStore as any).mockReturnValue(mismatchState);

    render(<ScenarioBuilder />);

    const warning = screen.getByText(/Total: 50 ≠ Count: 60/);
    expect(warning).toBeInTheDocument();
    expect(warning.className).toContain('text-warning');
  });

  it('can add a new scenario', async () => {
    render(<ScenarioBuilder />);

    const input = screen.getByPlaceholderText('New scenario name...');
    const addButton = screen.getByRole('button', { name: /add/i });

    fireEvent.change(input, { target: { value: 'performance_test' } });
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(mockStoreState.addScenario).toHaveBeenCalledWith({
        name: 'performance_test',
        count: 10,
      });
    });

    // Input should be cleared
    expect(input).toHaveValue('');
  });

  it('converts spaces to underscores in scenario names', async () => {
    render(<ScenarioBuilder />);

    const input = screen.getByPlaceholderText('New scenario name...');
    const addButton = screen.getByRole('button', { name: /add/i });

    fireEvent.change(input, { target: { value: 'test scenario name' } });
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(mockStoreState.addScenario).toHaveBeenCalledWith({
        name: 'test_scenario_name',
        count: 10,
      });
    });
  });

  it('adds scenario on Enter key press', async () => {
    render(<ScenarioBuilder />);

    const input = screen.getByPlaceholderText('New scenario name...');

    fireEvent.change(input, { target: { value: 'quick_test' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    await waitFor(() => {
      expect(mockStoreState.addScenario).toHaveBeenCalledWith({
        name: 'quick_test',
        count: 10,
      });
    });
  });

  it('disables add button when input is empty', () => {
    render(<ScenarioBuilder />);

    const addButton = screen.getByRole('button', { name: /add/i });
    expect(addButton).toBeDisabled();
  });

  it('can update scenario name', async () => {
    render(<ScenarioBuilder />);

    const nameInput = screen.getByDisplayValue('happy_path');
    fireEvent.change(nameInput, { target: { value: 'success_flow' } });

    await waitFor(() => {
      expect(mockStoreState.updateScenario).toHaveBeenCalledWith(0, {
        name: 'success_flow',
      });
    });
  });

  it('can update scenario count', async () => {
    render(<ScenarioBuilder />);

    const countInput = screen.getByDisplayValue('30');
    fireEvent.change(countInput, { target: { value: '40' } });

    await waitFor(() => {
      expect(mockStoreState.updateScenario).toHaveBeenCalledWith(0, {
        count: 40,
      });
    });
  });

  it('can remove a scenario', async () => {
    render(<ScenarioBuilder />);

    const removeButtons = screen.getAllByRole('button').filter(
      btn => btn.querySelector('svg')
    );

    // Click the second scenario's remove button
    fireEvent.click(removeButtons[1]);

    await waitFor(() => {
      expect(mockStoreState.removeScenario).toHaveBeenCalledWith(1);
    });
  });

  it('disables remove button when only one scenario exists', () => {
    const singleScenarioState = {
      ...mockStoreState,
      scenarios: [{ name: 'only_one', count: 50 }],
    };
    (useGeneratorStore as any).mockReturnValue(singleScenarioState);

    render(<ScenarioBuilder />);

    const removeButton = screen.getByRole('button', { name: '' });
    expect(removeButton).toBeDisabled();
  });

  it('validates count input minimum value', () => {
    render(<ScenarioBuilder />);

    const countInputs = screen.getAllByRole('spinbutton');
    countInputs.forEach(input => {
      expect(input.getAttribute('min')).toBe('1');
    });
  });

  it('trims whitespace from scenario names', async () => {
    render(<ScenarioBuilder />);

    const input = screen.getByPlaceholderText('New scenario name...');
    const addButton = screen.getByRole('button', { name: /add/i });

    fireEvent.change(input, { target: { value: '  test_scenario  ' } });
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(mockStoreState.addScenario).toHaveBeenCalledWith({
        name: 'test_scenario',
        count: 10,
      });
    });
  });
});