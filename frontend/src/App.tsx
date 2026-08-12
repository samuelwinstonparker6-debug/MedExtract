import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { Sidebar } from "@/components/layout/Sidebar";

import Dashboard from "@/pages/Dashboard";
import Upload from "@/pages/Upload";
import Queue from "@/pages/Queue";
import Similarity from "@/pages/Similarity";
import Analysis from "@/pages/Analysis";
import ProviderTemplates from "@/pages/ProviderTemplates";
import LicenseKeys from "@/pages/LicenseKeys";
import About from "@/pages/About";

function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-slate-950 text-slate-100">
        <Sidebar />
        <main className="flex-1 ml-64 min-h-screen">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/analysis/:id" element={<Analysis />} />
            <Route path="/similarity/:id" element={<Similarity />} />
            <Route path="/queue" element={<Queue />} />
            <Route path="/templates" element={<ProviderTemplates />} />
            <Route path="/license-keys" element={<LicenseKeys />} />
            <Route path="/about" element={<About />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

