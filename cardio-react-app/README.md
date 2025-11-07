# Cardio Data Visualizer - React App

Minimal React application for visualizing cardiovascular patient data from AWS HealthLake.

## 🚀 Quick Start

```bash
# Install and run
start.bat

# Or manually
npm install
npm start
```

## 📊 Features

- **Blood Pressure Trends** - Line charts for systolic/diastolic BP
- **Heart Rate Analysis** - Scatter plots by patient
- **Patient Summary** - Bar charts of measurements
- **Real-time Metrics** - Dashboard with key stats
- **Interactive Controls** - Toggle charts on/off

## 🛠️ Tech Stack

- React 18
- Recharts (charts)
- AWS SDK (HealthLake integration)
- CSS Grid (responsive layout)

## 📁 Structure

```
src/
├── App.js              # Main component
├── App.css             # Styles
├── HealthLakeService.js # AWS integration
└── index.js            # Entry point
```

## 🔧 AWS Integration

Replace mock data in `HealthLakeService.js` with actual AWS HealthLake API calls. Requires backend API for CORS and authentication.

## 🌐 Access

App runs on `http://localhost:3000`