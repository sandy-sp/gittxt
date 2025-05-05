import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import Home from "./pages/Home";
import Upload from "./pages/Upload";
import ScanDashboard from "./pages/ScanDashboard";

const router = createBrowserRouter([
  { element: <App />, children: [
      { path: "/", element: <Home /> },
      { path: "/upload", element: <Upload /> },
      { path: "/scan/:id", element: <ScanDashboard /> },
    ]},
]);

export default router;
