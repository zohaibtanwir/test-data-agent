import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DataPreview } from '@/components/preview/data-preview';
import { useGeneratorStore } from '@/stores/generator-store';

// Mock the store
vi.mock('@/stores/generator-store', () => ({
  useGeneratorStore: vi.fn(),
}));

// Mock Monaco Editor
vi.mock('@monaco-editor/react', () => ({
  default: vi.fn(({ value }: any) => (
    <div data-testid="monaco-editor">{value}</div>
  )),
}));

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn(() => Promise.resolve()),
  },
});

const mockSuccessState = {
  result: {
    success: true,
    requestId: 'req-123',
    data: JSON.stringify([
      { id: 1, name: 'Test Item 1', price: 29.99 },
      { id: 2, name: 'Test Item 2', price: 49.99 },
    ], null, 2),
    recordCount: 2,
    metadata: {
      generationPath: 'llm',
      llmTokensUsed: 1500,
      generationTimeMs: 2500,
      coherenceScore: 0.95,
      scenarioCounts: { happy_path: 2 },
    },
  },
  isLoading: false,
  error: null,
};

const mockLoadingState = {
  result: null,
  isLoading: true,
  error: null,
};

const mockErrorState = {
  result: null,
  isLoading: false,
  error: 'Failed to generate data: Connection timeout',
};

const mockEmptyState = {
  result: null,
  isLoading: false,
  error: null,
};

describe('DataPreview', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (useGeneratorStore as any).mockReturnValue(mockSuccessState);
  });

  it('renders header with title and tabs', () => {
    render(<DataPreview />);

    expect(screen.getByText('Generated Data')).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /json/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /csv/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /sql/i })).toBeInTheDocument();
  });

  it('shows empty state when no data', () => {
    (useGeneratorStore as any).mockReturnValue(mockEmptyState);
    render(<DataPreview />);

    expect(screen.getByText('No data yet')).toBeInTheDocument();
    expect(
      screen.getByText('Configure your request and click Generate to see data here')
    ).toBeInTheDocument();
  });

  it('shows loading state when generating', () => {
    (useGeneratorStore as any).mockReturnValue(mockLoadingState);
    render(<DataPreview />);

    expect(screen.getByText('Generating with LLM...')).toBeInTheDocument();
  });

  it('shows error state with message', () => {
    (useGeneratorStore as any).mockReturnValue(mockErrorState);
    render(<DataPreview />);

    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('Failed to generate data: Connection timeout')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  it('displays generated data in JSON viewer', () => {
    render(<DataPreview />);

    const editor = screen.getByTestId('monaco-editor');
    expect(editor).toBeInTheDocument();
    expect(editor.textContent).toContain('Test Item 1');
    expect(editor.textContent).toContain('Test Item 2');
  });

  it('switches between tabs', async () => {
    render(<DataPreview />);

    const csvTab = screen.getByRole('tab', { name: /csv/i });
    const sqlTab = screen.getByRole('tab', { name: /sql/i });

    fireEvent.click(csvTab);
    await waitFor(() => {
      expect(csvTab).toHaveAttribute('data-state', 'active');
    });

    fireEvent.click(sqlTab);
    await waitFor(() => {
      expect(sqlTab).toHaveAttribute('data-state', 'active');
    });
  });

  it('copies data to clipboard', async () => {
    render(<DataPreview />);

    const copyButton = screen.getAllByRole('button').find(
      btn => btn.querySelector('[class*="Copy"]')
    );

    if (copyButton) {
      fireEvent.click(copyButton);

      await waitFor(() => {
        expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
          mockSuccessState.result.data
        );
      });
    }
  });

  it('downloads data as file', () => {
    // Mock URL and document methods
    const mockCreateObjectURL = vi.fn(() => 'blob:url');
    const mockRevokeObjectURL = vi.fn();
    const mockClick = vi.fn();
    const mockCreateElement = vi.fn(() => ({
      href: '',
      download: '',
      click: mockClick,
    }));

    Object.assign(URL, {
      createObjectURL: mockCreateObjectURL,
      revokeObjectURL: mockRevokeObjectURL,
    });

    Object.assign(document, {
      createElement: mockCreateElement,
    });

    render(<DataPreview />);

    const downloadButton = screen.getAllByRole('button').find(
      btn => btn.querySelector('[class*="Download"]')
    );

    if (downloadButton) {
      fireEvent.click(downloadButton);

      expect(mockCreateObjectURL).toHaveBeenCalled();
      expect(mockClick).toHaveBeenCalled();
      expect(mockRevokeObjectURL).toHaveBeenCalled();
    }
  });

  it('disables action buttons when no data', () => {
    (useGeneratorStore as any).mockReturnValue(mockEmptyState);
    render(<DataPreview />);

    const buttons = screen.getAllByRole('button');
    const copyButton = buttons.find(btn => btn.querySelector('[class*="Copy"]'));
    const downloadButton = buttons.find(btn => btn.querySelector('[class*="Download"]'));

    expect(copyButton).toBeDisabled();
    expect(downloadButton).toBeDisabled();
  });

  it('renders metadata bar with statistics', () => {
    render(<DataPreview />);

    expect(screen.getByText('LLM')).toBeInTheDocument();
    expect(screen.getByText('1,500')).toBeInTheDocument(); // Tokens
    expect(screen.getByText('2.5s')).toBeInTheDocument(); // Time
    expect(screen.getByText('0.95')).toBeInTheDocument(); // Coherence score
  });

  it('shows metadata labels', () => {
    render(<DataPreview />);

    expect(screen.getByText('Path')).toBeInTheDocument();
    expect(screen.getByText('Tokens')).toBeInTheDocument();
    expect(screen.getByText('Time')).toBeInTheDocument();
    expect(screen.getByText('Coherence')).toBeInTheDocument();
  });

  it('does not show metadata bar when loading', () => {
    (useGeneratorStore as any).mockReturnValue(mockLoadingState);
    render(<DataPreview />);

    expect(screen.queryByText('Path')).not.toBeInTheDocument();
    expect(screen.queryByText('Tokens')).not.toBeInTheDocument();
  });

  it('does not show metadata bar when error', () => {
    (useGeneratorStore as any).mockReturnValue(mockErrorState);
    render(<DataPreview />);

    expect(screen.queryByText('Path')).not.toBeInTheDocument();
    expect(screen.queryByText('Tokens')).not.toBeInTheDocument();
  });

  it('formats JSON data properly', () => {
    render(<DataPreview />);

    const editor = screen.getByTestId('monaco-editor');
    // The data should be formatted with proper indentation
    expect(editor.textContent).toMatch(/\s{2}"id"/); // Check for indentation
  });

  it('handles CSV tab content', async () => {
    render(<DataPreview />);

    const csvTab = screen.getByRole('tab', { name: /csv/i });
    fireEvent.click(csvTab);

    await waitFor(() => {
      // In CSV view, it should show the data (currently showing raw JSON as placeholder)
      const preElement = screen.getByText((content, element) => {
        return element?.tagName === 'PRE' && content.includes('Test Item');
      });
      expect(preElement).toBeInTheDocument();
    });
  });

  it('handles SQL tab content', async () => {
    render(<DataPreview />);

    const sqlTab = screen.getByRole('tab', { name: /sql/i });
    fireEvent.click(sqlTab);

    await waitFor(() => {
      // In SQL view, it should show the data (currently showing raw JSON as placeholder)
      const preElement = screen.getByText((content, element) => {
        return element?.tagName === 'PRE' && content.includes('Test Item');
      });
      expect(preElement).toBeInTheDocument();
    });
  });
});