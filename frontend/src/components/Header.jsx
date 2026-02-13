const Header = ({ systemOnline = true, lastUpdated = null }) => {
  const statusText = systemOnline ? 'System Online' : 'System Degraded';
  const statusColor = systemOnline ? 'bg-green-500' : 'bg-yellow-500';

  return (
    <header className="bg-gray-900 text-white shadow-lg sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 py-4 md:py-6">
        <div className="flex flex-col gap-3 md:flex-row md:justify-between md:items-center">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold">SmartPark</h1>
            <p className="text-gray-300 text-sm">Real-time Parking Management System</p>
          </div>
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full animate-pulse ${statusColor}`}></div>
              <span className="text-sm text-gray-300">{statusText}</span>
            </div>
            <div className="text-xs text-gray-400">
              Last refresh: {lastUpdated ? new Date(lastUpdated).toLocaleTimeString() : 'Waiting for data...'}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
