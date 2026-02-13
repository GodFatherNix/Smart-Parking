import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import EventLog from '../EventLog';

const now = Date.now();

const events = [
  {
    id: 1,
    camera_id: 'cam-1',
    floor_id: 1,
    track_id: 'trk-1',
    vehicle_type: 'car',
    direction: 'entry',
    timestamp: new Date(now - 15 * 60 * 1000).toISOString(),
  },
  {
    id: 2,
    camera_id: 'cam-2',
    floor_id: 2,
    track_id: 'trk-2',
    vehicle_type: 'truck',
    direction: 'exit',
    timestamp: new Date(now - 30 * 60 * 1000).toISOString(),
  },
  {
    id: 3,
    camera_id: 'cam-3',
    floor_id: 1,
    track_id: 'trk-3',
    vehicle_type: 'motorcycle',
    direction: 'entry',
    timestamp: new Date(now - 8 * 24 * 60 * 60 * 1000).toISOString(),
  },
];

describe('EventLog', () => {
  it('renders events and filters by floor/vehicle/time', async () => {
    const user = userEvent.setup();
    render(<EventLog events={events} loading={false} error={''} />);

    expect(screen.getByText('trk-1')).toBeInTheDocument();
    expect(screen.getByText('trk-2')).toBeInTheDocument();

    await user.selectOptions(screen.getByDisplayValue('All Floors'), '2');
    expect(screen.queryByText('trk-1')).not.toBeInTheDocument();
    expect(screen.getByText('trk-2')).toBeInTheDocument();

    await user.selectOptions(screen.getByDisplayValue('All Vehicles'), 'truck');
    expect(screen.getByText('trk-2')).toBeInTheDocument();

    await user.selectOptions(screen.getByDisplayValue('Truck'), 'car');
    expect(screen.getByText('No events match the selected filters.')).toBeInTheDocument();
  });

  it('shows error and loading states', () => {
    const { rerender } = render(<EventLog events={[]} loading={true} error={''} />);
    expect(screen.getByText('Loading events...')).toBeInTheDocument();

    rerender(<EventLog events={[]} loading={false} error={'Request failed'} />);
    expect(screen.getByText(/Request failed/)).toBeInTheDocument();
  });
});
