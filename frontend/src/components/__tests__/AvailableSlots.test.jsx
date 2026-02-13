import { render, screen } from '@testing-library/react';
import AvailableSlots from '../AvailableSlots';

describe('AvailableSlots', () => {
  it('renders aggregate slot metrics correctly', () => {
    const floors = [
      { total_slots: 50, current_vehicles: 30, available_slots: 20 },
      { total_slots: 40, current_vehicles: 10, available_slots: 30 },
    ];

    render(<AvailableSlots floors={floors} loading={false} />);

    expect(screen.getByText('Total Capacity')).toBeInTheDocument();
    expect(screen.getByText('90')).toBeInTheDocument();
    expect(screen.getByText('40')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
    expect(screen.getByText('44%')).toBeInTheDocument();
  });

  it('shows loading skeleton while loading', () => {
    const { container } = render(<AvailableSlots floors={[]} loading={true} />);
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });
});
