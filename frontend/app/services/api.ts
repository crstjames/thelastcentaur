/**
 * API service for communicating with the backend
 */

// Base API URL from environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_V1_PREFIX = "/api/v1";

// Type definitions
export interface Game {
  id: string;
  name: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
  max_players?: number;
  current_players?: number;
  user_id?: string;
  game_state?: GameState;
}

export interface GameCommandResponse {
  command: string;
  response: string;
  game_id: string;
  timestamp: string;
  game_state?: Record<string, unknown>;
}

export interface MapResponse {
  tiles: Array<{
    id: string;
    position_x: number;
    position_y: number;
    terrain_type: string;
    description: string;
    is_visited: boolean;
    items: Record<string, unknown>;
    enemies: Record<string, unknown>;
    exits: string[];
  }>;
  current_position: {
    x: number;
    y: number;
  };
}

// Authentication API
export const authAPI = {
  /**
   * Login with username and password
   */
  login: async (
    username: string,
    password: string
  ): Promise<{ access_token: string; token_type: string; user: { id: string; username: string; email: string } }> => {
    // Create form data for OAuth2 password flow
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);
    formData.append("grant_type", "password");

    const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    });

    if (!response.ok) {
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          if (typeof errorData.detail === "string") {
            throw new Error(errorData.detail);
          } else if (Array.isArray(errorData.detail)) {
            throw new Error(errorData.detail.map((err: { msg: string }) => err.msg).join(", "));
          }
        }
        throw new Error("Login failed");
      } catch (err) {
        if (err instanceof Error) {
          throw err;
        }
        throw new Error("Login failed. Please try again.");
      }
    }

    // Get the token response
    const tokenData = await response.json();

    // For OAuth2 form-based login, we need to construct the user object
    // since the backend returns only the token
    return {
      access_token: tokenData.access_token,
      token_type: tokenData.token_type || "bearer",
      user: {
        id: "user-id", // This will be replaced when we implement proper user info endpoint
        username: username,
        email: "user@example.com", // This will be replaced when we implement proper user info endpoint
      },
    };
  },

  /**
   * Register a new user
   */
  register: async (
    username: string,
    email: string,
    password: string
  ): Promise<{ access_token: string; token_type: string; user: { id: string; username: string; email: string } }> => {
    const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, email, password }),
    });

    if (!response.ok) {
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          if (typeof errorData.detail === "string") {
            throw new Error(errorData.detail);
          } else if (Array.isArray(errorData.detail)) {
            throw new Error(errorData.detail.map((err: { msg: string }) => err.msg).join(", "));
          }
        }
        throw new Error("Registration failed");
      } catch (err) {
        if (err instanceof Error) {
          throw err;
        }
        throw new Error("Registration failed. Please try again.");
      }
    }

    // Get the user response
    const userData = await response.json();
    console.log("Registration successful:", userData);

    // After registration, we need to login to get the token
    try {
      return await authAPI.login(username, password);
    } catch (err) {
      console.error("Auto-login after registration failed:", err);
      if (err instanceof Error) {
        throw new Error(`Account created but login failed: ${err.message}. Please try logging in manually.`);
      }
      throw new Error("Account created but login failed. Please try logging in manually.");
    }
  },

  /**
   * Verify token
   */
  verifyToken: async (token: string): Promise<boolean> => {
    try {
      // We'll just try to access a protected endpoint to verify the token
      const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/game`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      return response.ok;
    } catch (error) {
      console.error("Token verification error:", error);
      return false;
    }
  },
};

/**
 * GameState interface
 */
export interface GameState {
  player?: {
    health?: number;
    max_health?: number;
    stamina?: number;
    max_stamina?: number;
    level?: number;
    experience?: number;
    inventory?: string[];
    position?: {
      x: number;
      y: number;
    };
  };
  environment?: {
    time_of_day?: string;
    weather?: string;
    temperature?: string;
  };
  current_tile?: {
    id?: string;
    description?: string;
    items?: string[];
    npcs?: string[];
    enemies?: string[];
  };
}

/**
 * Command response interface
 */
export interface CommandResponse {
  response: string;
  game_state?: GameState & {
    // Legacy properties for backward compatibility
    health?: number;
    location?: string;
    inventory?: string[];
    stamina?: number;
    gold?: number;
    experience?: number;
    level?: number;
  };
}

/**
 * Game history entry interface
 */
export interface GameHistoryEntry {
  id: string;
  command: string;
  response: string;
  timestamp: string;
}

/**
 * Game API
 */
export const gameAPI = {
  /**
   * List all games for the current user
   */
  listGames: async (token: string): Promise<Game[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/game/game`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        console.error(`Failed to load games: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to load games: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error("Network error when loading games:", error);
      throw error; // Re-throw to be handled by the component
    }
  },

  /**
   * Get a specific game
   */
  getGame: async (token: string, gameId: string): Promise<Game> => {
    try {
      const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/game/game/${gameId}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        console.error(`Failed to load game: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to load game: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error("Network error when loading game:", error);
      throw error; // Re-throw to be handled by the component
    }
  },

  /**
   * Create a new game
   */
  createGame: async (token: string, name: string, description: string): Promise<Game> => {
    try {
      const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/game/game`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name, description }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error(`Failed to create game: ${response.status} ${response.statusText}`, errorData);
        throw new Error(errorData.detail || `Failed to create game: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error("Network error when creating game:", error);
      throw error; // Re-throw to be handled by the component
    }
  },

  /**
   * Delete a game
   */
  deleteGame: async (token: string, gameId: string): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/game/game/${gameId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        console.error(`Failed to delete game: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to delete game: ${response.status}`);
      }
    } catch (error) {
      console.error("Network error when deleting game:", error);
      throw error; // Re-throw to be handled by the component
    }
  },

  /**
   * Update a game
   */
  updateGame: async (token: string, gameId: string, data: { name?: string; description?: string }): Promise<Game> => {
    try {
      const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/game/game/${gameId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        console.error(`Failed to update game: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to update game: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error("Network error when updating game:", error);
      throw error; // Re-throw to be handled by the component
    }
  },

  /**
   * Execute a command on a game
   */
  executeCommand: async (
    token: string,
    gameId: string,
    command: string,
    useLLM: boolean = true
  ): Promise<GameCommandResponse> => {
    try {
      const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/game/game/${gameId}/command`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ command, use_llm: useLLM }),
      });

      if (!response.ok) {
        console.error(`Failed to execute command: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to execute command: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error("Network error when executing command:", error);
      throw error; // Re-throw to be handled by the component
    }
  },

  /**
   * Get the game map
   */
  getMap: async (token: string, gameId: string): Promise<MapResponse> => {
    try {
      const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/game/game/${gameId}/map`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        console.error(`Failed to get map: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to get map: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error("Network error when getting map:", error);
      throw error; // Re-throw to be handled by the component
    }
  },

  /**
   * Get game history
   */
  getGameHistory: async (token: string, gameId: string): Promise<GameHistoryEntry[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/game/${gameId}/history`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        console.error(`Failed to load game history: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to load game history: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error("Network error when loading game history:", error);
      throw error; // Re-throw to be handled by the component
    }
  },

  /**
   * Send a command to the game (alias for executeCommand for backward compatibility)
   */
  sendCommand: async (
    token: string,
    gameId: string,
    command: string,
    useLLM: boolean = true
  ): Promise<GameCommandResponse> => {
    return gameAPI.executeCommand(token, gameId, command, useLLM);
  },
};
