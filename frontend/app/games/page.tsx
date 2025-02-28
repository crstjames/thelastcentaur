"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "../context/AuthContext";
import { gameAPI } from "../services/api";

// Game type definition
interface Game {
  id: string;
  name: string;
  description: string;
  status: string;
  created_at: string;
}

export default function GamesPage() {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showNewGameForm, setShowNewGameForm] = useState(false);
  const [newGameName, setNewGameName] = useState("");
  const [newGameDescription, setNewGameDescription] = useState("");
  const [creatingGame, setCreatingGame] = useState(false);

  const router = useRouter();
  const { isAuthenticated, token, logout, user } = useAuth();

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  // Load games
  useEffect(() => {
    if (isAuthenticated && token) {
      loadGames();
    }
  }, [isAuthenticated, token]);

  const loadGames = async () => {
    setLoading(true);
    setError("");

    try {
      if (!token) return;

      const gamesData = await gameAPI.listGames(token);
      setGames(gamesData);
    } catch (err) {
      setError("Failed to load games");
      console.error("Error loading games:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGame = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setCreatingGame(true);

    try {
      if (!token) return;

      const newGame = await gameAPI.createGame(token, newGameName, newGameDescription);
      setGames([...games, newGame]);
      setShowNewGameForm(false);
      setNewGameName("");
      setNewGameDescription("");
    } catch (err) {
      setError("Failed to create game");
      console.error("Error creating game:", err);
    } finally {
      setCreatingGame(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!isAuthenticated) {
    return null; // Will redirect in useEffect
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden">
      {/* Background with fallback gradient */}
      <div
        className="absolute inset-0 bg-cover bg-center z-0"
        style={{
          backgroundImage: "url('/images/forest-background.jpg'), linear-gradient(to bottom, #1a2e35, #0f172a)",
          imageRendering: "pixelated",
        }}
      />

      {/* Overlay for better text visibility */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-black/40 z-10" />

      <div className="relative z-20">
        <header className="bg-amber-900/80 shadow-lg backdrop-blur-sm border-b-2 border-amber-700/70">
          <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
            <div className="flex items-center">
              <h1 className="text-3xl font-bold text-amber-200 drop-shadow-[0_1px_2px_rgba(0,0,0,0.8)]">
                THE LAST CENTAUR
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-amber-200 font-medium">
                Welcome, <span className="font-bold">{user?.username || "Adventurer"}</span>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-amber-700 hover:bg-amber-600 text-amber-100 rounded-md text-sm border border-amber-500 shadow-md transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl font-semibold text-amber-100 drop-shadow-[0_1px_1px_rgba(0,0,0,0.8)]">
              Your Adventures
            </h2>
            <button
              onClick={() => setShowNewGameForm(!showNewGameForm)}
              className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-md border border-amber-400 shadow-md transition-colors"
            >
              {showNewGameForm ? "Cancel" : "New Adventure"}
            </button>
          </div>

          {error && (
            <div className="bg-red-900/70 border border-red-500 text-red-200 px-4 py-3 rounded mb-6">{error}</div>
          )}

          {showNewGameForm && (
            <div className="bg-amber-800/90 rounded-lg p-6 mb-8 border-2 border-amber-600 shadow-xl backdrop-blur-sm">
              <h3 className="text-xl font-medium mb-4 text-amber-200">Begin New Adventure</h3>
              <form onSubmit={handleCreateGame}>
                <div className="space-y-4">
                  <div>
                    <label htmlFor="gameName" className="block text-sm font-medium text-amber-200">
                      Adventure Name
                    </label>
                    <input
                      type="text"
                      id="gameName"
                      required
                      className="mt-1 block w-full px-3 py-2 border border-amber-500 bg-amber-100 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent text-amber-900"
                      value={newGameName}
                      onChange={(e) => setNewGameName(e.target.value)}
                    />
                  </div>

                  <div>
                    <label htmlFor="gameDescription" className="block text-sm font-medium text-amber-200">
                      Description
                    </label>
                    <textarea
                      id="gameDescription"
                      rows={3}
                      className="mt-1 block w-full px-3 py-2 border border-amber-500 bg-amber-100 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent text-amber-900"
                      value={newGameDescription}
                      onChange={(e) => setNewGameDescription(e.target.value)}
                    />
                  </div>
                </div>

                <div className="mt-6">
                  <button
                    type="submit"
                    disabled={creatingGame}
                    className="w-full flex justify-center py-2 px-4 border border-amber-400 rounded-md shadow-sm text-sm font-medium text-white bg-amber-600 hover:bg-amber-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500 disabled:opacity-50 transition-colors"
                  >
                    {creatingGame ? "Creating..." : "Begin Adventure"}
                  </button>
                </div>
              </form>
            </div>
          )}

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-amber-500 border-r-transparent"></div>
              <p className="mt-4 text-amber-200">Loading your adventures...</p>
            </div>
          ) : games.length === 0 ? (
            <div className="text-center py-12 bg-amber-800/80 rounded-lg border-2 border-amber-600 shadow-xl backdrop-blur-sm">
              <p className="text-xl text-amber-200">You don&apos;t have any adventures yet.</p>
              <p className="mt-2 text-amber-300/70">Create a new adventure to begin your journey!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {games.map((game) => (
                <Link
                  key={game.id}
                  href={`/play/${game.id}`}
                  className="block bg-amber-800/80 rounded-lg overflow-hidden shadow-lg hover:ring-2 hover:ring-amber-400 transition-all border-2 border-amber-600 backdrop-blur-sm"
                >
                  <div className="p-6">
                    <h3 className="text-xl font-semibold mb-2 text-amber-200">{game.name}</h3>
                    <p className="text-amber-300/80 mb-4 line-clamp-2">{game.description}</p>
                    <div className="flex justify-between items-center">
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          game.status === "ACTIVE"
                            ? "bg-green-900/70 text-green-300 border border-green-500"
                            : "bg-amber-700/70 text-amber-300 border border-amber-500"
                        }`}
                      >
                        {game.status}
                      </span>
                      <span className="text-xs text-amber-400/70">
                        {new Date(game.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </main>

        {/* Decorative elements */}
        <div className="absolute top-1/2 left-1/4 w-1 h-1 bg-white rounded-full animate-ping opacity-70 duration-1000"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-white rounded-full animate-ping opacity-70 duration-700 delay-300"></div>
        <div className="absolute bottom-1/3 right-1/4 w-1 h-1 bg-white rounded-full animate-ping opacity-70 duration-1500 delay-700"></div>

        {/* Game version or copyright */}
        <div className="absolute bottom-8 left-0 right-0 text-center text-white text-sm drop-shadow-[0_1px_1px_rgba(0,0,0,0.8)]">
          v0.1.0 Alpha • © 2023 The Last Centaur
        </div>
      </div>
    </div>
  );
}
