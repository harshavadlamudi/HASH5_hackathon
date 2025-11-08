import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#FF6B35', // Vibrant orange
      light: '#FF8C61',
      dark: '#E55A2B',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#FFA500', // Bright orange
      light: '#FFB733',
      dark: '#CC8400',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#000000', // Black
      paper: '#1A1A1A', // Dark gray cards
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#B0B0B0',
    },
    error: {
      main: '#FF4444',
    },
    warning: {
      main: '#FFA500',
    },
    success: {
      main: '#4CAF50',
    },
    info: {
      main: '#FF6B35',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    allVariants: {
      color: '#FFFFFF',
    },
    h4: {
      fontWeight: 700,
      color: '#FFFFFF',
    },
    h5: {
      fontWeight: 600,
      color: '#FFFFFF',
    },
    h6: {
      fontWeight: 600,
      color: '#FFFFFF',
    },
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#000000',
          color: '#FFFFFF',
          borderBottom: '2px solid #FF6B35',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#2A2A2A',
          border: '1px solid #404040',
          '&:hover': {
            borderColor: '#FF6B35',
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          backgroundColor: '#2A2A2A',
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          backgroundColor: '#2A2A2A',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        contained: {
          backgroundColor: '#FF6B35',
          color: '#FFFFFF',
          fontWeight: 600,
          '&:hover': {
            backgroundColor: '#E55A2B',
          },
        },
        outlined: {
          borderColor: '#FF6B35',
          color: '#FF6B35',
          '&:hover': {
            borderColor: '#E55A2B',
            backgroundColor: 'rgba(255, 107, 53, 0.08)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
        },
        colorPrimary: {
          backgroundColor: '#FF6B35',
          color: '#000000',
        },
        colorSecondary: {
          backgroundColor: '#FFA500',
          color: '#000000',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          color: '#B0B0B0',
          '&.Mui-selected': {
            color: '#FF6B35',
          },
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          backgroundColor: '#333333',
        },
        bar: {
          backgroundColor: '#FF6B35',
        },
      },
    },
  },
});

export default theme;
