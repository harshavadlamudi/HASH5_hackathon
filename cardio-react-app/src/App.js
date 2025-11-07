import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar, ScatterChart, Scatter } from 'recharts';
import './App.css';

const DATASTORE_ID = 'b4e3d8f5c2a1b9e7d6f8a2c4e1b3d5f7';

function App() {
  const [cardioData, setCardioData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState({});
  const [selectedCharts, setSelectedCharts] = useState(['bp', 'hr']);

  const fetchCardioData = async () => {
    setLoading(true);
    try {
      // Mock data for demo - replace with actual AWS HealthLake API call
      const mockData = [
        { date: '2024-01-01', systolic: 120, diastolic: 80, heartRate: 72, patientId: 'P001' },
        { date: '2024-01-02', systolic: 125, diastolic: 82, heartRate: 75, patientId: 'P001' },
        { date: '2024-01-03', systolic: 118, diastolic: 78, heartRate: 70, patientId: 'P002' },
        { date: '2024-01-04', systolic: 130, diastolic: 85, heartRate: 78, patientId: 'P002' },
        { date: '2024-01-05', systolic: 122, diastolic: 81, heartRate: 73, patientId: 'P003' }
      ];
      
      setCardioData(mockData);
      setMetrics({
        totalMeasurements: mockData.length,
        uniquePatients: [...new Set(mockData.map(d => d.patientId))].length,
        avgSystolic: Math.round(mockData.reduce((sum, d) => sum + d.systolic, 0) / mockData.length),
        avgHeartRate: Math.round(mockData.reduce((sum, d) => sum + d.heartRate, 0) / mockData.length)
      });
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchCardioData();
  }, []);

  const handleChartToggle = (chartType) => {
    setSelectedCharts(prev => 
      prev.includes(chartType) 
        ? prev.filter(c => c !== chartType)
        : [...prev, chartType]
    );
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🫀 Cardio Data Visualizer</h1>
        <button onClick={fetchCardioData} disabled={loading}>
          {loading ? 'Loading...' : 'Refresh Data'}
        </button>
      </header>

      <div className="metrics">
        <div className="metric">
          <h3>{metrics.totalMeasurements || 0}</h3>
          <p>Total Measurements</p>
        </div>
        <div className="metric">
          <h3>{metrics.uniquePatients || 0}</h3>
          <p>Unique Patients</p>
        </div>
        <div className="metric">
          <h3>{metrics.avgSystolic || 0}</h3>
          <p>Avg Systolic BP</p>
        </div>
        <div className="metric">
          <h3>{metrics.avgHeartRate || 0}</h3>
          <p>Avg Heart Rate</p>
        </div>
      </div>

      <div className="controls">
        <label>
          <input 
            type="checkbox" 
            checked={selectedCharts.includes('bp')}
            onChange={() => handleChartToggle('bp')}
          />
          Blood Pressure Trends
        </label>
        <label>
          <input 
            type="checkbox" 
            checked={selectedCharts.includes('hr')}
            onChange={() => handleChartToggle('hr')}
          />
          Heart Rate Analysis
        </label>
        <label>
          <input 
            type="checkbox" 
            checked={selectedCharts.includes('summary')}
            onChange={() => handleChartToggle('summary')}
          />
          Patient Summary
        </label>
      </div>

      <div className="charts">
        {selectedCharts.includes('bp') && (
          <div className="chart">
            <h3>Blood Pressure Trends</h3>
            <LineChart width={600} height={300} data={cardioData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="systolic" stroke="#8884d8" name="Systolic" />
              <Line type="monotone" dataKey="diastolic" stroke="#82ca9d" name="Diastolic" />
            </LineChart>
          </div>
        )}

        {selectedCharts.includes('hr') && (
          <div className="chart">
            <h3>Heart Rate Analysis</h3>
            <ScatterChart width={600} height={300} data={cardioData}>
              <CartesianGrid />
              <XAxis dataKey="date" />
              <YAxis dataKey="heartRate" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter dataKey="heartRate" fill="#8884d8" />
            </ScatterChart>
          </div>
        )}

        {selectedCharts.includes('summary') && (
          <div className="chart">
            <h3>Patient Summary</h3>
            <BarChart width={600} height={300} data={cardioData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="patientId" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="systolic" fill="#8884d8" name="Systolic BP" />
              <Bar dataKey="heartRate" fill="#82ca9d" name="Heart Rate" />
            </BarChart>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;