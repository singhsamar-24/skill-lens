import type { Priority, SkillLevel } from "../types";

export function pct(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function compactNumber(value: number): string {
  return new Intl.NumberFormat(undefined, { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

export function cx(...values: Array<string | false | null | undefined>): string {
  return values.filter(Boolean).join(" ");
}

export function priorityClass(priority: Priority): string {
  if (priority === "high") return "border-red-200 bg-red-50 text-red-700";
  if (priority === "medium") return "border-amber-200 bg-amber-50 text-amber-700";
  return "border-slate-200 bg-slate-50 text-slate-700";
}

export function levelClass(level?: SkillLevel | string | null): string {
  if (level === "strong" || level === "project_backed") return "border-emerald-200 bg-emerald-50 text-emerald-700";
  if (level === "moderate" || level === "claimed") return "border-amber-200 bg-amber-50 text-amber-700";
  return "border-slate-200 bg-slate-50 text-slate-700";
}

export function confidenceTone(score: number): "good" | "warn" | "bad" {
  if (score >= 0.7) return "good";
  if (score >= 0.4) return "warn";
  return "bad";
}

export function confidenceBarClass(score: number): string {
  const tone = confidenceTone(score);
  if (tone === "good") return "bg-emerald-600";
  if (tone === "warn") return "bg-amber-500";
  return "bg-red-500";
}
