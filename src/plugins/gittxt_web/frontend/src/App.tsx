import { useState, FormEvent } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  NavLink,
  useNavigate,
  Outlet,
  Link,
  useLocation,
} from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Upload, Github } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import api from "@/api";

/**
 * Centralised API helper that automatically prepends the base URL.
 */
const apiHelper = async (path: string, init?: RequestInit) => {
  try {
    const response = await api.request({
      url: path,
      method: init?.method || "GET",
      headers: init?.headers,
      data: init?.body ? JSON.parse(init.body as string) : undefined,
    });
    return response.data;
  } catch (error: any) {
    throw new Error(
      error.response?.data?.message || "An unexpected error occurred."
    );
  }
};

/* ───────────────────────────── Layout ───────────────────────────── */
function Layout({ children }: { children: React.ReactNode }) {
  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `px-3 py-2 rounded-xl transition-all ${
      isActive ? "bg-blue-500 text-white" : "text-gray-600 hover:bg-gray-200"
    }`;

  return (
    <div className="min-h-screen grid grid-rows-[auto_1fr] bg-slate-50">
      {/* Top‑nav */}
      <header className="flex items-center justify-between px-6 py-3 shadow-sm bg-white sticky top-0 z-10">
        <h1 className="text-xl font-bold">Gittxt UI</h1>
        <nav className="flex gap-2 text-sm">
          <NavLink to="/" className={navLinkClass} end>
            Home
          </NavLink>
          <NavLink to="/scan" className={navLinkClass}>
            Scan
          </NavLink>
          <NavLink to="/upload" className={navLinkClass}>
            Upload
          </NavLink>
        </nav>
      </header>
      {/* Routed pages */}
      <main className="p-6 container mx-auto w-full max-w-5xl">{children}</main>
    </div>
  );
}

/* ───────────────────────────── Pages ───────────────────────────── */
function HomePage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="prose lg:prose-xl"
    >
      <h2>Welcome to Gittxt Web</h2>
      <p>
        Use the navigation bar to scan a public GitHub repository, upload a ZIP,
        and view generated summaries ready for LLM consumption.
      </p>
    </motion.div>
  );
}

function ScanPage() {
  const [repo, setRepo] = useState("https://github.com/sandy-sp/gittxt");
  const [branch, setBranch] = useState<string>("");
  const [message, setMessage] = useState<string>("");
  const navigate = useNavigate();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setMessage("Scanning… this may take a bit ⌛");
    try {
      const payload = { repo_path: repo, branch: branch || undefined };
      const data = await apiHelper("/v1/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setMessage("✅ Scan complete! Redirecting…");
      navigate(`/summary/${data.data.scan_id}`);
    } catch (err: any) {
      setMessage(`❌ ${err.message}`);
    }
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <Card className="p-6 max-w-xl mx-auto">
        <CardContent className="space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Github size={18} /> Scan a Git repo
          </h2>
          <form onSubmit={handleSubmit} className="space-y-3">
            <Input
              value={repo}
              onChange={(e) => setRepo(e.target.value)}
              placeholder="https://github.com/user/repo"
            />
            <Input
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              placeholder="branch (optional)"
            />
            <Button type="submit" className="w-full">
              Start scan
            </Button>
          </form>
          {message && <p className="text-sm text-gray-700">{message}</p>}
        </CardContent>
      </Card>
    </motion.div>
  );
}

function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [note, setNote] = useState<string>("");
  const navigate = useNavigate();

  const handleUpload = async () => {
    if (!file) return;
    setNote("Uploading & scanning…");
    const form = new FormData();
    form.append("file", file);
    try {
      const data = await apiHelper("/v1/upload", {
        method: "POST",
        body: form,
      });
      navigate(`/summary/${data.data.scan_id}`);
    } catch (err: any) {
      setNote(`❌ ${err.message}`);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <Card className="p-6 max-w-xl mx-auto">
        <CardContent className="space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Upload size={18} /> Upload zipped repo
          </h2>
          <Input
            type="file"
            accept=".zip"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          <Button onClick={handleUpload} disabled={!file} className="w-full">
            Upload & scan
          </Button>
          {note && <p className="text-sm text-gray-700">{note}</p>}
        </CardContent>
      </Card>
    </motion.div>
  );
}

function SummaryPage() {
  // Placeholder – implement token charts / tree viewer later
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <h2 className="text-2xl font-bold mb-4">Summary</h2>
      <p>Coming soon – file breakdown, token charts, download links…</p>
    </motion.div>
  );
}

/* ───────────────────────────── App Router ───────────────────────────── */
export default function App() {
  const loc = useLocation();
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-background text-foreground">
        <header className="border-b p-4 flex justify-between items-center">
          <Link to="/" className="font-bold text-lg">
            gittxt{" "}
            <span className="text-primary" style={{ fontWeight: "inherit" }}>
              web
            </span>
          </Link>
          <Button asChild variant="outline">
            <a href="https://github.com/your-org/gittxt">GitHub</a>
          </Button>
        </header>

        <main className="flex-1 container mx-auto p-4">
          <AnimatePresence mode="wait">
            <motion.div
              key={loc.pathname}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              <Layout>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/scan" element={<ScanPage />} />
                  <Route path="/upload" element={<UploadPage />} />
                  <Route path="/summary/:id" element={<SummaryPage />} />
                </Routes>
              </Layout>
            </motion.div>
          </AnimatePresence>
        </main>

        <footer className="border-t p-4 text-xs text-muted-foreground text-center">
          © {new Date().getFullYear()} gittxt
        </footer>
      </div>
    </Router>
  );
}
