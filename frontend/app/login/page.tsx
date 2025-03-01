"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showDebug, setShowDebug] = useState(false);
  const [debugInfo, setDebugInfo] = useState<string>("");
  const [selectedServer, setSelectedServer] = useState("Main Server");
  const [formVisible, setFormVisible] = useState(false);

  const router = useRouter();
  const { login, isAuthenticated } = useAuth();

  // Clear error when inputs change
  useEffect(() => {
    if (error) setError("");
  }, [username, password]);

  // Fade in the form after the page loads - reduced delay for better responsiveness
  useEffect(() => {
    // Show form immediately rather than delaying
    setFormVisible(true);
  }, []);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push("/games");
    }
  }, [isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setDebugInfo("");

    try {
      await login(username, password);
      router.push("/games");
    } catch (error) {
      console.error("Login error:", error);

      if (error instanceof Error) {
        // Handle specific error messages
        if (
          error.message.includes("Incorrect username or password") ||
          error.message.includes("not found") ||
          error.message.includes("invalid") ||
          error.message.includes("Invalid authentication")
        ) {
          setError("Invalid username or password. Please try again.");
        } else if (
          error.message.includes("fetch") ||
          error.message.includes("network") ||
          error.message.includes("Failed to fetch") ||
          error.message.includes("Network request failed")
        ) {
          setError("Unable to connect to the server. Please check your internet connection and try again.");
        } else {
          setError(error.message);
        }
        setDebugInfo(JSON.stringify(error, null, 2));
      } else {
        setError("Login failed. Please try again.");
        setDebugInfo(JSON.stringify(error, null, 2));
      }
    } finally {
      setLoading(false);
    }
  };

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
          justify-content: center;
          color: white;
          text-align: center;
          z-index: 1;
          will-change: transform, opacity;
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

        .logo-container {
          position: absolute;
          top: 50px;
          left: 50%;
          transform: translateX(-50%);
          animation: fadeIn 0.5s ease-out;
          z-index: 4;
          opacity: ${formVisible ? 0.8 : 1};
          transition: opacity 0.3s ease-in-out;
          will-change: transform, opacity;
          text-align: center;
        }

        .logo-text-top {
          font-family: "Press Start 2P", cursive;
          font-size: 32px;
          color: #ffd700;
          text-shadow: 3px 3px 0px #b8860b, 6px 6px 0px #8b6914, 9px 9px 0px #000;
          margin-bottom: 8px;
          letter-spacing: 4px;
          transform: perspective(500px) rotateX(10deg);
        }

        .logo-text-bottom {
          font-family: "Press Start 2P", cursive;
          font-size: 48px;
          color: #ffd700;
          text-shadow: 3px 3px 0px #b8860b, 6px 6px 0px #8b6914, 9px 9px 0px #000;
          letter-spacing: 4px;
          transform: perspective(500px) rotateX(10deg);
        }

        .form-container {
          max-width: 450px;
          width: 90%;
          background-color: rgba(0, 0, 0, 0.7);
          border-radius: 10px;
          padding: 20px;
          z-index: 5;
          opacity: ${formVisible ? 1 : 0};
          transform: translateY(${formVisible ? "0" : "20px"});
          transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
          box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
          border: 2px solid #f97316;
          will-change: transform, opacity;
          margin: 60px auto 0;
        }

        .form-container select {
          display: none;
        }

        .input-field {
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

        .input-field:focus {
          outline: none;
          border-color: #f59e0b;
          box-shadow: 0 0 10px rgba(249, 115, 22, 0.5);
        }

        .input-label {
          font-family: "Press Start 2P", cursive;
          color: #f9d71c;
          font-size: 11px;
          margin-bottom: 6px;
          display: block;
          text-shadow: 2px 2px 0px #000;
          text-align: left;
        }

        .form-button {
          font-family: "Press Start 2P", cursive;
          background-color: #f97316;
          color: black;
          border: 2px solid #7c2d12;
          padding: 8px 16px;
          cursor: pointer;
          transition: background-color 0.2s ease;
          border-radius: 5px;
          font-size: 11px;
          margin-right: 10px;
          transform: translateY(0);
          transition: transform 0.1s ease, background-color 0.2s ease;
          will-change: transform;
        }

        .form-button:hover {
          background-color: #ea580c;
        }

        .form-button:active {
          transform: translateY(2px);
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

        .tab-container {
          display: flex;
          margin-bottom: 15px;
        }

        .tab {
          font-family: "Press Start 2P", cursive;
          padding: 10px 20px;
          cursor: pointer;
          font-size: 14px;
          text-shadow: 2px 2px 0px #000;
          transition: all 0.2s ease;
          will-change: opacity, transform;
        }

        .active-tab {
          background-color: #f97316;
          color: black;
          border: 2px solid #7c2d12;
          border-bottom: none;
          border-radius: 5px 5px 0 0;
        }

        .inactive-tab {
          background-color: rgba(0, 0, 0, 0.5);
          color: #f9d71c;
          border: 2px solid #7c2d12;
          border-bottom: none;
          border-radius: 5px 5px 0 0;
          opacity: 0.7;
          transition: opacity 0.2s ease;
        }

        .inactive-tab:hover {
          opacity: 1;
        }

        .back-section {
          margin-top: 80px;
          margin-bottom: 40px;
          text-align: center;
          width: 100%;
        }

        .back-button-container {
          position: relative;
          display: inline-block;
          z-index: 10;
          cursor: pointer;
          padding: 15px 30px;
          background: rgba(0, 0, 0, 0.4);
          border-radius: 5px;
          border: 2px solid #ffd700;
          transition: all 0.3s ease;
        }

        .back-text {
          font-family: "Press Start 2P", cursive;
          font-size: 20px;
          color: #ffd700;
          text-shadow: 2px 2px 0px #000;
          transition: all 0.3s ease;
          letter-spacing: 2px;
        }

        .back-button-container:hover {
          background: rgba(0, 0, 0, 0.6);
          transform: scale(1.05);
        }

        .back-button-container:hover .back-text {
          color: white;
          text-shadow: 3px 3px 0px #000;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
      `}</style>

      <div className="crt-frame"></div>
      <div className="crt-overlay"></div>

      <div className="crt-content">
        <div className="logo-container">
          <div className="logo-text-top">THE</div>
          <div className="logo-text-bottom">LAST CENTAUR</div>
        </div>

        <div className="form-container">
          <div className="tab-container">
            <div className="tab active-tab">LOGIN</div>
            <Link href="/register">
              <div className="tab inactive-tab">REGISTER</div>
            </Link>
          </div>

          {error && (
            <div className="error-message">
              <span>{error}</span>
              <button
                onClick={() => setShowDebug(!showDebug)}
                className="text-xs text-gray-300 hover:text-white float-right"
              >
                ?
              </button>
            </div>
          )}

          {showDebug && debugInfo && (
            <div className="bg-gray-900 p-3 rounded text-xs text-gray-400 overflow-auto max-h-32 mb-4">
              <pre>{debugInfo}</pre>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="username" className="input-label">
                USERNAME:
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="input-field"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>

            <div className="mb-4">
              <label htmlFor="password" className="input-label">
                PASSWORD:
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="input-field"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <div className="mb-4">
              <label htmlFor="server" className="input-label">
                SERVER:
              </label>
              <select
                id="server"
                name="server"
                className="input-field"
                value={selectedServer}
                onChange={(e) => setSelectedServer(e.target.value)}
              >
                <option value="Main Server">MAIN SERVER (1)</option>
                <option value="Test Server" disabled>
                  TEST SERVER (OFFLINE)
                </option>
              </select>
            </div>

            <div className="flex justify-between mt-6">
              <button type="submit" disabled={loading} className="form-button">
                {loading ? "LOGGING IN..." : "LOGIN"}
              </button>

              <button
                type="button"
                className="form-button"
                style={{ backgroundColor: "#b45309", borderColor: "#78350f" }}
              >
                FORGOT PASSWORD
              </button>
            </div>
          </form>
        </div>

        <div className="back-section">
          <Link href="/" className="back-button-container">
            <div className="back-text">BACK</div>
          </Link>
        </div>

        <div
          style={{
            position: "absolute",
            bottom: "20px",
            left: "50%",
            transform: "translateX(-50%)",
            fontFamily: "'Press Start 2P', cursive",
            fontSize: "15px",
            zIndex: 10,
          }}
        >
          v0.1.0 Alpha • © 2014 The Last Centaur
        </div>
      </div>
    </div>
  );
}
