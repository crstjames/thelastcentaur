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
  const { isAuthenticated, token, logout } = useAuth();

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
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold">The Last Centaur</h1>
          <button onClick={handleLogout} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md text-sm">
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-semibold">Your Games</h2>
          <button
            onClick={() => setShowNewGameForm(!showNewGameForm)}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-md"
          >
            {showNewGameForm ? "Cancel" : "New Game"}
          </button>
        </div>

        {error && (
          <div className="bg-red-900/50 border border-red-500 text-red-300 px-4 py-3 rounded mb-6">{error}</div>
        )}

        {showNewGameForm && (
          <div className="bg-gray-800 rounded-lg p-6 mb-8">
            <h3 className="text-xl font-medium mb-4">Create New Game</h3>
            <form onSubmit={handleCreateGame}>
              <div className="space-y-4">
                <div>
                  <label htmlFor="gameName" className="block text-sm font-medium text-gray-300">
                    Game Name
                  </label>
                  <input
                    type="text"
                    id="gameName"
                    required
                    className="mt-1 block w-full px-3 py-2 border border-gray-600 bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    value={newGameName}
                    onChange={(e) => setNewGameName(e.target.value)}
                  />
                </div>

                <div>
                  <label htmlFor="gameDescription" className="block text-sm font-medium text-gray-300">
                    Description
                  </label>
                  <textarea
                    id="gameDescription"
                    rows={3}
                    className="mt-1 block w-full px-3 py-2 border border-gray-600 bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    value={newGameDescription}
                    onChange={(e) => setNewGameDescription(e.target.value)}
                  />
                </div>
              </div>

              <div className="mt-6">
                <button
                  type="submit"
                  disabled={creatingGame}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  {creatingGame ? "Creating..." : "Create Game"}
                </button>
              </div>
            </form>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-500 border-r-transparent"></div>
            <p className="mt-4 text-gray-400">Loading your games...</p>
          </div>
        ) : games.length === 0 ? (
          <div className="text-center py-12 bg-gray-800 rounded-lg">
            <p className="text-xl text-gray-400">You don&apos;t have any games yet.</p>
            <p className="mt-2 text-gray-500">Create a new game to start your adventure!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {games.map((game) => (
              <Link
                key={game.id}
                href={`/play/${game.id}`}
                className="block bg-gray-800 rounded-lg overflow-hidden shadow-lg hover:ring-2 hover:ring-indigo-500 transition-all"
              >
                <div className="p-6">
                  <h3 className="text-xl font-semibold mb-2">{game.name}</h3>
                  <p className="text-gray-400 mb-4 line-clamp-2">{game.description}</p>
                  <div className="flex justify-between items-center">
                    <span
                      className={`px-2 py-1 rounded text-xs ${
                        game.status === "ACTIVE" ? "bg-green-900 text-green-300" : "bg-gray-700 text-gray-300"
                      }`}
                    >
                      {game.status}
                    </span>
                    <span className="text-xs text-gray-500">{new Date(game.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
