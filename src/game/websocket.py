from typing import Dict, List, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import asyncio
from datetime import datetime

from src.db.session import get_db
from src.db.models import User, GameInstance
from src.auth.deps import get_current_user_ws
from src.game.state_manager import GameStateManager

class ConnectionManager:
    """Manages WebSocket connections for game instances."""
    
    def __init__(self):
        """Initialize the connection manager."""
        # Map of game_id -> list of connected websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Map of game_id -> last event timestamp
        self.last_events: Dict[str, datetime] = {}
    
    async def connect(self, websocket: WebSocket, game_id: str):
        """Connect a websocket to a game instance."""
        await websocket.accept()
        
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
            self.last_events[game_id] = datetime.utcnow()
        
        self.active_connections[game_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, game_id: str):
        """Disconnect a websocket from a game instance."""
        if game_id in self.active_connections:
            if websocket in self.active_connections[game_id]:
                self.active_connections[game_id].remove(websocket)
            
            # Clean up if no more connections
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
                if game_id in self.last_events:
                    del self.last_events[game_id]
    
    async def broadcast(self, game_id: str, message: Dict[str, Any]):
        """Broadcast a message to all connected clients for a game instance."""
        if game_id in self.active_connections:
            # Update last event timestamp
            self.last_events[game_id] = datetime.utcnow()
            
            # Add timestamp to message
            message["timestamp"] = datetime.utcnow().isoformat()
            
            # Broadcast to all connections
            for connection in self.active_connections[game_id]:
                await connection.send_json(message)
    
    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send a message to a specific client."""
        # Add timestamp to message
        message["timestamp"] = datetime.utcnow().isoformat()
        await websocket.send_json(message)

# Create a global connection manager
manager = ConnectionManager()
# Create a global game state manager
game_state_manager = GameStateManager()

async def get_game_instance(game_id: str, user_id: str, db: AsyncSession) -> Optional[GameInstance]:
    """Get a game instance if it exists and belongs to the user."""
    stmt = select(GameInstance).where(
        GameInstance.id == game_id,
        GameInstance.user_id == user_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def handle_game_websocket(
    websocket: WebSocket,
    game_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_ws)
):
    """Handle WebSocket connections for a game instance."""
    # Verify game instance exists and belongs to user
    game_instance = await get_game_instance(game_id, current_user.id, db)
    if not game_instance:
        await websocket.close(code=4004, reason="Game instance not found or access denied")
        return
    
    # Connect to the game
    await manager.connect(websocket, game_id)
    
    # Load game instance
    await game_state_manager.load_game_instance(game_id, db)
    
    # Send initial game state
    await manager.send_personal_message(
        websocket,
        {
            "type": "game_state",
            "data": {
                "position": game_instance.current_position,
                "game_state": game_instance.game_state
            }
        }
    )
    
    try:
        # Main WebSocket loop
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            
            try:
                # Parse the message
                message = json.loads(data)
                message_type = message.get("type", "")
                
                if message_type == "command":
                    # Execute game command
                    command = message.get("command", "")
                    if command:
                        response = await game_state_manager.execute_command(game_id, command)
                        
                        # Refresh game instance to get updated state
                        stmt = select(GameInstance).where(GameInstance.id == game_id)
                        result = await db.execute(stmt)
                        game_instance = result.scalar_one_or_none()
                        
                        # Send command response
                        await manager.send_personal_message(
                            websocket,
                            {
                                "type": "command_response",
                                "command": command,
                                "response": response
                            }
                        )
                        
                        # Broadcast game update to all connected clients
                        await manager.broadcast(
                            game_id,
                            {
                                "type": "game_update",
                                "data": {
                                    "position": game_instance.current_position,
                                    "last_command": command,
                                    "last_response": response
                                }
                            }
                        )
                
                elif message_type == "ping":
                    # Respond to ping
                    await manager.send_personal_message(
                        websocket,
                        {
                            "type": "pong"
                        }
                    )
            
            except json.JSONDecodeError:
                # Invalid JSON
                await manager.send_personal_message(
                    websocket,
                    {
                        "type": "error",
                        "message": "Invalid JSON message"
                    }
                )
            
            except Exception as e:
                # Other errors
                await manager.send_personal_message(
                    websocket,
                    {
                        "type": "error",
                        "message": f"Error processing message: {str(e)}"
                    }
                )
    
    except WebSocketDisconnect:
        # Client disconnected
        manager.disconnect(websocket, game_id)
        
        # Broadcast disconnect to other clients
        await manager.broadcast(
            game_id,
            {
                "type": "player_disconnect",
                "player_id": current_user.id
            }
        )
    
    except Exception as e:
        # Unexpected error
        manager.disconnect(websocket, game_id)
        print(f"WebSocket error: {str(e)}") 