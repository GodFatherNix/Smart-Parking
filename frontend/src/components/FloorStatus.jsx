import { Loader } from 'lucide-react';

const FloorStatus = ({ floors, loading, error }) => {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-gray-600">Loading floor data...</span>
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

  if (!floors || floors.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center text-gray-600">
        No floors available
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-100 border-b">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Floor</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Total Slots</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Current Vehicles</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Available Slots</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Occupancy</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Last Updated</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {floors.map((floor) => {
              const occupancyPercent = floor.total_slots > 0 ? (floor.current_vehicles / floor.total_slots) * 100 : 0;
              const occupancyColor =
                occupancyPercent < 50 ? 'text-green-700' : occupancyPercent < 80 ? 'text-yellow-700' : 'text-red-700';

              return (
                <tr key={floor.id} className="hover:bg-gray-50 transition">
                  <td className="px-6 py-4 text-sm font-semibold text-gray-900">{floor.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-700">{floor.total_slots}</td>
                  <td className="px-6 py-4 text-sm text-gray-700">{floor.current_vehicles}</td>
                  <td className="px-6 py-4 text-sm font-semibold text-green-700">{floor.available_slots}</td>
                  <td className={`px-6 py-4 text-sm font-semibold ${occupancyColor}`}>{Math.round(occupancyPercent)}%</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{new Date(floor.updated_at).toLocaleTimeString()}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default FloorStatus;
