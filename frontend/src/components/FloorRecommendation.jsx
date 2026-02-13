import { TrendingUp } from 'lucide-react';

const FloorRecommendation = ({ recommendation, loading, error }) => {
  if (loading) {
    return <div className="card animate-pulse h-24"></div>;
  }

  if (error) {
    return (
      <div className="card bg-red-50 border border-red-200">
        <p className="text-red-800 text-sm">{error}</p>
      </div>
    );
  }

  if (!recommendation || !recommendation.recommended_floor) {
    return <div className="card bg-gray-50 text-gray-600">No recommendation available</div>;
  }

  const recommendedFloor = recommendation.recommended_floor;
  const alternatives = recommendation.available_alternatives || [];

  return (
    <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200">
      <div className="flex items-start justify-between gap-6">
        <div>
          <p className="text-gray-600 text-sm mb-1">Recommended Floor</p>
          <h3 className="text-3xl font-bold text-gray-900">{recommendedFloor.name}</h3>
          <p className="text-sm text-gray-600 mt-2">
            {recommendedFloor.available_slots} available slots (
            {Math.round((recommendedFloor.available_slots / recommendedFloor.total_slots) * 100)}%)
          </p>
          <p className="text-sm text-blue-800 mt-2">{recommendation.reason}</p>
          {alternatives.length > 0 && (
            <p className="text-xs text-gray-600 mt-2">
              Alternatives: {alternatives.map((floor) => floor.name).join(', ')}
            </p>
          )}
        </div>
        <div className="bg-blue-600 rounded-full p-3">
          <TrendingUp className="w-8 h-8 text-white" />
        </div>
      </div>
    </div>
  );
};

export default FloorRecommendation;
