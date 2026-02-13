# SmartPark Frontend

React + Tailwind CSS dashboard for real-time parking management system.

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

Server will run on http://localhost:3000

## Build

```bash
npm run build
```

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues
- `npm run format` - Format code with Prettier

## Project Structure

```
src/
├── components/       # React components
├── pages/           # Page components
├── services/        # API services
├── hooks/           # Custom React hooks
├── utils/           # Utility functions
├── App.jsx          # Main app component
└── main.jsx         # Entry point
```

## API Integration

The frontend connects to the backend API at `http://localhost:8000`. Configure via `.env` file.

## Features

- Real-time floor occupancy display
- Floor recommendation system
- Event log viewer
- Responsive design with Tailwind CSS
- API integration with Axios
