import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import Header from './Header';
import FloorStatus from './FloorStatus';
import FloorRecommendation from './FloorRecommendation';
import EventLog from './EventLog';
import Alert from './Alert';
import AvailableSlots from './AvailableSlots';
import CameraFeed from './CameraFeed';
import { eventsAPI, floorsAPI } from '../services/floorService';
import { createRealtimeClient } from '../services/realtime';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [floors, setFloors] = useState([]);
  const [events, setEvents] = useState([]);
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [overviewError, setOverviewError] = useState('');
  const [eventsError, setEventsError] = useState('');
  const [alerts, setAlerts] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const alertHistoryRef = useRef({});
  const wsClientRef = useRef(null);

  const floorsPollMs = Number(import.meta.env.VITE_FLOORS_POLL_MS || 5000);
  const eventsPollMs = Number(import.meta.env.VITE_EVENTS_POLL_MS || 5000);

  const pushAlert = useCallback((type, title, message, dedupeKey = null) => {
    if (dedupeKey) {
      const now = Date.now();
      const lastSeenAt = alertHistoryRef.current[dedupeKey] || 0;
      if (now - lastSeenAt < 15000) {
        return;
      }
      alertHistoryRef.current[dedupeKey] = now;
    }

    const id = Date.now() + Math.random();
    setAlerts((prev) => [...prev, { id, type, title, message }]);
    setTimeout(() => {
      setAlerts((prev) => prev.filter((alert) => alert.id !== id));
    }, 5000);
  }, []);

  const fetchOverviewData = useCallback(async (background = true) => {
    try {
      if (!background) {
        setLoading(true);
      }

      const [floorsResponse, recommendationResponse] = await Promise.all([
        floorsAPI.getFloors(),
        floorsAPI.getRecommendedFloor(),
      ]);

      setFloors(floorsResponse.floors || []);
      setRecommendation(recommendationResponse || null);
      setLastUpdated(new Date().toISOString());
      setOverviewError('');
    } catch (err) {
      const detail = err?.userMessage || 'Failed to fetch overview data';
      setOverviewError(detail);
      pushAlert('error', 'API Error', detail, 'overview-api-error');
    } finally {
      if (!background) {
        setLoading(false);
      }
    }
  }, [pushAlert]);

  const fetchEventsData = useCallback(async (background = true) => {
    try {
      if (!background) {
        setEventsLoading(true);
      }

      const response = await eventsAPI.getEvents({ hours: 24, limit: 500, offset: 0 });
      setEvents(response.events || []);
      setEventsError('');
    } catch (err) {
      const detail = err?.userMessage || 'Failed to fetch events';
      setEventsError(detail);
      pushAlert('warning', 'Event Log Error', detail, 'events-api-error');
    } finally {
      if (!background) {
        setEventsLoading(false);
      }
    }
  }, [pushAlert]);

  useEffect(() => {
    fetchOverviewData(false);
    fetchEventsData(false);

    const overviewInterval = setInterval(() => fetchOverviewData(true), floorsPollMs);
    const eventsInterval = setInterval(() => fetchEventsData(true), eventsPollMs);

    return () => {
      clearInterval(overviewInterval);
      clearInterval(eventsInterval);
    };
  }, [eventsPollMs, fetchEventsData, fetchOverviewData, floorsPollMs]);

  useEffect(() => {
    wsClientRef.current = createRealtimeClient({
      onOpen: () => {
        setWsConnected(true);
        pushAlert('info', 'Realtime Connected', 'WebSocket realtime stream connected.', 'ws-connected');
      },
      onClose: () => {
        setWsConnected(false);
      },
      onError: () => {
        setWsConnected(false);
      },
      onMessage: (payload) => {
        const type = payload?.type;
        const data = payload?.data || {};

        if (type === 'floors_update' && Array.isArray(data.floors)) {
          setFloors(data.floors);
          setLastUpdated(new Date().toISOString());
          setOverviewError('');
        }

        if (type === 'recommendation_update' && data.recommendation) {
          setRecommendation(data.recommendation);
          setLastUpdated(new Date().toISOString());
          setOverviewError('');
        }

        if (type === 'events_update' && Array.isArray(data.events)) {
          setEvents(data.events);
          setEventsError('');
        }

        if (type === 'event_created' && data.event) {
          setEvents((prev) => [data.event, ...prev].slice(0, 500));
          setEventsError('');
        }
      },
    });

    wsClientRef.current.connect();

    return () => {
      wsClientRef.current?.close();
    };
  }, [pushAlert]);

  useEffect(() => {
    if (floors.length === 0) {
      return;
    }
    const totalAvailable = floors.reduce((sum, floor) => sum + floor.available_slots, 0);
    if (totalAvailable <= 10) {
      pushAlert(
        'warning',
        'Low Availability',
        `Only ${totalAvailable} parking slots remain across all floors.`,
        'low-availability'
      );
    }
  }, [floors, pushAlert]);

  const orderedFloors = useMemo(() => {
    return [...floors].sort((a, b) => a.id - b.id);
  }, [floors]);

  const navItems = useMemo(
    () => [
      { id: 'overview', label: 'Overview', description: 'Capacity, recommendation, occupancy' },
      { id: 'events', label: 'Event Log', description: 'Entry/exit timeline and filters' },
    ],
    []
  );

  const isSystemOnline = !overviewError;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header systemOnline={isSystemOnline} lastUpdated={lastUpdated} />

      <main className="max-w-7xl mx-auto px-4 py-6 md:py-8">
        <div className="mb-4">
          <Alert
            type={wsConnected ? 'success' : 'info'}
            title={wsConnected ? 'Realtime Stream Active' : 'Polling Mode Active'}
            message={
              wsConnected
                ? 'WebSocket updates are live for floor and event data.'
                : 'Using 5-second polling for floor and event updates.'
            }
          />
        </div>

        <div className="mb-6 space-y-3">
          {alerts.map((alert) => (
            <Alert
              key={alert.id}
              type={alert.type}
              title={alert.title}
              message={alert.message}
              onClose={() => setAlerts((prev) => prev.filter((item) => item.id !== alert.id))}
            />
          ))}
          {overviewError && alerts.length === 0 && <Alert type="error" title="Data Error" message={overviewError} />}
        </div>

        <div className="md:hidden mb-6 overflow-x-auto">
          <div className="flex gap-2 min-w-max">
            {navItems.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-full border text-sm font-medium transition ${
                  activeTab === tab.id
                    ? 'bg-blue-600 border-blue-600 text-white'
                    : 'bg-white border-gray-300 text-gray-700 hover:border-gray-400'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-[240px,1fr] gap-6">
          <aside className="hidden md:block">
            <div className="bg-white rounded-lg shadow-md p-3 sticky top-28">
              <p className="px-3 py-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Navigation</p>
              <nav className="space-y-1">
                {navItems.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full text-left px-3 py-3 rounded-lg transition ${
                      activeTab === tab.id ? 'bg-blue-50 text-blue-700' : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    <div className="font-semibold text-sm">{tab.label}</div>
                    <div className="text-xs text-gray-500 mt-1">{tab.description}</div>
                  </button>
                ))}
              </nav>
            </div>
          </aside>

          <section>
            {activeTab === 'overview' && (
              <div className="space-y-8">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Available Slots</h2>
                  <AvailableSlots floors={orderedFloors} loading={loading} />
                </div>

                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Floor Recommendation</h2>
                  <FloorRecommendation recommendation={recommendation} loading={loading} error={overviewError} />
                </div>

                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Camera Feed</h2>
                  <CameraFeed />
                </div>

                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Floor Occupancy Table</h2>
                  <FloorStatus floors={orderedFloors} loading={loading} error={overviewError} />
                </div>
              </div>
            )}

            {activeTab === 'events' && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Event Log Viewer</h2>
                <EventLog events={events} loading={eventsLoading} error={eventsError} />
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
