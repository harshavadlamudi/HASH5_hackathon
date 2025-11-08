import React from 'react';
import { Container, AppBar, Toolbar, Typography, Box, Grid, Tabs, Tab } from '@mui/material';
import PatientList from './components/PatientList';
import PatientDetail from './components/PatientDetail';
import ReportGenerator from './components/ReportGenerator';
import Dashboard from './components/Dashboard';
import usePatientStore from './store/usePatientStore';

function App() {
  const { selectedPatient } = usePatientStore();
  const [patientSummary, setPatientSummary] = React.useState(null);
  const [activeView, setActiveView] = React.useState(0);

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#000000' }}>
      <AppBar position="sticky" elevation={2}>
        <Toolbar>
          <Box component="img" src="/logo.jpg" alt="Healogue" sx={{ height: 60, mr: 2 }} />
          <Typography variant="h5" sx={{ fontWeight: 600, flexGrow: 1 }}>
            Healogue
          </Typography>
          <Tabs 
            value={activeView} 
            onChange={(e, v) => setActiveView(v)}
            textColor="inherit"
            sx={{ mr: 2 }}
          >
            <Tab label="Dashboard" sx={{ color: 'white', textTransform: 'none' }} />
            <Tab label="Patients" sx={{ color: 'white', textTransform: 'none' }} />
          </Tabs>
          <Typography variant="body2" sx={{ color: '#FF6B35' }}>
            AI-Powered Healthcare Assistant
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ py: 3 }}>
        {activeView === 0 && <Dashboard />}
        
        {activeView === 1 && (
          <>
            <Box sx={{ mb: 3 }}>
              <PatientList />
            </Box>
            
            {selectedPatient && (
              <Grid container spacing={3}>
                <Grid item xs={12} md={5}>
                  <PatientDetail patientId={selectedPatient.id} onSummaryLoad={setPatientSummary} />
                </Grid>
                <Grid item xs={12} md={7}>
                  <ReportGenerator 
                    patientId={selectedPatient.id} 
                    patientName={selectedPatient.name}
                    patientSummary={patientSummary}
                  />
                </Grid>
              </Grid>
            )}
            
            {!selectedPatient && (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <Typography variant="h6" color="text.secondary">
                  👆 Select a patient from the dropdown above to view details
                </Typography>
              </Box>
            )}
          </>
        )}
      </Container>
    </Box>
  );
}

export default App;
