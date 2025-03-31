/**
 * API Routes Constants
 *
 * This file contains all API endpoint paths as constants.
 * Import and use these constants when making API calls to ensure consistency
 * and make it easier to update endpoints in the future.
 */

// Base API path
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const API_V1_PREFIX = "/api/v1";

// Auth endpoints
export const AUTH_ROUTES = {
  LOGIN: `${API_V1_PREFIX}/auth/login`,
  REGISTER: `${API_V1_PREFIX}/auth/register`,
};

// Game endpoints
export const GAME_ROUTES = {
  LIST: `${API_V1_PREFIX}/game`,
  CREATE: `${API_V1_PREFIX}/game`,
  DETAIL: (gameId: string) => `${API_V1_PREFIX}/game/${gameId}`,
  UPDATE: (gameId: string) => `${API_V1_PREFIX}/game/${gameId}`,
  DELETE: (gameId: string) => `${API_V1_PREFIX}/game/${gameId}`,
  COMMAND: (gameId: string) => `${API_V1_PREFIX}/game/${gameId}/command`,
  MAP: (gameId: string) => `${API_V1_PREFIX}/game/${gameId}/map`,
  HISTORY: (gameId: string) => `${API_V1_PREFIX}/game/${gameId}/history`,
  DEBUG_ROUTES: `${API_V1_PREFIX}/game/debug/routes`,
};

// Admin endpoints
export const ADMIN_ROUTES = {
  GAME_STATE: (gameId: string) => `${API_V1_PREFIX}/admin/admin/game/${gameId}`,
  ADD_INVENTORY: (gameId: string) => `${API_V1_PREFIX}/admin/admin/game/${gameId}/inventory/add`,
  TELEPORT: (gameId: string) => `${API_V1_PREFIX}/admin/admin/game/${gameId}/teleport`,
  DEFEAT_ENEMY: (gameId: string) => `${API_V1_PREFIX}/admin/admin/game/${gameId}/defeat_enemy`,
  FORCE_ITEM: (gameId: string) => `${API_V1_PREFIX}/admin/admin/game/${gameId}/force_item`,
  DEBUG_COMMAND: `${API_V1_PREFIX}/admin/admin/debug/command`,
  DEBUG_GAME_STATE: (gameId: string) => `${API_V1_PREFIX}/admin/admin/debug_game_state/${gameId}`,
};

// WebSocket endpoints
export const WS_ROUTES = {
  GAME: (gameId: string) => `ws://${API_BASE_URL.replace("http://", "")}/ws/game/${gameId}`,
};

/**
 * Helper function to build full URLs including the API_BASE_URL
 */
export const buildFullUrl = (path: string): string => {
  return `${API_BASE_URL}${path}`;
};

/**
 * Usage example:
 *
 * import { GAME_ROUTES, buildFullUrl } from '../constants/api-routes';
 *
 * // To get all games
 * const response = await fetch(buildFullUrl(GAME_ROUTES.LIST), {
 *   headers: { Authorization: `Bearer ${token}` }
 * });
 *
 * // To execute a command
 * const response = await fetch(buildFullUrl(GAME_ROUTES.COMMAND(gameId)), {
 *   method: 'POST',
 *   headers: { ... },
 *   body: JSON.stringify({ command: 'look' })
 * });
 */
