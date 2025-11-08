import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  Typography,
  LinearProgress,
  Tabs,
  Tab,
  IconButton,
  Tooltip
} from '@mui/material';
import PrintIcon from '@mui/icons-material/Print';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import DownloadIcon from '@mui/icons-material/Download';
import { reportService } from '../services/reportService';
import QAInterface from './QAInterface';

const ReportGenerator = ({ patientId, patientName, patientSummary }) => {
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState('');
  const [report, setReport] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    setGenerating(true);
    setProgress('Starting report generation...');
    setReport(null);

    try {
      const { job_id } = await reportService.generate(patientId);
      
      const completedReport = await reportService.pollUntilComplete(
        job_id,
        (status) => {
          setProgress(status.progress || status.status);
        }
      );

      setReport(completedReport);
      setProgress('Report completed!');
    } catch (error) {
      setProgress(`Error: ${error.message}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <Box sx={{ mb: 3 }}>
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h5" fontWeight={600} gutterBottom>
            📊 Comprehensive Medical Report
          </Typography>

          {!report && (
            <Box>
              <Button 
                variant="contained" 
                size="large"
                onClick={handleGenerate}
                disabled={generating}
                fullWidth
                sx={{ 
                  py: 1.5,
                  fontSize: '1rem',
                  fontWeight: 600,
                  textTransform: 'none'
                }}
              >
                {generating ? '⏳ Generating Report...' : '✨ Generate Comprehensive Report'}
              </Button>

              {generating && (
                <Box sx={{ mt: 3, p: 2, bgcolor: 'primary.50', borderRadius: 1 }}>
                  <LinearProgress sx={{ mb: 1.5 }} />
                  <Typography variant="body2" color="primary.dark" fontWeight={500}>
                    {progress}
                  </Typography>
                </Box>
              )}
            </Box>
          )}

          {report && (
            <Box>
              <Box sx={{ p: 1.5, bgcolor: 'success.50', borderRadius: 1, mb: 2 }}>
                <Typography variant="body2" color="success.dark" fontWeight={500}>
                  ✅ Report generated for {report.patient_name}
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Tabs 
                  value={activeTab} 
                  onChange={(e, v) => setActiveTab(v)} 
                  sx={{ flexGrow: 1 }}
                >
                  <Tab label="📊 Overview" sx={{ textTransform: 'none', fontWeight: 600 }} />
                  <Tab label="❤️ Cardiology" sx={{ textTransform: 'none', fontWeight: 600 }} />
                  <Tab label="🔬 Radiology" sx={{ textTransform: 'none', fontWeight: 600 }} />
                  <Tab label="🩸 Endocrinology" sx={{ textTransform: 'none', fontWeight: 600 }} />
                </Tabs>
                <Box>
                  <Tooltip title="Copy to clipboard">
                    <IconButton 
                      size="small"
                      onClick={() => {
                        const tabNames = ['comprehensive', 'cardiology', 'radiology', 'endocrinology'];
                        const content = report[tabNames[activeTab]];
                        navigator.clipboard.writeText(content);
                        setCopied(true);
                        setTimeout(() => setCopied(false), 2000);
                      }}
                    >
                      <ContentCopyIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Download as text">
                    <IconButton 
                      size="small"
                      onClick={() => {
                        const tabNames = ['comprehensive', 'cardiology', 'radiology', 'endocrinology'];
                        const tabLabels = ['Overview', 'Cardiology', 'Radiology', 'Endocrinology'];
                        const content = report[tabNames[activeTab]];
                        const blob = new Blob([content], { type: 'text/plain' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `${report.patient_name}-${tabLabels[activeTab]}-Report.txt`;
                        a.click();
                      }}
                    >
                      <DownloadIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Print">
                    <IconButton 
                      size="small"
                      onClick={() => {
                        const tabNames = ['comprehensive', 'cardiology', 'radiology', 'endocrinology'];
                        const tabLabels = ['Overview', 'Cardiology', 'Radiology', 'Endocrinology'];
                        const content = report[tabNames[activeTab]];
                        const printWindow = window.open('', '', 'width=800,height=600');
                        printWindow.document.write(`
                          <html>
                            <head>
                              <title>${report.patient_name} - ${tabLabels[activeTab]} Report</title>
                              <style>
                                body { font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }
                                h1 { color: #1976d2; }
                                pre { white-space: pre-wrap; }
                              </style>
                            </head>
                            <body>
                              <h1>${report.patient_name} - ${tabLabels[activeTab]} Report</h1>
                              <pre>${content}</pre>
                            </body>
                          </html>
                        `);
                        printWindow.document.close();
                        printWindow.print();
                      }}
                    >
                      <PrintIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
              {copied && (
                <Typography variant="caption" color="success.main" sx={{ display: 'block', mb: 1 }}>
                  ✓ Copied to clipboard!
                </Typography>
              )}

              <Box sx={{ mt: 2, p: 2.5, bgcolor: '#1A1A1A', borderRadius: 1, maxHeight: 400, overflow: 'auto', border: '1px solid', borderColor: '#404040' }}>
                {activeTab === 0 && (
                  <Typography variant="body2" style={{ whiteSpace: 'pre-wrap' }}>
                    {report.comprehensive}
                  </Typography>
                )}
                {activeTab === 1 && (
                  <Typography variant="body2" style={{ whiteSpace: 'pre-wrap' }}>
                    {report.cardiology}
                  </Typography>
                )}
                {activeTab === 2 && (
                  <Typography variant="body2" style={{ whiteSpace: 'pre-wrap' }}>
                    {report.radiology}
                  </Typography>
                )}
                {activeTab === 3 && (
                  <Typography variant="body2" style={{ whiteSpace: 'pre-wrap' }}>
                    {report.endocrinology}
                  </Typography>
                )}
              </Box>

              <Button 
                variant="outlined" 
                onClick={() => setReport(null)}
                sx={{ mt: 2 }}
              >
                Generate New Report
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      {report && (
        <QAInterface report={report} patientSummary={patientSummary} />
      )}
    </Box>
  );
};

export default ReportGenerator;
