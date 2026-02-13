const AvailableSlots = ({ floors = [], loading }) => {
  const totalSlots = floors.reduce((sum, floor) => sum + floor.total_slots, 0);
  const occupiedSlots = floors.reduce((sum, floor) => sum + floor.current_vehicles, 0);
  const availableSlots = floors.reduce((sum, floor) => sum + floor.available_slots, 0);
  const occupancyPercent = totalSlots > 0 ? Math.round((occupiedSlots / totalSlots) * 100) : 0;

  if (loading) {
    return <div className="card animate-pulse h-28"></div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="card">
        <p className="text-sm text-gray-500">Total Capacity</p>
        <p className="text-3xl font-bold text-gray-900">{totalSlots}</p>
      </div>
      <div className="card">
        <p className="text-sm text-gray-500">Occupied</p>
        <p className="text-3xl font-bold text-red-600">{occupiedSlots}</p>
      </div>
      <div className="card">
        <p className="text-sm text-gray-500">Available</p>
        <p className="text-3xl font-bold text-green-600">{availableSlots}</p>
      </div>
      <div className="card">
        <p className="text-sm text-gray-500">Occupancy</p>
        <p className="text-3xl font-bold text-blue-700">{occupancyPercent}%</p>
      </div>
    </div>
  );
};

export default AvailableSlots;
