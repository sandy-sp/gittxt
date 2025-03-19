// src/App.tsx
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import Scan from "./pages/Scan";
import Progress from "./pages/Progress";
import ArtifactsPage from "./pages/ArtifactsPage";
import Config from "./pages/Config";
import ToastProvider from "./components/ToastProvider";
import { ScanProvider } from "./context/ScanContext"; 
import Sidebar from "./components/Sidebar";

export default function App() {
  return (
    <ScanProvider>
      <ToastProvider>
        <Router>
          <div className="flex min-h-screen bg-gray-50">
            {/* Sidebar */}
            <Sidebar />

            {/* Main Content */}
            <main className="flex-1 p-8">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/scan" element={<Scan />} />
                <Route path="/progress/:scanId" element={<Progress />} />
                <Route path="/artifacts/:scanId" element={<ArtifactsPage />} />
                <Route path="/config" element={<Config />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
          </div>
        </Router>
      </ToastProvider>
    </ScanProvider>
  );
}
