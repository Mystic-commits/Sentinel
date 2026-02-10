"""
WebSocket Connection Manager

Manages WebSocket connections with connection tracking, heartbeat, and event broadcasting.
"""

from fastapi import WebSocket
from typing import Dict, Optional
import asyncio
import logging
import uuid
from datetime import datetime

from ..models.events import WebSocketEvent, EventType, ConnectionEvent, HeartbeatEvent

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections and event broadcasting.
    
    Features:
    - Connection tracking with unique client IDs
    - Automatic heartbeat keep-alive
    - Thread-safe connection management
    - Automatic cleanup of dead connections
    - Convenience methods for common events
    """
    
    def __init__(self):
        # Active connections mapped by client ID
        self.active_connections: Dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()
        self._heartbeat_task: Optional[asyncio.Task] = None
        logger.info("WebSocketManager initialized")
    
    async def startup(self):
        """Called on server startup."""
        logger.info("WebSocketManager starting up...")
        
        # Start heartbeat task
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        logger.info("WebSocketManager startup complete")
    
    async def shutdown(self):
        """Called on server shutdown - closes all connections."""
        logger.info("WebSocketManager shutting down...")
        
        # Cancel heartbeat
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        async with self._lock:
            connections = list(self.active_connections.values())
            self.active_connections.clear()
        
        for connection in connections:
            try:
                await connection.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
        
        logger.info("WebSocketManager shutdown complete")
    
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> str:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection to accept
            client_id: Optional client ID (auto-generated if not provided)
            
        Returns:
            str: Client ID for this connection
        """
        if client_id is None:
            client_id = str(uuid.uuid4())
        
        await websocket.accept()
        
        async with self._lock:
            self.active_connections[client_id] = websocket
        
        logger.info(f"Client {client_id} connected. Total: {len(self.active_connections)}")
        
        # Send connection acknowledgment
        event = ConnectionEvent(
            message="Connected to Sentinel WebSocket",
            data={"client_id": client_id}
        )
        await self.send_to_client(client_id, event)
        
        return client_id
    
    async def disconnect(self, client_id: str):
        """
        Unregister a WebSocket connection.
        
        Args:
            client_id: Client ID to disconnect
        """
        async with self._lock:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
        
        logger.info(f"Client {client_id} disconnected. Total: {len(self.active_connections)}")
    
    async def send_to_client(self, client_id: str, event: WebSocketEvent):
        """
        Send event to a specific client.
        
        Args:
            client_id: Client ID to send to
            event: Event to send
        """
        if client_id not in self.active_connections:
            logger.warning(f"Client {client_id} not found")
            return
        
        websocket = self.active_connections[client_id]
        
        try:
            await websocket.send_text(event.json())
            logger.debug(f"Sent {event.event_type} to client {client_id}")
        except Exception as e:
            logger.error(f"Error sending to client {client_id}: {e}")
            await self.disconnect(client_id)
    
    async def broadcast(self, event: WebSocketEvent):
        """
        Broadcast an event to all connected clients.
        
        Args:
            event: Event to broadcast
        """
        if not self.active_connections:
            logger.debug("No active connections to broadcast to")
            return
        
        dead_clients = []
        
        # Get snapshot of connections
        async with self._lock:
            connections = dict(self.active_connections)
        
        # Broadcast to all
        for client_id, websocket in connections.items():
            try:
                await websocket.send_text(event.json())
            except Exception as e:
                logger.warning(f"Failed to send to client {client_id}: {e}")
                dead_clients.append(client_id)
        
        # Clean up dead connections
        if dead_clients:
            for client_id in dead_clients:
                await self.disconnect(client_id)
        
        logger.debug(f"Broadcast {event.event_type} to {len(connections)} clients")
    
    async def broadcast_task_event(
        self,
        event_type: EventType,
        task_id: str,
        message: Optional[str] = None,
        data: Optional[Dict] = None
    ):
        """
        Convenience method to broadcast a task event.
        
        Args:
            event_type: Type of event
            task_id: Task ID
            message: Optional message
            data: Optional additional data
        """
        event = WebSocketEvent(
            event_type=event_type,
            task_id=task_id,
            message=message,
            data=data or {}
        )
        await self.broadcast(event)
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats to keep connections alive."""
        while True:
            try:
                await asyncio.sleep(30)  # Every 30 seconds
                
                event = HeartbeatEvent(message="ping")
                await self.broadcast(event)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
    
    def get_connection_count(self) -> int:
        """Get number of active connections."""
        return len(self.active_connections)


# Global singleton instance
ws_manager = WebSocketManager()

