import MockAdapter from 'axios-mock-adapter';
import { vi } from 'vitest';
import apiClient from '../api';

describe('api client retry behavior', () => {
  let mock;

  beforeEach(() => {
    vi.useFakeTimers();
    mock = new MockAdapter(apiClient);
  });

  afterEach(() => {
    mock.restore();
    vi.useRealTimers();
  });

  it('retries retryable GET requests and succeeds', async () => {
    mock.onGet('/retry-success').replyOnce(500).onGet('/retry-success').reply(200, { ok: true });

    const pending = apiClient.get('/retry-success');
    await vi.advanceTimersByTimeAsync(700);
    const response = await pending;

    expect(response.status).toBe(200);
    expect(response.data.ok).toBe(true);
  });

  it('does not retry non-retryable POST by default', async () => {
    mock.onPost('/post-fail').reply(500, { detail: 'server error' });

    await expect(apiClient.post('/post-fail', { a: 1 })).rejects.toHaveProperty('response.status', 500);
  });
});
