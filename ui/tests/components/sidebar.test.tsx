import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Sidebar } from '@/components/layout/sidebar';

const mockSchemas = [
  { name: 'cart', domain: 'ecommerce' },
  { name: 'order', domain: 'ecommerce' },
  { name: 'payment', domain: 'ecommerce' },
  { name: 'user', domain: 'core' },
  { name: 'address', domain: 'core' },
];

const defaultProps = {
  selectedSchema: null,
  onSchemaSelect: vi.fn(),
  onQuickGenerate: vi.fn(),
};

describe('Sidebar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all three sections', () => {
    render(<Sidebar {...defaultProps} />);

    expect(screen.getByText('Schemas')).toBeInTheDocument();
    expect(screen.getByText('Quick Generate')).toBeInTheDocument();
    expect(screen.getByText('Recent')).toBeInTheDocument();
  });

  it('renders all mock schemas', () => {
    render(<Sidebar {...defaultProps} />);

    // Check schema names
    expect(screen.getByText('cart')).toBeInTheDocument();
    expect(screen.getByText('order')).toBeInTheDocument();
    expect(screen.getByText('payment')).toBeInTheDocument();
    expect(screen.getByText('user')).toBeInTheDocument();
    expect(screen.getByText('address')).toBeInTheDocument();

    // Check domains are displayed
    const ecommerceDomains = screen.getAllByText('ecommerce');
    const coreDomains = screen.getAllByText('core');

    expect(ecommerceDomains.length).toBe(3);
    expect(coreDomains.length).toBe(2);
  });

  it('highlights selected schema', () => {
    const props = { ...defaultProps, selectedSchema: 'cart' };
    render(<Sidebar {...props} />);

    const cartButton = screen.getByText('cart').closest('button');
    expect(cartButton?.className).toContain('bg-accent-muted');
    expect(cartButton?.className).toContain('border-l-accent');
  });

  it('calls onSchemaSelect when schema is clicked', () => {
    render(<Sidebar {...defaultProps} />);

    const orderButton = screen.getByText('order').closest('button');
    if (orderButton) {
      fireEvent.click(orderButton);
      expect(defaultProps.onSchemaSelect).toHaveBeenCalledWith('order');
    }
  });

  it('renders quick generate buttons with counts', () => {
    render(<Sidebar {...defaultProps} />);

    const sampleCarts = screen.getByText('Sample Carts');
    const sampleOrders = screen.getByText('Sample Orders');
    const sampleUsers = screen.getByText('Sample Users');
    const edgeCases = screen.getByText('Edge Cases');

    expect(sampleCarts).toBeInTheDocument();
    expect(sampleOrders).toBeInTheDocument();
    expect(sampleUsers).toBeInTheDocument();
    expect(edgeCases).toBeInTheDocument();

    // Check counts are displayed
    const count10 = screen.getAllByText('10');
    const count25 = screen.getByText('25');
    const count20 = screen.getByText('20');

    expect(count10).toHaveLength(2); // Sample Carts and Sample Orders
    expect(count25).toBeInTheDocument();
    expect(count20).toBeInTheDocument();
  });

  it('calls onQuickGenerate when quick action is clicked', () => {
    render(<Sidebar {...defaultProps} />);

    const buttons = screen.getAllByRole('button');
    const cartButton = buttons.find(btn => btn.textContent?.includes('Sample Carts'));

    if (cartButton) {
      fireEvent.click(cartButton);
      expect(defaultProps.onQuickGenerate).toHaveBeenCalledWith('carts');
    }

    const orderButton = buttons.find(btn => btn.textContent?.includes('Sample Orders'));
    if (orderButton) {
      fireEvent.click(orderButton);
      expect(defaultProps.onQuickGenerate).toHaveBeenCalledWith('orders');
    }
  });

  it('renders recent items section', () => {
    render(<Sidebar {...defaultProps} />);

    expect(screen.getByText('ApplePay checkout carts')).toBeInTheDocument();
    expect(screen.getByText('Failed payment scenarios')).toBeInTheDocument();
  });

  it('shows schema icons', () => {
    render(<Sidebar {...defaultProps} />);

    const schemaButtons = screen.getAllByRole('button').filter(
      btn => btn.querySelector('.schema-icon')
    );

    // Should have icons for each schema
    expect(schemaButtons.length).toBeGreaterThanOrEqual(5);
  });

  it('applies hover styles to schema items', () => {
    render(<Sidebar {...defaultProps} />);

    const schemaButtons = screen.getAllByRole('button').filter(
      btn => btn.textContent?.includes('cart') ||
            btn.textContent?.includes('order') ||
            btn.textContent?.includes('payment')
    );

    schemaButtons.forEach(button => {
      expect(button.className).toContain('hover:bg-bg-tertiary');
    });
  });

  it('shows separators between sections', () => {
    const { container } = render(<Sidebar {...defaultProps} />);

    const separators = container.querySelectorAll('[class*="Separator"]');
    expect(separators.length).toBeGreaterThan(0);
  });

  it('has correct section headers with uppercase styling', () => {
    render(<Sidebar {...defaultProps} />);

    const headers = screen.getAllByText((content, element) => {
      return element?.tagName === 'H3' && element.className.includes('uppercase');
    });

    expect(headers.length).toBeGreaterThan(0);
  });

  it('scrolls within ScrollArea', () => {
    const { container } = render(<Sidebar {...defaultProps} />);

    const scrollArea = container.querySelector('[data-radix-scroll-area-viewport]');
    expect(scrollArea).toBeInTheDocument();
  });

  it('changes selected schema icon color', () => {
    const props = { ...defaultProps, selectedSchema: 'payment' };
    const { container } = render(<Sidebar {...props} />);

    const paymentButton = screen.getByText('payment').closest('button');
    const icon = paymentButton?.querySelector('.schema-icon');

    expect(icon?.className).toContain('bg-accent');
    expect(icon?.className).toContain('text-white');
  });

  it('displays all quick action icons', () => {
    render(<Sidebar {...defaultProps} />);

    const quickActionButtons = screen.getAllByRole('button').filter(
      btn => btn.textContent?.includes('Sample') || btn.textContent?.includes('Edge')
    );

    quickActionButtons.forEach(button => {
      const svg = button.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });
  });
});