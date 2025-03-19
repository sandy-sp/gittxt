// src/components/Sidebar.tsx
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";

export default function Sidebar() {
  const location = useLocation();
  const navItems = [
    { label: "Dashboard", path: "/" },
    { label: "New Scan", path: "/scan" },
    { label: "Progress", path: "/progress/example-scan-id" },
    { label: "Artifacts", path: "/artifacts/example-scan-id" },
    { label: "Config", path: "/config" },
  ];

  return (
    <aside className="w-64 bg-gray-900 text-white p-6 space-y-6">
      <h1 className="text-2xl font-bold">Gittxt UI</h1>
      <nav className="flex flex-col space-y-4">
        {navItems.map((item) => (
          <Link key={item.path} to={item.path}>
            <Button
              variant={location.pathname.startsWith(item.path) ? "default" : "ghost"}
              className="justify-start w-full"
            >
              {item.label}
            </Button>
          </Link>
        ))}
      </nav>
      <div className="mt-10 text-sm text-gray-400">LLM Dataset Extractor</div>
    </aside>
  );
}
