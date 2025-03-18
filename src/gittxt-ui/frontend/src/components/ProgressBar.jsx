import React from "react";

export default function ProgressBar({ value = 0 }) {
  return (
    <div style={{ width: "100%", background: "#e0e0e0", borderRadius: "4px", height: "20px" }}>
      <div 
        style={{
          width: `${value}%`,
          background: value < 100 ? "#4caf50" : "#00c853",
          height: "100%",
          borderRadius: "4px",
          transition: "width 0.5s ease"
        }}
      />
    </div>
  );
}
