# The Last Centaur API Reference

This document provides a comprehensive reference for all API endpoints in The Last Centaur game.

## Base URL

All API endpoints are prefixed with: `/api/v1`

## Authentication

Most endpoints require authentication using a JWT token in the Authorization header:

```
Authorization: Bearer {your_access_token}
```

## Endpoints

### Authentication

| Endpoint         | Method | Description                | Authentication |
| ---------------- | ------ | -------------------------- | -------------- |
| `/auth/register` | POST   | Register a new user        | No             |
| `/auth/login`    | POST   | Login and get access token | No             |

#### Register User

```
POST /api/v1/auth/register
```

Request body:

```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

Response:

```json
{
  "id": "string",
  "username": "string",
  "email": "string"
}
```

#### Login

```
POST /api/v1/auth/login
```

Request body (form-urlencoded):

```
username=string
password=string
```

Response:

```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### Game Endpoints

| Endpoint                  | Method | Description                          | Authentication |
| ------------------------- | ------ | ------------------------------------ | -------------- |
| `/game`                   | GET    | List all game instances for the user | Yes            |
| `/game`                   | POST   | Create a new game instance           | Yes            |
| `/game/{game_id}`         | GET    | Get a specific game instance         | Yes            |
| `/game/{game_id}`         | PUT    | Update a game instance               | Yes            |
| `/game/{game_id}`         | DELETE | Delete a game instance               | Yes            |
| `/game/{game_id}/command` | POST   | Execute a command on a game instance | Yes            |
| `/game/{game_id}/map`     | GET    | Get the map for a game instance      | Yes            |
| `/game/debug/routes`      | GET    | List all available API routes        | No             |

#### List Games

```
GET /api/v1/game
```

Response:

```json
[
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "status": "string",
    "created_at": "string",
    "updated_at": "string",
    "max_players": 0,
    "current_players": 0,
    "user_id": "string"
  }
]
```

#### Create Game

```
POST /api/v1/game
```

Request body:

```json
{
  "name": "string",
  "description": "string",
  "max_players": 1
}
```

Response:

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "status": "string",
  "created_at": "string",
  "updated_at": "string",
  "max_players": 0,
  "current_players": 0,
  "user_id": "string"
}
```

#### Get Game

```
GET /api/v1/game/{game_id}
```

Response:

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "status": "string",
  "created_at": "string",
  "updated_at": "string",
  "max_players": 0,
  "current_players": 0,
  "user_id": "string"
}
```

#### Update Game

```
PUT /api/v1/game/{game_id}
```

Request body:

```json
{
  "name": "string",
  "description": "string",
  "status": "string"
}
```

Response:

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "status": "string",
  "created_at": "string",
  "updated_at": "string",
  "max_players": 0,
  "current_players": 0,
  "user_id": "string"
}
```

#### Delete Game

```
DELETE /api/v1/game/{game_id}
```

Response: 204 No Content

#### Execute Command

```
POST /api/v1/game/{game_id}/command
```

Request body:

```json
{
  "command": "string",
  "use_llm": true
}
```

Response:

```json
{
  "command": "string",
  "response": "string",
  "game_id": "string",
  "timestamp": "string",
  "game_state": {}
}
```

#### Get Map

```
GET /api/v1/game/{game_id}/map
```

Response:

```json
{
  "tiles": [
    {
      "id": "string",
      "position_x": 0,
      "position_y": 0,
      "terrain_type": "string",
      "description": "string",
      "is_visited": true,
      "items": {},
      "enemies": {},
      "exits": []
    }
  ],
  "current_position": {
    "x": 0,
    "y": 0
  }
}
```

### Admin Endpoints

| Endpoint                                    | Method | Description             | Authentication |
| ------------------------------------------- | ------ | ----------------------- | -------------- |
| `/admin/admin/game/{game_id}`               | GET    | Get detailed game state | Yes            |
| `/admin/admin/game/{game_id}/inventory/add` | POST   | Add item to inventory   | Yes            |
| `/admin/admin/game/{game_id}/teleport`      | POST   | Teleport to area        | Yes            |
| `/admin/admin/game/{game_id}/defeat_enemy`  | POST   | Defeat an enemy         | Yes            |
| `/admin/admin/debug/command`                | POST   | Execute debug command   | Yes            |
| `/admin/admin/game/{game_id}/force_item`    | POST   | Force add item          | Yes            |
| `/admin/admin/debug_game_state/{game_id}`   | GET    | Debug game state        | Yes            |

## WebSocket

| Endpoint             | Description               |
| -------------------- | ------------------------- |
| `/ws/game/{game_id}` | Game WebSocket connection |

## Errors

The API uses standard HTTP status codes to indicate the success or failure of requests:

- 200: Success
- 201: Created
- 204: No Content
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 500: Internal Server Error

Error responses include a detail field with a description of the error.
