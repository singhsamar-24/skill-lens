import { NavLink, Outlet, Link } from "react-router-dom";
import { BarChart3, GitCompare, GraduationCap, LayoutDashboard, MessagesSquare, Sparkles } from "lucide-react";
import { cx } from "../lib/format";
import { motion, AnimatePresence } from "framer-motion";

const nav = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/compare", label: "Compare", icon: GitCompare },
  { to: "/roadmap", label: "Roadmap", icon: GraduationCap },
  { to: "/mentor", label: "Mentor", icon: MessagesSquare },
  { to: "/insights", label: "Insights", icon: BarChart3 },
];

export function AppShell() {
  return (
    <div className="min-h-screen bg-[#FDFDFE] text-ink font-sans">
      <header className="sticky top-0 z-50 border-b border-line bg-white/70 backdrop-blur-xl">
        <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <NavLink to="/" className="group flex items-center gap-3">
            <motion.div 
              whileHover={{ rotate: 180 }}
              className="grid h-10 w-10 place-items-center rounded-xl bg-ink text-white shadow-lg transition-all group-hover:bg-accent"
            >
              <Sparkles size={20} />
            </motion.div>
            <div className="flex flex-col">
              <span className="text-lg font-bold tracking-tight">SkillLens</span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-muted">Verification Platform</span>
            </div>
          </NavLink>
          <nav className="hidden items-center gap-1 md:flex">
            {nav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cx(
                    "relative inline-flex h-11 items-center gap-2 rounded-xl px-4 text-[13px] font-bold transition-all",
                    isActive ? "bg-slate-100 text-ink shadow-sm" : "text-muted hover:bg-slate-50 hover:text-ink",
                  )
                }
              >
                <item.icon size={16} />
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="flex items-center gap-4">
            <Link to="/#verification-station">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="rounded-xl bg-ink px-6 py-2.5 text-xs font-bold uppercase tracking-widest text-white shadow-lg hover:bg-slate-800"
              >
                Get Started
              </motion.button>
            </Link>
          </div>
        </div>
        <nav className="no-scrollbar flex gap-2 overflow-x-auto border-t border-line px-4 py-3 md:hidden bg-white">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cx(
                  "inline-flex h-10 shrink-0 items-center gap-2 rounded-xl px-4 text-xs font-bold transition-all",
                  isActive ? "bg-slate-100 text-ink shadow-sm" : "text-muted",
                )
              }
            >
              <item.icon size={15} />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="relative">
        {/* Background glow for all pages */}
        <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute -top-24 left-1/2 h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-accent/5 blur-[120px]" />
        </div>
        <Outlet />
      </main>
    </div>
  );
}
