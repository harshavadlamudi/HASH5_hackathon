import React, { useState } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography,
  TextField,
  Button,
  Chip,
  Paper,
  IconButton,
  Divider,
  Alert
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import DownloadIcon from '@mui/icons-material/Download';
import { qaService } from '../services/qaService';

const QUICK_QUESTIONS = [
  'What are my top health risks?',
  'What medications do I need?',
  'What should I do first?',
  'What follow-up appointments do I need?',
];

const QAInterface = ({ report, patientSummary }) => {
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleAsk = async (q) => {
    const questionText = q || question;
    if (!questionText.trim()) return;

    setLoading(true);
    try {
      const cachedReports = {
        patient_id: report.patient_id,
        patient_summary: patientSummary,
        cardiology: report.cardiology,
        radiology: report.radiology,
        endocrinology: report.endocrinology,
        comprehensive: report.comprehensive,
      };

      const response = await qaService.ask(questionText, cachedReports);
      
      setHistory([...history, response]);
      setQuestion('');
    } catch (error) {
      console.error('Error asking question:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={3}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            💬 Ask Questions About This Report
          </Typography>

          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Quick Questions:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {QUICK_QUESTIONS.map((q, index) => (
                <Chip
                  key={index}
                  label={q}
                  onClick={() => handleAsk(q)}
                  disabled={loading}
                  clickable
                />
              ))}
            </Box>
          </Box>

          <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
            <TextField
              fullWidth
              placeholder="Or ask your own question..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
              disabled={loading}
              size="small"
            />
            <Button 
              variant="contained" 
              onClick={() => handleAsk()}
              disabled={loading || !question.trim()}
            >
              {loading ? 'Asking...' : 'Ask'}
            </Button>
          </Box>

          {history.length > 0 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Conversation History ({history.length})
                </Typography>
                <Box>
                  <IconButton 
                    size="small" 
                    onClick={() => {
                      const text = history.map(h => `Q: ${h.question}\n\nA: ${h.answer}\n\n---\n\n`).join('');
                      const blob = new Blob([text], { type: 'text/plain' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = 'qa-conversation.txt';
                      a.click();
                    }}
                    title="Download conversation"
                  >
                    <DownloadIcon />
                  </IconButton>
                  <IconButton 
                    size="small" 
                    color="error"
                    onClick={() => setHistory([])}
                    title="Clear history"
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </Box>
              <Divider sx={{ mb: 2 }} />
              {history.map((item, index) => (
                <Paper key={index} sx={{ p: 2, mb: 2, bgcolor: '#1A1A1A', border: '1px solid', borderColor: '#404040' }}>
                  <Typography variant="subtitle2" color="primary" fontWeight={600} gutterBottom>
                    Q{index + 1}: {item.question}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1, mb: 2, whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                    {item.answer}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip 
                      label={item.ui_type} 
                      size="small" 
                      color="primary"
                      variant="outlined"
                    />
                    {item.sources.map((source, idx) => (
                      <Chip 
                        key={idx}
                        label={source} 
                        size="small" 
                        color="secondary"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Paper>
              ))}
            </Box>
          )}
          {history.length === 0 && (
            <Alert severity="info" sx={{ mt: 2 }}>
              No questions asked yet. Try one of the quick questions above or ask your own!
            </Alert>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default QAInterface;
