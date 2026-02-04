import { render } from '@testing-library/react-native';
import { ChocolateCard } from '../ChocolateCard';

describe('ChocolateCard', () => {
  const inStockChocolate = {
    id: '1',
    name: 'Dark Truffle',
    description: '70% cocoa dark chocolate',
    price: 5.99,
    stock_quantity: 50,
    cocoa_percentage: 70,
    created_at: '2024-01-15T12:00:00Z',
    updated_at: '2024-01-15T12:00:00Z',
  };

  const outOfStockChocolate = {
    id: '2',
    name: 'Milk Hazelnut',
    description: 'Creamy milk chocolate with hazelnut center',
    price: 4.99,
    stock_quantity: 0,
    cocoa_percentage: 35,
    created_at: '2024-01-15T12:00:00Z',
    updated_at: '2024-01-15T12:00:00Z',
  };

  it('renders chocolate name and price', () => {
    const { getByText } = render(<ChocolateCard chocolate={inStockChocolate} />);

    expect(getByText('Dark Truffle')).toBeTruthy();
    expect(getByText('$5.99')).toBeTruthy();
  });

  it('renders description when provided', () => {
    const { getByText } = render(<ChocolateCard chocolate={inStockChocolate} />);

    expect(getByText('70% cocoa dark chocolate')).toBeTruthy();
  });

  it('does not render description when not provided', () => {
    const { queryByText } = render(<ChocolateCard chocolate={outOfStockChocolate} />);

    expect(queryByText('Rich and creamy')).toBeNull();
  });

  it('shows In Stock badge when in stock', () => {
    const { getByText } = render(<ChocolateCard chocolate={inStockChocolate} />);

    expect(getByText('In Stock')).toBeTruthy();
  });

  it('shows Out of Stock badge when not in stock', () => {
    const { getByText } = render(<ChocolateCard chocolate={outOfStockChocolate} />);

    expect(getByText('Out of Stock')).toBeTruthy();
  });
});