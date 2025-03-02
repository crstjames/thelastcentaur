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
  const [gameToDelete, setGameToDelete] = useState<Game | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletingGame, setDeletingGame] = useState(false);

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

      try {
        const gamesData = await gameAPI.listGames(token);
        setGames(gamesData);
      } catch (apiErr) {
        console.error("API error loading games:", apiErr);
        setError("Unable to connect to the game server. Please try again later.");

        // Set empty games array to allow creating new games
        setGames([]);
      }
    } catch (err) {
      console.error("Unexpected error loading games:", err);
      setError("An unexpected error occurred. Please try again later.");
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

      try {
        const newGame = await gameAPI.createGame(token, newGameName, newGameDescription);
        setGames([...games, newGame]);
        setShowNewGameForm(false);
        setNewGameName("");
        setNewGameDescription("");
      } catch (apiErr) {
        console.error("API error creating game:", apiErr);
        if (apiErr instanceof Error && apiErr.message.includes("409")) {
          setError("A game with this name already exists. Please choose a different name.");
        } else {
          setError("Unable to connect to the game server. Please try again later.");
        }
      }
    } catch (err) {
      console.error("Unexpected error creating game:", err);
      setError("An unexpected error occurred. Please try again later.");
    } finally {
      setCreatingGame(false);
    }
  };

  const handleShowDeleteModal = (e: React.MouseEvent, game: Game) => {
    e.preventDefault();
    e.stopPropagation();
    setGameToDelete(game);
    setShowDeleteModal(true);
  };

  const handleCloseDeleteModal = () => {
    setShowDeleteModal(false);
    setGameToDelete(null);
  };

  const handleDeleteGame = async () => {
    if (!gameToDelete || !token) return;

    setDeletingGame(true);
    setError("");

    try {
      await gameAPI.deleteGame(token, gameToDelete.id);
      // Remove the deleted game from the state
      setGames(games.filter((game) => game.id !== gameToDelete.id));
      setShowDeleteModal(false);
      setGameToDelete(null);
    } catch (err) {
      console.error("Error deleting game:", err);
      setError("Failed to delete the adventure. Please try again later.");
    } finally {
      setDeletingGame(false);
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
          background-color: #2d1b00;
          background-image: url("/images/bg.png");
          background-size: cover;
          background-position: center;
          display: flex;
          flex-direction: column;
          align-items: center;
          color: white;
          z-index: 1;
          overflow-y: auto;
        }

        .crt-overlay {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background-color: rgba(0, 0, 0, 0.3);
          z-index: 1;
          pointer-events: none;
        }

        .header-container {
          width: 100%;
          padding: 30px 0 20px;
          display: flex;
          flex-direction: column;
          align-items: center;
          z-index: 10;
          position: relative;
          margin-bottom: 15px;
        }

        .game-title {
          font-family: "Press Start 2P", cursive;
          font-size: 46px;
          color: #ffd700;
          text-shadow: 3px 3px 0px #b8860b, 6px 6px 0px #8b6914, 9px 9px 0px #000;
          letter-spacing: 4px;
          transform: perspective(500px) rotateX(10deg);
          text-align: center;
        }

        .main-container {
          width: 90%;
          max-width: 1000px;
          margin: 0 auto;
          padding: 20px;
          z-index: 10;
        }

        .user-welcome {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0 0 10px 0;
          margin-bottom: 30px;
          border-bottom: 2px dashed rgba(249, 115, 22, 0.4);
          width: 100%;
        }

        .welcome-text {
          font-family: "Press Start 2P", cursive;
          font-size: 20px;
          color: #ffd700;
          text-shadow: 2px 2px 0px #000;
          letter-spacing: 1px;
        }

        .logout-button {
          font-family: "Press Start 2P", cursive;
          background-color: #f97316;
          color: black;
          border: 2px solid #7c2d12;
          padding: 8px 16px;
          cursor: pointer;
          transition: background-color 0.2s ease;
          border-radius: 5px;
          font-size: 10px;
          transform: translateY(0);
          transition: transform 0.1s ease, background-color 0.2s ease;
        }

        .logout-button:hover {
          background-color: #ea580c;
        }

        .logout-button:active {
          transform: translateY(2px);
        }

        .adventures-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 25px;
          padding-top: 5px;
        }

        .adventures-title {
          font-family: "Press Start 2P", cursive;
          font-size: 20px;
          color: #ffd700;
          text-shadow: 2px 2px 0px #000;
        }

        .new-button {
          font-family: "Press Start 2P", cursive;
          background-color: #ffd700;
          color: black;
          border: 2px solid #b8860b;
          padding: 8px 16px;
          cursor: pointer;
          transition: background-color 0.2s ease;
          border-radius: 5px;
          font-size: 10px;
        }

        .new-button:hover {
          background-color: #f0c800;
          box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
        }

        .error-message {
          background-color: rgba(220, 38, 38, 0.7);
          border: 1px solid #ef4444;
          color: white;
          padding: 10px;
          border-radius: 5px;
          margin-bottom: 15px;
          font-family: "Press Start 2P", cursive;
          font-size: 10px;
          text-align: left;
        }

        .game-form {
          background-color: rgba(0, 0, 0, 0.7);
          border-radius: 10px;
          padding: 20px;
          margin-bottom: 25px;
          border: 2px solid #f97316;
          box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }

        .form-title {
          font-family: "Press Start 2P", cursive;
          font-size: 16px;
          color: #ffd700;
          text-shadow: 2px 2px 0px #000;
          margin-bottom: 15px;
        }

        .form-label {
          font-family: "Press Start 2P", cursive;
          color: #f9d71c;
          font-size: 11px;
          margin-bottom: 6px;
          display: block;
          text-shadow: 2px 2px 0px #000;
        }

        .form-input {
          font-family: "Press Start 2P", cursive;
          background-color: rgba(10, 10, 10, 0.8);
          border: 2px solid #f97316;
          color: white;
          padding: 12px;
          margin-bottom: 20px;
          width: 100%;
          border-radius: 5px;
          font-size: 11px;
          box-sizing: border-box;
        }

        .form-input:focus {
          outline: none;
          border-color: #f59e0b;
          box-shadow: 0 0 10px rgba(249, 115, 22, 0.5);
        }

        .form-button {
          font-family: "Press Start 2P", cursive;
          width: 100%;
          background-color: #f97316;
          color: black;
          border: 2px solid #7c2d12;
          padding: 10px;
          cursor: pointer;
          transition: background-color 0.2s ease;
          border-radius: 5px;
          font-size: 12px;
          margin-top: 10px;
        }

        .form-button:hover {
          background-color: #ea580c;
        }

        .loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 40px 0;
        }

        .loading-spinner {
          width: 40px;
          height: 40px;
          border: 4px solid rgba(255, 215, 0, 0.3);
          border-radius: 50%;
          border-top-color: #ffd700;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }

        .loading-text {
          font-family: "Press Start 2P", cursive;
          font-size: 14px;
          color: #ffd700;
          text-shadow: 2px 2px 0px #000;
          margin-top: 15px;
        }

        .empty-message {
          font-family: "Press Start 2P", cursive;
          text-align: center;
          background-color: rgba(0, 0, 0, 0.7);
          border-radius: 10px;
          padding: 40px 20px;
          border: 2px solid #f97316;
        }

        .empty-title {
          font-size: 16px;
          color: #ffd700;
          text-shadow: 2px 2px 0px #000;
          margin-bottom: 10px;
        }

        .empty-subtitle {
          font-size: 12px;
          color: #f9d71c;
          opacity: 0.8;
          text-shadow: 1px 1px 0px #000;
        }

        .games-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 20px;
        }

        .game-card-container {
          position: relative;
        }

        .delete-button {
          position: absolute;
          top: 8px;
          right: 8px;
          width: 26px;
          height: 26px;
          border-radius: 50%;
          background-color: #dc2626;
          color: white;
          border: 2px solid #7f1d1d;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          font-weight: bold;
          cursor: pointer;
          z-index: 2;
          opacity: 0.8;
          transition: all 0.2s ease;
          font-family: Arial, sans-serif;
          padding: 0;
          line-height: 0;
        }

        .delete-button:hover {
          opacity: 1;
          transform: scale(1.1);
          box-shadow: 0 0 8px rgba(220, 38, 38, 0.6);
        }

        .game-card {
          background-color: rgba(0, 0, 0, 0.7);
          border-radius: 10px;
          overflow: hidden;
          border: 2px solid #f97316;
          transition: all 0.3s ease;
          cursor: pointer;
        }

        .game-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4);
          border-color: #ffd700;
        }

        .game-card-content {
          padding: 15px;
        }

        .game-card-title {
          font-family: "Press Start 2P", cursive;
          font-size: 14px;
          color: #ffd700;
          text-shadow: 2px 2px 0px #000;
          margin-bottom: 10px;
        }

        .game-card-description {
          font-family: "Press Start 2P", cursive;
          font-size: 10px;
          color: white;
          margin-bottom: 15px;
          line-height: 1.4;
          max-height: 70px;
          overflow: hidden;
        }

        .game-card-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .game-status {
          font-family: "Press Start 2P", cursive;
          font-size: 8px;
          background-color: rgba(34, 197, 94, 0.3);
          color: #4ade80;
          padding: 4px 8px;
          border-radius: 4px;
          border: 1px solid #4ade80;
        }

        .game-status.inactive {
          background-color: rgba(251, 191, 36, 0.3);
          color: #fbbf24;
          border-color: #fbbf24;
        }

        .game-date {
          font-family: "Press Start 2P", cursive;
          font-size: 8px;
          color: #f9d71c;
          opacity: 0.7;
        }

        .modal-backdrop {
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          background-color: rgba(0, 0, 0, 0.7);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 100;
        }

        .modal-container {
          background-color: rgba(10, 10, 10, 0.9);
          border: 3px solid #f97316;
          border-radius: 8px;
          width: 90%;
          max-width: 500px;
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
          padding: 20px;
          animation: modal-appear 0.3s ease-out forwards;
        }

        @keyframes modal-appear {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .modal-title {
          font-family: "Press Start 2P", cursive;
          font-size: 18px;
          color: #ffd700;
          text-shadow: 2px 2px 0px #000;
          margin-bottom: 15px;
          text-align: center;
        }

        .modal-content {
          font-family: "Press Start 2P", cursive;
          font-size: 12px;
          color: white;
          margin-bottom: 20px;
          line-height: 1.5;
          text-align: center;
        }

        .modal-content p {
          margin-bottom: 10px;
        }

        .modal-footer {
          display: flex;
          justify-content: center;
          gap: 15px;
        }

        .cancel-button {
          font-family: "Press Start 2P", cursive;
          background-color: #9ca3af;
          color: #1f2937;
          border: 2px solid #4b5563;
          padding: 10px 20px;
          cursor: pointer;
          border-radius: 5px;
          font-size: 12px;
          transition: all 0.2s ease;
        }

        .cancel-button:hover {
          background-color: #d1d5db;
        }

        .delete-confirm-button {
          font-family: "Press Start 2P", cursive;
          background-color: #dc2626;
          color: white;
          border: 2px solid #7f1d1d;
          padding: 10px 20px;
          cursor: pointer;
          border-radius: 5px;
          font-size: 12px;
          transition: all 0.2s ease;
        }

        .delete-confirm-button:hover {
          background-color: #ef4444;
        }

        .delete-confirm-button:disabled,
        .cancel-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .footer {
          position: absolute;
          bottom: 20px;
          left: 50%;
          transform: translateX(-50%);
          font-family: "Press Start 2P", cursive;
          font-size: 12px;
          color: white;
          text-shadow: 2px 2px 0px #000;
          z-index: 10;
        }
      `}</style>

      <div className="crt-frame"></div>
      <div className="crt-overlay"></div>

      <div className="crt-content">
        <header className="header-container">
          <div className="game-title">THE LAST CENTAUR</div>
        </header>

        <main className="main-container">
          <div className="user-welcome">
            <div className="welcome-text">Welcome, {user?.username}!</div>
            <button className="logout-button" onClick={handleLogout}>
              Logout
            </button>
          </div>

          <div className="adventures-header">
            <div className="adventures-title">Your Adventures</div>
            <button className="new-button" onClick={() => setShowNewGameForm(!showNewGameForm)}>
              {showNewGameForm ? "Cancel" : "New Adventure"}
            </button>
          </div>

          {error && <div className="error-message">{error}</div>}

          {showNewGameForm && (
            <div className="game-form">
              <div className="form-title">Begin New Adventure</div>
              <form onSubmit={handleCreateGame}>
                <label htmlFor="gameName" className="form-label">
                  Adventure Name:
                </label>
                <input
                  type="text"
                  id="gameName"
                  required
                  className="form-input"
                  value={newGameName}
                  onChange={(e) => setNewGameName(e.target.value)}
                />

                <label htmlFor="gameDescription" className="form-label">
                  Description:
                </label>
                <textarea
                  id="gameDescription"
                  rows={3}
                  className="form-input"
                  value={newGameDescription}
                  onChange={(e) => setNewGameDescription(e.target.value)}
                />

                <button type="submit" disabled={creatingGame} className="form-button">
                  {creatingGame ? "Creating..." : "Begin Adventure"}
                </button>
              </form>
            </div>
          )}

          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <div className="loading-text">Loading your adventures...</div>
            </div>
          ) : games.length === 0 ? (
            <div className="empty-message">
              <div className="empty-title">You don&apos;t have any adventures yet.</div>
              <div className="empty-subtitle">Create a new adventure to begin your journey!</div>
            </div>
          ) : (
            <div className="games-grid">
              {games.map((game) => (
                <div key={game.id} className="game-card-container">
                  <Link href={`/play/${game.id}`}>
                    <div className="game-card">
                      <div className="game-card-content">
                        <div className="game-card-title">{game.name}</div>
                        <div className="game-card-description">{game.description}</div>
                        <div className="game-card-footer">
                          <div className={`game-status ${game.status !== "ACTIVE" ? "inactive" : ""}`}>
                            {game.status}
                          </div>
                          <div className="game-date">{new Date(game.created_at).toLocaleDateString()}</div>
                        </div>
                      </div>
                    </div>
                  </Link>
                  <button
                    className="delete-button"
                    onClick={(e) => handleShowDeleteModal(e, game)}
                    title="Delete adventure"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </main>

        <div className="footer">v0.1.0 Alpha • © 2023 The Last Centaur</div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && gameToDelete && (
        <div className="modal-backdrop">
          <div className="modal-container">
            <div className="modal-title">Delete Adventure</div>
            <div className="modal-content">
              <p>Are you sure you want to delete &ldquo;{gameToDelete.name}&rdquo;?</p>
              <p>This action cannot be undone.</p>
            </div>
            <div className="modal-footer">
              <button className="cancel-button" onClick={handleCloseDeleteModal} disabled={deletingGame}>
                Cancel
              </button>
              <button className="delete-confirm-button" onClick={handleDeleteGame} disabled={deletingGame}>
                {deletingGame ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
