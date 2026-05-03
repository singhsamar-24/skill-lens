import { CheckCircle2, CircleAlert, XCircle } from "lucide-react";
import type { CompareResponse } from "../types";

export function SkillDistribution({ comparison }: { comparison?: CompareResponse }) {
  const verified = comparison?.verified_skills.length ?? 0;
  const weak = comparison?.claimed_unproven_skills.length ?? 0;
  const missing = comparison?.missing_skills.length ?? 0;
  const total = Math.max(1, verified + weak + missing);
  const segments = [
    { label: "Verified", value: verified, className: "bg-emerald-600", Icon: CheckCircle2, text: "text-emerald-700" },
    { label: "Weak", value: weak, className: "bg-amber-500", Icon: CircleAlert, text: "text-amber-700" },
    { label: "Missing", value: missing, className: "bg-red-500", Icon: XCircle, text: "text-red-700" },
  ];

  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-tight">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-ink">Skill distribution</p>
          <p className="mt-1 text-sm text-muted">Verified, weak, and missing signals</p>
        </div>
        <span className="text-sm font-semibold text-muted">{comparison ? `${verified + weak + missing} tracked` : "Pending"}</span>
      </div>
      <div className="mt-5 flex h-3 overflow-hidden rounded-full bg-slate-100">
        {segments.map((segment) => (
          <div
            key={segment.label}
            className={segment.className}
            style={{ width: comparison ? `${Math.max(segment.value ? 6 : 0, (segment.value / total) * 100)}%` : "0%" }}
          />
        ))}
      </div>
      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        {segments.map(({ label, value, Icon, text }) => (
          <div key={label} className="rounded-lg border border-line p-3">
            <div className={`flex items-center gap-2 ${text}`}>
              <Icon size={16} />
              <span className="text-xs font-semibold uppercase tracking-[0.14em]">{label}</span>
            </div>
            <p className="mt-2 text-2xl font-semibold text-ink">{comparison ? value : "--"}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
