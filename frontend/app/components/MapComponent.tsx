/**
 * Map component for displaying the game world
 */

import React from "react";

interface MapProps {
  playerPosition: string; // "x,y" format
  visitedTiles?: Set<string>;
}

const MapComponent: React.FC<MapProps> = ({ playerPosition = "0,0", visitedTiles = new Set() }) => {
  // Parse the player position
  const parseCoordinates = (locationStr: string): [number, number] => {
    // Try to extract x,y format
    const coordMatch = locationStr.match(/(\d+),(\d+)/);
    if (coordMatch) {
      // Parse as numbers - X is east/west, Y is north/south
      return [parseInt(coordMatch[1]), parseInt(coordMatch[2])];
    }
    // Default position if parsing fails
    return [0, 0];
  };

  const [playerX, playerY] = parseCoordinates(playerPosition);

  // Create a 10x10 map grid
  const renderMapGrid = () => {
    const rows = [];

    for (let rowIndex = 0; rowIndex < 10; rowIndex++) {
      // Invert the row index to flip the map vertically
      // This makes north (decreasing Y) go up on the screen
      const row = 9 - rowIndex;

      const cells = [];
      for (let col = 0; col < 10; col++) {
        // Check if this is the player's position
        const isPlayerPosition = playerX === col && playerY === row;

        // Check if this tile has been visited
        const tileKey = `${col},${row}`;
        const hasBeenVisited =
          visitedTiles.has(tileKey) || (Math.abs(col - playerX) <= 1 && Math.abs(row - playerY) <= 1);

        // Determine the tile color based on terrain
        let tileColor = "#333"; // Default gray for unexplored
        if (hasBeenVisited) {
          // Terrain types aligned with map orientation
          if (row < 3) tileColor = "#4682B4"; // Water - blue (south/bottom)
          else if (row < 5) tileColor = "#696969"; // Mountain - dark gray (south-central)
          else if (row < 8) tileColor = "#8B4513"; // Plains - brown (central)
          else tileColor = "#228B22"; // Forest - green (north/top)
        }

        cells.push(
          <div
            key={`${row}-${col}`}
            className="map-tile"
            style={{
              backgroundColor: tileColor,
              position: "relative",
              border: isPlayerPosition ? "1px solid #FFD700" : "1px solid #333",
            }}
          >
            {isPlayerPosition && (
              <div
                style={{
                  position: "absolute",
                  top: "50%",
                  left: "50%",
                  transform: "translate(-50%, -50%)",
                  width: "10px",
                  height: "10px",
                  borderRadius: "50%",
                  backgroundColor: "#FFD700",
                }}
              />
            )}
          </div>
        );
      }

      rows.push(
        <div key={`row-${row}`} className="map-row">
          {cells}
        </div>
      );
    }

    return rows;
  };

  return (
    <div className="map-section">
      <h3 className="section-title">MAP</h3>

      <div className="map-container">
        {/* North marker */}
        <div className="direction-markers">
          <span className="compass-direction">N</span>
        </div>

        {/* West-East row with map */}
        <div className="compass-container">
          <span className="compass-direction">W</span>

          <div className="game-map">{renderMapGrid()}</div>

          <span className="compass-direction">E</span>
        </div>

        {/* South marker */}
        <div className="direction-markers">
          <span className="compass-direction">S</span>
        </div>
      </div>

      {/* Current position indicator */}
      <div className="map-position">Current position: ({playerPosition})</div>

      {/* Legend */}
      <div className="map-legend">
        <div className="legend-items">
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: "#228B22" }}></div>
            <span>Forest</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: "#8B4513" }}></div>
            <span>Plains</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: "#696969" }}></div>
            <span>Mountain</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: "#4682B4" }}></div>
            <span>Water</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: "#333" }}></div>
            <span>Unexplored</span>
          </div>
        </div>
      </div>

      <style jsx>{`
        .map-section {
          padding-top: 0;
          margin-top: 0;
          position: relative;
          display: flex;
          flex-direction: column;
          align-items: center;
          width: 100%;
        }

        .section-title {
          color: #ffd700;
          font-family: "Press Start 2P", monospace;
          font-size: 0.8rem;
          text-shadow: 2px 2px 0px #000;
          margin-bottom: 0.5rem;
          text-align: center;
        }

        .map-container {
          position: relative;
          display: flex;
          flex-direction: column;
          align-items: center;
          margin: 1rem 0;
          width: 100%;
        }

        .direction-markers {
          display: flex;
          justify-content: center;
          font-family: "Press Start 2P", monospace;
          font-size: 0.8rem;
          color: #ffd700;
          padding: 0.25rem 0;
        }

        .compass-container {
          display: flex;
          justify-content: space-between;
          align-items: center;
          width: 100%;
          padding: 0.25rem 0;
        }

        .compass-direction {
          color: #ffd700;
          font-family: "Press Start 2P", monospace;
          font-size: 0.8rem;
          padding: 0 0.5rem;
        }

        .game-map {
          display: flex;
          flex-direction: column;
          border: 2px solid #996633;
          background-color: rgba(12, 12, 12, 0.9);
          padding: 0.25rem;
        }

        .map-row {
          display: flex;
          flex-direction: row;
        }

        .map-tile {
          width: 24px;
          height: 24px;
          margin: 1px;
        }

        .map-position {
          font-family: "Press Start 2P", monospace;
          font-size: 0.6rem;
          color: #ffd700;
          text-align: center;
          margin-top: 0.5rem;
        }

        .map-legend {
          margin-top: 0.5rem;
          font-size: 0.6rem;
          width: 100%;
        }

        .legend-items {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
          margin-top: 0.5rem;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-family: "Press Start 2P", monospace;
          font-size: 0.6rem;
          color: #d97706;
        }

        .legend-color {
          width: 12px;
          height: 12px;
          border: 1px solid #555;
        }
      `}</style>
    </div>
  );
};

export default MapComponent;
