"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { authAPI } from "../services/api";

// Define the auth state type
interface User {
  id: string;
  username: string;
  email: string;
}

interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  token: string | null;
  user: User | null;
}

// Define the auth context type
interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

// Create the auth context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth provider props
interface AuthProviderProps {
  children: ReactNode;
}

// Create the auth provider component
export function AuthProvider({ children }: AuthProviderProps) {
  // Initialize auth state
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    token: null,
    user: null,
  });

  // Check for existing token on mount
  useEffect(() => {
    const loadAuthState = async () => {
      try {
        const storedToken = localStorage.getItem("token");
        const storedUser = localStorage.getItem("user");

        if (storedToken && storedUser) {
          // Verify token is still valid
          const isValid = await authAPI.verifyToken(storedToken);

          if (isValid) {
            setAuthState({
              isAuthenticated: true,
              isLoading: false,
              token: storedToken,
              user: JSON.parse(storedUser),
            });
            return;
          } else {
            console.log("Stored token is invalid or expired");
          }
        }
      } catch (error) {
        console.error("Error loading auth state:", error);
      }

      // Clear invalid token/user
      localStorage.removeItem("token");
      localStorage.removeItem("user");

      setAuthState({
        isAuthenticated: false,
        isLoading: false,
        token: null,
        user: null,
      });
    };

    loadAuthState();
  }, []);

  // Login function
  const login = async (username: string, password: string) => {
    try {
      const response = await authAPI.login(username, password);
      console.log("Login response:", response);

      const { access_token, user } = response;

      // Save to localStorage
      localStorage.setItem("token", access_token);
      localStorage.setItem(
        "user",
        JSON.stringify({
          ...user,
          username, // Ensure we store the username from the login attempt
        })
      );

      // Update state
      setAuthState({
        isAuthenticated: true,
        isLoading: false,
        token: access_token,
        user: {
          ...user,
          username, // Ensure we use the username from the login attempt
        },
      });
    } catch (error) {
      console.error("Login error in context:", error);
      throw error;
    }
  };

  // Register function
  const register = async (username: string, email: string, password: string) => {
    try {
      const response = await authAPI.register(username, email, password);
      console.log("Registration response:", response);

      const { access_token, user } = response;

      // Save to localStorage
      localStorage.setItem("token", access_token);
      localStorage.setItem(
        "user",
        JSON.stringify({
          ...user,
          username, // Ensure we store the username from the registration
          email, // Ensure we store the email from the registration
        })
      );

      // Update state
      setAuthState({
        isAuthenticated: true,
        isLoading: false,
        token: access_token,
        user: {
          ...user,
          username, // Ensure we use the username from the registration
          email, // Ensure we use the email from the registration
        },
      });
    } catch (error) {
      console.error("Registration error in context:", error);
      throw error;
    }
  };

  // Logout function
  const logout = () => {
    // Clear localStorage
    localStorage.removeItem("token");
    localStorage.removeItem("user");

    // Update state
    setAuthState({
      isAuthenticated: false,
      isLoading: false,
      token: null,
      user: null,
    });
  };

  // Provide the auth context
  return (
    <AuthContext.Provider
      value={{
        ...authState,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use the auth context
export function useAuth() {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}
