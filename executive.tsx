// import React, { useState, useEffect, useRef } from 'react';
// import Box from '@mui/material/Box';
// import Button from '@mui/material/Button';
// import Grid from '@mui/material/Grid';
// import Stack from '@mui/material/Stack';
// import Typography from '@mui/material/Typography';
// import Card from '@mui/material/Card';
// import CardContent from '@mui/material/CardContent';
// import LinearProgress from '@mui/material/LinearProgress';
// import Alert from '@mui/material/Alert';
// import Chip from '@mui/material/Chip';

// // ==============================|| CALLBACK DEMO COMPONENT ||============================== //

// interface Message {
//   type: string;
//   message: string;
//   timestamp: Date;
//   status?: string;
//   data?: any;
// }

// interface Task {
//   task_id: string;
//   result?: any;
// }

// interface CallbackData {
//   status: string;
//   data: any;
// }

// export default function DashboardExecutive() {
//   const [isConnected, setIsConnected] = useState(false);
//   const [messages, setMessages] = useState<Message[]>([]);
//   const [currentTask, setCurrentTask] = useState<Task | null>(null);
//   const [taskStatus, setTaskStatus] = useState('idle');
//   const [progress, setProgress] = useState(0);
//   const [error, setError] = useState<string | null>(null);
  
//   const wsRef = useRef<WebSocket | null>(null);
//   const clientId = useRef(`client_${Math.random().toString(36).substr(2, 9)}`);

//   // WebSocket connection
//   const connectWebSocket = () => {
//     const ws = new WebSocket(`ws://localhost:8000/callbacks/ws/${clientId.current}`);
    
//     ws.onopen = () => {
//       setIsConnected(true);
//       setMessages(prev => [...prev, { type: 'system', message: 'WebSocket connected', timestamp: new Date() }]);
//     };

//     ws.onmessage = (event) => {
//       const data = JSON.parse(event.data);
//       setMessages(prev => [...prev, { ...data, timestamp: new Date() }]);
      
//       // Handle different callback types
//       if (data.type === 'callback') {
//         handleCallback(data);
//       }
//     };

//     ws.onclose = () => {
//       setIsConnected(false);
//       setMessages(prev => [...prev, { type: 'system', message: 'WebSocket disconnected', timestamp: new Date() }]);
//     };

//     ws.onerror = (error) => {
//       setError('WebSocket connection error');
//       console.error('WebSocket error:', error);
//     };

//     wsRef.current = ws;
//   };

//   // Handle incoming callbacks
//   const handleCallback = (callbackData: CallbackData) => {
//     const { status, data: callbackPayload } = callbackData;
    
//     setTaskStatus(status);
    
//     if (status === 'processing') {
//       setProgress(callbackPayload.progress || 0);
//     } else if (status === 'completed') {
//       setProgress(100);
//       setCurrentTask(prev => prev ? { ...prev, result: callbackPayload } : null);
//     } else if (status === 'error') {
//       setError(callbackPayload.error);
//     }
//   };

//   // Start a task with callbacks
//   const startTask = async () => {
//     try {
//       setError(null);
//       setTaskStatus('starting');
//       setProgress(0);
      
//       const response = await fetch(
//         `http://localhost:8000/callbacks/start-task/?client_id=${clientId.current}`,
//         {
//           method: 'POST',
//           headers: {
//             'Content-Type': 'application/json',
//           },
//           body: JSON.stringify({
//             message: 'Hello from React!',
//             timestamp: new Date().toISOString()
//           })
//         }
//       );

//       const result = await response.json();
      
//       if (response.ok) {
//         setCurrentTask(result);
//         setTaskStatus('started');
//         setMessages(prev => [...prev, { 
//           type: 'system', 
//           message: `Task started: ${result.task_id}`, 
//           timestamp: new Date() 
//         }]);
//       } else {
//         setError(result.detail || 'Failed to start task');
//       }
//     } catch (err) {
//       setError('Network error: ' + (err instanceof Error ? err.message : String(err)));
//     }
//   };

//   // Register a callback (HTTP-based)
//   const registerCallback = async () => {
//     try {
//       const taskId = `task_${Math.random().toString(36).substr(2, 9)}`;
      
//       const response = await fetch('http://localhost:8000/callbacks/register-callback/', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({
//           task_id: taskId,
//           callback_url: 'http://localhost:3000/api/callback', // Your React app callback endpoint
//           data: {
//             message: 'Registered callback',
//             timestamp: new Date().toISOString()
//           }
//         })
//       });

//       const result = await response.json();
      
//       if (response.ok) {
//         setMessages(prev => [...prev, { 
//           type: 'system', 
//           message: `Callback registered: ${result.task_id}`, 
//           timestamp: new Date() 
//         }]);
//       } else {
//         setError(result.detail || 'Failed to register callback');
//       }
//     } catch (err) {
//       setError('Network error: ' + (err instanceof Error ? err.message : String(err)));
//     }
//   };

