import { Lightbulb, MoveUpRight } from "lucide-react";
import type { CompareResponse } from "../types";
import { priorityClass } from "../lib/format";

export function InsightPanel({ comparison }: { comparison?: CompareResponse }) {
  const insights = comparison?.insights ?? [];
  const fallback = comparison?.recommendations ?? [];

  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-tight">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-ink">Judge-ready insights</p>
          <p className="mt-1 text-sm text-muted">What SkillLens can explain in the demo</p>
        </div>
        <div className="grid h-10 w-10 place-items-center rounded-md bg-slate-50 text-ink">
          <Lightbulb size={18} />
        </div>
      </div>
      <div className="mt-4 space-y-3">
        {insights.length ? (
          insights.slice(0, 4).map((item) => (
            <div key={item.title} className="rounded-lg border border-line p-3 transition hover:bg-slate-50">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-semibold text-ink">{item.title}</p>
                <span className={`rounded-full border px-2 py-1 text-xs font-semibold ${priorityClass(item.severity)}`}>{item.severity}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-muted">{item.detail}</p>
            </div>
          ))
        ) : fallback.length ? (
          fallback.slice(0, 4).map((item) => (
            <div key={item} className="flex gap-3 rounded-lg border border-line p-3 transition hover:bg-slate-50">
              <MoveUpRight className="mt-0.5 shrink-0 text-emerald-600" size={16} />
              <p className="text-sm leading-6 text-muted">{item}</p>
            </div>
          ))
        ) : (
          <p className="rounded-lg border border-dashed border-line p-4 text-sm leading-6 text-muted">
            Run an analysis to see over-claimed, under-sold, and strongest-area insights.
          </p>
        )}
      </div>
    </section>
  );
}
