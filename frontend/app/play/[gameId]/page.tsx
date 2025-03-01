"use client";

import { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "../../context/AuthContext";
import { gameAPI, Game } from "../../services/api";

// Message type definition
interface Message {
  id: string;
  content: string;
  sender: "user" | "system" | "character";
  timestamp: string;
}

// Player stats interface
interface PlayerStats {
  health: number;
  maxHealth: number;
  stamina: number;
  maxStamina: number;
  level: number;
  experience: number;
  nextLevelExp: number;
  gold: number;
  location: string;
  inventory: string[];
}

export default function PlayPage() {
  const [game, setGame] = useState<Game | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [sendingMessage, setSendingMessage] = useState(false);
  // Sample player stats - this would come from your API in real implementation
  const [playerStats, setPlayerStats] = useState<PlayerStats>({
    health: 75,
    maxHealth: 100,
    stamina: 60,
    maxStamina: 100,
    level: 1,
    experience: 250,
    nextLevelExp: 1000,
    gold: 15,
    location: "Forest Edge",
    inventory: ["Rusty Dagger", "Health Potion", "Torch", "Leather Armor"],
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const params = useParams();
  const router = useRouter();
  const { isAuthenticated, token, user } = useAuth();
  const gameId = params.gameId as string;

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  // Load game data
  useEffect(() => {
    if (isAuthenticated && token && gameId) {
      loadGame();
    }
  }, [isAuthenticated, token, gameId]);

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadGame = async () => {
    setLoading(true);
    setError("");

    try {
      if (!token) return;

      // Load game data with fallback
      let gameData;
      try {
        gameData = await gameAPI.getGame(token, gameId);
        setGame(gameData);
      } catch (gameErr) {
        console.error("Error loading game data:", gameErr);
        // Set fallback game data
        setGame({
          id: gameId,
          name: "Adventure One",
          description: "Your adventure in the world of The Last Centaur",
          status: "active",
          created_at: new Date().toISOString(),
          user_id: user?.id || "unknown",
        });
      }

      // Initialize messages array with default welcome messages
      // Skip loading game history for now as it's not implemented on the backend yet
      const historyMessages: Message[] = [
        {
          id: "system-welcome",
          content: "Welcome to The Last Centaur! Your adventure begins now...",
          sender: "system",
          timestamp: new Date().toISOString(),
        },
        {
          id: "character-intro",
          content:
            "You find yourself standing at the edge of a dense forest. The air is thick with the scent of pine and something... magical. What would you like to do?",
          sender: "character",
          timestamp: new Date().toISOString(),
        },
      ];

      // Set messages state
      setMessages(historyMessages);

      // Try to get initial state
      try {
        // Send initial command to get game state
        // Use LLM for the initial look command to get a rich description
        const initialStateCommand = await gameAPI.sendCommand(token, gameId, "look", true);

        // Update player stats from initial state
        if (initialStateCommand.game_state) {
          // Extract values from game_state with fallbacks
          const gameState = initialStateCommand.game_state;

          setPlayerStats({
            health: typeof gameState.health === "number" ? gameState.health : 100,
            maxHealth: 100,
            stamina: 100,
            maxStamina: 100,
            level: typeof gameState.level === "number" ? gameState.level : 1,
            experience: typeof gameState.experience === "number" ? gameState.experience : 0,
            nextLevelExp: 100,
            gold: typeof gameState.gold === "number" ? gameState.gold : 10,
            location: typeof gameState.location === "string" ? gameState.location : "Forest Edge",
            inventory: Array.isArray(gameState.inventory) ? gameState.inventory : [],
          });
        }
      } catch (stateErr) {
        console.error("Error getting initial state:", stateErr);
        // Set default player stats
        setPlayerStats({
          health: 100,
          maxHealth: 100,
          stamina: 100,
          maxStamina: 100,
          level: 1,
          experience: 0,
          nextLevelExp: 100,
          gold: 10,
          location: "Forest Edge",
          inventory: [],
        });
      }
    } catch (err) {
      console.error("Error in loadGame:", err);
      setError("Failed to load game. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  // Check if a command is an inventory check
  const isInventoryCommand = (cmd: string): boolean => {
    const lowerCmd = cmd.toLowerCase().trim();
    return (
      lowerCmd === "inventory" ||
      lowerCmd === "check inventory" ||
      lowerCmd === "show inventory" ||
      lowerCmd === "i" ||
      lowerCmd === "inv"
    );
  };

  // Fetch game state without using LLM (for UI updates only)
  const fetchGameState = async () => {
    if (!token || !gameId) return;

    try {
      // Get the latest game state
      const gameData = await gameAPI.getGame(token, gameId);

      if (gameData && gameData.game_state) {
        // Extract player stats from game data
        const gameState = gameData.game_state || {};
        console.log("Game state updated:", gameState);

        // Check both formats - the new nested player object and the old flat structure
        if (gameState.player) {
          // New format with nested player object
          const playerData = gameState.player;

          // Update player stats with the latest data
          setPlayerStats((prev) => ({
            ...prev,
            health: playerData.health ?? prev.health,
            maxHealth: playerData.max_health ?? prev.maxHealth,
            stamina: playerData.stamina ?? prev.stamina,
            maxStamina: playerData.max_stamina ?? prev.maxStamina,
            level: playerData.level ?? prev.level,
            experience: playerData.experience ?? prev.experience,
            gold: playerData.gold ?? prev.gold,
            location: gameState.current_tile?.terrain_type || prev.location,
            inventory: Array.isArray(playerData.inventory) ? playerData.inventory : prev.inventory,
          }));
        } else {
          // Old format with flat structure
          setPlayerStats((prev) => ({
            ...prev,
            health: gameState.health ?? prev.health,
            stamina: gameState.stamina ?? prev.stamina,
            level: gameState.level ?? prev.level,
            experience: gameState.experience ?? prev.experience,
            gold: gameState.gold ?? prev.gold,
            location: gameState.location ?? prev.location,
            inventory: Array.isArray(gameState.inventory) ? gameState.inventory : prev.inventory,
          }));
        }
      }
    } catch (stateErr) {
      console.error("Error fetching updated game state:", stateErr);
      // Continue without updating if there's an error
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || sendingMessage) return;

    setSendingMessage(true);

    // Add user message to the chat
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      content: inputMessage,
      sender: "user",
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");

    try {
      // Try to send command to the game engine API
      // Always use LLM for player-initiated commands, especially inventory checks
      // This ensures rich narrative responses for player-requested inventory checks
      const shouldUseLLM = true; // Default to using LLM for all player commands

      let commandResponse;
      try {
        commandResponse = await gameAPI.sendCommand(token!, gameId, inputMessage, shouldUseLLM);
      } catch (apiErr) {
        console.error("API error sending command:", apiErr);

        // Generate fallback response based on user input
        let responseContent = "I don't understand that command.";

        if (inputMessage.toLowerCase().includes("look")) {
          responseContent =
            "You see tall trees surrounding you, their branches swaying gently in the breeze. The forest floor is covered in fallen leaves and small plants.";
        } else if (inputMessage.toLowerCase().includes("path") || inputMessage.toLowerCase().includes("follow")) {
          responseContent =
            "You follow the narrow path through the trees. After walking for a few minutes, you come to a small clearing with a bubbling stream running through it.";
        } else if (inputMessage.toLowerCase().includes("water") || inputMessage.toLowerCase().includes("stream")) {
          responseContent =
            "You head toward the sound of water. Soon, you find a clear stream cutting through the forest. The water looks cool and refreshing.";
        } else if (inputMessage.toLowerCase().includes("help")) {
          responseContent =
            "Available commands: look, go [direction], examine [object], take [item], inventory, talk to [character]";
        } else if (isInventoryCommand(inputMessage)) {
          responseContent =
            "You check your belongings. " +
            (playerStats.inventory.length > 0
              ? `You are carrying: ${playerStats.inventory.join(", ")}.`
              : "Your inventory is empty.");
        }

        // Create a fallback response object
        commandResponse = {
          response: responseContent,
          game_state: {
            health: playerStats.health,
            location: inputMessage.toLowerCase().includes("follow") ? "Forest Clearing" : playerStats.location,
            inventory: playerStats.inventory,
            stamina: Math.max(0, playerStats.stamina - 5),
            gold: playerStats.gold,
            experience: playerStats.experience,
            level: playerStats.level,
          },
        };
      }

      // Add system response
      const systemResponse: Message = {
        id: `system-${Date.now()}`,
        content: commandResponse.response,
        sender: "character",
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, systemResponse]);

      // Update player stats if game_state is provided in the response
      if (commandResponse.game_state) {
        setPlayerStats((prev) => ({
          ...prev,
          health: commandResponse.game_state?.health ?? prev.health,
          location: commandResponse.game_state?.location ?? prev.location,
          inventory: commandResponse.game_state?.inventory ?? prev.inventory,
          // Update other stats as needed
          stamina: (commandResponse.game_state?.stamina as number) ?? prev.stamina,
          gold: (commandResponse.game_state?.gold as number) ?? prev.gold,
          experience: (commandResponse.game_state?.experience as number) ?? prev.experience,
          level: (commandResponse.game_state?.level as number) ?? prev.level,
        }));
      }

      // Fetch the latest game state to ensure we have the most up-to-date inventory and stats
      await fetchGameState();
    } catch (err) {
      console.error("Error sending message:", err);

      // Add error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        content: "There was an error processing your command. Please try again.",
        sender: "system",
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setSendingMessage(false);
    }
  };

  const handleBackToGames = () => {
    router.push("/games");
  };

  if (!isAuthenticated) {
    return null; // Will redirect in useEffect
  }

  return (
    <div className="crt-container">
      <style jsx>{`
        @font-face {
          font-family: "Press Start 2P";
          font-style: normal;
          font-weight: 400;
          src: url("https://fonts.gstatic.com/s/pressstart2p/v15/e3t4euO8T-267oIAQAu6jDQyK3nVivM.woff2") format("woff2");
          unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329,
            U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
        }

        .crt-container {
          height: 100vh;
          width: 100vw;
          overflow: hidden;
          position: relative;
          font-family: "Press Start 2P", monospace;
        }

        .crt-container::before {
          content: " ";
          display: block;
          position: absolute;
          top: 0;
          left: 0;
          bottom: 0;
          right: 0;
          background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%);
          background-size: 100% 4px;
          z-index: 2;
          pointer-events: none;
        }

        .crt-container::after {
          content: " ";
          display: block;
          position: absolute;
          top: 0;
          left: 0;
          bottom: 0;
          right: 0;
          background: rgba(18, 16, 16, 0.1);
          opacity: 0;
          z-index: 2;
          pointer-events: none;
          animation: flicker 0.15s infinite;
        }

        @keyframes flicker {
          0% {
            opacity: 0.27861;
          }
          5% {
            opacity: 0.34769;
          }
          10% {
            opacity: 0.23604;
          }
          15% {
            opacity: 0.90626;
          }
          20% {
            opacity: 0.18128;
          }
          25% {
            opacity: 0.83891;
          }
          30% {
            opacity: 0.65583;
          }
          35% {
            opacity: 0.67807;
          }
          40% {
            opacity: 0.26559;
          }
          45% {
            opacity: 0.84693;
          }
          50% {
            opacity: 0.96019;
          }
          55% {
            opacity: 0.08594;
          }
          60% {
            opacity: 0.20313;
          }
          65% {
            opacity: 0.71988;
          }
          70% {
            opacity: 0.53455;
          }
          75% {
            opacity: 0.37288;
          }
          80% {
            opacity: 0.71428;
          }
          85% {
            opacity: 0.70419;
          }
          90% {
            opacity: 0.7003;
          }
          95% {
            opacity: 0.36108;
          }
          100% {
            opacity: 0.24387;
          }
        }

        .crt-frame {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          box-shadow: inset 0 0 100px rgba(0, 0, 0, 0.5);
          border-radius: 20px;
          overflow: hidden;
          z-index: 3;
          pointer-events: none;
        }

        .crt-content {
          position: relative;
          height: 100%;
          width: 100%;
          background-color: #0c0c0c;
          background-image: url("/images/bg.png");
          background-size: cover;
          background-position: center;
          background-blend-mode: overlay;
          background-opacity: 0.1;
          display: flex;
          flex-direction: column;
          color: white;
          z-index: 1;
        }

        .game-header {
          background-color: #222;
          border-bottom: 2px solid #ffd700;
          padding: 0.5rem 1rem;
          margin-bottom: 0.5rem;
          font-family: "Press Start 2P", monospace;
        }

        .header-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .game-title {
          font-size: 1.25rem;
          font-weight: bold;
          color: #ffd700;
          text-shadow: 2px 2px 0px #b8860b;
        }

        .back-button {
          padding: 0.5rem 1rem;
          background-color: #663300;
          color: #ffd700;
          border: 1px solid #996633;
          border-radius: 0.25rem;
          cursor: pointer;
          font-family: "Press Start 2P", monospace;
          font-size: 0.6rem;
        }

        .back-button:hover {
          background-color: #7c2d12;
        }

        .game-main {
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          padding: 0.5rem;
          gap: 0.5rem;
          position: relative;
        }

        .loading-container {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: #1a1a1a;
          border-radius: 0.375rem;
        }

        .loading-content {
          text-align: center;
        }

        .spinner {
          display: inline-block;
          height: 2rem;
          width: 2rem;
          animation: spin 1s linear infinite;
          border-radius: 50%;
          border-width: 4px;
          border-style: solid;
          border-color: #ffd700 transparent #ffd700 transparent;
        }

        .loading-text {
          margin-top: 1rem;
          color: #ffd700;
          font-family: "Press Start 2P", monospace;
          font-size: 0.7rem;
        }

        .error-container {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: #1a1a1a;
          border-radius: 0.375rem;
        }

        .error-content {
          background-color: rgba(153, 27, 27, 0.7);
          border: 2px solid #991b1b;
          color: #fee2e2;
          padding: 1.5rem;
          border-radius: 0.375rem;
          font-family: "Press Start 2P", monospace;
          font-size: 0.7rem;
        }

        .error-text {
          font-size: 0.7rem;
          font-weight: 500;
        }

        .error-button {
          margin-top: 1rem;
          padding: 0.5rem 1rem;
          background-color: #7f1d1d;
          color: #fee2e2;
          border: 1px solid #b91c1c;
          border-radius: 0.25rem;
          cursor: pointer;
          font-family: "Press Start 2P", monospace;
          font-size: 0.6rem;
        }

        .game-content {
          display: flex;
          flex-direction: row;
          gap: 0.5rem;
          height: 100%;
        }

        .game-panel {
          width: 66%;
          display: flex;
          flex-direction: column;
          background-color: rgba(26, 26, 26, 0.9);
          border: 2px solid #996633;
          border-radius: 0.375rem;
          overflow: hidden;
          box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        }

        .narrative-area {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
          background-color: rgba(12, 12, 12, 0.9);
        }

        .messages-container {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .message {
          font-family: "Press Start 2P", monospace;
          font-size: 0.7rem;
          line-height: 1.5;
        }

        .user-message {
          color: #4ade80;
          border-left: 2px solid #4ade80;
          padding-left: 0.5rem;
        }

        .system-message {
          color: #fbbf24;
          border-left: 2px solid #fbbf24;
          padding-left: 0.5rem;
        }

        .character-message {
          color: #f5f5f5;
        }

        .message-timestamp {
          font-size: 0.6rem;
          color: #d97706;
          margin-bottom: 0.25rem;
        }

        .message-content {
          margin-left: 0.5rem;
        }

        .character-content {
          font-size: 0.8rem;
          font-weight: 500;
        }

        .character-paragraph {
          margin-bottom: 0.8rem;
          line-height: 1.4;
        }

        .character-paragraph:last-child {
          margin-bottom: 0;
        }

        .input-area {
          background-color: #333;
          border-top: 1px solid #996633;
          padding: 0.75rem;
        }

        .input-form {
          display: flex;
        }

        .command-input {
          flex: 1;
          padding: 0.5rem 0.75rem;
          background-color: #1a1a1a;
          border: 1px solid #996633;
          color: #f5f5f5;
          border-top-left-radius: 0.25rem;
          border-bottom-left-radius: 0.25rem;
          outline: none;
          font-family: "Press Start 2P", monospace;
          font-size: 0.7rem;
        }

        .submit-button {
          padding: 0.5rem 1rem;
          background-color: #996633;
          color: #f5f5f5;
          border: 1px solid #996633;
          border-top-right-radius: 0.25rem;
          border-bottom-right-radius: 0.25rem;
          cursor: pointer;
          font-family: "Press Start 2P", monospace;
          font-size: 0.7rem;
        }

        .submit-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .command-help {
          text-align: center;
          background-color: #0c0c0c;
          color: #d97706;
          font-size: 0.6rem;
          padding: 0.5rem;
          border-top: 1px solid #4a3520;
          font-family: "Press Start 2P", monospace;
        }

        .stats-panel {
          width: 33%;
          background-color: rgba(26, 26, 26, 0.9);
          border: 2px solid #996633;
          border-radius: 0.375rem;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        }

        .stats-header {
          background-color: #333;
          border-bottom: 1px solid #996633;
          padding: 0.75rem 1rem;
        }

        .stats-title {
          color: #ffd700;
          font-weight: bold;
          text-align: center;
          font-family: "Press Start 2P", monospace;
          font-size: 0.8rem;
          text-shadow: 2px 2px 0px #000;
        }

        .stats-content {
          flex: 1;
          padding: 1rem;
          overflow-y: auto;
          background-color: rgba(12, 12, 12, 0.9);
        }

        .stats-sections {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .character-section {
          border-bottom: 1px solid #4a3520;
          padding-bottom: 1rem;
        }

        .character-info {
          text-align: center;
          margin-bottom: 0.5rem;
        }

        .character-name {
          color: #ffd700;
          font-weight: bold;
          font-size: 0.9rem;
          font-family: "Press Start 2P", monospace;
          text-shadow: 2px 2px 0px #000;
        }

        .character-level {
          color: #f5f5f5;
          font-family: "Press Start 2P", monospace;
          font-size: 0.7rem;
        }

        .exp-container {
          margin-top: 1rem;
        }

        .stat-label-row {
          display: flex;
          justify-content: space-between;
          font-size: 0.6rem;
          color: #d97706;
          margin-bottom: 0.25rem;
          font-family: "Press Start 2P", monospace;
        }

        .progress-bar {
          width: 100%;
          background-color: #333;
          border-radius: 9999px;
          height: 0.5rem;
          border: 1px solid #4a3520;
        }

        .progress-fill {
          height: 100%;
          border-radius: 9999px;
        }

        .exp-fill {
          background-color: #3b82f6;
        }

        .character-stats {
          color: #f5f5f5;
          margin-top: 1rem;
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 0.5rem;
          font-family: "Press Start 2P", monospace;
          font-size: 0.6rem;
        }

        .stat-row {
          display: flex;
          justify-content: space-between;
        }

        .vitals-section {
          border-bottom: 1px solid #4a3520;
          padding-bottom: 1rem;
        }

        .section-title {
          color: #ffd700;
          font-weight: bold;
          margin-bottom: 0.75rem;
          font-family: "Press Start 2P", monospace;
          font-size: 0.8rem;
          text-shadow: 2px 2px 0px #000;
        }

        .health-container {
          margin-bottom: 0.75rem;
        }

        .health-fill {
          background-color: #dc2626;
        }

        .stamina-fill {
          background-color: #16a34a;
        }

        .inventory-section {
        }

        .inventory-items {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .inventory-item {
          color: #f5f5f5;
          font-size: 0.7rem;
          background-color: #333;
          border: 1px solid #4a3520;
          padding: 0.5rem 0.75rem;
          border-radius: 0.25rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-family: "Press Start 2P", monospace;
        }

        .game-footer {
          margin-top: 0.5rem;
          text-align: center;
          color: #d97706;
          font-size: 0.6rem;
          padding: 0.5rem;
          background-color: #222;
          border-top: 1px solid #4a3520;
          border-bottom-left-radius: 0.375rem;
          border-bottom-right-radius: 0.375rem;
          font-family: "Press Start 2P", monospace;
        }

        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
      <div className="crt-frame"></div>
      <div className="crt-content">
        {/* Game Title Header */}
        <header className="game-header">
          <div className="header-content">
            <h1 className="game-title">{game?.name || "Adventure One"}</h1>
            <div>
              <button onClick={handleBackToGames} className="back-button">
                Back to Adventures
              </button>
            </div>
          </div>
        </header>

        <main className="game-main">
          {loading ? (
            <div className="loading-container">
              <div className="loading-content">
                <div className="spinner"></div>
                <p className="loading-text">Loading your adventure...</p>
              </div>
            </div>
          ) : error ? (
            <div className="error-container">
              <div className="error-content">
                <p className="error-text">{error}</p>
                <button onClick={handleBackToGames} className="error-button">
                  Return to Adventures
                </button>
              </div>
            </div>
          ) : (
            <div className="game-content">
              {/* Main game content - 2/3 width */}
              <div className="game-panel">
                {/* Game narrative content */}
                <div className="narrative-area">
                  <div className="messages-container">
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`message ${
                          message.sender === "user"
                            ? "user-message"
                            : message.sender === "system"
                            ? "system-message"
                            : "character-message"
                        }`}
                      >
                        {message.sender === "user" ? (
                          <>
                            <div className="message-timestamp">
                              {new Date(message.timestamp).toLocaleTimeString()} - You:
                            </div>
                            <div className="message-content">{message.content}</div>
                          </>
                        ) : message.sender === "system" ? (
                          <>
                            <div className="message-timestamp">SYSTEM:</div>
                            <div className="message-content">{message.content}</div>
                          </>
                        ) : (
                          <>
                            <div className="message-timestamp">{new Date(message.timestamp).toLocaleTimeString()}</div>
                            <div className="character-content">
                              {message.content.split("\n\n").map((paragraph, index) =>
                                paragraph.trim() ? (
                                  <p key={index} className="character-paragraph">
                                    {paragraph}
                                  </p>
                                ) : null
                              )}
                            </div>
                          </>
                        )}
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </div>
                </div>

                {/* Input area */}
                <div className="input-area">
                  <form onSubmit={handleSendMessage} className="input-form">
                    <input
                      type="text"
                      placeholder="Type your command..."
                      className="command-input"
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      disabled={sendingMessage}
                    />
                    <button type="submit" disabled={sendingMessage || !inputMessage.trim()} className="submit-button">
                      {sendingMessage ? "..." : "ENTER"}
                    </button>
                  </form>
                </div>

                {/* Command help bar */}
                <div className="command-help">Type &apos;help&apos; for available commands</div>
              </div>

              {/* Character stats panel - 1/3 width */}
              <div className="stats-panel">
                {/* Stats header */}
                <div className="stats-header">
                  <h2 className="stats-title">CHARACTER STATS</h2>
                </div>

                {/* Stats content */}
                <div className="stats-content">
                  <div className="stats-sections">
                    {/* Character info section */}
                    <div className="character-section">
                      <div className="character-info">
                        <h3 className="character-name">{user?.username || "crstjames"}</h3>
                        <div className="character-level">Level {playerStats.level}</div>
                      </div>

                      {/* Experience */}
                      <div className="exp-container">
                        <div className="stat-label-row">
                          <span>Experience</span>
                          <span>
                            {playerStats.experience} / {playerStats.nextLevelExp}
                          </span>
                        </div>
                        <div className="progress-bar">
                          <div
                            className="progress-fill exp-fill"
                            style={{
                              width: `${Math.min(100, (playerStats.experience / playerStats.nextLevelExp) * 100)}%`,
                            }}
                          ></div>
                        </div>
                      </div>

                      <div className="character-stats">
                        <div className="stat-row">
                          <span>Gold:</span>
                          <span>{playerStats.gold}</span>
                        </div>
                        <div className="stat-row">
                          <span>Location:</span>
                          <span>{playerStats.location}</span>
                        </div>
                      </div>
                    </div>

                    {/* Vitals section */}
                    <div className="vitals-section">
                      <h3 className="section-title">VITALS</h3>

                      {/* Health */}
                      <div className="health-container">
                        <div className="stat-label-row">
                          <span>Health</span>
                          <span>
                            {playerStats.health} / {playerStats.maxHealth}
                          </span>
                        </div>
                        <div className="progress-bar">
                          <div
                            className="progress-fill health-fill"
                            style={{
                              width: `${Math.min(100, (playerStats.health / playerStats.maxHealth) * 100)}%`,
                            }}
                          ></div>
                        </div>
                      </div>

                      {/* Stamina */}
                      <div>
                        <div className="stat-label-row">
                          <span>Stamina</span>
                          <span>
                            {playerStats.stamina} / {playerStats.maxStamina}
                          </span>
                        </div>
                        <div className="progress-bar">
                          <div
                            className="progress-fill stamina-fill"
                            style={{
                              width: `${Math.min(100, (playerStats.stamina / playerStats.maxStamina) * 100)}%`,
                            }}
                          ></div>
                        </div>
                      </div>
                    </div>

                    {/* Inventory section */}
                    <div className="inventory-section">
                      <h3 className="section-title">INVENTORY</h3>
                      <div className="inventory-items">
                        {playerStats.inventory.map((item, index) => (
                          <div key={index} className="inventory-item">
                            <span>{item}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="game-footer">v0.1.0 Alpha • © 2023 The Last Centaur</footer>
      </div>
    </div>
  );
}
