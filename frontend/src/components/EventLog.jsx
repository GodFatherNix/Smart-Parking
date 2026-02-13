import { useMemo, useState } from 'react';
import { Loader } from 'lucide-react';

const EventLog = ({ events, loading, error }) => {
  const [floorFilter, setFloorFilter] = useState('all');
  const [vehicleFilter, setVehicleFilter] = useState('all');
  const [timeRange, setTimeRange] = useState('24');

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader className="w-6 h-6 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading events...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        <strong>Error:</strong> {error}
      </div>
    );
  }

  if (!events || events.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center text-gray-600">
        No events recorded yet
      </div>
    );
  }

  const getDirectionBadge = (direction) => {
    if (direction === 'entry') {
      return <span className="badge-success">ENTRY</span>;
    }
    return <span className="badge-danger">EXIT</span>;
  };

  const floorOptions = useMemo(() => {
    return [...new Set(events.map((event) => String(event.floor_id)))];
  }, [events]);

  const filteredEvents = useMemo(() => {
    const now = Date.now();
    const rangeMs = Number(timeRange) * 60 * 60 * 1000;

    return events.filter((event) => {
      const eventTime = new Date(event.timestamp).getTime();
      const withinTime = now - eventTime <= rangeMs;
      const floorMatch = floorFilter === 'all' || String(event.floor_id) === floorFilter;
      const vehicleMatch = vehicleFilter === 'all' || event.vehicle_type === vehicleFilter;
      return withinTime && floorMatch && vehicleMatch;
    });
  }, [events, floorFilter, vehicleFilter, timeRange]);

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-4 border-b bg-gray-50 grid grid-cols-1 md:grid-cols-3 gap-3">
        <select
          value={floorFilter}
          onChange={(e) => setFloorFilter(e.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="all">All Floors</option>
          {floorOptions.map((floorId) => (
            <option key={floorId} value={floorId}>
              Floor {floorId}
            </option>
          ))}
        </select>

        <select
          value={vehicleFilter}
          onChange={(e) => setVehicleFilter(e.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="all">All Vehicles</option>
          <option value="car">Car</option>
          <option value="motorcycle">Motorcycle</option>
          <option value="bus">Bus</option>
          <option value="truck">Truck</option>
        </select>

        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="1">Last 1 hour</option>
          <option value="6">Last 6 hours</option>
          <option value="24">Last 24 hours</option>
          <option value="168">Last 7 days</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-100 border-b">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Timestamp</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Camera</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Floor</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Vehicle Type</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Direction</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Track ID</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {filteredEvents.map((event) => (
              <tr key={event.id} className="hover:bg-gray-50 transition">
                <td className="px-6 py-3 text-sm text-gray-900">{new Date(event.timestamp).toLocaleString()}</td>
                <td className="px-6 py-3 text-sm text-gray-600">{event.camera_id}</td>
                <td className="px-6 py-3 text-sm text-gray-600">Floor {event.floor_id}</td>
                <td className="px-6 py-3 text-sm text-gray-600 capitalize">{event.vehicle_type}</td>
                <td className="px-6 py-3 text-sm">{getDirectionBadge(event.direction)}</td>
                <td className="px-6 py-3 text-sm text-gray-600 font-mono">{event.track_id}</td>
              </tr>
            ))}
            {filteredEvents.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-sm text-gray-500">
                  No events match the selected filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default EventLog;
