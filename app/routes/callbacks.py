import asyncio
import json
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}
# Store callback data
callback_data: Dict[str, Dict[str, Any]] = {}

class CallbackRequest(BaseModel):
    task_id: str
    callback_url: Optional[str] = None
    data: Dict[str, Any]

class CallbackResponse(BaseModel):
    task_id: str
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime

# Test endpoint to verify routing
@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify routing is working"""
    return {"message": "Callbacks router is working", "timestamp": datetime.now().isoformat()}

# WebSocket endpoint for real-time callbacks
@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    logger.info(f"WebSocket connection attempt from client_id: {client_id}")
    logger.info(f"WebSocket endpoint called with path: /callbacks/ws/{client_id}")
    
    try:
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for client_id: {client_id}")
        active_connections[client_id] = websocket
        
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "welcome",
            "client_id": client_id,
            "message": "WebSocket connection established",
            "timestamp": datetime.now().isoformat()
        }))
        
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()
            message = json.loads(data)
            logger.info(f"Received message from {client_id}: {message}")
            
            # Echo back for testing
            await websocket.send_text(json.dumps({
                "type": "echo",
                "message": f"Received: {message}",
                "timestamp": datetime.now().isoformat()
            }))
            
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
        if client_id in active_connections:
            del active_connections[client_id]
    except Exception as e:
        logger.error(f"Error in WebSocket connection for {client_id}: {str(e)}")
        if client_id in active_connections:
            del active_connections[client_id]
        raise

# HTTP endpoint for registering callbacks
@router.post("/register-callback/")
async def register_callback(request: CallbackRequest):
    """Register a callback for a specific task"""
    try:
        callback_data[request.task_id] = {
            "callback_url": request.callback_url,
            "data": request.data,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"Registered callback for task {request.task_id}")
        
        return JSONResponse({
            "task_id": request.task_id,
            "status": "registered",
            "message": "Callback registered successfully"
        })
        
    except Exception as e:
        logger.error(f"Error registering callback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# HTTP endpoint for triggering callbacks
@router.post("/trigger-callback/{task_id}")
async def trigger_callback(task_id: str, data: Dict[str, Any]):
    """Trigger a callback for a specific task"""
    try:
        if task_id not in callback_data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        callback_info = callback_data[task_id]
        callback_info["status"] = "completed"
        callback_info["result"] = data
        callback_info["completed_at"] = datetime.now().isoformat()
        
        # If there's a callback URL, you could make an HTTP request here
        if callback_info.get("callback_url"):
            # This would be implemented with httpx or requests
            logger.info(f"Would make HTTP callback to: {callback_info['callback_url']}")
        
        return JSONResponse({
            "task_id": task_id,
            "status": "triggered",
            "message": "Callback triggered successfully"
        })
        
    except Exception as e:
        logger.error(f"Error triggering callback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket callback function
async def send_websocket_callback(client_id: str, data: Dict[str, Any]):
    """Send a callback message via WebSocket"""
    if client_id in active_connections:
        try:
            message = {
                "type": "callback",
                "task_id": data.get("task_id"),
                "status": data.get("status", "completed"),
                "data": data.get("data"),
                "timestamp": datetime.now().isoformat()
            }
            
            await active_connections[client_id].send_text(json.dumps(message))
            logger.info(f"Sent WebSocket callback to {client_id}")
            
        except Exception as e:
            logger.error(f"Error sending WebSocket callback to {client_id}: {str(e)}")
            # Remove broken connection
            del active_connections[client_id]

# Background task example with callback
async def process_task_with_callback(task_id: str, client_id: str, data: Dict[str, Any]):
    """Example background task that sends callbacks"""
    try:
        # Simulate some processing
        await asyncio.sleep(2)
        
        # Send progress callback
        await send_websocket_callback(client_id, {
            "task_id": task_id,
            "status": "processing",
            "data": {"progress": 50, "message": "Processing data..."}
        })
        
        # Simulate more processing
        await asyncio.sleep(10)
        
        # Send completion callback
        await send_websocket_callback(client_id, {
            "task_id": task_id,
            "status": "completed",
            "data": {"result": "Task completed successfully", "processed_data": data}
        })
        
    except Exception as e:
        # Send error callback
        await send_websocket_callback(client_id, {
            "task_id": task_id,
            "status": "error",
            "data": {"error": str(e)}
        })

# Endpoint that starts a background task with callbacks
@router.post("/start-task/")
async def start_task_with_callback(
    background_tasks: BackgroundTasks,
    task_data: Dict[str, Any],
    client_id: str
):
    """Start a background task that will send callbacks"""
    task_id = str(uuid.uuid4())
    
    # Add task to background tasks
    background_tasks.add_task(
        process_task_with_callback,
        task_id,
        client_id,
        task_data
    )
    
    return JSONResponse({
        "task_id": task_id,
        "status": "started",
        "message": "Task started successfully. Listen for callbacks via WebSocket."
    })

# Get callback status
@router.get("/callback-status/{task_id}")
async def get_callback_status(task_id: str):
    """Get the status of a callback"""
    if task_id not in callback_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return JSONResponse(callback_data[task_id])

# Get active connections
@router.get("/active-connections/")
async def get_active_connections():
    """Get list of active WebSocket connections"""
    return JSONResponse({
        "active_connections": list(active_connections.keys()),
        "count": len(active_connections)
    })
