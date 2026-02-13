import { render, screen, waitFor } from '@testing-library/react';
import Dashboard from '../Dashboard';

vi.mock('../../services/floorService', () => ({
  floorsAPI: {
    getFloors: vi.fn().mockResolvedValue({
      floors: [
        {
          id: 1,
          name: 'Ground Floor',
          total_slots: 50,
          current_vehicles: 20,
          available_slots: 30,
          updated_at: new Date().toISOString(),
        },
      ],
    }),
    getRecommendedFloor: vi.fn().mockResolvedValue({
      recommended_floor: {
        id: 1,
        name: 'Ground Floor',
        total_slots: 50,
        current_vehicles: 20,
        available_slots: 30,
      },
      reason: 'Lowest occupancy',
      available_alternatives: [],
    }),
  },
  eventsAPI: {
    getEvents: vi.fn().mockResolvedValue({
      events: [
        {
          id: 1,
          camera_id: 'cam-1',
          floor_id: 1,
          track_id: 'track-1',
          vehicle_type: 'car',
          direction: 'entry',
          timestamp: new Date().toISOString(),
        },
      ],
    }),
  },
}));

describe('Dashboard layout', () => {
  it('renders header, navigation, and main sections', async () => {
    render(<Dashboard />);

    expect(screen.getByText('SmartPark')).toBeInTheDocument();
    expect(screen.getAllByText('Overview').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Event Log').length).toBeGreaterThan(0);

    await waitFor(() => {
      expect(screen.getByText('Available Slots')).toBeInTheDocument();
      expect(screen.getByText('Floor Recommendation')).toBeInTheDocument();
      expect(screen.getByText('Floor Occupancy Table')).toBeInTheDocument();
    });
  });
});
