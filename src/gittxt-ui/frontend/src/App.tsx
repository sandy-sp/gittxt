// src/App.tsx
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import Home from "./pages/Home";
import Scan from "./pages/Scan";
import Progress from "./pages/Progress";
import ArtifactsPage from "./pages/ArtifactsPage";
import Config from "./pages/Config";
import ToastProvider from "./components/ToastProvider";

export default function App() {
  return (
    <ToastProvider>
      <Router>
        <div className="flex min-h-screen bg-gray-50">
          {/* Sidebar */}
          <aside className="w-64 bg-gray-900 text-white flex flex-col justify-between p-6 space-y-6">
            <div>
              <h1 className="text-2xl font-bold mb-6">Gittxt UI</h1>
              <nav className="flex flex-col space-y-4">
                <Link to="/">
                  <Button variant="ghost" className="justify-start w-full">Dashboard</Button>
                </Link>
                <Link to="/scan">
                  <Button variant="ghost" className="justify-start w-full">New Scan</Button>
                </Link>
                <Link to="/progress/example-scan-id">
                  <Button variant="ghost" className="justify-start w-full">Progress</Button>
                </Link>
                <Link to="/artifacts/example-scan-id">
                  <Button variant="ghost" className="justify-start w-full">Artifacts</Button>
                </Link>
                <Link to="/config">
                  <Button variant="ghost" className="justify-start w-full">Config</Button>
                </Link>
              </nav>
            </div>
            <div className="text-sm text-gray-400 mt-6">
              LLM Dataset Extractor
            </div>
          </aside>

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
  );
}
