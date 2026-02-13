import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Alert from '../Alert';

describe('Alert', () => {
  it('renders title and message', () => {
    render(<Alert type="warning" title="Low Capacity" message="Only 5 slots left." />);

    expect(screen.getByText('Low Capacity')).toBeInTheDocument();
    expect(screen.getByText('Only 5 slots left.')).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();

    render(<Alert type="info" title="Info" message="Message" onClose={onClose} />);
    await user.click(screen.getByRole('button', { name: 'Close alert' }));

    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
