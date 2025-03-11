/**
 * This is an example component showing how the inventory should be styled
 * Separate from the main game interface to avoid conflicts
 */

import React from "react";

interface InventoryProps {
  items: string[];
  maxSlots?: number;
}

const InventoryExample: React.FC<InventoryProps> = ({ items = [], maxSlots = 8 }) => {
  // Filter out the old_map item
  const displayItems = items.filter((item) => item !== "old_map");
  const hasItems = displayItems.length > 0;

  return (
    <div className="inventory-section">
      <h3 className="section-title">INVENTORY</h3>

      <div className="inventory-container">
        {hasItems ? (
          <div className="inventory-grid">
            {/* Display actual inventory items */}
            {displayItems.slice(0, maxSlots).map((item, index) => (
              <div key={index} className="inventory-slot">
                <div className="inventory-item">{item.replace(/_/g, " ")}</div>
                <span className="item-count">×1</span>
              </div>
            ))}

            {/* Fill remaining slots with empty placeholders */}
            {displayItems.length < maxSlots && (
              <>
                {Array(maxSlots - displayItems.length)
                  .fill(null)
                  .map((_, i) => (
                    <div key={`empty-${i}`} className="inventory-slot inventory-slot-empty">
                      [empty]
                    </div>
                  ))}
              </>
            )}
          </div>
        ) : (
          <>
            <div className="inventory-empty">No items</div>
            <div className="inventory-grid" style={{ marginTop: "1rem" }}>
              {Array(maxSlots)
                .fill(null)
                .map((_, i) => (
                  <div key={`empty-${i}`} className="inventory-slot inventory-slot-empty">
                    [empty]
                  </div>
                ))}
            </div>
          </>
        )}
      </div>

      <style jsx>{`
        .inventory-section {
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

        .inventory-container {
          width: 100%;
          display: flex;
          flex-direction: column;
          margin-top: 1rem;
          border: 2px solid #996633;
          background-color: rgba(12, 12, 12, 0.9);
          padding: 0.5rem;
        }

        .inventory-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 0.5rem;
          width: 100%;
        }

        .inventory-slot {
          height: 40px;
          border: 1px solid #555;
          background-color: rgba(34, 34, 34, 0.7);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0.25rem;
          color: #d97706;
          font-family: "Press Start 2P", monospace;
          font-size: 0.6rem;
          position: relative;
        }

        .inventory-slot-empty {
          color: #666;
          border: 1px dashed #555;
        }

        .inventory-item {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: flex-start;
          padding-left: 0.5rem;
          color: #d97706;
          background-color: rgba(40, 26, 13, 0.7);
          font-family: "Press Start 2P", monospace;
          font-size: 0.6rem;
          border: 1px solid #996633;
          box-shadow: inset 0 0 5px rgba(255, 215, 0, 0.3);
          text-shadow: 1px 1px 0px #000;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .inventory-empty {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #996633;
          font-family: "Press Start 2P", monospace;
          font-size: 0.7rem;
          margin-top: 1rem;
          text-shadow: 1px 1px 0px #000;
        }

        .item-count {
          position: absolute;
          bottom: 2px;
          right: 4px;
          font-size: 0.5rem;
          color: #ffd700;
        }
      `}</style>
    </div>
  );
};

export default InventoryExample;

// Example usage:
// <InventoryExample items={["rusty_sword", "health_potion", "shadow_key", "stealth_cloak"]} />
