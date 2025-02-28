"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "./context/AuthContext";
import { useState, useRef, useEffect } from "react";

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false); // Start as not playing
  const [volume, setVolume] = useState(0.5);
  const [isMuted, setIsMuted] = useState(false);
  const [textVisible, setTextVisible] = useState(true);

  // Auto-redirect if already authenticated
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push("/games");
    }
  }, [isLoading, isAuthenticated, router]);

  // Text blinking effect for "Click to Start"
  useEffect(() => {
    const interval = setInterval(() => {
      setTextVisible((prev) => !prev);
    }, 800);
    return () => clearInterval(interval);
  }, []);

  const handleStartClick = () => {
    router.push("/login");
  };

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
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
          top: 20%;
          left: 50%;
          transform: translateX(-50%);
          animation: fadeIn 2s;
          max-width: 95%;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          z-index: 4;
          text-align: center;
        }

        .logo-text-top {
          font-family: "Press Start 2P", cursive;
          font-size: 64px;
          color: #ffd700;
          text-shadow: 3px 3px 0px #b8860b, 6px 6px 0px #8b6914, 9px 9px 0px #000;
          margin-bottom: 15px;
          letter-spacing: 6px;
          transform: perspective(500px) rotateX(10deg);
        }

        .logo-text-bottom {
          font-family: "Press Start 2P", cursive;
          font-size: 96px;
          color: #ffd700;
          text-shadow: 3px 3px 0px #b8860b, 6px 6px 0px #8b6914, 9px 9px 0px #000;
          letter-spacing: 6px;
          transform: perspective(500px) rotateX(10deg);
        }

        .start-prompt-container {
          position: absolute;
          bottom: 38%;
          left: 50%;
          transform: translateX(-50%);
          cursor: pointer;
          z-index: 5;
          margin-top: 80px;
        }

        .start-prompt {
          font-family: "Press Start 2P", cursive;
          font-size: 28px;
          color: white;
          text-shadow: 2px 2px 0px #000;
          padding: 15px;
          cursor: pointer;
          position: relative;
        }

        .social-links {
          position: absolute;
          top: 20px;
          right: 20px;
          display: flex;
          flex-direction: row;
          gap: 20px;
          z-index: 10;
        }

        .social-link {
          font-family: "Press Start 2P", cursive;
          font-size: 12px;
          color: #f9d71c;
          text-shadow: 2px 2px 0px #000;
          text-decoration: none;
          transition: color 0.3s;
        }

        .social-link:hover {
          color: #f97316;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes bounce {
          0%,
          20%,
          50%,
          80%,
          100% {
            transform: translateY(0);
          }
          40% {
            transform: translateY(-10px);
          }
          60% {
            transform: translateY(-5px);
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

        <div className="start-prompt-container" onClick={handleStartClick}>
          <div className="start-prompt" style={{ visibility: textVisible ? "visible" : "hidden" }}>
            CLICK TO START
          </div>
        </div>

        <div className="social-links">
          <a href="https://twitter.com/crstjames" className="social-link" target="_blank" rel="noopener noreferrer">
            X
          </a>
          <a
            href="https://discord.com/users/crstjames"
            className="social-link"
            target="_blank"
            rel="noopener noreferrer"
          >
            DISCORD
          </a>
          <a href="https://t.me/crstjames" className="social-link" target="_blank" rel="noopener noreferrer">
            TELEGRAM
          </a>
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
        <audio ref={audioRef} src="/audio/tlfc.mp3" loop />
        <div style={{ position: "absolute", bottom: "80px", left: "50%", transform: "translateX(-50%)", zIndex: 10 }}>
          <button
            onClick={togglePlay}
            style={{
              marginRight: "10px",
              padding: "5px 10px",
              backgroundColor: "#f97316",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
              fontFamily: "'Press Start 2P', cursive",
              fontSize: "10px",
            }}
          >
            {isPlaying ? "PAUSE" : "PLAY"}
          </button>
          <button
            onClick={toggleMute}
            style={{
              marginRight: "10px",
              padding: "5px 10px",
              backgroundColor: "#f97316",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
              fontFamily: "'Press Start 2P', cursive",
              fontSize: "10px",
            }}
          >
            {isMuted ? "UNMUTE" : "MUTE"}
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={volume}
            onChange={handleVolumeChange}
            style={{ cursor: "pointer" }}
          />
        </div>
      </div>
    </div>
  );
}
