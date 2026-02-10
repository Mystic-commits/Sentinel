"""
WebSocket Router

WebSocket endpoint for real-time event streaming with enhanced event types.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..websocket.manager import ws_manager
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time task events.
    
    Clients connect here to receive real-time updates about task progress.
    
    New Event Types (Comprehensive):
    - CONNECTION_ACK: Connection acknowledged
    - HEARTBEAT: Keep-alive ping (every 30s)
    - TASK_STARTED: Task created and started
    - SCAN_PROGRESS: File scanning progress updates
    - PLAN_READY: AI plan generated and ready for review
    - WAITING_FOR_APPROVAL: System waiting for user approval
    - EXECUTION_PROGRESS: File operation execution progress
    - TASK_COMPLETED: Task successfully completed
    - TASK_FAILED: Task failed with error
    
    Legacy Event Types (maintained for compatibility):
    - SCANNING: Scan started
    - SCAN_COMPLETE: Scan finished
    - PLANNING: Plan creation started
    - SAFETY_CHECK: Safety validation passed
    - SAFETY_FAILED: Safety validation failed
    - EXECUTING: Execution started
    - PROGRESS: Execution progress update
    - COMPLETE: Task completed successfully
    - ERROR: Error occurred
    
    Example (JavaScript):
        const ws = new WebSocket('ws://localhost:8000/ws/events');
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log(data.event_type, data.message, data.data);
        };
        
        ws.onopen = () => {
            console.log('Connected to Sentinel WebSocket');
        };
    """
    client_id = str(uuid.uuid4())
    
    # Connect with client ID
    await ws_manager.connect(websocket, client_id)
    logger.info(f"WebSocket client {client_id} connected")
    
    try:
        # Keep connection alive
        # Client can send messages, but we primarily broadcast to them
        while True:
            data = await websocket.receive_text()
            logger.debug(f"WebSocket received from {client_id}: {data}")
            
            # Optional: Handle client messages (e.g., subscriptions, filters)
            # For now, we just keep the connection alive
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket client {client_id} disconnected normally")
        await ws_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        await ws_manager.disconnect(client_id)

