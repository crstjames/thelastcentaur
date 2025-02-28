"use client";

import { useEffect } from "react";

export default function TestPage() {
  useEffect(() => {
    console.log("Test page mounted");
  }, []);

  return (
    <div
      style={{
        backgroundColor: "red",
        color: "white",
        padding: "20px",
        margin: "20px",
        border: "5px solid yellow",
        height: "300px",
        width: "300px",
      }}
    >
      <h1>Test Page</h1>
      <p>If you can see this, styling is working</p>
      <img
        src="/images/bg.png"
        alt="Background Test"
        style={{ width: "100px", height: "100px", objectFit: "cover", border: "2px solid white" }}
      />
    </div>
  );
}
