import { useMemo, useState } from "react";
import { ArrowDownUp, FileUp, Loader2, SearchCheck, UsersRound } from "lucide-react";
import { motion } from "framer-motion";
import { api } from "../lib/api";
import { priorityClass } from "../lib/format";
import type { RecruiterCandidateSummary, RecruiterEvaluationResult, RecruiterRankItem } from "../types";
import { Button, EmptyState, Page, Panel, SectionTitle, StatusPill } from "../components/ui";

const roleOptions = ["Software Engineer", "Backend Engineer", "Frontend Engineer", "Full Stack Engineer", "AI Engineer", "DevOps Engineer"];

export function Recruiter() {
  const [files, setFiles] = useState<File[]>([]);
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [uploaded, setUploaded] = useState<RecruiterCandidateSummary[]>([]);
  const [ranked, setRanked] = useState<RecruiterRankItem[]>([]);
  const [evaluations, setEvaluations] = useState<RecruiterEvaluationResult[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "evaluating" | "ranking" | "ready" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  const selectedRank = ranked.find((candidate) => candidate.candidate_id === selectedId) ?? ranked[0];
  const selectedEvaluation = evaluations.find((candidate) => candidate.candidate_id === selectedRank?.candidate_id);

  const stats = useMemo(() => {
    const average = ranked.length ? Math.round(ranked.reduce((sum, item) => sum + item.match_score, 0) / ranked.length) : 0;
    return { average, strong: ranked.filter((item) => item.match_score >= 70).length };
  }, [ranked]);

  async function uploadResumes() {
    if (!files.length) return;
    setStatus("uploading");
    setError(null);
    try {
      const response = await api.recruiterUpload(files);
      setUploaded(response.candidates);
      setRanked([]);
      setEvaluations([]);
      setSelectedId(response.candidates[0]?.id ?? null);
      setStatus("ready");
    } catch (uploadError) {
      setError((uploadError as Error).message);
      setStatus("error");
    }
  }

  async function evaluateCandidates() {
    setStatus("evaluating");
    setError(null);
    try {
      const evaluation = await api.recruiterEvaluate({ target_role: targetRole });
      const ranking = await api.recruiterRank(targetRole);
      setEvaluations(evaluation.results);
      setRanked(ranking.candidates);
      setSelectedId(ranking.candidates[0]?.candidate_id ?? evaluation.results[0]?.candidate_id ?? null);
      setStatus("ready");
    } catch (evaluateError) {
      setError((evaluateError as Error).message);
      setStatus("error");
    }
  }

  async function refreshRanking() {
    setStatus("ranking");
    setError(null);
    try {
      const ranking = await api.recruiterRank(targetRole);
      setRanked(ranking.candidates);
      setSelectedId(ranking.candidates[0]?.candidate_id ?? null);
      setStatus("ready");
    } catch (rankError) {
      setError((rankError as Error).message);
      setStatus("error");
    }
  }

  const busy = status === "uploading" || status === "evaluating" || status === "ranking";

  return (
    <Page>
      <div className="mb-10 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <StatusPill tone="blue">Recruiter Console</StatusPill>
          <h1 className="mt-4 text-4xl font-bold tracking-tight text-ink sm:text-5xl">Candidate ranking, from evidence.</h1>
          <p className="mt-4 max-w-3xl text-base font-medium leading-7 text-muted">
            Upload resumes, evaluate every candidate against a target role, and rank the pool with the same SkillLens evidence engine.
          </p>
        </div>
        <div className="grid grid-cols-2 gap-3 sm:min-w-72">
          <div className="rounded-lg border border-line bg-white p-4">
            <p className="text-xs font-bold uppercase tracking-widest text-muted">Average</p>
            <p className="mt-2 text-3xl font-bold text-ink">{stats.average}</p>
          </div>
          <div className="rounded-lg border border-line bg-white p-4">
            <p className="text-xs font-bold uppercase tracking-widest text-muted">Strong Fits</p>
            <p className="mt-2 text-3xl font-bold text-ink">{stats.strong}</p>
          </div>
        </div>
      </div>

      {error ? (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700">{error}</div>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.4fr]">
        <div className="space-y-6">
          <Panel>
            <SectionTitle kicker="Upload" title="Resume Batch" description="PDF resumes are parsed once, stored, and reused for ranking." />
            <label className="flex min-h-44 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-slate-300 bg-slate-50 px-6 text-center transition hover:border-accent hover:bg-white">
              <FileUp className="text-accent" size={30} />
              <span className="mt-3 text-sm font-bold text-ink">Choose PDF resumes</span>
              <span className="mt-1 text-xs font-medium text-muted">{files.length ? `${files.length} selected` : "Multiple files supported"}</span>
              <input
                className="sr-only"
                type="file"
                multiple
                accept="application/pdf"
                onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
              />
            </label>
            <Button className="mt-5 w-full" onClick={uploadResumes} disabled={!files.length || busy}>
              {status === "uploading" ? <Loader2 className="animate-spin" size={17} /> : <FileUp size={17} />}
              Upload Candidates
            </Button>
            {uploaded.length ? (
              <div className="mt-5 space-y-2">
                {uploaded.map((candidate) => (
                  <div key={candidate.id} className="rounded-lg border border-line px-3 py-2">
                    <p className="text-sm font-bold text-ink">{candidate.name}</p>
                    <p className="text-xs text-muted">{candidate.skills.slice(0, 4).map((skill) => skill.normalized).join(", ") || "Skills captured"}</p>
                  </div>
                ))}
              </div>
            ) : null}
          </Panel>

          <Panel>
            <SectionTitle kicker="Evaluate" title="Role Fit" description="Runs comparison, gap explanations, and role mapping for the saved pool." />
            <select
              className="h-12 w-full rounded-lg border border-line bg-white px-4 text-sm font-bold text-ink outline-none focus:border-accent"
              value={targetRole}
              onChange={(event) => setTargetRole(event.target.value)}
            >
              {roleOptions.map((role) => (
                <option key={role}>{role}</option>
              ))}
            </select>
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <Button onClick={evaluateCandidates} disabled={busy || (!uploaded.length && !ranked.length)} variant="accent">
                {status === "evaluating" ? <Loader2 className="animate-spin" size={17} /> : <SearchCheck size={17} />}
                Evaluate
              </Button>
              <Button onClick={refreshRanking} disabled={busy} variant="secondary">
                {status === "ranking" ? <Loader2 className="animate-spin" size={17} /> : <ArrowDownUp size={17} />}
                Refresh Rank
              </Button>
            </div>
          </Panel>
        </div>

        <Panel className="overflow-hidden">
          <SectionTitle
            kicker="Ranking"
            title="Candidate Board"
            description="Sorted by evidence score, with verified strengths and missing role-critical skills."
            action={ranked.length ? <StatusPill tone="good">{ranked.length} ranked</StatusPill> : <StatusPill>Pending</StatusPill>}
          />
          {ranked.length ? (
            <div className="overflow-x-auto">
              <table className="min-w-full border-separate border-spacing-0 text-left">
                <thead>
                  <tr className="text-xs font-bold uppercase tracking-widest text-muted">
                    <th className="border-b border-line pb-3">Rank</th>
                    <th className="border-b border-line pb-3">Candidate</th>
                    <th className="border-b border-line pb-3">Score</th>
                    <th className="border-b border-line pb-3">Signal</th>
                  </tr>
                </thead>
                <tbody>
                  {ranked.map((candidate) => (
                    <tr
                      key={`${candidate.rank}-${candidate.candidate_id}`}
                      className="cursor-pointer align-top"
                      onClick={() => setSelectedId(candidate.candidate_id)}
                    >
                      <td className="border-b border-line py-4 text-sm font-bold text-ink">#{candidate.rank}</td>
                      <td className="border-b border-line py-4">
                        <p className="text-sm font-bold text-ink">{candidate.name}</p>
                        <p className="text-xs text-muted">{candidate.email || candidate.github_username || "No contact detected"}</p>
                      </td>
                      <td className="border-b border-line py-4">
                        <span className="text-xl font-bold text-ink">{candidate.match_score}</span>
                      </td>
                      <td className="border-b border-line py-4">
                        <span className={`rounded-full border px-3 py-1 text-[11px] font-bold uppercase ${priorityClass(candidate.recommendation)}`}>
                          {candidate.recommendation}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState icon={UsersRound} title="No ranked candidates" body="Upload resumes and run evaluation to create the candidate board." />
          )}
        </Panel>
      </div>

      {selectedRank ? (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="mt-6">
          <Panel>
            <SectionTitle kicker="Candidate Detail" title={selectedRank.name} description={`Role target: ${selectedRank.target_role}`} />
            <div className="grid gap-6 lg:grid-cols-3">
              <DetailColumn title="Verified Skills" values={selectedRank.top_verified_skills} empty="No verified skills yet" tone="good" />
              <DetailColumn title="Missing Skills" values={selectedRank.top_missing_skills} empty="No critical gaps" tone="warn" />
              <div className="rounded-lg border border-line p-5">
                <p className="text-xs font-bold uppercase tracking-widest text-muted">Recruiter Notes</p>
                <ul className="mt-4 space-y-3">
                  {(selectedEvaluation?.explanations.recommendations ?? selectedRank.explanations.recommendations ?? []).slice(0, 3).map((item) => (
                    <li key={item} className="text-sm font-medium leading-6 text-muted">{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </Panel>
        </motion.div>
      ) : null}
    </Page>
  );
}

function DetailColumn({ title, values, empty, tone }: { title: string; values: string[]; empty: string; tone: "good" | "warn" }) {
  return (
    <div className="rounded-lg border border-line p-5">
      <p className="text-xs font-bold uppercase tracking-widest text-muted">{title}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {values.length ? values.map((value) => <StatusPill key={value} tone={tone}>{value}</StatusPill>) : <p className="text-sm text-muted">{empty}</p>}
      </div>
    </div>
  );
}
