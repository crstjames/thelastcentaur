"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showDebug, setShowDebug] = useState(false);
  const [debugInfo, setDebugInfo] = useState<string>("");
  const [selectedServer, setSelectedServer] = useState("Main Server");

  const router = useRouter();
  const { register, isAuthenticated } = useAuth();

  // Clear error when inputs change
  useEffect(() => {
    if (error) setError("");
  }, [username, email, password, confirmPassword]);

  // Redirect if already authenticated
  if (isAuthenticated) {
    router.push("/games");
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setDebugInfo("");

    // Validate form
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);

    try {
      await register(username, email, password);
      router.push("/games");
    } catch (error) {
      console.error("Registration error:", error);

      if (error instanceof Error) {
        // Check for common error messages
        if (
          error.message.includes("Username already registered") ||
          error.message.includes("username already exists") ||
          error.message.includes("already taken")
        ) {
          setError("This username is already taken. Please choose another one.");
        } else if (
          error.message.includes("Email already registered") ||
          error.message.includes("email already exists") ||
          error.message.includes("already in use")
        ) {
          setError("This email is already registered. Please use another email or try logging in.");
        } else {
          setError(error.message);
        }
        setDebugInfo(JSON.stringify(error, null, 2));
      } else {
        setError("Registration failed. Please try again.");
        setDebugInfo(JSON.stringify(error, null, 2));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden flex items-center justify-center">
      {/* Background with fallback gradient if image is missing */}
      <div
        className="absolute inset-0 bg-cover bg-center z-0"
        style={{
          backgroundImage: "url('/images/forest-background.jpg'), linear-gradient(to bottom, #1a2e35, #0f172a)",
          imageRendering: "pixelated",
        }}
      />

      {/* Overlay for better text visibility */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-black/40 z-10" />

      {/* Game title */}
      <div className="absolute top-16 left-0 right-0 z-20 text-center">
        <h1 className="text-6xl font-bold text-white drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)] tracking-wider">
          THE LAST CENTAUR
        </h1>
      </div>

      {/* Register container */}
      <div className="relative z-20 flex flex-col items-center justify-center w-full max-w-md px-4">
        <div className="flex flex-col items-center w-full">
          {/* Login and Register tabs */}
          <div className="flex mb-2 w-full justify-center">
            <Link
              href="/login"
              className="px-8 py-2 bg-amber-900/70 text-amber-200 font-semibold rounded-t-lg border-2 border-amber-700 mr-1 hover:bg-amber-800/80 transition-colors shadow-lg"
            >
              LOGIN
            </Link>
            <div className="px-8 py-2 bg-amber-700 text-white font-semibold rounded-t-lg border-2 border-amber-500 shadow-lg">
              REGISTER
            </div>
          </div>

          {/* Register form */}
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
                <label htmlFor="email" className="block text-amber-200 font-medium mb-1">
                  Email:
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  className="w-full px-3 py-2 bg-amber-100 border border-amber-500 rounded text-amber-900 placeholder-amber-700/50 focus:ring-2 focus:ring-amber-400 focus:border-transparent"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
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
                <label htmlFor="confirmPassword" className="block text-amber-200 font-medium mb-1">
                  Confirm Password:
                </label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  required
                  className="w-full px-3 py-2 bg-amber-100 border border-amber-500 rounded text-amber-900 placeholder-amber-700/50 focus:ring-2 focus:ring-amber-400 focus:border-transparent"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
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

              <div className="flex justify-center mt-6">
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-amber-600 text-white font-medium rounded border border-amber-400 hover:bg-amber-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md hover:shadow-lg"
                >
                  {loading ? "Creating account..." : "Create account"}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-1/2 left-1/4 w-1 h-1 bg-white rounded-full animate-ping opacity-70 duration-1000"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-white rounded-full animate-ping opacity-70 duration-700 delay-300"></div>
        <div className="absolute bottom-1/3 right-1/4 w-1 h-1 bg-white rounded-full animate-ping opacity-70 duration-1500 delay-700"></div>

        {/* Game version or copyright */}
        <div className="absolute bottom-8 text-white text-sm drop-shadow-[0_1px_1px_rgba(0,0,0,0.8)]">
          v0.1.0 Alpha • © 2023 The Last Centaur
        </div>
      </div>
    </div>
  );
}
