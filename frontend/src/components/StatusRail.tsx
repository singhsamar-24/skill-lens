import { CheckCircle2, CircleDashed, Loader2, XCircle } from "lucide-react";
import { useAnalysis } from "../state/analysis-store";
import { cx } from "../lib/format";

const labels = {
  github: "GitHub",
  resume: "Resume",
  leetcode: "LeetCode",
  compare: "Compare",
  roadmap: "Roadmap",
};

export function StatusRail() {
  const { statuses } = useAnalysis();
  return (
    <div className="grid gap-2 sm:grid-cols-5">
      {Object.entries(statuses).map(([key, status]) => (
        <div key={key} className="flex items-center gap-2 rounded-lg border border-line bg-white px-3 py-2 text-sm">
          {status === "loading" ? <Loader2 className="animate-spin text-accent" size={16} /> : null}
          {status === "ready" ? <CheckCircle2 className="text-emerald-600" size={16} /> : null}
          {status === "error" ? <XCircle className="text-red-600" size={16} /> : null}
          {status === "idle" ? <CircleDashed className="text-slate-400" size={16} /> : null}
          <span className="font-medium text-ink">{labels[key as keyof typeof labels]}</span>
          <span className={cx("ml-auto text-xs capitalize", status === "error" ? "text-red-600" : "text-muted")}>{status}</span>
        </div>
      ))}
    </div>
  );
}
