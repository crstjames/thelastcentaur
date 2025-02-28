"use client";

import { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "../../context/AuthContext";
import { gameAPI } from "../../services/api";

// Game type definition
interface Game {
  id: string;
  name: string;
  description: string;
  status: string;
  created_at: string;
}

// Message type definition
interface Message {
  id: string;
  content: string;
  sender: "user" | "system" | "character";
  timestamp: string;
}

export default function PlayPage() {
  const [game, setGame] = useState<Game | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [sendingMessage, setSendingMessage] = useState(false);
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

      // Load game data
      const gameData = await gameAPI.getGame(token, gameId);
      setGame(gameData);

      // Load initial messages or game state
      // This would be replaced with actual API calls to get game history
      setMessages([
        {
          id: "1",
          content: "Welcome to The Last Centaur! Your adventure begins now...",
          sender: "system",
          timestamp: new Date().toISOString(),
        },
        {
          id: "2",
          content:
            "You find yourself in a dense forest. The air is thick with the scent of pine and moss. Sunlight filters through the canopy above, creating dappled patterns on the forest floor.",
          sender: "character",
          timestamp: new Date().toISOString(),
        },
        {
          id: "3",
          content:
            "In the distance, you can hear the faint sound of running water. To your right, there's a narrow path winding between the trees. What would you like to do?",
          sender: "character",
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      setError("Failed to load game");
      console.error("Error loading game:", err);
    } finally {
      setLoading(false);
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
      // This would be replaced with actual API call to send message to game engine
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Simulate response based on user input
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
      }

      // Add system response
      const systemResponse: Message = {
        id: `system-${Date.now()}`,
        content: responseContent,
        sender: "character",
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, systemResponse]);
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
    <div className="relative min-h-screen w-full overflow-hidden flex flex-col">
      {/* Background with fallback gradient */}
      <div
        className="absolute inset-0 bg-cover bg-center z-0"
        style={{
          backgroundImage: "url('/images/forest-background.jpg'), linear-gradient(to bottom, #1a2e35, #0f172a)",
          imageRendering: "pixelated",
          opacity: 0.4, // Dimmed for better text readability
        }}
      />

      {/* Overlay for better text visibility */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/30 to-black/50 z-10" />

      <div className="relative z-20 flex flex-col h-screen">
        <header className="bg-amber-900/90 shadow-lg backdrop-blur-sm border-b-2 border-amber-700/70">
          <div className="max-w-7xl mx-auto px-4 py-3 sm:px-6 lg:px-8 flex justify-between items-center">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-amber-200 drop-shadow-[0_1px_2px_rgba(0,0,0,0.8)]">
                {game?.name || "Loading adventure..."}
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-amber-200 text-sm">
                <span className="font-bold">{user?.username || "Adventurer"}</span>
              </div>
              <button
                onClick={handleBackToGames}
                className="px-3 py-1 bg-amber-700 hover:bg-amber-600 text-amber-100 rounded-md text-sm border border-amber-500 shadow-md transition-colors"
              >
                Back to Adventures
              </button>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-hidden flex flex-col max-w-7xl w-full mx-auto px-4 py-4 sm:px-6 lg:px-8">
          {loading ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-amber-500 border-r-transparent"></div>
                <p className="mt-4 text-amber-200">Loading your adventure...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="bg-red-900/70 border border-red-500 text-red-200 px-6 py-4 rounded">
                <p className="text-lg font-medium">{error}</p>
                <button
                  onClick={handleBackToGames}
                  className="mt-4 px-4 py-2 bg-red-800 hover:bg-red-700 rounded border border-red-600"
                >
                  Return to Adventures
                </button>
              </div>
            </div>
          ) : (
            <>
              {/* Game messages */}
              <div className="flex-1 overflow-y-auto mb-4 pr-2 scrollbar-thin scrollbar-thumb-amber-700 scrollbar-track-amber-900/30">
                <div className="space-y-4 pb-2">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`px-4 py-3 rounded-lg max-w-3xl ${
                        message.sender === "user"
                          ? "ml-auto bg-amber-700/80 text-amber-100 border border-amber-600"
                          : message.sender === "system"
                          ? "mr-auto bg-gray-800/80 text-gray-200 border border-gray-700"
                          : "mr-auto bg-amber-800/80 text-amber-200 border border-amber-700"
                      }`}
                    >
                      <div className="text-sm">{message.content}</div>
                      <div className="text-xs mt-1 opacity-70 text-right">
                        {message.sender === "user" ? "You" : message.sender === "system" ? "System" : "Narrator"} •{" "}
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              </div>

              {/* Input form */}
              <div className="bg-amber-900/80 rounded-lg border-2 border-amber-700 p-3 backdrop-blur-sm">
                <form onSubmit={handleSendMessage} className="flex">
                  <input
                    type="text"
                    placeholder="What would you like to do?"
                    className="flex-1 px-4 py-2 bg-amber-100 border border-amber-600 rounded-l-md text-amber-900 placeholder-amber-700/50 focus:outline-none focus:ring-2 focus:ring-amber-500"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    disabled={sendingMessage}
                  />
                  <button
                    type="submit"
                    disabled={sendingMessage || !inputMessage.trim()}
                    className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-r-md border border-amber-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {sendingMessage ? "..." : "Send"}
                  </button>
                </form>
                <div className="mt-2 text-xs text-amber-300/70 px-2">Type &apos;help&apos; for available commands</div>
              </div>
            </>
          )}
        </main>

        {/* Game version or copyright */}
        <div className="relative z-20 text-center text-white text-xs py-2 bg-black/30 backdrop-blur-sm border-t border-gray-800">
          v0.1.0 Alpha • © 2023 The Last Centaur
        </div>
      </div>
    </div>
  );
}
