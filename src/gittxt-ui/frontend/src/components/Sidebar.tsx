// src/components/Sidebar.tsx
import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const { pathname } = useLocation();

  const navItems = [
    { label: "Dashboard", to: "/" },
    { label: "New Scan", to: "/scan" },
    { label: "Progress", to: "/progress/example-scan-id" },
    { label: "Artifacts", to: "/artifacts/example-scan-id" },
    { label: "Config", to: "/config" },
  ];

  return (
    <aside
      className={`${
        collapsed ? "w-20" : "w-64"
      } bg-gray-900 text-white flex flex-col justify-between p-4 transition-all duration-300`}
    >
      {/* Header */}
      <div>
        <div className="flex items-center justify-between mb-6">
          {!collapsed && <h1 className="text-xl font-bold">Gittxt</h1>}
          <button onClick={() => setCollapsed(!collapsed)}>
            {collapsed ? <Menu size={20} /> : <X size={20} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex flex-col space-y-3">
          {navItems.map((item) => (
            <Link key={item.to} to={item.to}>
              <Button
                variant={pathname.startsWith(item.to) ? "secondary" : "ghost"}
                className={`justify-start w-full ${
                  collapsed ? "px-2 py-1" : ""
                }`}
              >
                {collapsed ? item.label[0] : item.label}
              </Button>
            </Link>
          ))}
        </nav>
      </div>

      {/* Footer */}
      {!collapsed && (
        <div className="text-xs text-gray-400 mt-6">LLM Dataset Extractor</div>
      )}
    </aside>
  );
}
