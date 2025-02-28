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

  const router = useRouter();
  const { login, isAuthenticated } = useAuth();

  // Clear error when inputs change
  useEffect(() => {
    if (error) setError("");
  }, [username, password]);

  // Redirect if already authenticated
  if (isAuthenticated) {
    router.push("/games");
    return null;
  }

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
    <div className="relative min-h-screen w-full overflow-hidden flex items-center justify-center">
      {/* Background with strong gradient since image is missing */}
      <div
        className="absolute inset-0 bg-cover bg-center z-0"
        style={{
          background: "linear-gradient(to bottom, #2d1b00, #0f172a)",
        }}
      />

      {/* Overlay pattern for texture */}
      <div
        className="absolute inset-0 z-10 opacity-10"
        style={{
          backgroundImage:
            'url(\'data:image/svg+xml,%3Csvg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="%239C92AC" fill-opacity="0.4" fill-rule="evenodd"%3E%3Ccircle cx="3" cy="3" r="3"/%3E%3Ccircle cx="13" cy="13" r="3"/%3E%3C/g%3E%3C/svg%3E\')',
        }}
      />

      {/* Game title */}
      <div className="absolute top-16 left-0 right-0 z-20 text-center">
        <h1 className="text-6xl font-bold text-amber-300 drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)] tracking-wider">
          THE LAST CENTAUR
        </h1>
      </div>

      {/* Login container */}
      <div className="relative z-20 flex flex-col items-center justify-center w-full max-w-md px-4">
        <div className="flex flex-col items-center w-full">
          {/* Login and Register tabs */}
          <div className="flex mb-2 w-full justify-center">
            <div className="px-8 py-2 bg-amber-700 text-white font-semibold rounded-t-lg border-2 border-amber-500 shadow-lg">
              LOGIN
            </div>
            <Link
              href="/register"
              className="px-8 py-2 bg-amber-900/70 text-amber-200 font-semibold rounded-t-lg border-2 border-amber-700 ml-1 hover:bg-amber-800/80 transition-colors shadow-lg"
            >
              REGISTER
            </Link>
          </div>

          {/* Login form */}
          <div className="w-full bg-amber-800/90 rounded-lg border-2 border-amber-600 p-6 shadow-xl backdrop-blur-sm">
            {error && (
              <div className="bg-red-900/70 border border-red-500 text-red-200 px-4 py-3 rounded relative mb-4">
                <span className="block sm:inline">{error}</span>
                <button onClick={() => setShowDebug(!showDebug)} className="absolute top-0 right-0 px-4 py-3">
                  <span className="text-xs text-red-300 hover:text-white">?</span>
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
                <label htmlFor="username" className="block text-amber-200 font-medium mb-1">
                  Username:
                </label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  className="w-full px-3 py-2 bg-amber-100 border border-amber-500 rounded text-amber-900 placeholder-amber-700/50 focus:ring-2 focus:ring-amber-400 focus:border-transparent"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>

              <div className="mb-4">
                <label htmlFor="password" className="block text-amber-200 font-medium mb-1">
                  Password:
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  className="w-full px-3 py-2 bg-amber-100 border border-amber-500 rounded text-amber-900 placeholder-amber-700/50 focus:ring-2 focus:ring-amber-400 focus:border-transparent"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              <div className="mb-4">
                <label htmlFor="server" className="block text-amber-200 font-medium mb-1">
                  Server:
                </label>
                <select
                  id="server"
                  name="server"
                  className="w-full px-3 py-2 bg-amber-100 border border-amber-500 rounded text-amber-900 focus:ring-2 focus:ring-amber-400 focus:border-transparent"
                  value={selectedServer}
                  onChange={(e) => setSelectedServer(e.target.value)}
                >
                  <option value="Main Server">Main Server (1)</option>
                  <option value="Test Server" disabled>
                    Test Server (Offline)
                  </option>
                </select>
              </div>

              <div className="flex justify-between mt-6">
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-amber-600 text-white font-medium rounded border border-amber-400 hover:bg-amber-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md hover:shadow-lg"
                >
                  {loading ? "Logging in..." : "Login"}
                </button>

                <button
                  type="button"
                  className="px-4 py-2 bg-amber-900 text-amber-200 font-medium rounded border border-amber-700 hover:bg-amber-800 transition-colors shadow-md hover:shadow-lg"
                >
                  Forgot password
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-1/2 left-1/4 w-1 h-1 bg-amber-300 rounded-full animate-ping opacity-70 duration-1000"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-amber-300 rounded-full animate-ping opacity-70 duration-700 delay-300"></div>
        <div className="absolute bottom-1/3 right-1/4 w-1 h-1 bg-amber-300 rounded-full animate-ping opacity-70 duration-1500 delay-700"></div>

        {/* Game version or copyright */}
        <div className="absolute bottom-8 text-amber-200 text-sm drop-shadow-[0_1px_1px_rgba(0,0,0,0.8)]">
          v0.1.0 Alpha • © 2023 The Last Centaur
        </div>
      </div>
    </div>
  );
}
