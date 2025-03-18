import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import Config from "./pages/Config";
import Scan from "./pages/Scan";
import Tree from "./pages/Tree";

function App() {
  return (
    <Router>
      <nav style={{ padding: "1rem", background: "#f3f3f3" }}>
        <Link to="/" style={{ marginRight: "1rem" }}>Home</Link>
        <Link to="/config" style={{ marginRight: "1rem" }}>Config</Link>
        <Link to="/scan" style={{ marginRight: "1rem" }}>Scan</Link>
        <Link to="/tree" style={{ marginRight: "1rem" }}>Tree</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/config" element={<Config />} />
        <Route path="/scan" element={<Scan />} />
        <Route path="/tree" element={<Tree />} />
      </Routes>
    </Router>
  );
}

export default App;
