import apiClient from './api';

export const floorsAPI = {
  // Get all floors with occupancy
  getFloors: async () => {
    const response = await apiClient.get('/floors');
    return response.data;
  },

  // Get recommended floor
  getRecommendedFloor: async () => {
    const response = await apiClient.get('/recommend');
    return response.data;
  },

  // Create new floor
  createFloor: async (floorData) => {
    const response = await apiClient.post('/floors', floorData);
    return response.data;
  },

  // Update floor
  updateFloor: async (floorId, floorData) => {
    const response = await apiClient.put(`/floors/${floorId}`, floorData);
    return response.data;
  },
};

export const eventsAPI = {
  // Get events with optional filtering
  getEvents: async (filters = {}) => {
    const response = await apiClient.get('/events', { params: filters });
    return response.data;
  },

  // Submit entry/exit event from vision service
  submitEvent: async (eventData) => {
    const response = await apiClient.post('/event', eventData);
    return response.data;
  },
};

export const healthAPI = {
  // Health check
  checkHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};
