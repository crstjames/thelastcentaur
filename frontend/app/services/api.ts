/**
 * API service for communicating with the backend
 */

// Base API URL from environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_V1_PREFIX = "/api/v1";
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

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
 * Game interface
 */
export interface Game {
  id: string;
  name: string;
  description: string;
  status: string;
  created_at: string;
  user_id: string;
}

/**
 * Command response interface
 */
export interface CommandResponse {
  response: string;
  game_state?: {
    location: string;
    inventory: string[];
    health: number;
    [key: string]: unknown;
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
    const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/games`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Failed to fetch games");
    }

    return response.json();
  },

  /**
   * Get a specific game
   */
  getGame: async (token: string, gameId: string): Promise<Game> => {
    const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/games/${gameId}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Failed to fetch game");
    }

    return response.json();
  },

  /**
   * Create a new game
   */
  createGame: async (token: string, name: string, description: string): Promise<Game> => {
    const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/games`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ name, description }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Failed to create game");
    }

    return response.json();
  },

  /**
   * Send a command to the game
   */
  sendCommand: async (token: string, gameId: string, command: string): Promise<CommandResponse> => {
    const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/games/${gameId}/command`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ command }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Failed to send command");
    }

    return response.json();
  },

  /**
   * Get game history
   */
  getGameHistory: async (token: string, gameId: string): Promise<GameHistoryEntry[]> => {
    const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/games/${gameId}/history`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Failed to fetch game history");
    }

    return response.json();
  },
};

/**
 * WebSocket message interface
 */
export interface WebSocketMessage {
  type: string;
  data: {
    message?: string;
    command?: string;
    response?: string;
    [key: string]: unknown;
  };
}

/**
 * Connect to game WebSocket
 */
export function connectGameWebSocket(
  gameId: string,
  token: string,
  callbacks: {
    onOpen?: () => void;
    onMessage?: (data: WebSocketMessage) => void;
    onClose?: () => void;
    onError?: (error: Event) => void;
  }
): WebSocket {
  const socket = new WebSocket(`${WS_URL}/ws/game/${gameId}?token=${token}`);

  socket.onopen = () => {
    if (callbacks.onOpen) callbacks.onOpen();
  };

  socket.onmessage = (event) => {
    if (callbacks.onMessage) {
      try {
        const data = JSON.parse(event.data) as WebSocketMessage;
        callbacks.onMessage(data);
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    }
  };

  socket.onclose = () => {
    if (callbacks.onClose) callbacks.onClose();
  };

  socket.onerror = (error) => {
    if (callbacks.onError) callbacks.onError(error);
  };

  return socket;
}
