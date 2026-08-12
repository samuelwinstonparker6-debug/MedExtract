import { NavLink } from "react-router-dom";
import { 
  LayoutDashboard, 
  UploadCloud, 
  AlertTriangle, 
  FileSearch,
  KeyRound,
  Info,
} from "lucide-react";

export function Sidebar() {
  const links = [
    { to: "/", icon: <LayoutDashboard size={20} />, label: "Dashboard" },
    { to: "/upload", icon: <UploadCloud size={20} />, label: "Upload Documents" },
    { to: "/templates", icon: <FileSearch size={20} />, label: "Provider Templates" },
    { to: "/license-keys", icon: <KeyRound size={20} />, label: "License Generator" },
    { to: "/about", icon: <Info size={20} />, label: "About" },
    { to: "/queue", icon: <AlertTriangle size={20} />, label: "Investigation Queue" },
  ];

  return (
    <div className="w-64 bg-slate-900 h-screen text-slate-300 flex flex-col border-r border-slate-800 fixed left-0 top-0">
      <div className="h-16 flex items-center px-6 border-b border-slate-800">
        <div className="flex items-center gap-2 text-white font-bold text-xl tracking-tight">
          <span className="text-blue-500">Med</span>Extract
        </div>
      </div>
      <div className="flex-1 py-4 flex flex-col gap-1 px-3">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                isActive 
                  ? "bg-blue-600/10 text-blue-400 font-medium" 
                  : "hover:bg-slate-800 hover:text-white"
              }`
            }
          >
            {link.icon}
            <span>{link.label}</span>
          </NavLink>
        ))}
      </div>
      <div className="p-4 text-xs text-slate-600 border-t border-slate-800">
        v2.0.0 Enterprise Edition
      </div>
    </div>
  );
}

