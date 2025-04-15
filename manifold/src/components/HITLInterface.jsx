import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Divider,
  Grid,
  IconButton,
  Paper,
  Tab,
  Tabs,
  TextField,
  Typography,
  useTheme
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  HourglassEmpty as HourglassEmptyIcon
} from '@mui/icons-material';

// API base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// WebSocket URL
const WS_URL = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws';

/**
 * Human-in-the-Loop Interface Component
 */
const HITLInterface = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hitlRequests, setHitlRequests] = useState([]);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [responseDialogOpen, setResponseDialogOpen] = useState(false);
  const [responseText, setResponseText] = useState('');
  const [responseNotes, setResponseNotes] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);

  // Connect to WebSocket
  useEffect(() => {
    const ws = new WebSocket(`${WS_URL}/hitl`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
      setSocket(ws);
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);
      
      if (data.type === 'new_request') {
        // Add new request to the list
        setHitlRequests(prev => [data.request, ...prev]);
      } else if (data.type === 'update_request') {
        // Update existing request
        setHitlRequests(prev => 
          prev.map(req => 
            req.request_id === data.request.request_id ? data.request : req
          )
        );
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  // Fetch HITL requests
  const fetchHitlRequests = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let url = `${API_BASE_URL}/hitl/requests`;
      
      if (tabValue === 1) {
        url = `${API_BASE_URL}/hitl/requests/status/pending`;
      } else if (tabValue === 2) {
        url = `${API_BASE_URL}/hitl/requests/status/completed`;
      }
      
      const response = await axios.get(url);
      setHitlRequests(response.data);
    } catch (err) {
      console.error('Error fetching HITL requests:', err);
      setError('Failed to fetch HITL requests. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchHitlRequests();
  }, [tabValue]);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Open response dialog
  const handleOpenResponseDialog = (request) => {
    setSelectedRequest(request);
    setResponseText('');
    setResponseNotes('');
    setResponseDialogOpen(true);
  };

  // Close response dialog
  const handleCloseResponseDialog = () => {
    setResponseDialogOpen(false);
    setSelectedRequest(null);
  };

  // Submit response
  const handleSubmitResponse = async () => {
    if (!selectedRequest) return;
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/hitl/requests/${selectedRequest.request_id}/respond`,
        {
          response: responseText,
          response_details: { notes: responseNotes },
          human_id: 'user' // Replace with actual user ID
        }
      );
      
      // Update the request in the list
      setHitlRequests(prev => 
        prev.map(req => 
          req.request_id === selectedRequest.request_id ? response.data : req
        )
      );
      
      handleCloseResponseDialog();
    } catch (err) {
      console.error('Error submitting response:', err);
      setError('Failed to submit response. Please try again.');
    }
  };

  // Get status chip color
  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return theme.palette.warning.main;
      case 'completed':
        return theme.palette.success.main;
      default:
        return theme.palette.info.main;
    }
  };

  // Get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <HourglassEmptyIcon />;
      case 'completed':
        return <CheckCircleIcon />;
      default:
        return <InfoIcon />;
    }
  };

  // Get urgency icon
  const getUrgencyIcon = (urgency) => {
    switch (urgency) {
      case 'high':
        return <WarningIcon color="error" />;
      case 'normal':
        return <InfoIcon color="primary" />;
      case 'low':
        return <InfoIcon color="action" />;
      default:
        return null;
    }
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Human-in-the-Loop Interface
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Chip 
            label={connected ? 'Connected' : 'Disconnected'} 
            color={connected ? 'success' : 'error'} 
            sx={{ mr: 2 }}
          />
          <IconButton onClick={fetchHitlRequests} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} centered>
          <Tab label="All Requests" />
          <Tab label="Pending" />
          <Tab label="Completed" />
        </Tabs>
      </Paper>

      {error && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: theme.palette.error.light }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : hitlRequests.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6">No HITL requests found</Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {hitlRequests.map((request) => (
            <Grid item xs={12} md={6} lg={4} key={request.request_id}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  borderLeft: `4px solid ${getStatusColor(request.status)}`
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Chip 
                      icon={getStatusIcon(request.status)}
                      label={request.status.toUpperCase()} 
                      size="small"
                      sx={{ 
                        bgcolor: getStatusColor(request.status),
                        color: 'white'
                      }}
                    />
                    <Chip 
                      label={request.request_type} 
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                  
                  <Typography variant="h6" component="h2" gutterBottom>
                    {request.request_description}
                  </Typography>
                  
                  <Divider sx={{ my: 1 }} />
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Task ID:</strong> {request.task_id}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Created:</strong> {formatDate(request.created_at)}
                  </Typography>
                  
                  {request.completed_at && (
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      <strong>Completed:</strong> {formatDate(request.completed_at)}
                    </Typography>
                  )}
                  
                  {request.options && request.options.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        <strong>Options:</strong>
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {request.options.map((option, index) => (
                          <Chip 
                            key={index}
                            label={option.option_text || option.option_id} 
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                  
                  {request.response && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        <strong>Response:</strong> {request.response}
                      </Typography>
                      {request.response_details && request.response_details.notes && (
                        <Typography variant="body2" color="text.secondary">
                          <strong>Notes:</strong> {request.response_details.notes}
                        </Typography>
                      )}
                    </Box>
                  )}
                </CardContent>
                
                <CardActions>
                  {request.status === 'pending' ? (
                    <Button 
                      variant="contained" 
                      color="primary"
                      fullWidth
                      onClick={() => handleOpenResponseDialog(request)}
                    >
                      Respond
                    </Button>
                  ) : (
                    <Button 
                      variant="outlined" 
                      color="primary"
                      fullWidth
                      disabled
                    >
                      Completed
                    </Button>
                  )}
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Response Dialog */}
      <Dialog open={responseDialogOpen} onClose={handleCloseResponseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          Respond to Request
        </DialogTitle>
        <DialogContent>
          {selectedRequest && (
            <>
              <DialogContentText gutterBottom>
                {selectedRequest.request_description}
              </DialogContentText>
              
              {selectedRequest.options && selectedRequest.options.length > 0 && (
                <Box sx={{ my: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Available Options:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {selectedRequest.options.map((option, index) => (
                      <Chip 
                        key={index}
                        label={option.option_text || option.option_id} 
                        onClick={() => setResponseText(option.option_id)}
                        color={responseText === option.option_id ? 'primary' : 'default'}
                        sx={{ m: 0.5 }}
                      />
                    ))}
                  </Box>
                </Box>
              )}
              
              <TextField
                label="Your Response"
                value={responseText}
                onChange={(e) => setResponseText(e.target.value)}
                fullWidth
                margin="normal"
                required
              />
              
              <TextField
                label="Additional Notes"
                value={responseNotes}
                onChange={(e) => setResponseNotes(e.target.value)}
                fullWidth
                margin="normal"
                multiline
                rows={4}
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseResponseDialog} color="inherit">
            Cancel
          </Button>
          <Button 
            onClick={handleSubmitResponse} 
            color="primary" 
            variant="contained"
            disabled={!responseText}
          >
            Submit Response
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default HITLInterface;