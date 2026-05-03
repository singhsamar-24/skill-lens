import type { ReactNode } from "react";
import { motion, HTMLMotionProps } from "framer-motion";
import { cx } from "../lib/format";

export function Page({ children, className, narrow = false }: { children: ReactNode; className?: string, narrow?: boolean }) {
  return (
    <motion.main
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className={cx(
        "mx-auto w-full px-4 py-8 sm:px-6 lg:px-8",
        narrow ? "max-w-5xl" : "max-w-7xl",
        className
      )}
    >
      {children}
    </motion.main>
  );
}

export function Panel({ children, className, hoverable = false }: { children: ReactNode; className?: string, hoverable?: boolean }) {
  return (
    <div 
      className={cx(
        "rounded-2xl border border-line bg-white p-6 shadow-tight transition-all duration-300",
        hoverable && "hover:border-accent/40 hover:shadow-soft hover:-translate-y-1",
        className
      )}
    >
      {children}
    </div>
  );
}

export function GlassPanel({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cx("rounded-3xl border border-line bg-white/70 shadow-soft backdrop-blur-xl p-6", className)}>
      {children}
    </div>
  );
}

export function SectionTitle({ kicker, title, action, description }: { kicker?: string; title: string; action?: ReactNode; description?: string }) {
  return (
    <div className="mb-8 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
      <div className="space-y-1">
        {kicker ? <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-accent">{kicker}</p> : null}
        <h2 className="text-3xl font-bold tracking-tight text-ink">{title}</h2>
        {description ? <p className="max-w-2xl text-sm text-muted">{description}</p> : null}
      </div>
      {action ? <div className="mt-4 sm:mt-0">{action}</div> : null}
    </div>
  );
}

export function Button({
  children,
  className,
  variant = "primary",
  size = "md",
  ...props
}: HTMLMotionProps<"button"> & { variant?: "primary" | "secondary" | "ghost" | "accent", size?: "sm" | "md" | "lg" }) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={cx(
        "inline-flex items-center justify-center gap-2 rounded-xl font-bold transition-all disabled:cursor-not-allowed disabled:opacity-40",
        size === "sm" && "h-9 px-3 text-xs",
        size === "md" && "h-11 px-5 text-sm",
        size === "lg" && "h-14 px-8 text-base",
        variant === "primary" && "bg-ink text-white hover:bg-slate-800 shadow-lg shadow-ink/10",
        variant === "secondary" && "border border-line bg-white text-ink hover:bg-slate-50 shadow-sm",
        variant === "accent" && "bg-accent text-white hover:bg-emerald-600 shadow-lg shadow-accent/20",
        variant === "ghost" && "bg-transparent text-muted hover:text-ink hover:bg-slate-50",
        className,
      )}
      {...props}
    >
      {children}
    </motion.button>
  );
}

export function SkeletonBlock({ className }: { className?: string }) {
  return <div className={cx("skeleton rounded-xl", className)} />;
}

export function EmptyState({ title, body, icon: Icon }: { title: string; body: string; icon?: any }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-3xl border border-dashed border-line bg-slate-50/50 p-12 text-center">
      {Icon && (
        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-white text-slate-300 shadow-sm">
          <Icon size={32} />
        </div>
      )}
      <p className="text-base font-bold text-ink">{title}</p>
      <p className="mx-auto mt-2 max-w-sm text-sm leading-relaxed text-muted">{body}</p>
    </div>
  );
}

export function StatusPill({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "good" | "warn" | "blue" | "bad" }) {
  return (
    <span
      className={cx(
        "inline-flex items-center rounded-full border px-3 py-1 text-[11px] font-bold uppercase tracking-wider transition-colors",
        tone === "neutral" && "border-slate-200 bg-slate-100 text-slate-600",
        tone === "good" && "border-emerald-200 bg-emerald-50 text-emerald-700",
        tone === "warn" && "border-amber-200 bg-amber-50 text-amber-700",
        tone === "blue" && "border-blue-200 bg-blue-50 text-blue-700",
        tone === "bad" && "border-red-200 bg-red-50 text-red-700",
      )}
    >
      {children}
    </span>
  );
}
