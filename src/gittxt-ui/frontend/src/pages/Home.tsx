// src/pages/Home.tsx
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center h-screen space-y-6">
      <h1 className="text-4xl font-bold">Welcome to Gittxt UI</h1>
      <p className="text-lg text-gray-600">Extract AI-ready datasets from GitHub repos.</p>
      <Link
        to="/scan"
        className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition"
      >
        Start New Scan
      </Link>
    </div>
  );
}
