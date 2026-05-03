import type { ReactNode } from "react";
import { Panel } from "./ui";

export function MetricCard({ label, value, detail, icon }: { label: string; value: string | number; detail: string; icon: ReactNode }) {
  return (
    <Panel className="p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-muted">{label}</p>
          <p className="mt-2 text-3xl font-semibold tracking-normal text-ink">{value}</p>
          <p className="mt-2 text-xs leading-5 text-muted">{detail}</p>
        </div>
        <div className="grid h-10 w-10 place-items-center rounded-md border border-line bg-slate-50 text-accent">{icon}</div>
      </div>
    </Panel>
  );
}
