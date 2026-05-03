import { CheckCircle2 } from "lucide-react";
import type { RoadmapResponse } from "../types";

export function RoadmapTimeline({ roadmap }: { roadmap: RoadmapResponse }) {
  return (
    <div className="space-y-4">
      {roadmap.milestones.map((milestone, index) => (
        <article key={`${milestone.week}-${milestone.title}`} className="relative rounded-lg border border-line p-5">
          <div className="flex flex-wrap items-center gap-3">
            <span className="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">{milestone.week}</span>
            <h3 className="text-lg font-semibold text-ink">{milestone.title}</h3>
          </div>
          <p className="mt-3 text-sm font-medium text-muted">{milestone.project}</p>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">Tasks</p>
              <ul className="mt-3 space-y-2">
                {milestone.tasks.map((task) => (
                  <li key={task} className="flex gap-2 text-sm leading-6 text-muted">
                    <CheckCircle2 className="mt-1 shrink-0 text-emerald-600" size={15} />
                    {task}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">Outcomes</p>
              <ul className="mt-3 space-y-2">
                {milestone.outcomes.map((outcome) => (
                  <li key={outcome} className="text-sm leading-6 text-muted">
                    {outcome}
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <span className="absolute right-4 top-4 text-xs font-semibold text-slate-300">{String(index + 1).padStart(2, "0")}</span>
        </article>
      ))}
    </div>
  );
}
