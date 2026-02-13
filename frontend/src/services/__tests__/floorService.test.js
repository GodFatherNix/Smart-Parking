import MockAdapter from 'axios-mock-adapter';
import apiClient from '../api';
import { eventsAPI, floorsAPI, healthAPI } from '../floorService';

describe('floorService API integration', () => {
  let mock;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
  });

  afterEach(() => {
    mock.restore();
  });

  it('fetches floors and recommendation', async () => {
    mock.onGet('/floors').reply(200, { success: true, floors: [] });
    mock.onGet('/recommend').reply(200, { success: true, recommended_floor: { id: 1 } });

    const floors = await floorsAPI.getFloors();
    const recommendation = await floorsAPI.getRecommendedFloor();

    expect(floors.success).toBe(true);
    expect(recommendation.recommended_floor.id).toBe(1);
  });

  it('fetches and posts events with params', async () => {
    mock.onGet('/events').reply((config) => {
      expect(config.params.hours).toBe(24);
      return [200, { success: true, events: [] }];
    });
    mock.onPost('/event').reply(200, { success: true, event_id: 10 });

    const events = await eventsAPI.getEvents({ hours: 24 });
    const posted = await eventsAPI.submitEvent({ camera_id: 'cam-1' });

    expect(events.success).toBe(true);
    expect(posted.event_id).toBe(10);
  });

  it('calls health endpoint', async () => {
    mock.onGet('/health').reply(200, { status: 'healthy' });
    const response = await healthAPI.checkHealth();
    expect(response.status).toBe('healthy');
  });
});