//   // Trigger a callback manually
//   const triggerCallback = async (taskId: string) => {
//     try {
//       const response = await fetch(`http://localhost:8000/callbacks/trigger-callback/${taskId}`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({
//           result: 'Manual trigger result',
//           timestamp: new Date().toISOString()
//         })
//       });

//       const result = await response.json();
      
//       if (response.ok) {
//         setMessages(prev => [...prev, { 
//           type: 'system', 
//           message: `Callback triggered: ${result.task_id}`, 
//           timestamp: new Date() 
//         }]);
//       } else {
//         setError(result.detail || 'Failed to trigger callback');
//       }
//     } catch (err) {
//       setError('Network error: ' + (err instanceof Error ? err.message : String(err)));
//     }
//   };

//   // Connect on component mount
//   useEffect(() => {
//     connectWebSocket();
    
//     return () => {
//       if (wsRef.current) {
//         wsRef.current.close();
//       }
//     };
//   }, []);

//   return (
//     <Grid container spacing={3}>
//       {/* Header */}
//       <Grid size={12}>
//         <Typography variant="h4" gutterBottom>
//           FastAPI Callback Demo
//         </Typography>
//         <Chip 
//           label={isConnected ? 'Connected' : 'Disconnected'} 
//           color={isConnected ? 'success' : 'error'}
//           sx={{ mb: 2 }}
//         />
//       </Grid>

//       {/* Control Panel */}
//       <Grid size={{ xs: 12, md: 6 }}>
//         <Card>
//           <CardContent>
//             <Typography variant="h6" gutterBottom>
//               Control Panel
//             </Typography>
//             <Stack spacing={2}>
//               <Button 
//                 variant="contained" 
//                 onClick={startTask}
//                 disabled={!isConnected || taskStatus === 'processing'}
//               >
//                 Start Background Task
//               </Button>
              
//               <Button 
//                 variant="outlined" 
//                 onClick={registerCallback}
//                 disabled={!isConnected}
//               >
//                 Register HTTP Callback
//               </Button>
              
//               {currentTask && (
//                 <Button 
//                   variant="outlined" 
//                   onClick={() => triggerCallback(currentTask.task_id)}
//                   disabled={!isConnected}
//                 >
//                   Trigger Manual Callback
//                 </Button>
//               )}
//             </Stack>
//           </CardContent>
//         </Card>
//       </Grid>

//       {/* Task Status */}
//       <Grid size={{ xs: 12, md: 6 }}>
//         <Card>
//           <CardContent>
//             <Typography variant="h6" gutterBottom>
//               Task Status
//             </Typography>
//             <Stack spacing={2}>
//               <Typography variant="body2">
//                 Status: <Chip label={String(taskStatus)} color="primary" size="small" />
//               </Typography>
              
//               {taskStatus === 'processing' && (
//                 <Box>
//                   <Typography variant="body2" gutterBottom>
//                     Progress: {String(progress)}%
//                   </Typography>
//                   <LinearProgress variant="determinate" value={progress} />
//                 </Box>
//               )}
              
//               {currentTask && (
//                 <Typography variant="body2">
//                   Task ID: {String(currentTask.task_id)}
//                 </Typography>
//               )}
              
//               {error && (
//                 <Alert severity="error" onClose={() => setError(null)}>
//                   {String(error)}
//                 </Alert>
//               )}
//             </Stack>
//           </CardContent>
//         </Card>
//       </Grid>

//       {/* Messages Log */}
//       <Grid size={12}>
//         <Card>
//           <CardContent>
//             <Typography variant="h6" gutterBottom>
//               Callback Messages
//             </Typography>
//             <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
//               {messages.map((msg, index) => (
//                 <Box key={index} sx={{ mb: 1, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
//                   <Typography variant="caption" color="text.secondary">
//                     {msg.timestamp.toLocaleTimeString()}
//                   </Typography>
//                   <Typography variant="body2">
//                     {msg.type === 'callback' ? (
//                       <span>
//                         <strong>Callback:</strong> {String(msg.status || '')} - {typeof msg.data === 'object' ? JSON.stringify(msg.data) : String(msg.data || '')}
//                       </span>
//                     ) : msg.type === 'echo' ? (
//                       <span>
//                         <strong>Echo:</strong> {String(msg.message || '')}
//                       </span>
//                     ) : (
//                       <span>
//                         <strong>System:</strong> {String(msg.message || '')}
//                       </span>
//                     )}
//                   </Typography>
//                 </Box>
//               ))}
//             </Box>
//           </CardContent>
//         </Card>
//       </Grid>
//     </Grid>
//   );
// }
