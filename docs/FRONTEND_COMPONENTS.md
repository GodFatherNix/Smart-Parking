# Frontend Components Documentation

## Components Overview

All components are located in `src/components/` and are ready to use.

---

## 1. Dashboard Component

**File:** `src/components/Dashboard.jsx`

Main container component that orchestrates all other components.

### Features:
- Tab navigation (Overview / Event Log)
- Real-time data display
- Responsive layout

### Props:
None (self-contained)

### Usage:
```jsx
import Dashboard from './components/Dashboard';

function App() {
  return <Dashboard />;
}
```

### Tab Structure:
- **Overview Tab**: Shows floor recommendation and floor status
- **Event Log Tab**: Shows recent parking events

---

## 2. Header Component

**File:** `src/components/Header.jsx`

Top navigation bar with system branding and status.

### Features:
- Project title and description
- System status indicator (green dot = online)
- Clean, professional design

### Props:
None

### Usage:
```jsx
import Header from './components/Header';

export default function App() {
  return (
    <>
      <Header />
      {/* Rest of app */}
    </>
  );
}
```

---

## 3. FloorStatus Component

**File:** `src/components/FloorStatus.jsx`

Displays individual floor occupancy cards in a grid.

### Features:
- Card layout with floor name and occupancy
- Visual progress bar (color-coded: green/yellow/red)
- Available slots count
- Last updated timestamp
- Responsive grid (1-3 columns)

### Props:
```javascript
{
  floors: Array<{
    id: number,
    name: string,
    total_slots: number,
    current_vehicles: number,
    available_slots: number,
    updated_at: string (ISO datetime)
  }>,
  loading: boolean,
  error: string | null
}
```

### Usage:
```jsx
import FloorStatus from './components/FloorStatus';

const floors = [
  {
    id: 1,
    name: 'Ground Floor',
    total_slots: 50,
    current_vehicles: 35,
    available_slots: 15,
    updated_at: new Date().toISOString()
  }
];

<FloorStatus 
  floors={floors} 
  loading={false} 
  error={null} 
/>
```

### Color Coding:
- **Green** (< 50% occupied): Good availability
- **Yellow** (50-80% occupied): Moderate availability
- **Red** (> 80% occupied): Low availability

---

## 4. FloorRecommendation Component

**File:** `src/components/FloorRecommendation.jsx`

Highlights the optimal floor with highest availability.

### Features:
- Large, prominent display
- Floor name and available slots
- Occupancy percentage
- Trending up icon
- Gradient background

### Props:
```javascript
{
  recommendedFloor: {
    id: number,
    name: string,
    total_slots: number,
    available_slots: number
  } | null,
  loading: boolean,
  error: string | null
}
```

### Usage:
```jsx
import FloorRecommendation from './components/FloorRecommendation';

const floor = {
  id: 2,
  name: 'First Floor',
  total_slots: 40,
  available_slots: 28
};

<FloorRecommendation 
  recommendedFloor={floor}
  loading={false}
  error={null}
/>
```

---

## 5. EventLog Component

**File:** `src/components/EventLog.jsx`

Displays recent parking entry/exit events in a scrollable table.

### Features:
- Responsive data table
- Color-coded entry/exit badges
- Timestamp formatting
- Camera ID and vehicle type columns
- Track ID for event tracing
- Hover effects on rows

### Props:
```javascript
{
  events: Array<{
    id: number,
    camera_id: string,
    floor_id: number,
    track_id: string,
    vehicle_type: 'car' | 'motorcycle' | 'bus' | 'truck',
    direction: 'entry' | 'exit',
    timestamp: string (ISO datetime)
  }>,
  loading: boolean,
  error: string | null
}
```

### Usage:
```jsx
import EventLog from './components/EventLog';

const events = [
  {
    id: 1,
    camera_id: 'CAM-001',
    floor_id: 1,
    track_id: 'TRK-2026-001',
    vehicle_type: 'car',
    direction: 'entry',
    timestamp: new Date().toISOString()
  }
];

<EventLog 
  events={events}
  loading={false}
  error={null}
/>
```

### Badge Colors:
- **Entry** (📥): Green background
- **Exit** (📤): Red background

---

## 6. Alert Component

**File:** `src/components/Alert.jsx`

Reusable alert/notification component with multiple types.

### Features:
- 4 alert types: success, error, warning, info
- Icon per type
- Close button
- Color-coded styling

