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
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="max-w-md w-full space-y-8 p-10 bg-gray-800 rounded-xl shadow-lg">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white">The Last Centaur</h1>
          <p className="mt-2 text-gray-400">Sign in to continue your adventure</p>
        </div>

        {error && (
          <div className="bg-red-900/50 border border-red-500 text-red-300 px-4 py-3 rounded relative">
            <span className="block sm:inline">{error}</span>
            <button onClick={() => setShowDebug(!showDebug)} className="absolute top-0 right-0 px-4 py-3">
              <span className="text-xs text-red-300 hover:text-white">?</span>
            </button>
          </div>
        )}

        {showDebug && debugInfo && (
          <div className="bg-gray-900 p-3 rounded text-xs text-gray-400 overflow-auto max-h-32">
            <pre>{debugInfo}</pre>
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="username" className="sr-only">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-600 bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-600 bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </div>

          <div className="text-center text-sm">
            <p className="text-gray-400">
              Don&apos;t have an account?{" "}
              <Link href="/register" className="text-indigo-400 hover:text-indigo-300">
                Register
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