### Props:
```javascript
{
  type: 'success' | 'error' | 'warning' | 'info',
  title: string (optional),
  message: string,
  onClose: function (optional)
}
```

### Usage:
```jsx
import Alert from './components/Alert';

<Alert 
  type="success"
  title="Success!"
  message="Floor data updated successfully"
  onClose={() => setShowAlert(false)}
/>

<Alert 
  type="error"
  message="Failed to load floor data"
/>

<Alert 
  type="warning"
  message="Floor G is nearly full (95%)"
/>

<Alert 
  type="info"
  message="This is mock data for development"
/>
```

---

## Custom Hooks

### useFetch

**File:** `src/hooks/useFetch.js`

Hook for one-time data fetching.

```javascript
import { useFetch } from './hooks/useFetch';
import { floorsAPI } from './services/floorService';

function MyComponent() {
  const { data, loading, error } = useFetch(floorsAPI.getFloors);
  
  // data: response data or null
  // loading: boolean
  // error: error message or null
}
```

### usePolling

**File:** `src/hooks/useFetch.js`

Hook for periodic data polling (real-time updates).

```javascript
import { usePolling } from './hooks/useFetch';
import { floorsAPI } from './services/floorService';

function MyComponent() {
  // Polls every 5 seconds (configurable)
  const { data, loading, error } = usePolling(
    floorsAPI.getFloors, 
    5000  // interval in ms
  );
}
```

---

## API Services

### floorService

**File:** `src/services/floorService.js`

Predefined API functions for backend communication.

```javascript
// Get all floors
floorsAPI.getFloors()

// Get recommended floor
floorsAPI.getRecommendedFloor()

// Create new floor
floorsAPI.createFloor({ name, total_slots })

// Update floor
floorsAPI.updateFloor(floorId, { name, total_slots })

// Get events (with optional filters)
eventsAPI.getEvents({ floor_id, start_date, end_date })

// Submit entry/exit event
eventsAPI.submitEvent({ 
  camera_id, 
  floor_id, 
  track_id, 
  vehicle_type, 
  direction 
})

// Health check
healthAPI.checkHealth()
```

---

## Tailwind CSS Classes

Custom utility classes defined in `src/index.css`:

### Cards
```jsx
<div className="card">  {/* White bg, rounded, shadow, padding */}
  Content
</div>
```

### Buttons
```jsx
<button className="btn-primary">Primary Button</button>
<button className="btn-secondary">Secondary Button</button>
<button className="btn-danger">Danger Button</button>
```

### Badges
```jsx
<span className="badge-success">Success</span>
<span className="badge-warning">Warning</span>
<span className="badge-danger">Danger</span>
```

---

## Component Integration Example

```jsx
import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import Header from './components/Header';
import FloorStatus from './components/FloorStatus';
import FloorRecommendation from './components/FloorRecommendation';
import EventLog from './components/EventLog';
import Alert from './components/Alert';
import { usePolling } from './hooks/useFetch';
import { floorsAPI, eventsAPI } from './services/floorService';

export default function App() {
  const [showAlert, setShowAlert] = useState(true);
  
  // Fetch floors every 5 seconds
  const { data: floors } = usePolling(floorsAPI.getFloors, 5000);
  
  // Fetch recommended floor
  const { data: recommended } = usePolling(
    floorsAPI.getRecommendedFloor,
    5000
  );
  
  // Fetch recent events
  const { data: events } = usePolling(eventsAPI.getEvents, 5000);

  return (
    <>
      <Header />
      <main className="max-w-7xl mx-auto px-4 py-8">
        {showAlert && (
          <Alert 
            type="info"
            message="Dashboard connected to backend"
            onClose={() => setShowAlert(false)}
          />
        )}
        
        <FloorRecommendation recommendedFloor={recommended} />
        <FloorStatus floors={floors} />
        <EventLog events={events} />
      </main>
    </>
  );
}
```

---

## Current Mock Data (for development)

Dashboard comes with mock data to visualize the UI without backend connection.

To switch to real API calls:
1. Replace mock data with `useFetch` or `usePolling` hooks
2. Use services from `src/services/floorService.js`
3. Ensure backend API is running on `http://localhost:8000`

---

## Next Steps

1. **Phase 2**: Backend API endpoints (PUT /floors, POST /events, etc.)
2. **Phase 3**: Connect frontend to real backend APIs
3. **Phase 4**: Add WebSocket support for true real-time updates
